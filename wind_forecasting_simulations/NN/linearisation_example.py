import sympy as sym

x, y, ts = sym.symbols('x, y, ts')

f = sym.Matrix([x**2 + sym.sin(x*y), 
                0.5 * ts * sym.exp(sym.cos(x + y**3 - 1))])
z = sym.Matrix([x, y])

Jf = f.jacobian(z)
Jfeq = Jf.subs([(x, 0), (y, 0)])

print(Jfeq.evalf())