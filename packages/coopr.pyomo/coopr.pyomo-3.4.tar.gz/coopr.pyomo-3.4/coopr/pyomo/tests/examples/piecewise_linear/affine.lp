\* Source Pyomo model name=unknown *\

min 
obj:
+1.000000 n
+1.000000 p
 +0.0 ONE_VAR_CONSTANT

s.t.

c_e_pn_con_:
+1.000000 Z
+1.000000 n
-1.000000 p
= 7.0

c_e_con_DCC_constraint1_:
+1.000000 X
+1.000000 con_DCC_lambda(1_1)
-2.000000 con_DCC_lambda(1_2)
-2.000000 con_DCC_lambda(2_2)
-6.000000 con_DCC_lambda(2_3)
-6.000000 con_DCC_lambda(3_3)
-10.000000 con_DCC_lambda(3_4)
= 0.0

c_e_con_DCC_constraint2_:
+1.000000 Z
+1.000000 con_DCC_lambda(1_1)
+8.000000 con_DCC_lambda(2_3)
+8.000000 con_DCC_lambda(3_3)
-12.000000 con_DCC_lambda(3_4)
= 0.0

c_e_con_DCC_constraint3(1)_:
+1.000000 con_DCC_bin_y(1)
-1.000000 con_DCC_lambda(1_1)
-1.000000 con_DCC_lambda(1_2)
= 0.0

c_e_con_DCC_constraint3(2)_:
+1.000000 con_DCC_bin_y(2)
-1.000000 con_DCC_lambda(2_2)
-1.000000 con_DCC_lambda(2_3)
= 0.0

c_e_con_DCC_constraint3(3)_:
+1.000000 con_DCC_bin_y(3)
-1.000000 con_DCC_lambda(3_3)
-1.000000 con_DCC_lambda(3_4)
= 0.0

c_e_con_DCC_constraint4_:
+1.000000 con_DCC_bin_y(1)
+1.000000 con_DCC_bin_y(2)
+1.000000 con_DCC_bin_y(3)
= 1.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
   -1.0 <= X <= 10.0
    -inf <= Z <= +inf
   0 <= p <= +inf
   0 <= n <= +inf
   0 <= con_DCC_lambda(1_1) <= +inf
   0 <= con_DCC_lambda(1_2) <= +inf
   0 <= con_DCC_lambda(2_2) <= +inf
   0 <= con_DCC_lambda(2_3) <= +inf
   0 <= con_DCC_lambda(3_3) <= +inf
   0 <= con_DCC_lambda(3_4) <= +inf
   0 <= con_DCC_bin_y(1) <= 1
   0 <= con_DCC_bin_y(2) <= 1
   0 <= con_DCC_bin_y(3) <= 1
binary
  con_DCC_bin_y(1)
  con_DCC_bin_y(2)
  con_DCC_bin_y(3)
end 
