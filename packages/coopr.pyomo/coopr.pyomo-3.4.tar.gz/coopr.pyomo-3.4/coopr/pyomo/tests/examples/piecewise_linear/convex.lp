\* Source Pyomo model name=unknown *\

min 
obj:
+1.000000 Z
+0.0 ONE_VAR_CONSTANT

s.t.

c_u_con_simplified_piecewise_constraint(0)_:
-1.000000 X
-1.000000 Z
<= -2.0

c_u_con_simplified_piecewise_constraint(1)_:
+1.000000 X
-1.000000 Z
<= 0.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
   -5 <= X <= 5
    -inf <= Z <= +inf
end 
