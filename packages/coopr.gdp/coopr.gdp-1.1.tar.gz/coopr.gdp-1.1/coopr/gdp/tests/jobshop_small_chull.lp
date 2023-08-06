\* Source Pyomo model name=unknown *\

min 
makespan:
+1.000000 ms
 +0.0 ONE_VAR_CONSTANT

s.t.

c_u_Feas(A)_:
-1.000000 ms
+1.000000 t(A)
<= -8.0

c_u_Feas(B)_:
-1.000000 ms
+1.000000 t(B)
<= -5.0

c_u_Feas(C)_:
-1.000000 ms
+1.000000 t(C)
<= -6.0

c_u_NoClash(A_C_1_0)c_hi_:
+2.000000 NoClash(A_C_1_0)indicator_var
-1.000000 NoClash(A_C_1_0)t(A)
+1.000000 NoClash(A_C_1_0)t(C)
<= 0.0

c_u_NoClash(B_C_2_0)c_hi_:
+6.000000 NoClash(B_C_2_0)indicator_var
-1.000000 NoClash(B_C_2_0)t(B)
+1.000000 NoClash(B_C_2_0)t(C)
<= 0.0

c_u_NoClash(A_B_3_1)c_hi_:
+5.000000 NoClash(A_B_3_1)indicator_var
+1.000000 NoClash(A_B_3_1)t(A)
-1.000000 NoClash(A_B_3_1)t(B)
<= 0.0

c_u_NoClash(A_C_1_1)c_hi_:
+5.000000 NoClash(A_C_1_1)indicator_var
+1.000000 NoClash(A_C_1_1)t(A)
-1.000000 NoClash(A_C_1_1)t(C)
<= 0.0

c_u_NoClash(B_C_2_1)c_hi_:
+1.000000 NoClash(B_C_2_1)indicator_var
+1.000000 NoClash(B_C_2_1)t(B)
-1.000000 NoClash(B_C_2_1)t(C)
<= 0.0

c_u_NoClash(A_B_3_0)c_hi_:
-1.000000 NoClash(A_B_3_0)t(A)
+1.000000 NoClash(A_B_3_0)t(B)
<= 0.0

c_e_disj_(A_B_3)_t(A)_:
-1.000000 NoClash(A_B_3_0)t(A)
-1.000000 NoClash(A_B_3_1)t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A_B_3)_t(B)_:
-1.000000 NoClash(A_B_3_0)t(B)
-1.000000 NoClash(A_B_3_1)t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(A_C_1)_t(A)_:
-1.000000 NoClash(A_C_1_0)t(A)
-1.000000 NoClash(A_C_1_1)t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A_C_1)_t(C)_:
-1.000000 NoClash(A_C_1_0)t(C)
-1.000000 NoClash(A_C_1_1)t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(B_C_2)_t(B)_:
-1.000000 NoClash(B_C_2_0)t(B)
-1.000000 NoClash(B_C_2_1)t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B_C_2)_t(C)_:
-1.000000 NoClash(B_C_2_0)t(C)
-1.000000 NoClash(B_C_2_1)t(C)
+1.000000 t(C)
= 0.0

c_u_NoClash(A_B_3_0)t(A)_hi_:
-19.000000 NoClash(A_B_3_0)indicator_var
+1.000000 NoClash(A_B_3_0)t(A)
<= 0.0

c_u_NoClash(A_B_3_0)t(B)_hi_:
-19.000000 NoClash(A_B_3_0)indicator_var
+1.000000 NoClash(A_B_3_0)t(B)
<= 0.0

c_u_NoClash(A_B_3_1)t(A)_hi_:
-19.000000 NoClash(A_B_3_1)indicator_var
+1.000000 NoClash(A_B_3_1)t(A)
<= 0.0

c_u_NoClash(A_B_3_1)t(B)_hi_:
-19.000000 NoClash(A_B_3_1)indicator_var
+1.000000 NoClash(A_B_3_1)t(B)
<= 0.0

