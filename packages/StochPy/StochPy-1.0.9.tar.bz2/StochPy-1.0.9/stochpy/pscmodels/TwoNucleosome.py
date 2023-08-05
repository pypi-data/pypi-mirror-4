model = """# PySCeS test input file
# Stochastic Simulation Algorithm input format
# Nucleosome Model (Cell Paper)

R1:
    M1 + A2 > U1 + A2
    k1*M1*A2

R2:
    M1 > U1
    k2*M1

R3:
    U1 + M2 > M1 + M2
    k1*U1*M2

R4:
    U1 + A2 > U1 + A2
    k1*U1*A2

R5:
    U1 > M1
    k2*U1

R6:
    U1 > A1
    k2*U1 

R7:
    A1 + M2 > U1 + M2
    k1*A1*M2

R8:
    A1 > U1
    k2*A1

R9:
    M2 + A1 > U2 + A1
    k1*M2*A1

R10:
    M2 > U2
    k2*M2

R11:
    U2 + M1 > M2 + M1
    k1*U2*M1

R12:
    U2 + A1 > A2 + A1
    k1*U2*A1

R13:
    U2 > M2
    k2*U2

R14:
    U2 > A2
    k2*U2

R15:
    A2 + M1 > U2 + M1
    k1*A2*M1

R16:
    A2 > U2
    k2*A2

# InitPar
k1 = 1.0
k2 = 0.1

# InitVar
M1 = 1
U1 = 0
A1 = 0
M2 = 1
U2 = 0
A2 = 0
"""
