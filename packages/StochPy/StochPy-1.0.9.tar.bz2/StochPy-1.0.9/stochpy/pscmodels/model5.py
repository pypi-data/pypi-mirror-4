model = """R1:
    M1 > U1
    knoise*M1
R2:
    EmM1 > EmU1
    knoise*EmM1
R3:
    U1 > A1
    knoise*U1
R4:
    A1 > U1
    knoise*A1
R5:
    EmA1 > EmU1
    knoise*EmA1
R6:
    EmM1 > M1
    koff*EmM1
R7:
    EmU1 > U1
    koff*EmU1
R8:
    EmA1 > A1
    koff*EmA1
R9:
    EmU1 > EmM1
    kenz*EmU1
R10:
    M1 > EmM1
    krec*M1
R11:
    U1 + EmM2 > M1 + EmM2
    kenz_neigh*U1*EmM2
R12:
    EmU1 + EmM2 > EmM1 + EmM2
    kenz_neigh*EmU1*EmM2
R13:
    EmU1 + M2 > EmM1 + M2
    kenz_neigh*EmU1*M2
R14:
    A1 + EmM2 > U1 + EmM2
    kneighbour*A1*EmM2
R15:
    EmA1 + EmM2 > EmU1 + EmM2
    kneighbour*EmA1*EmM2
R16:
    EmA1 + M2 > EmU1 + M2
    kneighbour*EmA1*M2
R17:
    M1 + A2 > U1 + A2
    kneighbour*M1*A2
R18:
    EmM1 + A2 > EmU1 + A2
    kneighbour*EmM1*A2
R19:
    M1 + EmA2 > U1 + EmA2
    kneighbour*M1*EmA2
R20:
    U1 + A2 > A1 + A2
    kneighbour*U1*A2
R21:
    EmU1 + A2 > EmA1 + A2
    kneighbour*EmU1*A2
R22:
    U1 + EmA2 > A1 + EmA2
    kneighbour*U1*EmA2
R23:
    M2 > U2
    knoise*M2
R24:
    EmM2 > EmU2
    knoise*EmM2
R25:
    U2 > A2
    knoise*U2
R26:
    A2 > U2
    knoise*A2
R27:
    EmA2 > EmU2
    knoise*EmA2
R28:
    EmM2 > M2
    koff*EmM2
R29:
    EmU2 > U2
    koff*EmU2
R30:
    EmA2 > A2
    koff*EmA2
R31:
    EmU2 > EmM2
    kenz*EmU2
R32:
    M2 > EmM2
    krec*M2
R33:
    U2 + EmM3 > M2 + EmM3
    kenz_neigh*U2*EmM3
R34:
    EmU2 + EmM3 > EmM2 + EmM3
    kenz_neigh*EmU2*EmM3
R35:
    EmU2 + M3 > EmM2 + M3
    kenz_neigh*EmU2*M3
R36:
    U2 + EmM1 > M2 + EmM1
    kenz_neigh*U2*EmM1
R37:
    EmU2 + EmM1 > EmM2 + EmM1
    kenz_neigh*EmU2*EmM1
R38:
    EmU2 + M1 > EmM2 + M1
    kenz_neigh*EmU2*M1
R39:
    A2 + EmM3 > U2 + EmM3
    kneighbour*A2*EmM3
R40:
    EmA2 + EmM3 > EmU2 + EmM3
    kneighbour*EmA2*EmM3
R41:
    EmA2 + M3 > EmU2 + M3
    kneighbour*EmA2*M3
R42:
    A2 + EmM1 > U2 + EmM1
    kneighbour*A2*EmM1
R43:
    EmA2 + EmM1 > EmU2 + EmM1
    kneighbour*EmA2*EmM1
R44:
    EmA2 + M1 > EmU2 + M1
    kneighbour*EmA2*M1
R45:
    M2 + A1 > U2 + A1
    kneighbour*M2*A1
R46:
    EmM2 + A1 > EmU2 + A1
    kneighbour*EmM2*A1
R47:
    M2 + EmA1 > U2 + EmA1
    kneighbour*M2*EmA1
R48:
    M2 + A3 > U2 + A3
    kneighbour*M2*A3
R49:
    EmM2 + A3 > EmU2 + A3
    kneighbour*EmM2*A3
R50:
    M2 + EmA3 > U2 + EmA3
    kneighbour*M2*EmA3
R51:
    U2 + A1 > A2 + A1
    kneighbour*U2*A1
R52:
    EmU2 + A1 > EmA2 + A1
    kneighbour*EmU2*A1
R53:
    U2 + EmA1 > A2 + EmA1
    kneighbour*U2*EmA1
R54:
    U2 + A3 > A2 + A3
    kneighbour*U2*A3
R55:
    EmU2 + A3 > EmA2 + A3
    kneighbour*EmU2*A3
R56:
    U2 + EmA3 > A2 + EmA3
    kneighbour*U2*EmA3
R57:
    M3 > U3
    knoise*M3
R58:
    EmM3 > EmU3
    knoise*EmM3
R59:
    U3 > A3
    knoise*U3
R60:
    A3 > U3
    knoise*A3
R61:
    EmA3 > EmU3
    knoise*EmA3
R62:
    EmM3 > M3
    koff*EmM3
R63:
    EmU3 > U3
    koff*EmU3
R64:
    EmA3 > A3
    koff*EmA3
R65:
    EmU3 > EmM3
    kenz*EmU3
R66:
    M3 > EmM3
    krec*M3
R67:
    U3 + EmM4 > M3 + EmM4
    kenz_neigh*U3*EmM4
R68:
    EmU3 + EmM4 > EmM3 + EmM4
    kenz_neigh*EmU3*EmM4
R69:
    EmU3 + M4 > EmM3 + M4
    kenz_neigh*EmU3*M4
R70:
    U3 + EmM2 > M3 + EmM2
    kenz_neigh*U3*EmM2
R71:
    EmU3 + EmM2 > EmM3 + EmM2
    kenz_neigh*EmU3*EmM2
R72:
    EmU3 + M2 > EmM3 + M2
    kenz_neigh*EmU3*M2
R73:
    A3 + EmM4 > U3 + EmM4
    kneighbour*A3*EmM4
R74:
    EmA3 + EmM4 > EmU3 + EmM4
    kneighbour*EmA3*EmM4
R75:
    EmA3 + M4 > EmU3 + M4
    kneighbour*EmA3*M4
R76:
    A3 + EmM2 > U3 + EmM2
    kneighbour*A3*EmM2
R77:
    EmA3 + EmM2 > EmU3 + EmM2
    kneighbour*EmA3*EmM2
R78:
    EmA3 + M2 > EmU3 + M2
    kneighbour*EmA3*M2
R79:
    M3 + A2 > U3 + A2
    kneighbour*M3*A2
R80:
    EmM3 + A2 > EmU3 + A2
    kneighbour*EmM3*A2
R81:
    M3 + EmA2 > U3 + EmA2
    kneighbour*M3*EmA2
R82:
    M3 + A4 > U3 + A4
    kneighbour*M3*A4
R83:
    EmM3 + A4 > EmU3 + A4
    kneighbour*EmM3*A4
R84:
    M3 + EmA4 > U3 + EmA4
    kneighbour*M3*EmA4
R85:
    U3 + A2 > A3 + A2
    kneighbour*U3*A2
R86:
    EmU3 + A2 > EmA3 + A2
    kneighbour*EmU3*A2
R87:
    U3 + EmA2 > A3 + EmA2
    kneighbour*U3*EmA2
R88:
    U3 + A4 > A3 + A4
    kneighbour*U3*A4
R89:
    EmU3 + A4 > EmA3 + A4
    kneighbour*EmU3*A4
R90:
    U3 + EmA4 > A3 + EmA4
    kneighbour*U3*EmA4
R91:
    M4 > U4
    knoise*M4
R92:
    EmM4 > EmU4
    knoise*EmM4
R93:
    U4 > A4
    knoise*U4
R94:
    A4 > U4
    knoise*A4
R95:
    EmA4 > EmU4
    knoise*EmA4
R96:
    EmM4 > M4
    koff*EmM4
R97:
    EmU4 > U4
    koff*EmU4
R98:
    EmA4 > A4
    koff*EmA4
R99:
    EmU4 > EmM4
    kenz*EmU4
R100:
    M4 > EmM4
    krec*M4
R101:
    U4 + EmM5 > M4 + EmM5
    kenz_neigh*U4*EmM5
R102:
    EmU4 + EmM5 > EmM4 + EmM5
    kenz_neigh*EmU4*EmM5
R103:
    EmU4 + M5 > EmM4 + M5
    kenz_neigh*EmU4*M5
R104:
    U4 + EmM3 > M4 + EmM3
    kenz_neigh*U4*EmM3
R105:
    EmU4 + EmM3 > EmM4 + EmM3
    kenz_neigh*EmU4*EmM3
R106:
    EmU4 + M3 > EmM4 + M3
    kenz_neigh*EmU4*M3
R107:
    A4 + EmM5 > U4 + EmM5
    kneighbour*A4*EmM5
R108:
    EmA4 + EmM5 > EmU4 + EmM5
    kneighbour*EmA4*EmM5
R109:
    EmA4 + M5 > EmU4 + M5
    kneighbour*EmA4*M5
R110:
    A4 + EmM3 > U4 + EmM3
    kneighbour*A4*EmM3
R111:
    EmA4 + EmM3 > EmU4 + EmM3
    kneighbour*EmA4*EmM3
R112:
    EmA4 + M3 > EmU4 + M3
    kneighbour*EmA4*M3
R113:
    M4 + A3 > U4 + A3
    kneighbour*M4*A3
R114:
    EmM4 + A3 > EmU4 + A3
    kneighbour*EmM4*A3
R115:
    M4 + EmA3 > U4 + EmA3
    kneighbour*M4*EmA3
R116:
    M4 + A5 > U4 + A5
    kneighbour*M4*A5
R117:
    EmM4 + A5 > EmU4 + A5
    kneighbour*EmM4*A5
R118:
    M4 + EmA5 > U4 + EmA5
    kneighbour*M4*EmA5
R119:
    U4 + A3 > A4 + A3
    kneighbour*U4*A3
R120:
    EmU4 + A3 > EmA4 + A3
    kneighbour*EmU4*A3
R121:
    U4 + EmA3 > A4 + EmA3
    kneighbour*U4*EmA3
R122:
    U4 + A5 > A4 + A5
    kneighbour*U4*A5
R123:
    EmU4 + A5 > EmA4 + A5
    kneighbour*EmU4*A5
R124:
    U4 + EmA5 > A4 + EmA5
    kneighbour*U4*EmA5
R125:
    M5 > U5
    knoise*M5
R126:
    EmM5 > EmU5
    knoise*EmM5
R127:
    U5 > A5
    knoise*U5
R128:
    A5 > U5
    knoise*A5
R129:
    EmA5 > EmU5
    knoise*EmA5
R130:
    EmM5 > M5
    koff*EmM5
R131:
    EmU5 > U5
    koff*EmU5
R132:
    EmA5 > A5
    koff*EmA5
R133:
    EmU5 > EmM5
    kenz*EmU5
R134:
    M5 > EmM5
    krec*M5
R135:
    U5 + EmM6 > M5 + EmM6
    kenz_neigh*U5*EmM6
R136:
    EmU5 + EmM6 > EmM5 + EmM6
    kenz_neigh*EmU5*EmM6
R137:
    EmU5 + M6 > EmM5 + M6
    kenz_neigh*EmU5*M6
R138:
    U5 + EmM4 > M5 + EmM4
    kenz_neigh*U5*EmM4
R139:
    EmU5 + EmM4 > EmM5 + EmM4
    kenz_neigh*EmU5*EmM4
R140:
    EmU5 + M4 > EmM5 + M4
    kenz_neigh*EmU5*M4
R141:
    A5 + EmM6 > U5 + EmM6
    kneighbour*A5*EmM6
R142:
    EmA5 + EmM6 > EmU5 + EmM6
    kneighbour*EmA5*EmM6
R143:
    EmA5 + M6 > EmU5 + M6
    kneighbour*EmA5*M6
R144:
    A5 + EmM4 > U5 + EmM4
    kneighbour*A5*EmM4
R145:
    EmA5 + EmM4 > EmU5 + EmM4
    kneighbour*EmA5*EmM4
R146:
    EmA5 + M4 > EmU5 + M4
    kneighbour*EmA5*M4
R147:
    M5 + A4 > U5 + A4
    kneighbour*M5*A4
R148:
    EmM5 + A4 > EmU5 + A4
    kneighbour*EmM5*A4
R149:
    M5 + EmA4 > U5 + EmA4
    kneighbour*M5*EmA4
R150:
    M5 + A6 > U5 + A6
    kneighbour*M5*A6
R151:
    EmM5 + A6 > EmU5 + A6
    kneighbour*EmM5*A6
R152:
    M5 + EmA6 > U5 + EmA6
    kneighbour*M5*EmA6
R153:
    U5 + A4 > A5 + A4
    kneighbour*U5*A4
R154:
    EmU5 + A4 > EmA5 + A4
    kneighbour*EmU5*A4
R155:
    U5 + EmA4 > A5 + EmA4
    kneighbour*U5*EmA4
R156:
    U5 + A6 > A5 + A6
    kneighbour*U5*A6
R157:
    EmU5 + A6 > EmA5 + A6
    kneighbour*EmU5*A6
R158:
    U5 + EmA6 > A5 + EmA6
    kneighbour*U5*EmA6
R159:
    M6 > U6
    knoise*M6
R160:
    EmM6 > EmU6
    knoise*EmM6
R161:
    U6 > A6
    knoise*U6
R162:
    A6 > U6
    knoise*A6
R163:
    EmA6 > EmU6
    knoise*EmA6
R164:
    EmM6 > M6
    koff*EmM6
R165:
    EmU6 > U6
    koff*EmU6
R166:
    EmA6 > A6
    koff*EmA6
R167:
    EmU6 > EmM6
    kenz*EmU6
R168:
    M6 > EmM6
    krec*M6
R169:
    U6 + EmM7 > M6 + EmM7
    kenz_neigh*U6*EmM7
R170:
    EmU6 + EmM7 > EmM6 + EmM7
    kenz_neigh*EmU6*EmM7
R171:
    EmU6 + M7 > EmM6 + M7
    kenz_neigh*EmU6*M7
R172:
    U6 + EmM5 > M6 + EmM5
    kenz_neigh*U6*EmM5
R173:
    EmU6 + EmM5 > EmM6 + EmM5
    kenz_neigh*EmU6*EmM5
R174:
    EmU6 + M5 > EmM6 + M5
    kenz_neigh*EmU6*M5
R175:
    A6 + EmM7 > U6 + EmM7
    kneighbour*A6*EmM7
R176:
    EmA6 + EmM7 > EmU6 + EmM7
    kneighbour*EmA6*EmM7
R177:
    EmA6 + M7 > EmU6 + M7
    kneighbour*EmA6*M7
R178:
    A6 + EmM5 > U6 + EmM5
    kneighbour*A6*EmM5
R179:
    EmA6 + EmM5 > EmU6 + EmM5
    kneighbour*EmA6*EmM5
R180:
    EmA6 + M5 > EmU6 + M5
    kneighbour*EmA6*M5
R181:
    M6 + A5 > U6 + A5
    kneighbour*M6*A5
R182:
    EmM6 + A5 > EmU6 + A5
    kneighbour*EmM6*A5
R183:
    M6 + EmA5 > U6 + EmA5
    kneighbour*M6*EmA5
R184:
    M6 + A7 > U6 + A7
    kneighbour*M6*A7
R185:
    EmM6 + A7 > EmU6 + A7
    kneighbour*EmM6*A7
R186:
    M6 + EmA7 > U6 + EmA7
    kneighbour*M6*EmA7
R187:
    U6 + A5 > A6 + A5
    kneighbour*U6*A5
R188:
    EmU6 + A5 > EmA6 + A5
    kneighbour*EmU6*A5
R189:
    U6 + EmA5 > A6 + EmA5
    kneighbour*U6*EmA5
R190:
    U6 + A7 > A6 + A7
    kneighbour*U6*A7
R191:
    EmU6 + A7 > EmA6 + A7
    kneighbour*EmU6*A7
R192:
    U6 + EmA7 > A6 + EmA7
    kneighbour*U6*EmA7
R193:
    M7 > U7
    knoise*M7
R194:
    EmM7 > EmU7
    knoise*EmM7
R195:
    U7 > A7
    knoise*U7
R196:
    A7 > U7
    knoise*A7
R197:
    EmA7 > EmU7
    knoise*EmA7
R198:
    EmM7 > M7
    koff*EmM7
R199:
    EmU7 > U7
    koff*EmU7
R200:
    EmA7 > A7
    koff*EmA7
R201:
    EmU7 > EmM7
    kenz*EmU7
R202:
    M7 > EmM7
    krec*M7
R203:
    U7 + EmM8 > M7 + EmM8
    kenz_neigh*U7*EmM8
R204:
    EmU7 + EmM8 > EmM7 + EmM8
    kenz_neigh*EmU7*EmM8
R205:
    EmU7 + M8 > EmM7 + M8
    kenz_neigh*EmU7*M8
R206:
    U7 + EmM6 > M7 + EmM6
    kenz_neigh*U7*EmM6
R207:
    EmU7 + EmM6 > EmM7 + EmM6
    kenz_neigh*EmU7*EmM6
R208:
    EmU7 + M6 > EmM7 + M6
    kenz_neigh*EmU7*M6
R209:
    A7 + EmM8 > U7 + EmM8
    kneighbour*A7*EmM8
R210:
    EmA7 + EmM8 > EmU7 + EmM8
    kneighbour*EmA7*EmM8
R211:
    EmA7 + M8 > EmU7 + M8
    kneighbour*EmA7*M8
R212:
    A7 + EmM6 > U7 + EmM6
    kneighbour*A7*EmM6
R213:
    EmA7 + EmM6 > EmU7 + EmM6
    kneighbour*EmA7*EmM6
R214:
    EmA7 + M6 > EmU7 + M6
    kneighbour*EmA7*M6
R215:
    M7 + A6 > U7 + A6
    kneighbour*M7*A6
R216:
    EmM7 + A6 > EmU7 + A6
    kneighbour*EmM7*A6
R217:
    M7 + EmA6 > U7 + EmA6
    kneighbour*M7*EmA6
R218:
    M7 + A8 > U7 + A8
    kneighbour*M7*A8
R219:
    EmM7 + A8 > EmU7 + A8
    kneighbour*EmM7*A8
R220:
    M7 + EmA8 > U7 + EmA8
    kneighbour*M7*EmA8
R221:
    U7 + A6 > A7 + A6
    kneighbour*U7*A6
R222:
    EmU7 + A6 > EmA7 + A6
    kneighbour*EmU7*A6
R223:
    U7 + EmA6 > A7 + EmA6
    kneighbour*U7*EmA6
R224:
    U7 + A8 > A7 + A8
    kneighbour*U7*A8
R225:
    EmU7 + A8 > EmA7 + A8
    kneighbour*EmU7*A8
R226:
    U7 + EmA8 > A7 + EmA8
    kneighbour*U7*EmA8
R227:
    M8 > U8
    knoise*M8
R228:
    EmM8 > EmU8
    knoise*EmM8
R229:
    U8 > A8
    knoise*U8
R230:
    A8 > U8
    knoise*A8
R231:
    EmA8 > EmU8
    knoise*EmA8
R232:
    EmM8 > M8
    koff*EmM8
R233:
    EmU8 > U8
    koff*EmU8
R234:
    EmA8 > A8
    koff*EmA8
R235:
    EmU8 > EmM8
    kenz*EmU8
R236:
    M8 > EmM8
    krec*M8
R237:
    U8 + EmM9 > M8 + EmM9
    kenz_neigh*U8*EmM9
R238:
    EmU8 + EmM9 > EmM8 + EmM9
    kenz_neigh*EmU8*EmM9
R239:
    EmU8 + M9 > EmM8 + M9
    kenz_neigh*EmU8*M9
R240:
    U8 + EmM7 > M8 + EmM7
    kenz_neigh*U8*EmM7
R241:
    EmU8 + EmM7 > EmM8 + EmM7
    kenz_neigh*EmU8*EmM7
R242:
    EmU8 + M7 > EmM8 + M7
    kenz_neigh*EmU8*M7
R243:
    A8 + EmM9 > U8 + EmM9
    kneighbour*A8*EmM9
R244:
    EmA8 + EmM9 > EmU8 + EmM9
    kneighbour*EmA8*EmM9
R245:
    EmA8 + M9 > EmU8 + M9
    kneighbour*EmA8*M9
R246:
    A8 + EmM7 > U8 + EmM7
    kneighbour*A8*EmM7
R247:
    EmA8 + EmM7 > EmU8 + EmM7
    kneighbour*EmA8*EmM7
R248:
    EmA8 + M7 > EmU8 + M7
    kneighbour*EmA8*M7
R249:
    M8 + A7 > U8 + A7
    kneighbour*M8*A7
R250:
    EmM8 + A7 > EmU8 + A7
    kneighbour*EmM8*A7
R251:
    M8 + EmA7 > U8 + EmA7
    kneighbour*M8*EmA7
R252:
    M8 + A9 > U8 + A9
    kneighbour*M8*A9
R253:
    EmM8 + A9 > EmU8 + A9
    kneighbour*EmM8*A9
R254:
    M8 + EmA9 > U8 + EmA9
    kneighbour*M8*EmA9
R255:
    U8 + A7 > A8 + A7
    kneighbour*U8*A7
R256:
    EmU8 + A7 > EmA8 + A7
    kneighbour*EmU8*A7
R257:
    U8 + EmA7 > A8 + EmA7
    kneighbour*U8*EmA7
R258:
    U8 + A9 > A8 + A9
    kneighbour*U8*A9
R259:
    EmU8 + A9 > EmA8 + A9
    kneighbour*EmU8*A9
R260:
    U8 + EmA9 > A8 + EmA9
    kneighbour*U8*EmA9
R261:
    M9 > U9
    knoise*M9
R262:
    EmM9 > EmU9
    knoise*EmM9
R263:
    U9 > A9
    knoise*U9
R264:
    A9 > U9
    knoise*A9
R265:
    EmA9 > EmU9
    knoise*EmA9
R266:
    EmM9 > M9
    koff*EmM9
R267:
    EmU9 > U9
    koff*EmU9
R268:
    EmA9 > A9
    koff*EmA9
R269:
    EmU9 > EmM9
    kenz*EmU9
R270:
    M9 > EmM9
    krec*M9
R271:
    U9 + EmM10 > M9 + EmM10
    kenz_neigh*U9*EmM10
R272:
    EmU9 + EmM10 > EmM9 + EmM10
    kenz_neigh*EmU9*EmM10
R273:
    EmU9 + M10 > EmM9 + M10
    kenz_neigh*EmU9*M10
R274:
    U9 + EmM8 > M9 + EmM8
    kenz_neigh*U9*EmM8
R275:
    EmU9 + EmM8 > EmM9 + EmM8
    kenz_neigh*EmU9*EmM8
R276:
    EmU9 + M8 > EmM9 + M8
    kenz_neigh*EmU9*M8
R277:
    A9 + EmM10 > U9 + EmM10
    kneighbour*A9*EmM10
R278:
    EmA9 + EmM10 > EmU9 + EmM10
    kneighbour*EmA9*EmM10
R279:
    EmA9 + M10 > EmU9 + M10
    kneighbour*EmA9*M10
R280:
    A9 + EmM8 > U9 + EmM8
    kneighbour*A9*EmM8
R281:
    EmA9 + EmM8 > EmU9 + EmM8
    kneighbour*EmA9*EmM8
R282:
    EmA9 + M8 > EmU9 + M8
    kneighbour*EmA9*M8
R283:
    M9 + A8 > U9 + A8
    kneighbour*M9*A8
R284:
    EmM9 + A8 > EmU9 + A8
    kneighbour*EmM9*A8
R285:
    M9 + EmA8 > U9 + EmA8
    kneighbour*M9*EmA8
R286:
    M9 + A10 > U9 + A10
    kneighbour*M9*A10
R287:
    EmM9 + A10 > EmU9 + A10
    kneighbour*EmM9*A10
R288:
    M9 + EmA10 > U9 + EmA10
    kneighbour*M9*EmA10
R289:
    U9 + A8 > A9 + A8
    kneighbour*U9*A8
R290:
    EmU9 + A8 > EmA9 + A8
    kneighbour*EmU9*A8
R291:
    U9 + EmA8 > A9 + EmA8
    kneighbour*U9*EmA8
R292:
    U9 + A10 > A9 + A10
    kneighbour*U9*A10
R293:
    EmU9 + A10 > EmA9 + A10
    kneighbour*EmU9*A10
R294:
    U9 + EmA10 > A9 + EmA10
    kneighbour*U9*EmA10
R295:
    M10 > U10
    knoise*M10
R296:
    EmM10 > EmU10
    knoise*EmM10
R297:
    U10 > A10
    knoise*U10
R298:
    A10 > U10
    knoise*A10
R299:
    EmA10 > EmU10
    knoise*EmA10
R300:
    EmM10 > M10
    koff*EmM10
R301:
    EmU10 > U10
    koff*EmU10
R302:
    EmA10 > A10
    koff*EmA10
R303:
    EmU10 > EmM10
    kenz*EmU10
R304:
    M10 > EmM10
    krec*M10
R305:
    U10 + EmM11 > M10 + EmM11
    kenz_neigh*U10*EmM11
R306:
    EmU10 + EmM11 > EmM10 + EmM11
    kenz_neigh*EmU10*EmM11
R307:
    EmU10 + M11 > EmM10 + M11
    kenz_neigh*EmU10*M11
R308:
    U10 + EmM9 > M10 + EmM9
    kenz_neigh*U10*EmM9
R309:
    EmU10 + EmM9 > EmM10 + EmM9
    kenz_neigh*EmU10*EmM9
R310:
    EmU10 + M9 > EmM10 + M9
    kenz_neigh*EmU10*M9
R311:
    A10 + EmM11 > U10 + EmM11
    kneighbour*A10*EmM11
R312:
    EmA10 + EmM11 > EmU10 + EmM11
    kneighbour*EmA10*EmM11
R313:
    EmA10 + M11 > EmU10 + M11
    kneighbour*EmA10*M11
R314:
    A10 + EmM9 > U10 + EmM9
    kneighbour*A10*EmM9
R315:
    EmA10 + EmM9 > EmU10 + EmM9
    kneighbour*EmA10*EmM9
R316:
    EmA10 + M9 > EmU10 + M9
    kneighbour*EmA10*M9
R317:
    M10 + A9 > U10 + A9
    kneighbour*M10*A9
R318:
    EmM10 + A9 > EmU10 + A9
    kneighbour*EmM10*A9
R319:
    M10 + EmA9 > U10 + EmA9
    kneighbour*M10*EmA9
R320:
    M10 + A11 > U10 + A11
    kneighbour*M10*A11
R321:
    EmM10 + A11 > EmU10 + A11
    kneighbour*EmM10*A11
R322:
    M10 + EmA11 > U10 + EmA11
    kneighbour*M10*EmA11
R323:
    U10 + A9 > A10 + A9
    kneighbour*U10*A9
R324:
    EmU10 + A9 > EmA10 + A9
    kneighbour*EmU10*A9
R325:
    U10 + EmA9 > A10 + EmA9
    kneighbour*U10*EmA9
R326:
    U10 + A11 > A10 + A11
    kneighbour*U10*A11
R327:
    EmU10 + A11 > EmA10 + A11
    kneighbour*EmU10*A11
R328:
    U10 + EmA11 > A10 + EmA11
    kneighbour*U10*EmA11
R329:
    M11 > U11
    knoise*M11
R330:
    EmM11 > EmU11
    knoise*EmM11
R331:
    U11 > A11
    knoise*U11
R332:
    A11 > U11
    knoise*A11
R333:
    EmA11 > EmU11
    knoise*EmA11
R334:
    EmM11 > M11
    koff*EmM11
R335:
    EmU11 > U11
    koff*EmU11
R336:
    EmA11 > A11
    koff*EmA11
R337:
    EmU11 > EmM11
    kenz*EmU11
R338:
    M11 > EmM11
    krec*M11
R339:
    U11 + EmM12 > M11 + EmM12
    kenz_neigh*U11*EmM12
R340:
    EmU11 + EmM12 > EmM11 + EmM12
    kenz_neigh*EmU11*EmM12
R341:
    EmU11 + M12 > EmM11 + M12
    kenz_neigh*EmU11*M12
R342:
    U11 + EmM10 > M11 + EmM10
    kenz_neigh*U11*EmM10
R343:
    EmU11 + EmM10 > EmM11 + EmM10
    kenz_neigh*EmU11*EmM10
R344:
    EmU11 + M10 > EmM11 + M10
    kenz_neigh*EmU11*M10
R345:
    A11 + EmM12 > U11 + EmM12
    kneighbour*A11*EmM12
R346:
    EmA11 + EmM12 > EmU11 + EmM12
    kneighbour*EmA11*EmM12
R347:
    EmA11 + M12 > EmU11 + M12
    kneighbour*EmA11*M12
R348:
    A11 + EmM10 > U11 + EmM10
    kneighbour*A11*EmM10
R349:
    EmA11 + EmM10 > EmU11 + EmM10
    kneighbour*EmA11*EmM10
R350:
    EmA11 + M10 > EmU11 + M10
    kneighbour*EmA11*M10
R351:
    M11 + A10 > U11 + A10
    kneighbour*M11*A10
R352:
    EmM11 + A10 > EmU11 + A10
    kneighbour*EmM11*A10
R353:
    M11 + EmA10 > U11 + EmA10
    kneighbour*M11*EmA10
R354:
    M11 + A12 > U11 + A12
    kneighbour*M11*A12
R355:
    EmM11 + A12 > EmU11 + A12
    kneighbour*EmM11*A12
R356:
    M11 + EmA12 > U11 + EmA12
    kneighbour*M11*EmA12
R357:
    U11 + A10 > A11 + A10
    kneighbour*U11*A10
R358:
    EmU11 + A10 > EmA11 + A10
    kneighbour*EmU11*A10
R359:
    U11 + EmA10 > A11 + EmA10
    kneighbour*U11*EmA10
R360:
    U11 + A12 > A11 + A12
    kneighbour*U11*A12
R361:
    EmU11 + A12 > EmA11 + A12
    kneighbour*EmU11*A12
R362:
    U11 + EmA12 > A11 + EmA12
    kneighbour*U11*EmA12
R363:
    M12 > U12
    knoise*M12
R364:
    EmM12 > EmU12
    knoise*EmM12
R365:
    U12 > A12
    knoise*U12
R366:
    A12 > U12
    knoise*A12
R367:
    EmA12 > EmU12
    knoise*EmA12
R368:
    EmM12 > M12
    koff*EmM12
R369:
    EmU12 > U12
    koff*EmU12
R370:
    EmA12 > A12
    koff*EmA12
R371:
    EmU12 > EmM12
    kenz*EmU12
R372:
    M12 > EmM12
    krec*M12
R373:
    U12 + EmM13 > M12 + EmM13
    kenz_neigh*U12*EmM13
R374:
    EmU12 + EmM13 > EmM12 + EmM13
    kenz_neigh*EmU12*EmM13
R375:
    EmU12 + M13 > EmM12 + M13
    kenz_neigh*EmU12*M13
R376:
    U12 + EmM11 > M12 + EmM11
    kenz_neigh*U12*EmM11
R377:
    EmU12 + EmM11 > EmM12 + EmM11
    kenz_neigh*EmU12*EmM11
R378:
    EmU12 + M11 > EmM12 + M11
    kenz_neigh*EmU12*M11
R379:
    A12 + EmM13 > U12 + EmM13
    kneighbour*A12*EmM13
R380:
    EmA12 + EmM13 > EmU12 + EmM13
    kneighbour*EmA12*EmM13
R381:
    EmA12 + M13 > EmU12 + M13
    kneighbour*EmA12*M13
R382:
    A12 + EmM11 > U12 + EmM11
    kneighbour*A12*EmM11
R383:
    EmA12 + EmM11 > EmU12 + EmM11
    kneighbour*EmA12*EmM11
R384:
    EmA12 + M11 > EmU12 + M11
    kneighbour*EmA12*M11
R385:
    M12 + A11 > U12 + A11
    kneighbour*M12*A11
R386:
    EmM12 + A11 > EmU12 + A11
    kneighbour*EmM12*A11
R387:
    M12 + EmA11 > U12 + EmA11
    kneighbour*M12*EmA11
R388:
    M12 + A13 > U12 + A13
    kneighbour*M12*A13
R389:
    EmM12 + A13 > EmU12 + A13
    kneighbour*EmM12*A13
R390:
    M12 + EmA13 > U12 + EmA13
    kneighbour*M12*EmA13
R391:
    U12 + A11 > A12 + A11
    kneighbour*U12*A11
R392:
    EmU12 + A11 > EmA12 + A11
    kneighbour*EmU12*A11
R393:
    U12 + EmA11 > A12 + EmA11
    kneighbour*U12*EmA11
R394:
    U12 + A13 > A12 + A13
    kneighbour*U12*A13
R395:
    EmU12 + A13 > EmA12 + A13
    kneighbour*EmU12*A13
R396:
    U12 + EmA13 > A12 + EmA13
    kneighbour*U12*EmA13
R397:
    M13 > U13
    knoise*M13
R398:
    EmM13 > EmU13
    knoise*EmM13
R399:
    U13 > A13
    knoise*U13
R400:
    A13 > U13
    knoise*A13
R401:
    EmA13 > EmU13
    knoise*EmA13
R402:
    EmM13 > M13
    koff*EmM13
R403:
    EmU13 > U13
    koff*EmU13
R404:
    EmA13 > A13
    koff*EmA13
R405:
    EmU13 > EmM13
    kenz*EmU13
R406:
    M13 > EmM13
    krec*M13
R407:
    U13 + EmM14 > M13 + EmM14
    kenz_neigh*U13*EmM14
R408:
    EmU13 + EmM14 > EmM13 + EmM14
    kenz_neigh*EmU13*EmM14
R409:
    EmU13 + M14 > EmM13 + M14
    kenz_neigh*EmU13*M14
R410:
    U13 + EmM12 > M13 + EmM12
    kenz_neigh*U13*EmM12
R411:
    EmU13 + EmM12 > EmM13 + EmM12
    kenz_neigh*EmU13*EmM12
R412:
    EmU13 + M12 > EmM13 + M12
    kenz_neigh*EmU13*M12
R413:
    A13 + EmM14 > U13 + EmM14
    kneighbour*A13*EmM14
R414:
    EmA13 + EmM14 > EmU13 + EmM14
    kneighbour*EmA13*EmM14
R415:
    EmA13 + M14 > EmU13 + M14
    kneighbour*EmA13*M14
R416:
    A13 + EmM12 > U13 + EmM12
    kneighbour*A13*EmM12
R417:
    EmA13 + EmM12 > EmU13 + EmM12
    kneighbour*EmA13*EmM12
R418:
    EmA13 + M12 > EmU13 + M12
    kneighbour*EmA13*M12
R419:
    M13 + A12 > U13 + A12
    kneighbour*M13*A12
R420:
    EmM13 + A12 > EmU13 + A12
    kneighbour*EmM13*A12
R421:
    M13 + EmA12 > U13 + EmA12
    kneighbour*M13*EmA12
R422:
    M13 + A14 > U13 + A14
    kneighbour*M13*A14
R423:
    EmM13 + A14 > EmU13 + A14
    kneighbour*EmM13*A14
R424:
    M13 + EmA14 > U13 + EmA14
    kneighbour*M13*EmA14
R425:
    U13 + A12 > A13 + A12
    kneighbour*U13*A12
R426:
    EmU13 + A12 > EmA13 + A12
    kneighbour*EmU13*A12
R427:
    U13 + EmA12 > A13 + EmA12
    kneighbour*U13*EmA12
R428:
    U13 + A14 > A13 + A14
    kneighbour*U13*A14
R429:
    EmU13 + A14 > EmA13 + A14
    kneighbour*EmU13*A14
R430:
    U13 + EmA14 > A13 + EmA14
    kneighbour*U13*EmA14
R431:
    M14 > U14
    knoise*M14
R432:
    EmM14 > EmU14
    knoise*EmM14
R433:
    U14 > A14
    knoise*U14
R434:
    A14 > U14
    knoise*A14
R435:
    EmA14 > EmU14
    knoise*EmA14
R436:
    EmM14 > M14
    koff*EmM14
R437:
    EmU14 > U14
    koff*EmU14
R438:
    EmA14 > A14
    koff*EmA14
R439:
    EmU14 > EmM14
    kenz*EmU14
R440:
    M14 > EmM14
    krec*M14
R441:
    U14 + EmM15 > M14 + EmM15
    kenz_neigh*U14*EmM15
R442:
    EmU14 + EmM15 > EmM14 + EmM15
    kenz_neigh*EmU14*EmM15
R443:
    EmU14 + M15 > EmM14 + M15
    kenz_neigh*EmU14*M15
R444:
    U14 + EmM13 > M14 + EmM13
    kenz_neigh*U14*EmM13
R445:
    EmU14 + EmM13 > EmM14 + EmM13
    kenz_neigh*EmU14*EmM13
R446:
    EmU14 + M13 > EmM14 + M13
    kenz_neigh*EmU14*M13
R447:
    A14 + EmM15 > U14 + EmM15
    kneighbour*A14*EmM15
R448:
    EmA14 + EmM15 > EmU14 + EmM15
    kneighbour*EmA14*EmM15
R449:
    EmA14 + M15 > EmU14 + M15
    kneighbour*EmA14*M15
R450:
    A14 + EmM13 > U14 + EmM13
    kneighbour*A14*EmM13
R451:
    EmA14 + EmM13 > EmU14 + EmM13
    kneighbour*EmA14*EmM13
R452:
    EmA14 + M13 > EmU14 + M13
    kneighbour*EmA14*M13
R453:
    M14 + A13 > U14 + A13
    kneighbour*M14*A13
R454:
    EmM14 + A13 > EmU14 + A13
    kneighbour*EmM14*A13
R455:
    M14 + EmA13 > U14 + EmA13
    kneighbour*M14*EmA13
R456:
    M14 + A15 > U14 + A15
    kneighbour*M14*A15
R457:
    EmM14 + A15 > EmU14 + A15
    kneighbour*EmM14*A15
R458:
    M14 + EmA15 > U14 + EmA15
    kneighbour*M14*EmA15
R459:
    U14 + A13 > A14 + A13
    kneighbour*U14*A13
R460:
    EmU14 + A13 > EmA14 + A13
    kneighbour*EmU14*A13
R461:
    U14 + EmA13 > A14 + EmA13
    kneighbour*U14*EmA13
R462:
    U14 + A15 > A14 + A15
    kneighbour*U14*A15
R463:
    EmU14 + A15 > EmA14 + A15
    kneighbour*EmU14*A15
R464:
    U14 + EmA15 > A14 + EmA15
    kneighbour*U14*EmA15
R465:
    M15 > U15
    knoise*M15
R466:
    EmM15 > EmU15
    knoise*EmM15
R467:
    U15 > A15
    knoise*U15
R468:
    A15 > U15
    knoise*A15
R469:
    EmA15 > EmU15
    knoise*EmA15
R470:
    EmM15 > M15
    koff*EmM15
R471:
    EmU15 > U15
    koff*EmU15
R472:
    EmA15 > A15
    koff*EmA15
R473:
    EmU15 > EmM15
    kenz*EmU15
R474:
    M15 > EmM15
    krec*M15
R475:
    U15 + EmM16 > M15 + EmM16
    kenz_neigh*U15*EmM16
R476:
    EmU15 + EmM16 > EmM15 + EmM16
    kenz_neigh*EmU15*EmM16
R477:
    EmU15 + M16 > EmM15 + M16
    kenz_neigh*EmU15*M16
R478:
    U15 + EmM14 > M15 + EmM14
    kenz_neigh*U15*EmM14
R479:
    EmU15 + EmM14 > EmM15 + EmM14
    kenz_neigh*EmU15*EmM14
R480:
    EmU15 + M14 > EmM15 + M14
    kenz_neigh*EmU15*M14
R481:
    A15 + EmM16 > U15 + EmM16
    kneighbour*A15*EmM16
R482:
    EmA15 + EmM16 > EmU15 + EmM16
    kneighbour*EmA15*EmM16
R483:
    EmA15 + M16 > EmU15 + M16
    kneighbour*EmA15*M16
R484:
    A15 + EmM14 > U15 + EmM14
    kneighbour*A15*EmM14
R485:
    EmA15 + EmM14 > EmU15 + EmM14
    kneighbour*EmA15*EmM14
R486:
    EmA15 + M14 > EmU15 + M14
    kneighbour*EmA15*M14
R487:
    M15 + A14 > U15 + A14
    kneighbour*M15*A14
R488:
    EmM15 + A14 > EmU15 + A14
    kneighbour*EmM15*A14
R489:
    M15 + EmA14 > U15 + EmA14
    kneighbour*M15*EmA14
R490:
    M15 + A16 > U15 + A16
    kneighbour*M15*A16
R491:
    EmM15 + A16 > EmU15 + A16
    kneighbour*EmM15*A16
R492:
    M15 + EmA16 > U15 + EmA16
    kneighbour*M15*EmA16
R493:
    U15 + A14 > A15 + A14
    kneighbour*U15*A14
R494:
    EmU15 + A14 > EmA15 + A14
    kneighbour*EmU15*A14
R495:
    U15 + EmA14 > A15 + EmA14
    kneighbour*U15*EmA14
R496:
    U15 + A16 > A15 + A16
    kneighbour*U15*A16
R497:
    EmU15 + A16 > EmA15 + A16
    kneighbour*EmU15*A16
R498:
    U15 + EmA16 > A15 + EmA16
    kneighbour*U15*EmA16
R499:
    M16 > U16
    knoise*M16
R500:
    EmM16 > EmU16
    knoise*EmM16
R501:
    U16 > A16
    knoise*U16
R502:
    A16 > U16
    knoise*A16
R503:
    EmA16 > EmU16
    knoise*EmA16
R504:
    EmM16 > M16
    koff*EmM16
R505:
    EmU16 > U16
    koff*EmU16
R506:
    EmA16 > A16
    koff*EmA16
R507:
    EmU16 > EmM16
    kenz*EmU16
R508:
    M16 > EmM16
    krec*M16
R509:
    U16 + EmM17 > M16 + EmM17
    kenz_neigh*U16*EmM17
R510:
    EmU16 + EmM17 > EmM16 + EmM17
    kenz_neigh*EmU16*EmM17
R511:
    EmU16 + M17 > EmM16 + M17
    kenz_neigh*EmU16*M17
R512:
    U16 + EmM15 > M16 + EmM15
    kenz_neigh*U16*EmM15
R513:
    EmU16 + EmM15 > EmM16 + EmM15
    kenz_neigh*EmU16*EmM15
R514:
    EmU16 + M15 > EmM16 + M15
    kenz_neigh*EmU16*M15
R515:
    A16 + EmM17 > U16 + EmM17
    kneighbour*A16*EmM17
R516:
    EmA16 + EmM17 > EmU16 + EmM17
    kneighbour*EmA16*EmM17
R517:
    EmA16 + M17 > EmU16 + M17
    kneighbour*EmA16*M17
R518:
    A16 + EmM15 > U16 + EmM15
    kneighbour*A16*EmM15
R519:
    EmA16 + EmM15 > EmU16 + EmM15
    kneighbour*EmA16*EmM15
R520:
    EmA16 + M15 > EmU16 + M15
    kneighbour*EmA16*M15
R521:
    M16 + A15 > U16 + A15
    kneighbour*M16*A15
R522:
    EmM16 + A15 > EmU16 + A15
    kneighbour*EmM16*A15
R523:
    M16 + EmA15 > U16 + EmA15
    kneighbour*M16*EmA15
R524:
    M16 + A17 > U16 + A17
    kneighbour*M16*A17
R525:
    EmM16 + A17 > EmU16 + A17
    kneighbour*EmM16*A17
R526:
    M16 + EmA17 > U16 + EmA17
    kneighbour*M16*EmA17
R527:
    U16 + A15 > A16 + A15
    kneighbour*U16*A15
R528:
    EmU16 + A15 > EmA16 + A15
    kneighbour*EmU16*A15
R529:
    U16 + EmA15 > A16 + EmA15
    kneighbour*U16*EmA15
R530:
    U16 + A17 > A16 + A17
    kneighbour*U16*A17
R531:
    EmU16 + A17 > EmA16 + A17
    kneighbour*EmU16*A17
R532:
    U16 + EmA17 > A16 + EmA17
    kneighbour*U16*EmA17
R533:
    M17 > U17
    knoise*M17
R534:
    EmM17 > EmU17
    knoise*EmM17
R535:
    U17 > A17
    knoise*U17
R536:
    A17 > U17
    knoise*A17
R537:
    EmA17 > EmU17
    knoise*EmA17
R538:
    EmM17 > M17
    koff*EmM17
R539:
    EmU17 > U17
    koff*EmU17
R540:
    EmA17 > A17
    koff*EmA17
R541:
    EmU17 > EmM17
    kenz*EmU17
R542:
    M17 > EmM17
    krec*M17
R543:
    U17 + EmM18 > M17 + EmM18
    kenz_neigh*U17*EmM18
R544:
    EmU17 + EmM18 > EmM17 + EmM18
    kenz_neigh*EmU17*EmM18
R545:
    EmU17 + M18 > EmM17 + M18
    kenz_neigh*EmU17*M18
R546:
    U17 + EmM16 > M17 + EmM16
    kenz_neigh*U17*EmM16
R547:
    EmU17 + EmM16 > EmM17 + EmM16
    kenz_neigh*EmU17*EmM16
R548:
    EmU17 + M16 > EmM17 + M16
    kenz_neigh*EmU17*M16
R549:
    A17 + EmM18 > U17 + EmM18
    kneighbour*A17*EmM18
R550:
    EmA17 + EmM18 > EmU17 + EmM18
    kneighbour*EmA17*EmM18
R551:
    EmA17 + M18 > EmU17 + M18
    kneighbour*EmA17*M18
R552:
    A17 + EmM16 > U17 + EmM16
    kneighbour*A17*EmM16
R553:
    EmA17 + EmM16 > EmU17 + EmM16
    kneighbour*EmA17*EmM16
R554:
    EmA17 + M16 > EmU17 + M16
    kneighbour*EmA17*M16
R555:
    M17 + A16 > U17 + A16
    kneighbour*M17*A16
R556:
    EmM17 + A16 > EmU17 + A16
    kneighbour*EmM17*A16
R557:
    M17 + EmA16 > U17 + EmA16
    kneighbour*M17*EmA16
R558:
    M17 + A18 > U17 + A18
    kneighbour*M17*A18
R559:
    EmM17 + A18 > EmU17 + A18
    kneighbour*EmM17*A18
R560:
    M17 + EmA18 > U17 + EmA18
    kneighbour*M17*EmA18
R561:
    U17 + A16 > A17 + A16
    kneighbour*U17*A16
R562:
    EmU17 + A16 > EmA17 + A16
    kneighbour*EmU17*A16
R563:
    U17 + EmA16 > A17 + EmA16
    kneighbour*U17*EmA16
R564:
    U17 + A18 > A17 + A18
    kneighbour*U17*A18
R565:
    EmU17 + A18 > EmA17 + A18
    kneighbour*EmU17*A18
R566:
    U17 + EmA18 > A17 + EmA18
    kneighbour*U17*EmA18
R567:
    M18 > U18
    knoise*M18
R568:
    EmM18 > EmU18
    knoise*EmM18
R569:
    U18 > A18
    knoise*U18
R570:
    A18 > U18
    knoise*A18
R571:
    EmA18 > EmU18
    knoise*EmA18
R572:
    EmM18 > M18
    koff*EmM18
R573:
    EmU18 > U18
    koff*EmU18
R574:
    EmA18 > A18
    koff*EmA18
R575:
    EmU18 > EmM18
    kenz*EmU18
R576:
    M18 > EmM18
    krec*M18
R577:
    U18 + EmM19 > M18 + EmM19
    kenz_neigh*U18*EmM19
R578:
    EmU18 + EmM19 > EmM18 + EmM19
    kenz_neigh*EmU18*EmM19
R579:
    EmU18 + M19 > EmM18 + M19
    kenz_neigh*EmU18*M19
R580:
    U18 + EmM17 > M18 + EmM17
    kenz_neigh*U18*EmM17
R581:
    EmU18 + EmM17 > EmM18 + EmM17
    kenz_neigh*EmU18*EmM17
R582:
    EmU18 + M17 > EmM18 + M17
    kenz_neigh*EmU18*M17
R583:
    A18 + EmM19 > U18 + EmM19
    kneighbour*A18*EmM19
R584:
    EmA18 + EmM19 > EmU18 + EmM19
    kneighbour*EmA18*EmM19
R585:
    EmA18 + M19 > EmU18 + M19
    kneighbour*EmA18*M19
R586:
    A18 + EmM17 > U18 + EmM17
    kneighbour*A18*EmM17
R587:
    EmA18 + EmM17 > EmU18 + EmM17
    kneighbour*EmA18*EmM17
R588:
    EmA18 + M17 > EmU18 + M17
    kneighbour*EmA18*M17
R589:
    M18 + A17 > U18 + A17
    kneighbour*M18*A17
R590:
    EmM18 + A17 > EmU18 + A17
    kneighbour*EmM18*A17
R591:
    M18 + EmA17 > U18 + EmA17
    kneighbour*M18*EmA17
R592:
    M18 + A19 > U18 + A19
    kneighbour*M18*A19
R593:
    EmM18 + A19 > EmU18 + A19
    kneighbour*EmM18*A19
R594:
    M18 + EmA19 > U18 + EmA19
    kneighbour*M18*EmA19
R595:
    U18 + A17 > A18 + A17
    kneighbour*U18*A17
R596:
    EmU18 + A17 > EmA18 + A17
    kneighbour*EmU18*A17
R597:
    U18 + EmA17 > A18 + EmA17
    kneighbour*U18*EmA17
R598:
    U18 + A19 > A18 + A19
    kneighbour*U18*A19
R599:
    EmU18 + A19 > EmA18 + A19
    kneighbour*EmU18*A19
R600:
    U18 + EmA19 > A18 + EmA19
    kneighbour*U18*EmA19
R601:
    M19 > U19
    knoise*M19
R602:
    EmM19 > EmU19
    knoise*EmM19
R603:
    U19 > A19
    knoise*U19
R604:
    A19 > U19
    knoise*A19
R605:
    EmA19 > EmU19
    knoise*EmA19
R606:
    EmM19 > M19
    koff*EmM19
R607:
    EmU19 > U19
    koff*EmU19
R608:
    EmA19 > A19
    koff*EmA19
R609:
    EmU19 > EmM19
    kenz*EmU19
R610:
    M19 > EmM19
    krec*M19
R611:
    U19 + EmM20 > M19 + EmM20
    kenz_neigh*U19*EmM20
R612:
    EmU19 + EmM20 > EmM19 + EmM20
    kenz_neigh*EmU19*EmM20
R613:
    EmU19 + M20 > EmM19 + M20
    kenz_neigh*EmU19*M20
R614:
    U19 + EmM18 > M19 + EmM18
    kenz_neigh*U19*EmM18
R615:
    EmU19 + EmM18 > EmM19 + EmM18
    kenz_neigh*EmU19*EmM18
R616:
    EmU19 + M18 > EmM19 + M18
    kenz_neigh*EmU19*M18
R617:
    A19 + EmM20 > U19 + EmM20
    kneighbour*A19*EmM20
R618:
    EmA19 + EmM20 > EmU19 + EmM20
    kneighbour*EmA19*EmM20
R619:
    EmA19 + M20 > EmU19 + M20
    kneighbour*EmA19*M20
R620:
    A19 + EmM18 > U19 + EmM18
    kneighbour*A19*EmM18
R621:
    EmA19 + EmM18 > EmU19 + EmM18
    kneighbour*EmA19*EmM18
R622:
    EmA19 + M18 > EmU19 + M18
    kneighbour*EmA19*M18
R623:
    M19 + A18 > U19 + A18
    kneighbour*M19*A18
R624:
    EmM19 + A18 > EmU19 + A18
    kneighbour*EmM19*A18
R625:
    M19 + EmA18 > U19 + EmA18
    kneighbour*M19*EmA18
R626:
    M19 + A20 > U19 + A20
    kneighbour*M19*A20
R627:
    EmM19 + A20 > EmU19 + A20
    kneighbour*EmM19*A20
R628:
    M19 + EmA20 > U19 + EmA20
    kneighbour*M19*EmA20
R629:
    U19 + A18 > A19 + A18
    kneighbour*U19*A18
R630:
    EmU19 + A18 > EmA19 + A18
    kneighbour*EmU19*A18
R631:
    U19 + EmA18 > A19 + EmA18
    kneighbour*U19*EmA18
R632:
    U19 + A20 > A19 + A20
    kneighbour*U19*A20
R633:
    EmU19 + A20 > EmA19 + A20
    kneighbour*EmU19*A20
R634:
    U19 + EmA20 > A19 + EmA20
    kneighbour*U19*EmA20
R635:
    M20 > U20
    knoise*M20
R636:
    EmM20 > EmU20
    knoise*EmM20
R637:
    U20 > A20
    knoise*U20
R638:
    A20 > U20
    knoise*A20
R639:
    EmA20 > EmU20
    knoise*EmA20
R640:
    EmM20 > M20
    koff*EmM20
R641:
    EmU20 > U20
    koff*EmU20
R642:
    EmA20 > A20
    koff*EmA20
R643:
    EmU20 > EmM20
    kenz*EmU20
R644:
    M20 > EmM20
    krec*M20
R645:
    U20 + EmM19 > M20 + EmM19
    kenz_neigh*U20*EmM19
R646:
    EmU20 + EmM19 > EmM20 + EmM19
    kenz_neigh*EmU20*EmM19
R647:
    EmU20 + M19 > EmM20 + M19
    kenz_neigh*EmU20*M19
R648:
    A20 + EmM19 > U20 + EmM19
    kneighbour*A20*EmM19
R649:
    EmA20 + EmM19 > EmU20 + EmM19
    kneighbour*EmA20*EmM19
R650:
    EmA20 + M19 > EmU20 + M19
    kneighbour*EmA20*M19
R651:
    M20 + A19 > U20 + A19
    kneighbour*M20*A19
R652:
    EmM20 + A19 > EmU20 + A19
    kneighbour*EmM20*A19
R653:
    M20 + EmA19 > U20 + EmA19
    kneighbour*M20*EmA19
R654:
    U20 + A19 > A20 + A19
    kneighbour*U20*A19
R655:
    EmU20 + A19 > EmA20 + A19
    kneighbour*EmU20*A19
R656:
    U20 + EmA19 > A20 + EmA19
    kneighbour*U20*EmA19
R657:
    EmM1 + M2 > M1 + EmM2
    kdif*EmM1*M2
R658:
    EmM1 + U2 > M1 + EmU2
    kdif*EmM1*U2
R659:
    EmM1 + A2 > M1 + EmA2
    kdif*EmM1*A2
R660:
    EmU1 + M2 > U1 + EmM2
    kdif*EmU1*M2
R661:
    EmU1 + U2 > U1 + EmU2
    kdif*EmU1*U2
R662:
    EmU1 + A2 > U1 + EmA2
    kdif*EmU1*A2
R663:
    EmA1 + M2 > A1 + EmM2
    kdif*EmA1*M2
R664:
    EmA1 + U2 > A1 + EmU2
    kdif*EmA1*U2
R665:
    EmA1 + A2 > A1 + EmA2
    kdif*EmA1*A2
R666:
    EmM2 + M3 > M2 + EmM3
    kdif*EmM2*M3
R667:
    EmM2 + U3 > M2 + EmU3
    kdif*EmM2*U3
R668:
    EmM2 + A3 > M2 + EmA3
    kdif*EmM2*A3
R669:
    EmU2 + M3 > U2 + EmM3
    kdif*EmU2*M3
R670:
    EmU2 + U3 > U2 + EmU3
    kdif*EmU2*U3
R671:
    EmU2 + A3 > U2 + EmA3
    kdif*EmU2*A3
R672:
    EmA2 + M3 > A2 + EmM3
    kdif*EmA2*M3
R673:
    EmA2 + U3 > A2 + EmU3
    kdif*EmA2*U3
R674:
    EmA2 + A3 > A2 + EmA3
    kdif*EmA2*A3
R675:
    EmM3 + M4 > M3 + EmM4
    kdif*EmM3*M4
R676:
    EmM3 + U4 > M3 + EmU4
    kdif*EmM3*U4
R677:
    EmM3 + A4 > M3 + EmA4
    kdif*EmM3*A4
R678:
    EmU3 + M4 > U3 + EmM4
    kdif*EmU3*M4
R679:
    EmU3 + U4 > U3 + EmU4
    kdif*EmU3*U4
R680:
    EmU3 + A4 > U3 + EmA4
    kdif*EmU3*A4
R681:
    EmA3 + M4 > A3 + EmM4
    kdif*EmA3*M4
R682:
    EmA3 + U4 > A3 + EmU4
    kdif*EmA3*U4
R683:
    EmA3 + A4 > A3 + EmA4
    kdif*EmA3*A4
R684:
    EmM4 + M5 > M4 + EmM5
    kdif*EmM4*M5
R685:
    EmM4 + U5 > M4 + EmU5
    kdif*EmM4*U5
R686:
    EmM4 + A5 > M4 + EmA5
    kdif*EmM4*A5
R687:
    EmU4 + M5 > U4 + EmM5
    kdif*EmU4*M5
R688:
    EmU4 + U5 > U4 + EmU5
    kdif*EmU4*U5
R689:
    EmU4 + A5 > U4 + EmA5
    kdif*EmU4*A5
R690:
    EmA4 + M5 > A4 + EmM5
    kdif*EmA4*M5
R691:
    EmA4 + U5 > A4 + EmU5
    kdif*EmA4*U5
R692:
    EmA4 + A5 > A4 + EmA5
    kdif*EmA4*A5
R693:
    EmM5 + M6 > M5 + EmM6
    kdif*EmM5*M6
R694:
    EmM5 + U6 > M5 + EmU6
    kdif*EmM5*U6
R695:
    EmM5 + A6 > M5 + EmA6
    kdif*EmM5*A6
R696:
    EmU5 + M6 > U5 + EmM6
    kdif*EmU5*M6
R697:
    EmU5 + U6 > U5 + EmU6
    kdif*EmU5*U6
R698:
    EmU5 + A6 > U5 + EmA6
    kdif*EmU5*A6
R699:
    EmA5 + M6 > A5 + EmM6
    kdif*EmA5*M6
R700:
    EmA5 + U6 > A5 + EmU6
    kdif*EmA5*U6
R701:
    EmA5 + A6 > A5 + EmA6
    kdif*EmA5*A6
R702:
    EmM6 + M7 > M6 + EmM7
    kdif*EmM6*M7
R703:
    EmM6 + U7 > M6 + EmU7
    kdif*EmM6*U7
R704:
    EmM6 + A7 > M6 + EmA7
    kdif*EmM6*A7
R705:
    EmU6 + M7 > U6 + EmM7
    kdif*EmU6*M7
R706:
    EmU6 + U7 > U6 + EmU7
    kdif*EmU6*U7
R707:
    EmU6 + A7 > U6 + EmA7
    kdif*EmU6*A7
R708:
    EmA6 + M7 > A6 + EmM7
    kdif*EmA6*M7
R709:
    EmA6 + U7 > A6 + EmU7
    kdif*EmA6*U7
R710:
    EmA6 + A7 > A6 + EmA7
    kdif*EmA6*A7
R711:
    EmM7 + M8 > M7 + EmM8
    kdif*EmM7*M8
R712:
    EmM7 + U8 > M7 + EmU8
    kdif*EmM7*U8
R713:
    EmM7 + A8 > M7 + EmA8
    kdif*EmM7*A8
R714:
    EmU7 + M8 > U7 + EmM8
    kdif*EmU7*M8
R715:
    EmU7 + U8 > U7 + EmU8
    kdif*EmU7*U8
R716:
    EmU7 + A8 > U7 + EmA8
    kdif*EmU7*A8
R717:
    EmA7 + M8 > A7 + EmM8
    kdif*EmA7*M8
R718:
    EmA7 + U8 > A7 + EmU8
    kdif*EmA7*U8
R719:
    EmA7 + A8 > A7 + EmA8
    kdif*EmA7*A8
R720:
    EmM8 + M9 > M8 + EmM9
    kdif*EmM8*M9
R721:
    EmM8 + U9 > M8 + EmU9
    kdif*EmM8*U9
R722:
    EmM8 + A9 > M8 + EmA9
    kdif*EmM8*A9
R723:
    EmU8 + M9 > U8 + EmM9
    kdif*EmU8*M9
R724:
    EmU8 + U9 > U8 + EmU9
    kdif*EmU8*U9
R725:
    EmU8 + A9 > U8 + EmA9
    kdif*EmU8*A9
R726:
    EmA8 + M9 > A8 + EmM9
    kdif*EmA8*M9
R727:
    EmA8 + U9 > A8 + EmU9
    kdif*EmA8*U9
R728:
    EmA8 + A9 > A8 + EmA9
    kdif*EmA8*A9
R729:
    EmM9 + M10 > M9 + EmM10
    kdif*EmM9*M10
R730:
    EmM9 + U10 > M9 + EmU10
    kdif*EmM9*U10
R731:
    EmM9 + A10 > M9 + EmA10
    kdif*EmM9*A10
R732:
    EmU9 + M10 > U9 + EmM10
    kdif*EmU9*M10
R733:
    EmU9 + U10 > U9 + EmU10
    kdif*EmU9*U10
R734:
    EmU9 + A10 > U9 + EmA10
    kdif*EmU9*A10
R735:
    EmA9 + M10 > A9 + EmM10
    kdif*EmA9*M10
R736:
    EmA9 + U10 > A9 + EmU10
    kdif*EmA9*U10
R737:
    EmA9 + A10 > A9 + EmA10
    kdif*EmA9*A10
R738:
    EmM10 + M11 > M10 + EmM11
    kdif*EmM10*M11
R739:
    EmM10 + U11 > M10 + EmU11
    kdif*EmM10*U11
R740:
    EmM10 + A11 > M10 + EmA11
    kdif*EmM10*A11
R741:
    EmU10 + M11 > U10 + EmM11
    kdif*EmU10*M11
R742:
    EmU10 + U11 > U10 + EmU11
    kdif*EmU10*U11
R743:
    EmU10 + A11 > U10 + EmA11
    kdif*EmU10*A11
R744:
    EmA10 + M11 > A10 + EmM11
    kdif*EmA10*M11
R745:
    EmA10 + U11 > A10 + EmU11
    kdif*EmA10*U11
R746:
    EmA10 + A11 > A10 + EmA11
    kdif*EmA10*A11
R747:
    EmM11 + M12 > M11 + EmM12
    kdif*EmM11*M12
R748:
    EmM11 + U12 > M11 + EmU12
    kdif*EmM11*U12
R749:
    EmM11 + A12 > M11 + EmA12
    kdif*EmM11*A12
R750:
    EmU11 + M12 > U11 + EmM12
    kdif*EmU11*M12
R751:
    EmU11 + U12 > U11 + EmU12
    kdif*EmU11*U12
R752:
    EmU11 + A12 > U11 + EmA12
    kdif*EmU11*A12
R753:
    EmA11 + M12 > A11 + EmM12
    kdif*EmA11*M12
R754:
    EmA11 + U12 > A11 + EmU12
    kdif*EmA11*U12
R755:
    EmA11 + A12 > A11 + EmA12
    kdif*EmA11*A12
R756:
    EmM12 + M13 > M12 + EmM13
    kdif*EmM12*M13
R757:
    EmM12 + U13 > M12 + EmU13
    kdif*EmM12*U13
R758:
    EmM12 + A13 > M12 + EmA13
    kdif*EmM12*A13
R759:
    EmU12 + M13 > U12 + EmM13
    kdif*EmU12*M13
R760:
    EmU12 + U13 > U12 + EmU13
    kdif*EmU12*U13
R761:
    EmU12 + A13 > U12 + EmA13
    kdif*EmU12*A13
R762:
    EmA12 + M13 > A12 + EmM13
    kdif*EmA12*M13
R763:
    EmA12 + U13 > A12 + EmU13
    kdif*EmA12*U13
R764:
    EmA12 + A13 > A12 + EmA13
    kdif*EmA12*A13
R765:
    EmM13 + M14 > M13 + EmM14
    kdif*EmM13*M14
R766:
    EmM13 + U14 > M13 + EmU14
    kdif*EmM13*U14
R767:
    EmM13 + A14 > M13 + EmA14
    kdif*EmM13*A14
R768:
    EmU13 + M14 > U13 + EmM14
    kdif*EmU13*M14
R769:
    EmU13 + U14 > U13 + EmU14
    kdif*EmU13*U14
R770:
    EmU13 + A14 > U13 + EmA14
    kdif*EmU13*A14
R771:
    EmA13 + M14 > A13 + EmM14
    kdif*EmA13*M14
R772:
    EmA13 + U14 > A13 + EmU14
    kdif*EmA13*U14
R773:
    EmA13 + A14 > A13 + EmA14
    kdif*EmA13*A14
R774:
    EmM14 + M15 > M14 + EmM15
    kdif*EmM14*M15
R775:
    EmM14 + U15 > M14 + EmU15
    kdif*EmM14*U15
R776:
    EmM14 + A15 > M14 + EmA15
    kdif*EmM14*A15
R777:
    EmU14 + M15 > U14 + EmM15
    kdif*EmU14*M15
R778:
    EmU14 + U15 > U14 + EmU15
    kdif*EmU14*U15
R779:
    EmU14 + A15 > U14 + EmA15
    kdif*EmU14*A15
R780:
    EmA14 + M15 > A14 + EmM15
    kdif*EmA14*M15
R781:
    EmA14 + U15 > A14 + EmU15
    kdif*EmA14*U15
R782:
    EmA14 + A15 > A14 + EmA15
    kdif*EmA14*A15
R783:
    EmM15 + M16 > M15 + EmM16
    kdif*EmM15*M16
R784:
    EmM15 + U16 > M15 + EmU16
    kdif*EmM15*U16
R785:
    EmM15 + A16 > M15 + EmA16
    kdif*EmM15*A16
R786:
    EmU15 + M16 > U15 + EmM16
    kdif*EmU15*M16
R787:
    EmU15 + U16 > U15 + EmU16
    kdif*EmU15*U16
R788:
    EmU15 + A16 > U15 + EmA16
    kdif*EmU15*A16
R789:
    EmA15 + M16 > A15 + EmM16
    kdif*EmA15*M16
R790:
    EmA15 + U16 > A15 + EmU16
    kdif*EmA15*U16
R791:
    EmA15 + A16 > A15 + EmA16
    kdif*EmA15*A16
R792:
    EmM16 + M17 > M16 + EmM17
    kdif*EmM16*M17
R793:
    EmM16 + U17 > M16 + EmU17
    kdif*EmM16*U17
R794:
    EmM16 + A17 > M16 + EmA17
    kdif*EmM16*A17
R795:
    EmU16 + M17 > U16 + EmM17
    kdif*EmU16*M17
R796:
    EmU16 + U17 > U16 + EmU17
    kdif*EmU16*U17
R797:
    EmU16 + A17 > U16 + EmA17
    kdif*EmU16*A17
R798:
    EmA16 + M17 > A16 + EmM17
    kdif*EmA16*M17
R799:
    EmA16 + U17 > A16 + EmU17
    kdif*EmA16*U17
R800:
    EmA16 + A17 > A16 + EmA17
    kdif*EmA16*A17
R801:
    EmM17 + M18 > M17 + EmM18
    kdif*EmM17*M18
R802:
    EmM17 + U18 > M17 + EmU18
    kdif*EmM17*U18
R803:
    EmM17 + A18 > M17 + EmA18
    kdif*EmM17*A18
R804:
    EmU17 + M18 > U17 + EmM18
    kdif*EmU17*M18
R805:
    EmU17 + U18 > U17 + EmU18
    kdif*EmU17*U18
R806:
    EmU17 + A18 > U17 + EmA18
    kdif*EmU17*A18
R807:
    EmA17 + M18 > A17 + EmM18
    kdif*EmA17*M18
R808:
    EmA17 + U18 > A17 + EmU18
    kdif*EmA17*U18
R809:
    EmA17 + A18 > A17 + EmA18
    kdif*EmA17*A18
R810:
    EmM18 + M19 > M18 + EmM19
    kdif*EmM18*M19
R811:
    EmM18 + U19 > M18 + EmU19
    kdif*EmM18*U19
R812:
    EmM18 + A19 > M18 + EmA19
    kdif*EmM18*A19
R813:
    EmU18 + M19 > U18 + EmM19
    kdif*EmU18*M19
R814:
    EmU18 + U19 > U18 + EmU19
    kdif*EmU18*U19
R815:
    EmU18 + A19 > U18 + EmA19
    kdif*EmU18*A19
R816:
    EmA18 + M19 > A18 + EmM19
    kdif*EmA18*M19
R817:
    EmA18 + U19 > A18 + EmU19
    kdif*EmA18*U19
R818:
    EmA18 + A19 > A18 + EmA19
    kdif*EmA18*A19
R819:
    EmM19 + M20 > M19 + EmM20
    kdif*EmM19*M20
R820:
    EmM19 + U20 > M19 + EmU20
    kdif*EmM19*U20
R821:
    EmM19 + A20 > M19 + EmA20
    kdif*EmM19*A20
R822:
    EmU19 + M20 > U19 + EmM20
    kdif*EmU19*M20
R823:
    EmU19 + U20 > U19 + EmU20
    kdif*EmU19*U20
R824:
    EmU19 + A20 > U19 + EmA20
    kdif*EmU19*A20
R825:
    EmA19 + M20 > A19 + EmM20
    kdif*EmA19*M20
R826:
    EmA19 + U20 > A19 + EmU20
    kdif*EmA19*U20
R827:
    EmA19 + A20 > A19 + EmA20
    kdif*EmA19*A20
R828:
    EmM2 + M1 > M2 + EmM1
    kdif*EmM2*M1
R829:
    EmM2 + U1 > M2 + EmU1
    kdif*EmM2*U1
R830:
    EmM2 + A1 > M2 + EmA1
    kdif*EmM2*A1
R831:
    EmU2 + M1 > U2 + EmM1
    kdif*EmU2*M1
R832:
    EmU2 + U1 > U2 + EmU1
    kdif*EmU2*U1
R833:
    EmU2 + A1 > U2 + EmA1
    kdif*EmU2*A1
R834:
    EmA2 + M1 > A2 + EmM1
    kdif*EmA2*M1
R835:
    EmA2 + U1 > A2 + EmU1
    kdif*EmA2*U1
R836:
    EmA2 + A1 > A2 + EmA1
    kdif*EmA2*A1
R837:
    EmM3 + M2 > M3 + EmM2
    kdif*EmM3*M2
R838:
    EmM3 + U2 > M3 + EmU2
    kdif*EmM3*U2
R839:
    EmM3 + A2 > M3 + EmA2
    kdif*EmM3*A2
R840:
    EmU3 + M2 > U3 + EmM2
    kdif*EmU3*M2
R841:
    EmU3 + U2 > U3 + EmU2
    kdif*EmU3*U2
R842:
    EmU3 + A2 > U3 + EmA2
    kdif*EmU3*A2
R843:
    EmA3 + M2 > A3 + EmM2
    kdif*EmA3*M2
R844:
    EmA3 + U2 > A3 + EmU2
    kdif*EmA3*U2
R845:
    EmA3 + A2 > A3 + EmA2
    kdif*EmA3*A2
R846:
    EmM4 + M3 > M4 + EmM3
    kdif*EmM4*M3
R847:
    EmM4 + U3 > M4 + EmU3
    kdif*EmM4*U3
R848:
    EmM4 + A3 > M4 + EmA3
    kdif*EmM4*A3
R849:
    EmU4 + M3 > U4 + EmM3
    kdif*EmU4*M3
R850:
    EmU4 + U3 > U4 + EmU3
    kdif*EmU4*U3
R851:
    EmU4 + A3 > U4 + EmA3
    kdif*EmU4*A3
R852:
    EmA4 + M3 > A4 + EmM3
    kdif*EmA4*M3
R853:
    EmA4 + U3 > A4 + EmU3
    kdif*EmA4*U3
R854:
    EmA4 + A3 > A4 + EmA3
    kdif*EmA4*A3
R855:
    EmM5 + M4 > M5 + EmM4
    kdif*EmM5*M4
R856:
    EmM5 + U4 > M5 + EmU4
    kdif*EmM5*U4
R857:
    EmM5 + A4 > M5 + EmA4
    kdif*EmM5*A4
R858:
    EmU5 + M4 > U5 + EmM4
    kdif*EmU5*M4
R859:
    EmU5 + U4 > U5 + EmU4
    kdif*EmU5*U4
R860:
    EmU5 + A4 > U5 + EmA4
    kdif*EmU5*A4
R861:
    EmA5 + M4 > A5 + EmM4
    kdif*EmA5*M4
R862:
    EmA5 + U4 > A5 + EmU4
    kdif*EmA5*U4
R863:
    EmA5 + A4 > A5 + EmA4
    kdif*EmA5*A4
R864:
    EmM6 + M5 > M6 + EmM5
    kdif*EmM6*M5
R865:
    EmM6 + U5 > M6 + EmU5
    kdif*EmM6*U5
R866:
    EmM6 + A5 > M6 + EmA5
    kdif*EmM6*A5
R867:
    EmU6 + M5 > U6 + EmM5
    kdif*EmU6*M5
R868:
    EmU6 + U5 > U6 + EmU5
    kdif*EmU6*U5
R869:
    EmU6 + A5 > U6 + EmA5
    kdif*EmU6*A5
R870:
    EmA6 + M5 > A6 + EmM5
    kdif*EmA6*M5
R871:
    EmA6 + U5 > A6 + EmU5
    kdif*EmA6*U5
R872:
    EmA6 + A5 > A6 + EmA5
    kdif*EmA6*A5
R873:
    EmM7 + M6 > M7 + EmM6
    kdif*EmM7*M6
R874:
    EmM7 + U6 > M7 + EmU6
    kdif*EmM7*U6
R875:
    EmM7 + A6 > M7 + EmA6
    kdif*EmM7*A6
R876:
    EmU7 + M6 > U7 + EmM6
    kdif*EmU7*M6
R877:
    EmU7 + U6 > U7 + EmU6
    kdif*EmU7*U6
R878:
    EmU7 + A6 > U7 + EmA6
    kdif*EmU7*A6
R879:
    EmA7 + M6 > A7 + EmM6
    kdif*EmA7*M6
R880:
    EmA7 + U6 > A7 + EmU6
    kdif*EmA7*U6
R881:
    EmA7 + A6 > A7 + EmA6
    kdif*EmA7*A6
R882:
    EmM8 + M7 > M8 + EmM7
    kdif*EmM8*M7
R883:
    EmM8 + U7 > M8 + EmU7
    kdif*EmM8*U7
R884:
    EmM8 + A7 > M8 + EmA7
    kdif*EmM8*A7
R885:
    EmU8 + M7 > U8 + EmM7
    kdif*EmU8*M7
R886:
    EmU8 + U7 > U8 + EmU7
    kdif*EmU8*U7
R887:
    EmU8 + A7 > U8 + EmA7
    kdif*EmU8*A7
R888:
    EmA8 + M7 > A8 + EmM7
    kdif*EmA8*M7
R889:
    EmA8 + U7 > A8 + EmU7
    kdif*EmA8*U7
R890:
    EmA8 + A7 > A8 + EmA7
    kdif*EmA8*A7
R891:
    EmM9 + M8 > M9 + EmM8
    kdif*EmM9*M8
R892:
    EmM9 + U8 > M9 + EmU8
    kdif*EmM9*U8
R893:
    EmM9 + A8 > M9 + EmA8
    kdif*EmM9*A8
R894:
    EmU9 + M8 > U9 + EmM8
    kdif*EmU9*M8
R895:
    EmU9 + U8 > U9 + EmU8
    kdif*EmU9*U8
R896:
    EmU9 + A8 > U9 + EmA8
    kdif*EmU9*A8
R897:
    EmA9 + M8 > A9 + EmM8
    kdif*EmA9*M8
R898:
    EmA9 + U8 > A9 + EmU8
    kdif*EmA9*U8
R899:
    EmA9 + A8 > A9 + EmA8
    kdif*EmA9*A8
R900:
    EmM10 + M9 > M10 + EmM9
    kdif*EmM10*M9
R901:
    EmM10 + U9 > M10 + EmU9
    kdif*EmM10*U9
R902:
    EmM10 + A9 > M10 + EmA9
    kdif*EmM10*A9
R903:
    EmU10 + M9 > U10 + EmM9
    kdif*EmU10*M9
R904:
    EmU10 + U9 > U10 + EmU9
    kdif*EmU10*U9
R905:
    EmU10 + A9 > U10 + EmA9
    kdif*EmU10*A9
R906:
    EmA10 + M9 > A10 + EmM9
    kdif*EmA10*M9
R907:
    EmA10 + U9 > A10 + EmU9
    kdif*EmA10*U9
R908:
    EmA10 + A9 > A10 + EmA9
    kdif*EmA10*A9
R909:
    EmM11 + M10 > M11 + EmM10
    kdif*EmM11*M10
R910:
    EmM11 + U10 > M11 + EmU10
    kdif*EmM11*U10
R911:
    EmM11 + A10 > M11 + EmA10
    kdif*EmM11*A10
R912:
    EmU11 + M10 > U11 + EmM10
    kdif*EmU11*M10
R913:
    EmU11 + U10 > U11 + EmU10
    kdif*EmU11*U10
R914:
    EmU11 + A10 > U11 + EmA10
    kdif*EmU11*A10
R915:
    EmA11 + M10 > A11 + EmM10
    kdif*EmA11*M10
R916:
    EmA11 + U10 > A11 + EmU10
    kdif*EmA11*U10
R917:
    EmA11 + A10 > A11 + EmA10
    kdif*EmA11*A10
R918:
    EmM12 + M11 > M12 + EmM11
    kdif*EmM12*M11
R919:
    EmM12 + U11 > M12 + EmU11
    kdif*EmM12*U11
R920:
    EmM12 + A11 > M12 + EmA11
    kdif*EmM12*A11
R921:
    EmU12 + M11 > U12 + EmM11
    kdif*EmU12*M11
R922:
    EmU12 + U11 > U12 + EmU11
    kdif*EmU12*U11
R923:
    EmU12 + A11 > U12 + EmA11
    kdif*EmU12*A11
R924:
    EmA12 + M11 > A12 + EmM11
    kdif*EmA12*M11
R925:
    EmA12 + U11 > A12 + EmU11
    kdif*EmA12*U11
R926:
    EmA12 + A11 > A12 + EmA11
    kdif*EmA12*A11
R927:
    EmM13 + M12 > M13 + EmM12
    kdif*EmM13*M12
R928:
    EmM13 + U12 > M13 + EmU12
    kdif*EmM13*U12
R929:
    EmM13 + A12 > M13 + EmA12
    kdif*EmM13*A12
R930:
    EmU13 + M12 > U13 + EmM12
    kdif*EmU13*M12
R931:
    EmU13 + U12 > U13 + EmU12
    kdif*EmU13*U12
R932:
    EmU13 + A12 > U13 + EmA12
    kdif*EmU13*A12
R933:
    EmA13 + M12 > A13 + EmM12
    kdif*EmA13*M12
R934:
    EmA13 + U12 > A13 + EmU12
    kdif*EmA13*U12
R935:
    EmA13 + A12 > A13 + EmA12
    kdif*EmA13*A12
R936:
    EmM14 + M13 > M14 + EmM13
    kdif*EmM14*M13
R937:
    EmM14 + U13 > M14 + EmU13
    kdif*EmM14*U13
R938:
    EmM14 + A13 > M14 + EmA13
    kdif*EmM14*A13
R939:
    EmU14 + M13 > U14 + EmM13
    kdif*EmU14*M13
R940:
    EmU14 + U13 > U14 + EmU13
    kdif*EmU14*U13
R941:
    EmU14 + A13 > U14 + EmA13
    kdif*EmU14*A13
R942:
    EmA14 + M13 > A14 + EmM13
    kdif*EmA14*M13
R943:
    EmA14 + U13 > A14 + EmU13
    kdif*EmA14*U13
R944:
    EmA14 + A13 > A14 + EmA13
    kdif*EmA14*A13
R945:
    EmM15 + M14 > M15 + EmM14
    kdif*EmM15*M14
R946:
    EmM15 + U14 > M15 + EmU14
    kdif*EmM15*U14
R947:
    EmM15 + A14 > M15 + EmA14
    kdif*EmM15*A14
R948:
    EmU15 + M14 > U15 + EmM14
    kdif*EmU15*M14
R949:
    EmU15 + U14 > U15 + EmU14
    kdif*EmU15*U14
R950:
    EmU15 + A14 > U15 + EmA14
    kdif*EmU15*A14
R951:
    EmA15 + M14 > A15 + EmM14
    kdif*EmA15*M14
R952:
    EmA15 + U14 > A15 + EmU14
    kdif*EmA15*U14
R953:
    EmA15 + A14 > A15 + EmA14
    kdif*EmA15*A14
R954:
    EmM16 + M15 > M16 + EmM15
    kdif*EmM16*M15
R955:
    EmM16 + U15 > M16 + EmU15
    kdif*EmM16*U15
R956:
    EmM16 + A15 > M16 + EmA15
    kdif*EmM16*A15
R957:
    EmU16 + M15 > U16 + EmM15
    kdif*EmU16*M15
R958:
    EmU16 + U15 > U16 + EmU15
    kdif*EmU16*U15
R959:
    EmU16 + A15 > U16 + EmA15
    kdif*EmU16*A15
R960:
    EmA16 + M15 > A16 + EmM15
    kdif*EmA16*M15
R961:
    EmA16 + U15 > A16 + EmU15
    kdif*EmA16*U15
R962:
    EmA16 + A15 > A16 + EmA15
    kdif*EmA16*A15
R963:
    EmM17 + M16 > M17 + EmM16
    kdif*EmM17*M16
R964:
    EmM17 + U16 > M17 + EmU16
    kdif*EmM17*U16
R965:
    EmM17 + A16 > M17 + EmA16
    kdif*EmM17*A16
R966:
    EmU17 + M16 > U17 + EmM16
    kdif*EmU17*M16
R967:
    EmU17 + U16 > U17 + EmU16
    kdif*EmU17*U16
R968:
    EmU17 + A16 > U17 + EmA16
    kdif*EmU17*A16
R969:
    EmA17 + M16 > A17 + EmM16
    kdif*EmA17*M16
R970:
    EmA17 + U16 > A17 + EmU16
    kdif*EmA17*U16
R971:
    EmA17 + A16 > A17 + EmA16
    kdif*EmA17*A16
R972:
    EmM18 + M17 > M18 + EmM17
    kdif*EmM18*M17
R973:
    EmM18 + U17 > M18 + EmU17
    kdif*EmM18*U17
R974:
    EmM18 + A17 > M18 + EmA17
    kdif*EmM18*A17
R975:
    EmU18 + M17 > U18 + EmM17
    kdif*EmU18*M17
R976:
    EmU18 + U17 > U18 + EmU17
    kdif*EmU18*U17
R977:
    EmU18 + A17 > U18 + EmA17
    kdif*EmU18*A17
R978:
    EmA18 + M17 > A18 + EmM17
    kdif*EmA18*M17
R979:
    EmA18 + U17 > A18 + EmU17
    kdif*EmA18*U17
R980:
    EmA18 + A17 > A18 + EmA17
    kdif*EmA18*A17
R981:
    EmM19 + M18 > M19 + EmM18
    kdif*EmM19*M18
R982:
    EmM19 + U18 > M19 + EmU18
    kdif*EmM19*U18
R983:
    EmM19 + A18 > M19 + EmA18
    kdif*EmM19*A18
R984:
    EmU19 + M18 > U19 + EmM18
    kdif*EmU19*M18
R985:
    EmU19 + U18 > U19 + EmU18
    kdif*EmU19*U18
R986:
    EmU19 + A18 > U19 + EmA18
    kdif*EmU19*A18
R987:
    EmA19 + M18 > A19 + EmM18
    kdif*EmA19*M18
R988:
    EmA19 + U18 > A19 + EmU18
    kdif*EmA19*U18
R989:
    EmA19 + A18 > A19 + EmA18
    kdif*EmA19*A18
R990:
    EmM20 + M19 > M20 + EmM19
    kdif*EmM20*M19
R991:
    EmM20 + U19 > M20 + EmU19
    kdif*EmM20*U19
R992:
    EmM20 + A19 > M20 + EmA19
    kdif*EmM20*A19
R993:
    EmU20 + M19 > U20 + EmM19
    kdif*EmU20*M19
R994:
    EmU20 + U19 > U20 + EmU19
    kdif*EmU20*U19
R995:
    EmU20 + A19 > U20 + EmA19
    kdif*EmU20*A19
R996:
    EmA20 + M19 > A20 + EmM19
    kdif*EmA20*M19
R997:
    EmA20 + U19 > A20 + EmU19
    kdif*EmA20*U19
R998:
    EmA20 + A19 > A20 + EmA19
    kdif*EmA20*A19
R999:
    M10 > EmM10
    kon*M10
R1000:
    U10 > EmU10
    kon*U10
R1001:
    A10 > EmA10
    kon*A10

# InitPar
knoise = 1.0
kneighbour = 2.0
kenz = 5.0
kon = 1.0
koff = 0.1
kdif = 0.6
kenz_neigh = 6.0
krec = 0.1

# InitVar
M1=0
EmM1=0
U1=0
EmU1=1
A1=0
EmA1=0
M2=0
EmM2=0
U2=0
EmU2=1
A2=0
EmA2=0
M3=0
EmM3=0
U3=0
EmU3=1
A3=0
EmA3=0
M4=1
EmM4=0
U4=0
EmU4=0
A4=0
EmA4=0
M5=0
EmM5=0
U5=1
EmU5=0
A5=0
EmA5=0
M6=0
EmM6=0
U6=0
EmU6=0
A6=0
EmA6=1
M7=1
EmM7=0
U7=0
EmU7=0
A7=0
EmA7=0
M8=1
EmM8=0
U8=0
EmU8=0
A8=0
EmA8=0
M9=0
EmM9=0
U9=0
EmU9=1
A9=0
EmA9=0
M10=0
EmM10=0
U10=0
EmU10=1
A10=0
EmA10=0
M11=0
EmM11=0
U11=0
EmU11=1
A11=0
EmA11=0
M12=0
EmM12=0
U12=0
EmU12=1
A12=0
EmA12=0
M13=0
EmM13=0
U13=0
EmU13=1
A13=0
EmA13=0
M14=0
EmM14=0
U14=0
EmU14=0
A14=1
EmA14=0
M15=0
EmM15=1
U15=0
EmU15=0
A15=0
EmA15=0
M16=0
EmM16=1
U16=0
EmU16=0
A16=0
EmA16=0
M17=0
EmM17=0
U17=0
EmU17=1
A17=0
EmA17=0
M18=0
EmM18=0
U18=0
EmU18=0
A18=1
EmA18=0
M19=0
EmM19=0
U19=0
EmU19=0
A19=0
EmA19=1
M20=0
EmM20=0
U20=0
EmU20=1
A20=0
EmA20=0
"""
