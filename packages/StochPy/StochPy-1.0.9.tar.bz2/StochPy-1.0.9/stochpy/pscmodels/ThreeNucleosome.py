model = """# PySCeS test input file
# Stochastic Simulation Algorithm input format
# Nucleosome Model (Cell Paper)


R1: 
    M1 + A2 > U1 + A2 
    k2*M1*A2
R2: 
    M1 > U1 
    k1*M1
R3: 
    U1 + M2 > M1 + M2 
    k2*U1*M2
R4: 
    U1 + A2 > A1 + A2 
    k2*U1*A2
R5: 
    U1 > M1 
    k1*U1
R6: 
    U1 > A1 
    k1*U1
R7: 
    A1 + M2 > U1 + M2 
    k2*A1*M2
R8: 
    A1 > U1 
    k1*A1
R9: 
    M1 + A3 > U1 + A3 
    k3*M1*A3
R10: 
    U1 + M3 > M1 + M3 
    k3*U1*M3
R11: 
    U1 + A3 > A1 + A3 
    k3*U1*A3
R12: 
    A1 + M3 > U1 + M3 
    k3*A1*M3
R13: 
    M2 + A1 > U2 + A1 
    k2*M2*A1
R14: 
    M2 + A3 > U2 + A3 
    k2*M2*A3
R15: 
    M2 > U2 
    k1*M2
R16: 
    U2 + M1 > M2 + M1 
    k2*U2*M1
R17: 
    U2 + M3 > M2 + M3 
    k2*U2*M3
R18: 
    U2 + A1 > A2 + A1 
    k2*U2*A1
R19: 
    U2 + A3 > A2 + A3 
    k2*U2*A3
R20: 
    U2 > M2 
    k1*U2
R21: 
    U2 > A2 
    k1*U2
R22: 
    A2 + M1 > U2 + M1 
    k2*A2*M1
R23: 
    A2 + M3 > U2 + M3 
    k2*A2*M3
R24: 
    A2 > U2 
    k1*A2
R25: 
    M3 + A2 > U3 + A2 
    k2*M3*A2
R26: 
    M3 > U3 
    k1*M3
R27: 
    U3 + M2 > M3 + M2 
    k2*U3*M2
R28: 
    U3 + A2 > A3 + A2 
    k2*U3*A2
R29: 
    U3 > M3 
    k1*U3
R30: 
    U3 > A3 
    k1*U3
R31: 
    A3 + M2 > U3 + M2 
    k2*A3*M2
R32: 
    A3 > U3 
    k1*A3
R33: 
    M3 + A1 > U3 + A1 
    k3*M3*A1
R34: 
    U3 + M1 > M3 + M1 
    k3*U3*M1
R35: 
    U3 + A1 > A3 + A1 
    k3*U3*A1
R36: 
    A3 + M1 > U3 + M1 
    k3*A3*M1

R37:
    U1 + E1 > M1
    kenz*U1*E1

R38:
    U2 + E2 > M2
    kenz*U2*E2

R39:
    U3 + E3 > M3
    kenz*U3*E3

R40: 
    pool > E1 + pool
    kon

R41:
    E1 + pool > pool
    koff*E1

R42:
    E1  > E2
    kdif*E1

R43: 
    pool > E2 + pool
    kon

R44:
    E2 + pool > pool
    koff*E2

R45: 
    E2 > E1
    kdif*E2

R46: 
    E2 > E3
    kdif*E2

R47: 
    pool > E3 + pool
    kon

R48:
    E3 + pool > pool
    koff*E3

R49:
    E3  > E2
    kdif*E3

# InitPar
k1 = 0.33
k2 = 1.0
k3 = 0.5
kenz = 100
kon = 1
koff= 1
kdif = 1

# InitVar
pool = 0
E1 = 0
E2 = 0
E3 = 0
M1 = 0
U1 = 1
A1 = 0
M2 = 0
U2 = 1
A2 = 0
M3 = 1
U3 = 0
A3 = 0
"""
