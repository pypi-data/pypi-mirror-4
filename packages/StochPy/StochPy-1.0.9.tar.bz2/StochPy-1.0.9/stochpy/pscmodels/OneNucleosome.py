model = """# PySCeS test input file
# Stochastic Simulation Algorithm input format
# Nucleosome Model (Cell Paper)

R1:
    M1 > U1
    k1*M1

R2:
    U1 > M1
    k1*U1

R3:
    U1 > A1
    k1*U1

R4:
    A1 > U1
    k1*A1

R5:
    M1 > U1
    k2*M1

R6:
    A1 > U1
    k2*A1

R7:
    U1 > M1
    k2*U1

R8:
    U1 > A1
    k2*U1

# InitPar
k1 = 1.0
k2 = 0.1

# InitVar
M1 = 0
U1 = 1
A1 = 0
"""
