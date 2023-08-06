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
from coopr.pyomo.base import expr
from coopr.pyomo.base.var import _VarData
from coopr.gdp import *

import logging
logger = logging.getLogger('coopr.pyomo')

class ConvexHull_Transformation(object):

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
        disaggregatedVars = {}

        for disjunct in block.components(Disjunct).itervalues():
            if disjunct._data:
                for d in disjunct._data.itervalues():
                    self._transform_disjunct(d, block, disaggregatedVars)
            else:
                self._transform_disjunct(disjunct, block, disaggregatedVars)

        def _generate_name(idx):
            if type(idx) in (tuple, list):
                if len(idx) == 0:
                    return ''
                else:
                    return '['+','.join([_generate_name(x) for x in idx])+']'
            else:
                return str(idx)

        # Correlate the disaggregated variables across the disjunctions
        disjunctions = block.components(Disjunction)
        for Disj in disjunctions.itervalues():
            for idx, disjuncts in Disj._disjuncts.iteritems():
                localVars = {}
                cName = _generate_name(idx)
                cName = Disj.cname() + (len(cName) and "."+cName or "")
                for d in disjuncts:
                    for eid, e in disaggregatedVars.get(id(d), ['',{}])[1].iteritems():
                        localVars.setdefault(eid, (e[0],[]))[1].append(e[2])
                for d in disjuncts:
                    for eid, v in localVars.iteritems():
                        if eid not in disaggregatedVars.get(id(d), ['',{}])[1]:
                            tmp = Var(domain=v[0].domain)
                            tmp.setlb(min(0,value(v[0].lb)))
                            tmp.setub(max(0,value(v[0].ub)))
                            disaggregatedVars[id(d)][1][eid] = (v[0], d.indicator_var, tmp)
                            v[1].append(tmp)
                for v in sorted(localVars.values(), key=lambda x: x[0].cname()):
                    newC = Constraint( expr = v[0] == sum(v[1]) )
                    block.add_component( cName+"."+v[0].cname(), newC )
                    newC.construct()

        # Promote the local disaggregated variables and add BigM
        # constraints to force them to 0 when not active.
        for d_data in sorted(disaggregatedVars.values(), key=lambda x: x[0]):
            for e in sorted(d_data[1].values(), key=lambda x: x[0].cname()):
                # add the disaggregated variable
                block.add_component( d_data[0]+e[0].cname(), e[2] )
                e[2].construct()
                # add Big-M constraints on disaggregated variable to
                # force to 0 if not active
                if e[2].lb is not None and value(e[2].lb) != 0:
                    newC = Constraint(expr=value(e[2].lb) * e[1] <= e[2])
                    block.add_component( d_data[0]+e[0].cname()+"_lo", newC )
                    newC.construct()
                if e[2].ub is not None and value(e[2].ub) != 0:
                    newC = Constraint(expr=e[2] <= value(e[2].ub) * e[1])
                    block.add_component( d_data[0]+e[0].cname()+"_hi", newC )
                    newC.construct()

        # Recreate each Disjunction as a simple constraint
        #
        # Note: we do this at the end because the "disjunctions" opject
        # is a lightweight reference to the underlying component data:
        # replacing Disjunctions with Constraints results in this
        # PseudoMap being *empty* after this block!
        for name, obj in disjunctions.iteritems():
            def _cGenerator(block, *idx):
                if idx == None:
                    cData = obj._data[None]
                else:
                    cData = obj._data[idx]
                if cData._equality:
                    return (cData.body, cData.upper)
                else:
                    return (cData.lower, cData.body, cData.upper)
            newC = Constraint(obj._index, rule=_cGenerator)
            block.del_component(name)
            block.add_component(name, newC)
            newC.construct()


    def _transform_disjunct(self, disjunct, block, disaggregatedVars):
        # Calculate a unique name by concatenating all parent block names
        fullName = disjunct.cname(True)

        varMap = disaggregatedVars.setdefault(id(disjunct), [fullName,{}])[1]

        # Transform each component within this disjunct
        for name, obj in disjunct.components().iteritems():
            handler = self.handlers.get(obj.type(), None)
            if handler is None:
                raise GDP_Error(
                    "No cHull transformation handler registered "
                    "for modeling components of type %s" % obj.type() )
            handler(fullName+name, obj, varMap, disjunct, block)


    def _xform_skip(self, _name, var, varMap, disjunct, block):
        pass


    def _xform_var(self, name, var, varMap, disjunct, block):
        # "Promote" the local variables up to the main model
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug("GDP(cHull): Promoting local variable '%s' as '%s'",
                         var.cname(), name)
        block.add_component(name, var)


    def _xform_constraint(self, _name, constraint, varMap, disjunct, block):
        lin_body_suffix = block.subcomponent("lin_body")
        if (lin_body_suffix is None) or (not lin_body_suffix.type() is Suffix) or (not lin_body_suffix.active is True):
            lin_body_suffix = None
        for cname, c in constraint._data.iteritems():
            name = _name + (cname and '.'+cname or '')

            if (not lin_body_suffix is None) and (not lin_body_suffix.getValue(c) is None):
                raise GDP_Error('GDP(cHull) cannot process linear ' \
                      'constraint bodies (yet) (found at ' + name + ').')

            constant = 0
            try:
                cannonical = generate_canonical_repn(c.body)
                if isinstance(cannonical, LinearCanonicalRepn):
                    NL = False
                else:
                    NL = canonical_is_nonlinear(cannonical)
            except:
                NL = True
            exp = self._var_subst(NL, c.body, disjunct.indicator_var, varMap)
            if NL:
                exp = exp * disjunct.indicator_var
            else:
                # We need to make sure to pull out the constant terms
                # from the expression and put them into the lb/ub
                if cannonical.constant == None:
                    constant = 0
                else:
                    constant = cannonical.constant

            if c.lower is not None:
                if __debug__ and logger.isEnabledFor(logging.DEBUG):
                    logger.debug("GDP(cHull): Promoting constraint " +
                                 "'%s' as '%s_lo'", name, name)
                bound = c.lower() - constant
                if bound != 0:
                    newC = Constraint( expr = bound*disjunct.indicator_var \
                                       <= exp - constant )
                else:
                    newC = Constraint( expr = bound <= exp - constant )
                block.add_component( name+"_lo", newC )
                newC.construct()
            if c.upper is not None:
                if __debug__ and logger.isEnabledFor(logging.DEBUG):
                    logger.debug("GDP(cHull): Promoting constraint " +
                                 "'%s' as '%s_hi'", name, name)
                bound = c.upper() - constant
                if bound != 0:
                    newC = Constraint( expr = exp - constant <= \
                                       bound*disjunct.indicator_var )
                else:
                    newC = Constraint( expr = exp - constant <= bound )
                block.add_component( name+"_hi", newC )
                newC.construct()

    def _var_subst(self, NL, exp, y, varMap):
        # Recursively traverse the S-expression and substitute all model
        # variables with disaggregated local disjunct variables (logic
        # stolen from collect_cannonical_repn())

        #
        # Expression
        #
        if isinstance(exp,expr.Expression):
            if isinstance(exp,expr._ProductExpression):
                exp._numerator = [self._var_subst(NL, e, y, varMap) for e in exp._numerator]
                exp._denominator = [self._var_subst(NL, e, y, varMap) for e in exp._denominator]
            elif isinstance(exp, expr._IdentityExpression) or \
                     isinstance(exp,expr._SumExpression) or \
                     isinstance(exp,expr._AbsExpression) or \
                     isinstance(exp,expr._PowExpression):
                exp._args = [self._var_subst(NL, e, y, varMap) for e in exp._args]
            else:
                raise ValueError("Unsupported expression type: "+str(exp))
        #
        # Constant
        #
        elif exp.is_fixed():
            pass
        #
        # Variable
        #
        elif isinstance(exp, _VarData):
            # Check if this disjunct has used this variable before...
            if id(exp) not in varMap:
                # create a new variable
                if exp.lb is None or exp.ub is None:
                    raise GDP_Error("Disjunct constraint referenced unbounded model variable; "\
                          "all variables must be bounded to use the Convex Hull transformation.")
                v = Var(domain=exp.domain)
                v.setlb(min(0,value(exp.lb)))
                v.setub(max(0,value(exp.ub)))
                varMap[id(exp)] = (exp, y, v)
            if NL:
                return varMap[id(exp)][2] / y
            else:
                return varMap[id(exp)][2]
        elif exp.type() is Var:
            raise GDP_Error("Unexpected Var encoundered in expression")
        #
        # ERROR
        #
        else:
            raise ValueError("Unexpected expression type: "+str(exp))

        return exp

class ConvexHull_Transformation_Plugin(Plugin):
    implements(IPyomoScriptModifyInstance)

    def __init__(self):
        Plugin.__init__(self)

    def apply(self, **kwds):
        xform = ConvexHull_Transformation()
        return xform.apply(**kwds)

transform = ConvexHull_Transformation_Plugin()