c_u_NoClash(A_C_1_0)t(A)_hi_:
-19.000000 NoClash(A_C_1_0)indicator_var
+1.000000 NoClash(A_C_1_0)t(A)
<= 0.0

c_u_NoClash(A_C_1_0)t(C)_hi_:
-19.000000 NoClash(A_C_1_0)indicator_var
+1.000000 NoClash(A_C_1_0)t(C)
<= 0.0

c_u_NoClash(A_C_1_1)t(A)_hi_:
-19.000000 NoClash(A_C_1_1)indicator_var
+1.000000 NoClash(A_C_1_1)t(A)
<= 0.0

c_u_NoClash(A_C_1_1)t(C)_hi_:
-19.000000 NoClash(A_C_1_1)indicator_var
+1.000000 NoClash(A_C_1_1)t(C)
<= 0.0

c_u_NoClash(B_C_2_0)t(B)_hi_:
-19.000000 NoClash(B_C_2_0)indicator_var
+1.000000 NoClash(B_C_2_0)t(B)
<= 0.0

c_u_NoClash(B_C_2_0)t(C)_hi_:
-19.000000 NoClash(B_C_2_0)indicator_var
+1.000000 NoClash(B_C_2_0)t(C)
<= 0.0

c_u_NoClash(B_C_2_1)t(B)_hi_:
-19.000000 NoClash(B_C_2_1)indicator_var
+1.000000 NoClash(B_C_2_1)t(B)
<= 0.0

c_u_NoClash(B_C_2_1)t(C)_hi_:
-19.000000 NoClash(B_C_2_1)indicator_var
+1.000000 NoClash(B_C_2_1)t(C)
<= 0.0

c_e_disj(A_B_3)_:
+1.000000 NoClash(A_B_3_0)indicator_var
+1.000000 NoClash(A_B_3_1)indicator_var
= 1.0

c_e_disj(A_C_1)_:
+1.000000 NoClash(A_C_1_0)indicator_var
+1.000000 NoClash(A_C_1_1)indicator_var
= 1.0

c_e_disj(B_C_2)_:
+1.000000 NoClash(B_C_2_0)indicator_var
+1.000000 NoClash(B_C_2_1)indicator_var
= 1.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
    -inf <= ms <= +inf
   0 <= t(A) <= 19
   0 <= t(B) <= 19
   0 <= t(C) <= 19
   0 <= NoClash(A_C_1_0)indicator_var <= 1
   0 <= NoClash(B_C_2_0)indicator_var <= 1
   0 <= NoClash(A_B_3_1)indicator_var <= 1
   0 <= NoClash(A_C_1_1)indicator_var <= 1
   0 <= NoClash(B_C_2_1)indicator_var <= 1
   0 <= NoClash(A_B_3_0)indicator_var <= 1
   0 <= NoClash(A_B_3_0)t(A) <= 19
   0 <= NoClash(A_B_3_0)t(B) <= 19
   0 <= NoClash(A_B_3_1)t(A) <= 19
   0 <= NoClash(A_B_3_1)t(B) <= 19
   0 <= NoClash(A_C_1_0)t(A) <= 19
   0 <= NoClash(A_C_1_0)t(C) <= 19
   0 <= NoClash(A_C_1_1)t(A) <= 19
   0 <= NoClash(A_C_1_1)t(C) <= 19
   0 <= NoClash(B_C_2_0)t(B) <= 19
   0 <= NoClash(B_C_2_0)t(C) <= 19
   0 <= NoClash(B_C_2_1)t(B) <= 19
   0 <= NoClash(B_C_2_1)t(C) <= 19
binary
  NoClash(A_C_1_0)indicator_var
  NoClash(B_C_2_0)indicator_var
  NoClash(A_B_3_1)indicator_var
  NoClash(A_C_1_1)indicator_var
  NoClash(B_C_2_1)indicator_var
  NoClash(A_B_3_0)indicator_var
end 
