#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

from pyutilib.component.core import Plugin, implements
from coopr.pyomo import *
from coopr.pyomo.expr.canonical_repn import LinearCanonicalRepn
from coopr.gdp import *

import logging
logger = logging.getLogger('coopr.pyomo')


class BigM_Transformation(object):

    def __init__(self):
        self.handlers = {
            Constraint : self._xform_constraint,
            Var : self._xform_var,
            Connector : self._xform_skip,
            Param : self._xform_skip,
            }

    def apply(self, **kwds):
        options = kwds.pop('options', {})
        model = kwds.pop('model', None)
        instance = kwds.pop('instance', None)

        for block in instance.all_blocks():
            self._transformBlock(block)

        # REQUIRED: re-call preprocess()
        instance.preprocess()


    def _transformBlock(self, block):
        for disjunct in list(block.components(Disjunct).itervalues()):
            for d in disjunct.itervalues():
                self._bigM_transform(d, block)
            block.reclassify_subcomponent_type(disjunct, Block)


        # Recreate each Disjunction as a simple constraint
        for name, obj in block.components(Disjunction).iteritems():
            def _cGenerator(block, *idx):
                if idx == ():
                    cData = obj._data[None]
                else:
                    cData = obj._data[idx]
                if cData._equality:
                    return (cData.body, cData.upper)
                else:
                    return (cData.lower, cData.body, cData.upper)
            if obj.dim() == 0:
                newC = Constraint(rule=_cGenerator)
            elif obj._index_set:
                newC = Constraint(*obj._index_set, rule=_cGenerator)
            else:
                newC = Constraint(obj.index_set(), rule=_cGenerator)
            block.del_component(name)
            block.add_component(name, newC)
            newC.construct()


    def _bigM_transform(self, disjunct, block):
        # Transform each component within this disjunct
        for name, obj in list(disjunct.components().iteritems()):
            handler = self.handlers.get(obj.type(), None)
            if handler is None:
                raise GDP_Error(
                    "No BigM transformation handler registered "
                    "for modeling components of type %s" % obj.type() )
            handler(name, obj, disjunct, block)


    def _xform_skip(self, _name, constraint, disjunct, block):
        pass

    def _xform_constraint(self, _name, constraint, disjunct, block):
        M = disjunct.next_M()
        lin_body_suffix = block.subcomponent("lin_body")
        if (lin_body_suffix is None) or (not lin_body_suffix.type() is Suffix) or (not lin_body_suffix.active is True):
            lin_body_suffix = None
        for cname, c in constraint._data.iteritems():
            if not c.active:
                continue
            c.active = False

            name = _name + (cname and '.'+cname or '')

            if (not lin_body_suffix is None) and (not lin_body_suffix.getValue(c) is None):
                raise GDP_Error('GDP(BigM) cannot process linear ' \
                      'constraint bodies (yet) (found at ' + name + ').')

            if isinstance(M, list):
                if len(M):
                    m = M.pop(0)
                else:
                    m = (None,None)
            else:
                m = M
            if not isinstance(m, tuple):
                if m is None:
                    m = (None, None)
                else:
                    m = (-1*m,m)

            # If we need an M (either for upper and/or lower bounding of
            # the expression, then try and estimate it
            if ( c.lower is not None and m[0] is None ) or \
                   ( c.upper is not None and m[1] is None ):
                m = self._estimate_M(c.body, name, m)

            bounds = (c.lower, c.upper)
            for i in (0,1):
                if bounds[i] is None:
                    continue
                if m[i] is None:
                    raise GDP_Error("Cannot relax disjunctive " + \
                          "constraint %s because M is not defined." % name)
                n = name;
                if bounds[1-i] is None:
                    n += '_eq'
                else:
                    n += ('_lo','_hi')[i]

                if __debug__ and logger.isEnabledFor(logging.DEBUG):
                    logger.debug("GDP(BigM): Promoting local constraint "
                                 "'%s' as '%s'", constraint.name, n)
                M_expr = (m[i]-bounds[i])*(1-disjunct.indicator_var)
                if i == 0:
                    newC = Constraint(expr=c.lower <= c.body - M_expr)
                else:
                    newC = Constraint(expr=c.body - M_expr <= c.upper)
                disjunct.add_component(n, newC)
                newC.construct()


    def _xform_var(self, name, var, disjunct, block):
        pass
        # "Promote" the local variables up to the main model
        #if __debug__ and logger.isEnabledFor(logging.DEBUG):
        #    logger.debug("GDP(BigM): Promoting local variable '%s' as '%s'",
        #                 var.name, name)
        #block.add_component(name, var)


    def _estimate_M(self, expr, name, m):
        # Calculate a best guess at M
        repn = generate_canonical_repn(expr)
        M = [0,0]

        if not isinstance(repn, LinearCanonicalRepn):
            logger.error("GDP(BigM): cannot estimate M for nonlinear "
                         "expressions.\n\t(found while processing %s)",
                         name)
            return m

        if repn.constant != None:
            for i in (0,1):
                if M[i] is not None:
                    M[i] += repn.constant

        for i in xrange(0,len(repn.linear)):
            var = repn.variables[i]
            coef = repn.linear[i]
            bounds = (value(var.lb), value(var.ub))
            for i in (0,1):
                # reverse the bounds if the coefficient is negative
                if coef > 0:
                    j = i
                else:
                    j = 1-i

                try:
                    M[j] += value(bounds[i]) * coef
                except:
                    M[j] = None


        # Allow user-defined M values to override the estimates
        for i in (0,1):
            if m[i] is not None:
                M[i] = m[i]
        return tuple(M)


class BigM_Transformation_Plugin(Plugin):
    implements(IPyomoScriptModifyInstance)

    def __init__(self):
        Plugin.__init__(self)

    def apply(self, **kwds):
        xform = BigM_Transformation()
        return xform.apply(**kwds)


transform = BigM_Transformation_Plugin()
