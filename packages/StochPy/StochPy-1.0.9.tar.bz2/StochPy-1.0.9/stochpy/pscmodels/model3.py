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
    U1 + EmM2 > M1 + EmM2
    kenz_neigh*U1*EmM2
R11:
    EmU1 + EmM2 > EmM1 + EmM2
    kenz_neigh*EmU1*EmM2
R12:
    EmU1 + M2 > EmM1 + M2
    kenz_neigh*EmU1*M2
R13:
    A1 + EmM2 > U1 + EmM2
    kneighbour*A1*EmM2
R14:
    EmA1 + EmM2 > EmU1 + EmM2
    kneighbour*EmA1*EmM2
R15:
    EmA1 + M2 > EmU1 + M2
    kneighbour*EmA1*M2
R16:
    M1 + A2 > U1 + A2
    kneighbour*M1*A2
R17:
    EmM1 + A2 > EmU1 + A2
    kneighbour*EmM1*A2
R18:
    M1 + EmA2 > U1 + EmA2
    kneighbour*M1*EmA2
R19:
    U1 + A2 > A1 + A2
    kneighbour*U1*A2
R20:
    EmU1 + A2 > EmA1 + A2
    kneighbour*EmU1*A2
R21:
    U1 + EmA2 > A1 + EmA2
    kneighbour*U1*EmA2
R22:
    M2 > U2
    knoise*M2
R23:
    EmM2 > EmU2
    knoise*EmM2
R24:
    U2 > A2
    knoise*U2
R25:
    A2 > U2
    knoise*A2
R26:
    EmA2 > EmU2
    knoise*EmA2
R27:
    EmM2 > M2
    koff*EmM2
R28:
    EmU2 > U2
    koff*EmU2
R29:
    EmA2 > A2
    koff*EmA2
R30:
    EmU2 > EmM2
    kenz*EmU2
R31:
    U2 + EmM3 > M2 + EmM3
    kenz_neigh*U2*EmM3
R32:
    EmU2 + EmM3 > EmM2 + EmM3
    kenz_neigh*EmU2*EmM3
R33:
    EmU2 + M3 > EmM2 + M3
    kenz_neigh*EmU2*M3
R34:
    U2 + EmM1 > M2 + EmM1
    kenz_neigh*U2*EmM1
R35:
    EmU2 + EmM1 > EmM2 + EmM1
    kenz_neigh*EmU2*EmM1
R36:
    EmU2 + M1 > EmM2 + M1
    kenz_neigh*EmU2*M1
R37:
    A2 + EmM3 > U2 + EmM3
    kneighbour*A2*EmM3
R38:
    EmA2 + EmM3 > EmU2 + EmM3
    kneighbour*EmA2*EmM3
R39:
    EmA2 + M3 > EmU2 + M3
    kneighbour*EmA2*M3
R40:
    A2 + EmM1 > U2 + EmM1
    kneighbour*A2*EmM1
R41:
    EmA2 + EmM1 > EmU2 + EmM1
    kneighbour*EmA2*EmM1
R42:
    EmA2 + M1 > EmU2 + M1
    kneighbour*EmA2*M1
R43:
    M2 + A1 > U2 + A1
    kneighbour*M2*A1
R44:
    EmM2 + A1 > EmU2 + A1
    kneighbour*EmM2*A1
R45:
    M2 + EmA1 > U2 + EmA1
    kneighbour*M2*EmA1
R46:
    M2 + A3 > U2 + A3
    kneighbour*M2*A3
R47:
    EmM2 + A3 > EmU2 + A3
    kneighbour*EmM2*A3
R48:
    M2 + EmA3 > U2 + EmA3
    kneighbour*M2*EmA3
R49:
    U2 + A1 > A2 + A1
    kneighbour*U2*A1
R50:
    EmU2 + A1 > EmA2 + A1
    kneighbour*EmU2*A1
R51:
    U2 + EmA1 > A2 + EmA1
    kneighbour*U2*EmA1
R52:
    U2 + A3 > A2 + A3
    kneighbour*U2*A3
R53:
    EmU2 + A3 > EmA2 + A3
    kneighbour*EmU2*A3
R54:
    U2 + EmA3 > A2 + EmA3
    kneighbour*U2*EmA3
R55:
    M3 > U3
    knoise*M3
R56:
    EmM3 > EmU3
    knoise*EmM3
R57:
    U3 > A3
    knoise*U3
R58:
    A3 > U3
    knoise*A3
R59:
    EmA3 > EmU3
    knoise*EmA3
R60:
    EmM3 > M3
    koff*EmM3
R61:
    EmU3 > U3
    koff*EmU3
R62:
    EmA3 > A3
    koff*EmA3
R63:
    EmU3 > EmM3
    kenz*EmU3
R64:
    U3 + EmM4 > M3 + EmM4
    kenz_neigh*U3*EmM4
R65:
    EmU3 + EmM4 > EmM3 + EmM4
    kenz_neigh*EmU3*EmM4
R66:
    EmU3 + M4 > EmM3 + M4
    kenz_neigh*EmU3*M4
R67:
    U3 + EmM2 > M3 + EmM2
    kenz_neigh*U3*EmM2
R68:
    EmU3 + EmM2 > EmM3 + EmM2
    kenz_neigh*EmU3*EmM2
R69:
    EmU3 + M2 > EmM3 + M2
    kenz_neigh*EmU3*M2
R70:
    A3 + EmM4 > U3 + EmM4
    kneighbour*A3*EmM4
R71:
    EmA3 + EmM4 > EmU3 + EmM4
    kneighbour*EmA3*EmM4
R72:
    EmA3 + M4 > EmU3 + M4
    kneighbour*EmA3*M4
R73:
    A3 + EmM2 > U3 + EmM2
    kneighbour*A3*EmM2
R74:
    EmA3 + EmM2 > EmU3 + EmM2
    kneighbour*EmA3*EmM2
R75:
    EmA3 + M2 > EmU3 + M2
    kneighbour*EmA3*M2
R76:
    M3 + A2 > U3 + A2
    kneighbour*M3*A2
R77:
    EmM3 + A2 > EmU3 + A2
    kneighbour*EmM3*A2
R78:
    M3 + EmA2 > U3 + EmA2
    kneighbour*M3*EmA2
R79:
    M3 + A4 > U3 + A4
    kneighbour*M3*A4
R80:
    EmM3 + A4 > EmU3 + A4
    kneighbour*EmM3*A4
R81:
    M3 + EmA4 > U3 + EmA4
    kneighbour*M3*EmA4
R82:
    U3 + A2 > A3 + A2
    kneighbour*U3*A2
R83:
    EmU3 + A2 > EmA3 + A2
    kneighbour*EmU3*A2
R84:
    U3 + EmA2 > A3 + EmA2
    kneighbour*U3*EmA2
R85:
    U3 + A4 > A3 + A4
    kneighbour*U3*A4
R86:
    EmU3 + A4 > EmA3 + A4
    kneighbour*EmU3*A4
R87:
    U3 + EmA4 > A3 + EmA4
    kneighbour*U3*EmA4
R88:
    M4 > U4
    knoise*M4
R89:
    EmM4 > EmU4
    knoise*EmM4
R90:
    U4 > A4
    knoise*U4
R91:
    A4 > U4
    knoise*A4
R92:
    EmA4 > EmU4
    knoise*EmA4
R93:
    EmM4 > M4
    koff*EmM4
R94:
    EmU4 > U4
    koff*EmU4
R95:
    EmA4 > A4
    koff*EmA4
R96:
    EmU4 > EmM4
    kenz*EmU4
R97:
    U4 + EmM5 > M4 + EmM5
    kenz_neigh*U4*EmM5
R98:
    EmU4 + EmM5 > EmM4 + EmM5
    kenz_neigh*EmU4*EmM5
R99:
    EmU4 + M5 > EmM4 + M5
    kenz_neigh*EmU4*M5
R100:
    U4 + EmM3 > M4 + EmM3
    kenz_neigh*U4*EmM3
R101:
    EmU4 + EmM3 > EmM4 + EmM3
    kenz_neigh*EmU4*EmM3
R102:
    EmU4 + M3 > EmM4 + M3
    kenz_neigh*EmU4*M3
R103:
    A4 + EmM5 > U4 + EmM5
    kneighbour*A4*EmM5
R104:
    EmA4 + EmM5 > EmU4 + EmM5
    kneighbour*EmA4*EmM5
R105:
    EmA4 + M5 > EmU4 + M5
    kneighbour*EmA4*M5
R106:
    A4 + EmM3 > U4 + EmM3
    kneighbour*A4*EmM3
R107:
    EmA4 + EmM3 > EmU4 + EmM3
    kneighbour*EmA4*EmM3
R108:
    EmA4 + M3 > EmU4 + M3
    kneighbour*EmA4*M3
R109:
    M4 + A3 > U4 + A3
    kneighbour*M4*A3
R110:
    EmM4 + A3 > EmU4 + A3
    kneighbour*EmM4*A3
R111:
    M4 + EmA3 > U4 + EmA3
    kneighbour*M4*EmA3
R112:
    M4 + A5 > U4 + A5
    kneighbour*M4*A5
R113:
    EmM4 + A5 > EmU4 + A5
    kneighbour*EmM4*A5
R114:
    M4 + EmA5 > U4 + EmA5
    kneighbour*M4*EmA5
R115:
    U4 + A3 > A4 + A3
    kneighbour*U4*A3
R116:
    EmU4 + A3 > EmA4 + A3
    kneighbour*EmU4*A3
R117:
    U4 + EmA3 > A4 + EmA3
    kneighbour*U4*EmA3
R118:
    U4 + A5 > A4 + A5
    kneighbour*U4*A5
R119:
    EmU4 + A5 > EmA4 + A5
    kneighbour*EmU4*A5
R120:
    U4 + EmA5 > A4 + EmA5
    kneighbour*U4*EmA5
R121:
    M5 > U5
    knoise*M5
R122:
    EmM5 > EmU5
    knoise*EmM5
R123:
    U5 > A5
    knoise*U5
R124:
    A5 > U5
    knoise*A5
R125:
    EmA5 > EmU5
    knoise*EmA5
R126:
    EmM5 > M5
    koff*EmM5
R127:
    EmU5 > U5
    koff*EmU5
R128:
    EmA5 > A5
    koff*EmA5
R129:
    EmU5 > EmM5
    kenz*EmU5
R130:
    U5 + EmM6 > M5 + EmM6
    kenz_neigh*U5*EmM6
R131:
    EmU5 + EmM6 > EmM5 + EmM6
    kenz_neigh*EmU5*EmM6
R132:
    EmU5 + M6 > EmM5 + M6
    kenz_neigh*EmU5*M6
R133:
    U5 + EmM4 > M5 + EmM4
    kenz_neigh*U5*EmM4
R134:
    EmU5 + EmM4 > EmM5 + EmM4
    kenz_neigh*EmU5*EmM4
R135:
    EmU5 + M4 > EmM5 + M4
    kenz_neigh*EmU5*M4
R136:
    A5 + EmM6 > U5 + EmM6
    kneighbour*A5*EmM6
R137:
    EmA5 + EmM6 > EmU5 + EmM6
    kneighbour*EmA5*EmM6
R138:
    EmA5 + M6 > EmU5 + M6
    kneighbour*EmA5*M6
R139:
    A5 + EmM4 > U5 + EmM4
    kneighbour*A5*EmM4
R140:
    EmA5 + EmM4 > EmU5 + EmM4
    kneighbour*EmA5*EmM4
R141:
    EmA5 + M4 > EmU5 + M4
    kneighbour*EmA5*M4
R142:
    M5 + A4 > U5 + A4
    kneighbour*M5*A4
R143:
    EmM5 + A4 > EmU5 + A4
    kneighbour*EmM5*A4
R144:
    M5 + EmA4 > U5 + EmA4
    kneighbour*M5*EmA4
R145:
    M5 + A6 > U5 + A6
    kneighbour*M5*A6
R146:
    EmM5 + A6 > EmU5 + A6
    kneighbour*EmM5*A6
R147:
    M5 + EmA6 > U5 + EmA6
    kneighbour*M5*EmA6
R148:
    U5 + A4 > A5 + A4
    kneighbour*U5*A4
R149:
    EmU5 + A4 > EmA5 + A4
    kneighbour*EmU5*A4
R150:
    U5 + EmA4 > A5 + EmA4
    kneighbour*U5*EmA4
R151:
    U5 + A6 > A5 + A6
    kneighbour*U5*A6
R152:
    EmU5 + A6 > EmA5 + A6
    kneighbour*EmU5*A6
R153:
    U5 + EmA6 > A5 + EmA6
    kneighbour*U5*EmA6
R154:
    M6 > U6
    knoise*M6
R155:
    EmM6 > EmU6
    knoise*EmM6
R156:
    U6 > A6
    knoise*U6
R157:
    A6 > U6
    knoise*A6
R158:
    EmA6 > EmU6
    knoise*EmA6
R159:
    EmM6 > M6
    koff*EmM6
R160:
    EmU6 > U6
    koff*EmU6
R161:
    EmA6 > A6
    koff*EmA6
R162:
    EmU6 > EmM6
    kenz*EmU6
R163:
    U6 + EmM7 > M6 + EmM7
    kenz_neigh*U6*EmM7
R164:
    EmU6 + EmM7 > EmM6 + EmM7
    kenz_neigh*EmU6*EmM7
R165:
    EmU6 + M7 > EmM6 + M7
    kenz_neigh*EmU6*M7
R166:
    U6 + EmM5 > M6 + EmM5
    kenz_neigh*U6*EmM5
R167:
    EmU6 + EmM5 > EmM6 + EmM5
    kenz_neigh*EmU6*EmM5
R168:
    EmU6 + M5 > EmM6 + M5
    kenz_neigh*EmU6*M5
R169:
    A6 + EmM7 > U6 + EmM7
    kneighbour*A6*EmM7
R170:
    EmA6 + EmM7 > EmU6 + EmM7
    kneighbour*EmA6*EmM7
R171:
    EmA6 + M7 > EmU6 + M7
    kneighbour*EmA6*M7
R172:
    A6 + EmM5 > U6 + EmM5
    kneighbour*A6*EmM5
R173:
    EmA6 + EmM5 > EmU6 + EmM5
    kneighbour*EmA6*EmM5
R174:
    EmA6 + M5 > EmU6 + M5
    kneighbour*EmA6*M5
R175:
    M6 + A5 > U6 + A5
    kneighbour*M6*A5
R176:
    EmM6 + A5 > EmU6 + A5
    kneighbour*EmM6*A5
R177:
    M6 + EmA5 > U6 + EmA5
    kneighbour*M6*EmA5
R178:
    M6 + A7 > U6 + A7
    kneighbour*M6*A7
R179:
    EmM6 + A7 > EmU6 + A7
    kneighbour*EmM6*A7
R180:
    M6 + EmA7 > U6 + EmA7
    kneighbour*M6*EmA7
R181:
    U6 + A5 > A6 + A5
    kneighbour*U6*A5
R182:
    EmU6 + A5 > EmA6 + A5
    kneighbour*EmU6*A5
R183:
    U6 + EmA5 > A6 + EmA5
    kneighbour*U6*EmA5
R184:
    U6 + A7 > A6 + A7
    kneighbour*U6*A7
R185:
    EmU6 + A7 > EmA6 + A7
    kneighbour*EmU6*A7
R186:
    U6 + EmA7 > A6 + EmA7
    kneighbour*U6*EmA7
R187:
    M7 > U7
    knoise*M7
R188:
    EmM7 > EmU7
    knoise*EmM7
R189:
    U7 > A7
    knoise*U7
R190:
    A7 > U7
    knoise*A7
R191:
    EmA7 > EmU7
    knoise*EmA7
R192:
    EmM7 > M7
    koff*EmM7
R193:
    EmU7 > U7
    koff*EmU7
R194:
    EmA7 > A7
    koff*EmA7
R195:
    EmU7 > EmM7
    kenz*EmU7
R196:
    U7 + EmM8 > M7 + EmM8
    kenz_neigh*U7*EmM8
R197:
    EmU7 + EmM8 > EmM7 + EmM8
    kenz_neigh*EmU7*EmM8
R198:
    EmU7 + M8 > EmM7 + M8
    kenz_neigh*EmU7*M8
R199:
    U7 + EmM6 > M7 + EmM6
    kenz_neigh*U7*EmM6
R200:
    EmU7 + EmM6 > EmM7 + EmM6
    kenz_neigh*EmU7*EmM6
R201:
    EmU7 + M6 > EmM7 + M6
    kenz_neigh*EmU7*M6
R202:
    A7 + EmM8 > U7 + EmM8
    kneighbour*A7*EmM8
R203:
    EmA7 + EmM8 > EmU7 + EmM8
    kneighbour*EmA7*EmM8
R204:
    EmA7 + M8 > EmU7 + M8
    kneighbour*EmA7*M8
R205:
    A7 + EmM6 > U7 + EmM6
    kneighbour*A7*EmM6
R206:
    EmA7 + EmM6 > EmU7 + EmM6
    kneighbour*EmA7*EmM6
R207:
    EmA7 + M6 > EmU7 + M6
    kneighbour*EmA7*M6
R208:
    M7 + A6 > U7 + A6
    kneighbour*M7*A6
R209:
    EmM7 + A6 > EmU7 + A6
    kneighbour*EmM7*A6
R210:
    M7 + EmA6 > U7 + EmA6
    kneighbour*M7*EmA6
R211:
    M7 + A8 > U7 + A8
    kneighbour*M7*A8
R212:
    EmM7 + A8 > EmU7 + A8
    kneighbour*EmM7*A8
R213:
    M7 + EmA8 > U7 + EmA8
    kneighbour*M7*EmA8
R214:
    U7 + A6 > A7 + A6
    kneighbour*U7*A6
R215:
    EmU7 + A6 > EmA7 + A6
    kneighbour*EmU7*A6
R216:
    U7 + EmA6 > A7 + EmA6
    kneighbour*U7*EmA6
R217:
    U7 + A8 > A7 + A8
    kneighbour*U7*A8
R218:
    EmU7 + A8 > EmA7 + A8
    kneighbour*EmU7*A8
R219:
    U7 + EmA8 > A7 + EmA8
    kneighbour*U7*EmA8
R220:
    M8 > U8
    knoise*M8
R221:
    EmM8 > EmU8
    knoise*EmM8
R222:
    U8 > A8
    knoise*U8
R223:
    A8 > U8
    knoise*A8
R224:
    EmA8 > EmU8
    knoise*EmA8
R225:
    EmM8 > M8
    koff*EmM8
R226:
    EmU8 > U8
    koff*EmU8
R227:
    EmA8 > A8
    koff*EmA8
R228:
    EmU8 > EmM8
    kenz*EmU8
R229:
    U8 + EmM9 > M8 + EmM9
    kenz_neigh*U8*EmM9
R230:
    EmU8 + EmM9 > EmM8 + EmM9
    kenz_neigh*EmU8*EmM9
R231:
    EmU8 + M9 > EmM8 + M9
    kenz_neigh*EmU8*M9
R232:
    U8 + EmM7 > M8 + EmM7
    kenz_neigh*U8*EmM7
R233:
    EmU8 + EmM7 > EmM8 + EmM7
    kenz_neigh*EmU8*EmM7
R234:
    EmU8 + M7 > EmM8 + M7
    kenz_neigh*EmU8*M7
R235:
    A8 + EmM9 > U8 + EmM9
    kneighbour*A8*EmM9
R236:
    EmA8 + EmM9 > EmU8 + EmM9
    kneighbour*EmA8*EmM9
R237:
    EmA8 + M9 > EmU8 + M9
    kneighbour*EmA8*M9
R238:
    A8 + EmM7 > U8 + EmM7
    kneighbour*A8*EmM7
R239:
    EmA8 + EmM7 > EmU8 + EmM7
    kneighbour*EmA8*EmM7
R240:
    EmA8 + M7 > EmU8 + M7
    kneighbour*EmA8*M7
R241:
    M8 + A7 > U8 + A7
    kneighbour*M8*A7
R242:
    EmM8 + A7 > EmU8 + A7
    kneighbour*EmM8*A7
R243:
    M8 + EmA7 > U8 + EmA7
    kneighbour*M8*EmA7
R244:
    M8 + A9 > U8 + A9
    kneighbour*M8*A9
R245:
    EmM8 + A9 > EmU8 + A9
    kneighbour*EmM8*A9
R246:
    M8 + EmA9 > U8 + EmA9
    kneighbour*M8*EmA9
R247:
    U8 + A7 > A8 + A7
    kneighbour*U8*A7
R248:
    EmU8 + A7 > EmA8 + A7
    kneighbour*EmU8*A7
R249:
    U8 + EmA7 > A8 + EmA7
    kneighbour*U8*EmA7
R250:
    U8 + A9 > A8 + A9
    kneighbour*U8*A9
R251:
    EmU8 + A9 > EmA8 + A9
    kneighbour*EmU8*A9
R252:
    U8 + EmA9 > A8 + EmA9
    kneighbour*U8*EmA9
R253:
    M9 > U9
    knoise*M9
R254:
    EmM9 > EmU9
    knoise*EmM9
R255:
    U9 > A9
    knoise*U9
R256:
    A9 > U9
    knoise*A9
R257:
    EmA9 > EmU9
    knoise*EmA9
R258:
    EmM9 > M9
    koff*EmM9
R259:
    EmU9 > U9
    koff*EmU9
R260:
    EmA9 > A9
    koff*EmA9
R261:
    EmU9 > EmM9
    kenz*EmU9
R262:
    U9 + EmM10 > M9 + EmM10
    kenz_neigh*U9*EmM10
R263:
    EmU9 + EmM10 > EmM9 + EmM10
    kenz_neigh*EmU9*EmM10
R264:
    EmU9 + M10 > EmM9 + M10
    kenz_neigh*EmU9*M10
R265:
    U9 + EmM8 > M9 + EmM8
    kenz_neigh*U9*EmM8
R266:
    EmU9 + EmM8 > EmM9 + EmM8
    kenz_neigh*EmU9*EmM8
R267:
    EmU9 + M8 > EmM9 + M8
    kenz_neigh*EmU9*M8
R268:
    A9 + EmM10 > U9 + EmM10
    kneighbour*A9*EmM10
R269:
    EmA9 + EmM10 > EmU9 + EmM10
    kneighbour*EmA9*EmM10
R270:
    EmA9 + M10 > EmU9 + M10
    kneighbour*EmA9*M10
R271:
    A9 + EmM8 > U9 + EmM8
    kneighbour*A9*EmM8
R272:
    EmA9 + EmM8 > EmU9 + EmM8
    kneighbour*EmA9*EmM8
R273:
    EmA9 + M8 > EmU9 + M8
    kneighbour*EmA9*M8
R274:
    M9 + A8 > U9 + A8
    kneighbour*M9*A8
R275:
    EmM9 + A8 > EmU9 + A8
    kneighbour*EmM9*A8
R276:
    M9 + EmA8 > U9 + EmA8
    kneighbour*M9*EmA8
R277:
    M9 + A10 > U9 + A10
    kneighbour*M9*A10
R278:
    EmM9 + A10 > EmU9 + A10
    kneighbour*EmM9*A10
R279:
    M9 + EmA10 > U9 + EmA10
    kneighbour*M9*EmA10
R280:
    U9 + A8 > A9 + A8
    kneighbour*U9*A8
R281:
    EmU9 + A8 > EmA9 + A8
    kneighbour*EmU9*A8
R282:
    U9 + EmA8 > A9 + EmA8
    kneighbour*U9*EmA8
R283:
    U9 + A10 > A9 + A10
    kneighbour*U9*A10
R284:
    EmU9 + A10 > EmA9 + A10
    kneighbour*EmU9*A10
R285:
    U9 + EmA10 > A9 + EmA10
    kneighbour*U9*EmA10
R286:
    M10 > U10
    knoise*M10
R287:
    EmM10 > EmU10
    knoise*EmM10
R288:
    U10 > A10
    knoise*U10
R289:
    A10 > U10
    knoise*A10
R290:
    EmA10 > EmU10
    knoise*EmA10
R291:
    EmM10 > M10
    koff*EmM10
R292:
    EmU10 > U10
    koff*EmU10
R293:
    EmA10 > A10
    koff*EmA10
R294:
    EmU10 > EmM10
    kenz*EmU10
R295:
    U10 + EmM11 > M10 + EmM11
    kenz_neigh*U10*EmM11
R296:
    EmU10 + EmM11 > EmM10 + EmM11
    kenz_neigh*EmU10*EmM11
R297:
    EmU10 + M11 > EmM10 + M11
    kenz_neigh*EmU10*M11
R298:
    U10 + EmM9 > M10 + EmM9
    kenz_neigh*U10*EmM9
R299:
    EmU10 + EmM9 > EmM10 + EmM9
    kenz_neigh*EmU10*EmM9
R300:
    EmU10 + M9 > EmM10 + M9
    kenz_neigh*EmU10*M9
R301:
    A10 + EmM11 > U10 + EmM11
    kneighbour*A10*EmM11
R302:
    EmA10 + EmM11 > EmU10 + EmM11
    kneighbour*EmA10*EmM11
R303:
    EmA10 + M11 > EmU10 + M11
    kneighbour*EmA10*M11
R304:
    A10 + EmM9 > U10 + EmM9
    kneighbour*A10*EmM9
R305:
    EmA10 + EmM9 > EmU10 + EmM9
    kneighbour*EmA10*EmM9
R306:
    EmA10 + M9 > EmU10 + M9
    kneighbour*EmA10*M9
R307:
    M10 + A9 > U10 + A9
    kneighbour*M10*A9
R308:
    EmM10 + A9 > EmU10 + A9
    kneighbour*EmM10*A9
R309:
    M10 + EmA9 > U10 + EmA9
    kneighbour*M10*EmA9
R310:
    M10 + A11 > U10 + A11
    kneighbour*M10*A11
R311:
    EmM10 + A11 > EmU10 + A11
    kneighbour*EmM10*A11
R312:
    M10 + EmA11 > U10 + EmA11
    kneighbour*M10*EmA11
R313:
    U10 + A9 > A10 + A9
    kneighbour*U10*A9
R314:
    EmU10 + A9 > EmA10 + A9
    kneighbour*EmU10*A9
R315:
    U10 + EmA9 > A10 + EmA9
    kneighbour*U10*EmA9
R316:
    U10 + A11 > A10 + A11
    kneighbour*U10*A11
R317:
    EmU10 + A11 > EmA10 + A11
    kneighbour*EmU10*A11
R318:
    U10 + EmA11 > A10 + EmA11
    kneighbour*U10*EmA11
R319:
    M11 > U11
    knoise*M11
R320:
    EmM11 > EmU11
    knoise*EmM11
R321:
    U11 > A11
    knoise*U11
R322:
    A11 > U11
    knoise*A11
R323:
    EmA11 > EmU11
    knoise*EmA11
R324:
    EmM11 > M11
    koff*EmM11
R325:
    EmU11 > U11
    koff*EmU11
R326:
    EmA11 > A11
    koff*EmA11
R327:
    EmU11 > EmM11
    kenz*EmU11
R328:
    U11 + EmM12 > M11 + EmM12
    kenz_neigh*U11*EmM12
R329:
    EmU11 + EmM12 > EmM11 + EmM12
    kenz_neigh*EmU11*EmM12
R330:
    EmU11 + M12 > EmM11 + M12
    kenz_neigh*EmU11*M12
R331:
    U11 + EmM10 > M11 + EmM10
    kenz_neigh*U11*EmM10
R332:
    EmU11 + EmM10 > EmM11 + EmM10
    kenz_neigh*EmU11*EmM10
R333:
    EmU11 + M10 > EmM11 + M10
    kenz_neigh*EmU11*M10
R334:
    A11 + EmM12 > U11 + EmM12
    kneighbour*A11*EmM12
R335:
    EmA11 + EmM12 > EmU11 + EmM12
    kneighbour*EmA11*EmM12
R336:
    EmA11 + M12 > EmU11 + M12
    kneighbour*EmA11*M12
R337:
    A11 + EmM10 > U11 + EmM10
    kneighbour*A11*EmM10
R338:
    EmA11 + EmM10 > EmU11 + EmM10
    kneighbour*EmA11*EmM10
R339:
    EmA11 + M10 > EmU11 + M10
    kneighbour*EmA11*M10
R340:
    M11 + A10 > U11 + A10
    kneighbour*M11*A10
R341:
    EmM11 + A10 > EmU11 + A10
    kneighbour*EmM11*A10
R342:
    M11 + EmA10 > U11 + EmA10
    kneighbour*M11*EmA10
R343:
    M11 + A12 > U11 + A12
    kneighbour*M11*A12
R344:
    EmM11 + A12 > EmU11 + A12
    kneighbour*EmM11*A12
R345:
    M11 + EmA12 > U11 + EmA12
    kneighbour*M11*EmA12
R346:
    U11 + A10 > A11 + A10
    kneighbour*U11*A10
R347:
    EmU11 + A10 > EmA11 + A10
    kneighbour*EmU11*A10
R348:
    U11 + EmA10 > A11 + EmA10
    kneighbour*U11*EmA10
R349:
    U11 + A12 > A11 + A12
    kneighbour*U11*A12
R350:
    EmU11 + A12 > EmA11 + A12
    kneighbour*EmU11*A12
R351:
    U11 + EmA12 > A11 + EmA12
    kneighbour*U11*EmA12
R352:
    M12 > U12
    knoise*M12
R353:
    EmM12 > EmU12
    knoise*EmM12
R354:
    U12 > A12
    knoise*U12
R355:
    A12 > U12
    knoise*A12
R356:
    EmA12 > EmU12
    knoise*EmA12
R357:
    EmM12 > M12
    koff*EmM12
R358:
    EmU12 > U12
    koff*EmU12
R359:
    EmA12 > A12
    koff*EmA12
R360:
    EmU12 > EmM12
    kenz*EmU12
R361:
    U12 + EmM13 > M12 + EmM13
    kenz_neigh*U12*EmM13
R362:
    EmU12 + EmM13 > EmM12 + EmM13
    kenz_neigh*EmU12*EmM13
R363:
    EmU12 + M13 > EmM12 + M13
    kenz_neigh*EmU12*M13
R364:
    U12 + EmM11 > M12 + EmM11
    kenz_neigh*U12*EmM11
R365:
    EmU12 + EmM11 > EmM12 + EmM11
    kenz_neigh*EmU12*EmM11
R366:
    EmU12 + M11 > EmM12 + M11
    kenz_neigh*EmU12*M11
R367:
    A12 + EmM13 > U12 + EmM13
    kneighbour*A12*EmM13
R368:
    EmA12 + EmM13 > EmU12 + EmM13
    kneighbour*EmA12*EmM13
R369:
    EmA12 + M13 > EmU12 + M13
    kneighbour*EmA12*M13
R370:
    A12 + EmM11 > U12 + EmM11
    kneighbour*A12*EmM11
R371:
    EmA12 + EmM11 > EmU12 + EmM11
    kneighbour*EmA12*EmM11
R372:
    EmA12 + M11 > EmU12 + M11
    kneighbour*EmA12*M11
R373:
    M12 + A11 > U12 + A11
    kneighbour*M12*A11
R374:
    EmM12 + A11 > EmU12 + A11
    kneighbour*EmM12*A11
R375:
    M12 + EmA11 > U12 + EmA11
    kneighbour*M12*EmA11
R376:
    M12 + A13 > U12 + A13
    kneighbour*M12*A13
R377:
    EmM12 + A13 > EmU12 + A13
    kneighbour*EmM12*A13
R378:
    M12 + EmA13 > U12 + EmA13
    kneighbour*M12*EmA13
R379:
    U12 + A11 > A12 + A11
    kneighbour*U12*A11
R380:
    EmU12 + A11 > EmA12 + A11
    kneighbour*EmU12*A11
R381:
    U12 + EmA11 > A12 + EmA11
    kneighbour*U12*EmA11
R382:
    U12 + A13 > A12 + A13
    kneighbour*U12*A13
R383:
    EmU12 + A13 > EmA12 + A13
    kneighbour*EmU12*A13
R384:
    U12 + EmA13 > A12 + EmA13
    kneighbour*U12*EmA13
R385:
    M13 > U13
    knoise*M13
R386:
    EmM13 > EmU13
    knoise*EmM13
R387:
    U13 > A13
    knoise*U13
R388:
    A13 > U13
    knoise*A13
R389:
    EmA13 > EmU13
    knoise*EmA13
R390:
    EmM13 > M13
    koff*EmM13
R391:
    EmU13 > U13
    koff*EmU13
R392:
    EmA13 > A13
    koff*EmA13
R393:
    EmU13 > EmM13
    kenz*EmU13
R394:
    U13 + EmM14 > M13 + EmM14
    kenz_neigh*U13*EmM14
R395:
    EmU13 + EmM14 > EmM13 + EmM14
    kenz_neigh*EmU13*EmM14
R396:
    EmU13 + M14 > EmM13 + M14
    kenz_neigh*EmU13*M14
R397:
    U13 + EmM12 > M13 + EmM12
    kenz_neigh*U13*EmM12
R398:
    EmU13 + EmM12 > EmM13 + EmM12
    kenz_neigh*EmU13*EmM12
R399:
    EmU13 + M12 > EmM13 + M12
    kenz_neigh*EmU13*M12
R400:
    A13 + EmM14 > U13 + EmM14
    kneighbour*A13*EmM14
R401:
    EmA13 + EmM14 > EmU13 + EmM14
    kneighbour*EmA13*EmM14
R402:
    EmA13 + M14 > EmU13 + M14
    kneighbour*EmA13*M14
R403:
    A13 + EmM12 > U13 + EmM12
    kneighbour*A13*EmM12
R404:
    EmA13 + EmM12 > EmU13 + EmM12
    kneighbour*EmA13*EmM12
R405:
    EmA13 + M12 > EmU13 + M12
    kneighbour*EmA13*M12
R406:
    M13 + A12 > U13 + A12
    kneighbour*M13*A12
R407:
    EmM13 + A12 > EmU13 + A12
    kneighbour*EmM13*A12
R408:
    M13 + EmA12 > U13 + EmA12
    kneighbour*M13*EmA12
R409:
    M13 + A14 > U13 + A14
    kneighbour*M13*A14
R410:
    EmM13 + A14 > EmU13 + A14
    kneighbour*EmM13*A14
R411:
    M13 + EmA14 > U13 + EmA14
    kneighbour*M13*EmA14
R412:
    U13 + A12 > A13 + A12
    kneighbour*U13*A12
R413:
    EmU13 + A12 > EmA13 + A12
    kneighbour*EmU13*A12
R414:
    U13 + EmA12 > A13 + EmA12
    kneighbour*U13*EmA12
R415:
    U13 + A14 > A13 + A14
    kneighbour*U13*A14
R416:
    EmU13 + A14 > EmA13 + A14
    kneighbour*EmU13*A14
R417:
    U13 + EmA14 > A13 + EmA14
    kneighbour*U13*EmA14
R418:
    M14 > U14
    knoise*M14
R419:
    EmM14 > EmU14
    knoise*EmM14
R420:
    U14 > A14
    knoise*U14
R421:
    A14 > U14
    knoise*A14
R422:
    EmA14 > EmU14
    knoise*EmA14
R423:
    EmM14 > M14
    koff*EmM14
R424:
    EmU14 > U14
    koff*EmU14
R425:
    EmA14 > A14
    koff*EmA14
R426:
    EmU14 > EmM14
    kenz*EmU14
R427:
    U14 + EmM15 > M14 + EmM15
    kenz_neigh*U14*EmM15
R428:
    EmU14 + EmM15 > EmM14 + EmM15
    kenz_neigh*EmU14*EmM15
R429:
    EmU14 + M15 > EmM14 + M15
    kenz_neigh*EmU14*M15
R430:
    U14 + EmM13 > M14 + EmM13
    kenz_neigh*U14*EmM13
R431:
    EmU14 + EmM13 > EmM14 + EmM13
    kenz_neigh*EmU14*EmM13
R432:
    EmU14 + M13 > EmM14 + M13
    kenz_neigh*EmU14*M13
R433:
    A14 + EmM15 > U14 + EmM15
    kneighbour*A14*EmM15
R434:
    EmA14 + EmM15 > EmU14 + EmM15
    kneighbour*EmA14*EmM15
R435:
    EmA14 + M15 > EmU14 + M15
    kneighbour*EmA14*M15
R436:
    A14 + EmM13 > U14 + EmM13
    kneighbour*A14*EmM13
R437:
    EmA14 + EmM13 > EmU14 + EmM13
    kneighbour*EmA14*EmM13
R438:
    EmA14 + M13 > EmU14 + M13
    kneighbour*EmA14*M13
R439:
    M14 + A13 > U14 + A13
    kneighbour*M14*A13
R440:
    EmM14 + A13 > EmU14 + A13
    kneighbour*EmM14*A13
R441:
    M14 + EmA13 > U14 + EmA13
    kneighbour*M14*EmA13
R442:
    M14 + A15 > U14 + A15
    kneighbour*M14*A15
R443:
    EmM14 + A15 > EmU14 + A15
    kneighbour*EmM14*A15
R444:
    M14 + EmA15 > U14 + EmA15
    kneighbour*M14*EmA15
R445:
    U14 + A13 > A14 + A13
    kneighbour*U14*A13
R446:
    EmU14 + A13 > EmA14 + A13
    kneighbour*EmU14*A13
R447:
    U14 + EmA13 > A14 + EmA13
    kneighbour*U14*EmA13
R448:
    U14 + A15 > A14 + A15
    kneighbour*U14*A15
R449:
    EmU14 + A15 > EmA14 + A15
    kneighbour*EmU14*A15
R450:
    U14 + EmA15 > A14 + EmA15
    kneighbour*U14*EmA15
R451:
    M15 > U15
    knoise*M15
R452:
    EmM15 > EmU15
    knoise*EmM15
R453:
    U15 > A15
    knoise*U15
R454:
    A15 > U15
    knoise*A15
R455:
    EmA15 > EmU15
    knoise*EmA15
R456:
    EmM15 > M15
    koff*EmM15
R457:
    EmU15 > U15
    koff*EmU15
R458:
    EmA15 > A15
    koff*EmA15
R459:
    EmU15 > EmM15
    kenz*EmU15
R460:
    U15 + EmM16 > M15 + EmM16
    kenz_neigh*U15*EmM16
R461:
    EmU15 + EmM16 > EmM15 + EmM16
    kenz_neigh*EmU15*EmM16
R462:
    EmU15 + M16 > EmM15 + M16
    kenz_neigh*EmU15*M16
R463:
    U15 + EmM14 > M15 + EmM14
    kenz_neigh*U15*EmM14
R464:
    EmU15 + EmM14 > EmM15 + EmM14
    kenz_neigh*EmU15*EmM14
R465:
    EmU15 + M14 > EmM15 + M14
    kenz_neigh*EmU15*M14
R466:
    A15 + EmM16 > U15 + EmM16
    kneighbour*A15*EmM16
R467:
    EmA15 + EmM16 > EmU15 + EmM16
    kneighbour*EmA15*EmM16
R468:
    EmA15 + M16 > EmU15 + M16
    kneighbour*EmA15*M16
R469:
    A15 + EmM14 > U15 + EmM14
    kneighbour*A15*EmM14
R470:
    EmA15 + EmM14 > EmU15 + EmM14
    kneighbour*EmA15*EmM14
R471:
    EmA15 + M14 > EmU15 + M14
    kneighbour*EmA15*M14
R472:
    M15 + A14 > U15 + A14
    kneighbour*M15*A14
R473:
    EmM15 + A14 > EmU15 + A14
    kneighbour*EmM15*A14
R474:
    M15 + EmA14 > U15 + EmA14
    kneighbour*M15*EmA14
R475:
    M15 + A16 > U15 + A16
    kneighbour*M15*A16
R476:
    EmM15 + A16 > EmU15 + A16
    kneighbour*EmM15*A16
R477:
    M15 + EmA16 > U15 + EmA16
    kneighbour*M15*EmA16
R478:
    U15 + A14 > A15 + A14
    kneighbour*U15*A14
R479:
    EmU15 + A14 > EmA15 + A14
    kneighbour*EmU15*A14
R480:
    U15 + EmA14 > A15 + EmA14
    kneighbour*U15*EmA14
R481:
    U15 + A16 > A15 + A16
    kneighbour*U15*A16
R482:
    EmU15 + A16 > EmA15 + A16
    kneighbour*EmU15*A16
R483:
    U15 + EmA16 > A15 + EmA16
    kneighbour*U15*EmA16
R484:
    M16 > U16
    knoise*M16
R485:
    EmM16 > EmU16
    knoise*EmM16
R486:
    U16 > A16
    knoise*U16
R487:
    A16 > U16
    knoise*A16
R488:
    EmA16 > EmU16
    knoise*EmA16
R489:
    EmM16 > M16
    koff*EmM16
R490:
    EmU16 > U16
    koff*EmU16
R491:
    EmA16 > A16
    koff*EmA16
R492:
    EmU16 > EmM16
    kenz*EmU16
R493:
    U16 + EmM17 > M16 + EmM17
    kenz_neigh*U16*EmM17
R494:
    EmU16 + EmM17 > EmM16 + EmM17
    kenz_neigh*EmU16*EmM17
R495:
    EmU16 + M17 > EmM16 + M17
    kenz_neigh*EmU16*M17
R496:
    U16 + EmM15 > M16 + EmM15
    kenz_neigh*U16*EmM15
R497:
    EmU16 + EmM15 > EmM16 + EmM15
    kenz_neigh*EmU16*EmM15
R498:
    EmU16 + M15 > EmM16 + M15
    kenz_neigh*EmU16*M15
R499:
    A16 + EmM17 > U16 + EmM17
    kneighbour*A16*EmM17
R500:
    EmA16 + EmM17 > EmU16 + EmM17
    kneighbour*EmA16*EmM17
R501:
    EmA16 + M17 > EmU16 + M17
    kneighbour*EmA16*M17
R502:
    A16 + EmM15 > U16 + EmM15
    kneighbour*A16*EmM15
R503:
    EmA16 + EmM15 > EmU16 + EmM15
    kneighbour*EmA16*EmM15
R504:
    EmA16 + M15 > EmU16 + M15
    kneighbour*EmA16*M15
R505:
    M16 + A15 > U16 + A15
    kneighbour*M16*A15
R506:
    EmM16 + A15 > EmU16 + A15
    kneighbour*EmM16*A15
R507:
    M16 + EmA15 > U16 + EmA15
    kneighbour*M16*EmA15
R508:
    M16 + A17 > U16 + A17
    kneighbour*M16*A17
R509:
    EmM16 + A17 > EmU16 + A17
    kneighbour*EmM16*A17
R510:
    M16 + EmA17 > U16 + EmA17
    kneighbour*M16*EmA17
R511:
    U16 + A15 > A16 + A15
    kneighbour*U16*A15
R512:
    EmU16 + A15 > EmA16 + A15
    kneighbour*EmU16*A15
R513:
    U16 + EmA15 > A16 + EmA15
    kneighbour*U16*EmA15
R514:
    U16 + A17 > A16 + A17
    kneighbour*U16*A17
R515:
    EmU16 + A17 > EmA16 + A17
    kneighbour*EmU16*A17
R516:
    U16 + EmA17 > A16 + EmA17
    kneighbour*U16*EmA17
R517:
    M17 > U17
    knoise*M17
R518:
    EmM17 > EmU17
    knoise*EmM17
R519:
    U17 > A17
    knoise*U17
R520:
    A17 > U17
    knoise*A17
R521:
    EmA17 > EmU17
    knoise*EmA17
R522:
    EmM17 > M17
    koff*EmM17
R523:
    EmU17 > U17
    koff*EmU17
R524:
    EmA17 > A17
    koff*EmA17
R525:
    EmU17 > EmM17
    kenz*EmU17
R526:
    U17 + EmM18 > M17 + EmM18
    kenz_neigh*U17*EmM18
R527:
    EmU17 + EmM18 > EmM17 + EmM18
    kenz_neigh*EmU17*EmM18
R528:
    EmU17 + M18 > EmM17 + M18
    kenz_neigh*EmU17*M18
R529:
    U17 + EmM16 > M17 + EmM16
    kenz_neigh*U17*EmM16
R530:
    EmU17 + EmM16 > EmM17 + EmM16
    kenz_neigh*EmU17*EmM16
R531:
    EmU17 + M16 > EmM17 + M16
    kenz_neigh*EmU17*M16
R532:
    A17 + EmM18 > U17 + EmM18
    kneighbour*A17*EmM18
R533:
    EmA17 + EmM18 > EmU17 + EmM18
    kneighbour*EmA17*EmM18
R534:
    EmA17 + M18 > EmU17 + M18
    kneighbour*EmA17*M18
R535:
    A17 + EmM16 > U17 + EmM16
    kneighbour*A17*EmM16
R536:
    EmA17 + EmM16 > EmU17 + EmM16
    kneighbour*EmA17*EmM16
R537:
    EmA17 + M16 > EmU17 + M16
    kneighbour*EmA17*M16
R538:
    M17 + A16 > U17 + A16
    kneighbour*M17*A16
R539:
    EmM17 + A16 > EmU17 + A16
    kneighbour*EmM17*A16
R540:
    M17 + EmA16 > U17 + EmA16
    kneighbour*M17*EmA16
R541:
    M17 + A18 > U17 + A18
    kneighbour*M17*A18
R542:
    EmM17 + A18 > EmU17 + A18
    kneighbour*EmM17*A18
R543:
    M17 + EmA18 > U17 + EmA18
    kneighbour*M17*EmA18
R544:
    U17 + A16 > A17 + A16
    kneighbour*U17*A16
R545:
    EmU17 + A16 > EmA17 + A16
    kneighbour*EmU17*A16
R546:
    U17 + EmA16 > A17 + EmA16
    kneighbour*U17*EmA16
R547:
    U17 + A18 > A17 + A18
    kneighbour*U17*A18
R548:
    EmU17 + A18 > EmA17 + A18
    kneighbour*EmU17*A18
R549:
    U17 + EmA18 > A17 + EmA18
    kneighbour*U17*EmA18
R550:
    M18 > U18
    knoise*M18
R551:
    EmM18 > EmU18
    knoise*EmM18
R552:
    U18 > A18
    knoise*U18
R553:
    A18 > U18
    knoise*A18
R554:
    EmA18 > EmU18
    knoise*EmA18
R555:
    EmM18 > M18
    koff*EmM18
R556:
    EmU18 > U18
    koff*EmU18
R557:
    EmA18 > A18
    koff*EmA18
R558:
    EmU18 > EmM18
    kenz*EmU18
R559:
    U18 + EmM19 > M18 + EmM19
    kenz_neigh*U18*EmM19
R560:
    EmU18 + EmM19 > EmM18 + EmM19
    kenz_neigh*EmU18*EmM19
R561:
    EmU18 + M19 > EmM18 + M19
    kenz_neigh*EmU18*M19
R562:
    U18 + EmM17 > M18 + EmM17
    kenz_neigh*U18*EmM17
R563:
    EmU18 + EmM17 > EmM18 + EmM17
    kenz_neigh*EmU18*EmM17
R564:
    EmU18 + M17 > EmM18 + M17
    kenz_neigh*EmU18*M17
R565:
    A18 + EmM19 > U18 + EmM19
    kneighbour*A18*EmM19
R566:
    EmA18 + EmM19 > EmU18 + EmM19
    kneighbour*EmA18*EmM19
R567:
    EmA18 + M19 > EmU18 + M19
    kneighbour*EmA18*M19
R568:
    A18 + EmM17 > U18 + EmM17
    kneighbour*A18*EmM17
R569:
    EmA18 + EmM17 > EmU18 + EmM17
    kneighbour*EmA18*EmM17
R570:
    EmA18 + M17 > EmU18 + M17
    kneighbour*EmA18*M17
R571:
    M18 + A17 > U18 + A17
    kneighbour*M18*A17
R572:
    EmM18 + A17 > EmU18 + A17
    kneighbour*EmM18*A17
R573:
    M18 + EmA17 > U18 + EmA17
    kneighbour*M18*EmA17
R574:
    M18 + A19 > U18 + A19
    kneighbour*M18*A19
R575:
    EmM18 + A19 > EmU18 + A19
    kneighbour*EmM18*A19
R576:
    M18 + EmA19 > U18 + EmA19
    kneighbour*M18*EmA19
R577:
    U18 + A17 > A18 + A17
    kneighbour*U18*A17
R578:
    EmU18 + A17 > EmA18 + A17
    kneighbour*EmU18*A17
R579:
    U18 + EmA17 > A18 + EmA17
    kneighbour*U18*EmA17
R580:
    U18 + A19 > A18 + A19
    kneighbour*U18*A19
R581:
    EmU18 + A19 > EmA18 + A19
    kneighbour*EmU18*A19
R582:
    U18 + EmA19 > A18 + EmA19
    kneighbour*U18*EmA19
R583:
    M19 > U19
    knoise*M19
R584:
    EmM19 > EmU19
    knoise*EmM19
R585:
    U19 > A19
    knoise*U19
R586:
    A19 > U19
    knoise*A19
R587:
    EmA19 > EmU19
    knoise*EmA19
R588:
    EmM19 > M19
    koff*EmM19
R589:
    EmU19 > U19
    koff*EmU19
R590:
    EmA19 > A19
    koff*EmA19
R591:
    EmU19 > EmM19
    kenz*EmU19
R592:
    U19 + EmM20 > M19 + EmM20
    kenz_neigh*U19*EmM20
R593:
    EmU19 + EmM20 > EmM19 + EmM20
    kenz_neigh*EmU19*EmM20
R594:
    EmU19 + M20 > EmM19 + M20
    kenz_neigh*EmU19*M20
R595:
    U19 + EmM18 > M19 + EmM18
    kenz_neigh*U19*EmM18
R596:
    EmU19 + EmM18 > EmM19 + EmM18
    kenz_neigh*EmU19*EmM18
R597:
    EmU19 + M18 > EmM19 + M18
    kenz_neigh*EmU19*M18
R598:
    A19 + EmM20 > U19 + EmM20
    kneighbour*A19*EmM20
R599:
    EmA19 + EmM20 > EmU19 + EmM20
    kneighbour*EmA19*EmM20
R600:
    EmA19 + M20 > EmU19 + M20
    kneighbour*EmA19*M20
R601:
    A19 + EmM18 > U19 + EmM18
    kneighbour*A19*EmM18
R602:
    EmA19 + EmM18 > EmU19 + EmM18
    kneighbour*EmA19*EmM18
R603:
    EmA19 + M18 > EmU19 + M18
    kneighbour*EmA19*M18
R604:
    M19 + A18 > U19 + A18
    kneighbour*M19*A18
R605:
    EmM19 + A18 > EmU19 + A18
    kneighbour*EmM19*A18
R606:
    M19 + EmA18 > U19 + EmA18
    kneighbour*M19*EmA18
R607:
    M19 + A20 > U19 + A20
    kneighbour*M19*A20
R608:
    EmM19 + A20 > EmU19 + A20
    kneighbour*EmM19*A20
R609:
    M19 + EmA20 > U19 + EmA20
    kneighbour*M19*EmA20
R610:
    U19 + A18 > A19 + A18
    kneighbour*U19*A18
R611:
    EmU19 + A18 > EmA19 + A18
    kneighbour*EmU19*A18
R612:
    U19 + EmA18 > A19 + EmA18
    kneighbour*U19*EmA18
R613:
    U19 + A20 > A19 + A20
    kneighbour*U19*A20
R614:
    EmU19 + A20 > EmA19 + A20
    kneighbour*EmU19*A20
R615:
    U19 + EmA20 > A19 + EmA20
    kneighbour*U19*EmA20
R616:
    M20 > U20
    knoise*M20
R617:
    EmM20 > EmU20
    knoise*EmM20
R618:
    U20 > A20
    knoise*U20
R619:
    A20 > U20
    knoise*A20
R620:
    EmA20 > EmU20
    knoise*EmA20
R621:
    EmM20 > M20
    koff*EmM20
R622:
    EmU20 > U20
    koff*EmU20
R623:
    EmA20 > A20
    koff*EmA20
R624:
    EmU20 > EmM20
    kenz*EmU20
R625:
    U20 + EmM19 > M20 + EmM19
    kenz_neigh*U20*EmM19
R626:
    EmU20 + EmM19 > EmM20 + EmM19
    kenz_neigh*EmU20*EmM19
R627:
    EmU20 + M19 > EmM20 + M19
    kenz_neigh*EmU20*M19
R628:
    A20 + EmM19 > U20 + EmM19
    kneighbour*A20*EmM19
R629:
    EmA20 + EmM19 > EmU20 + EmM19
    kneighbour*EmA20*EmM19
R630:
    EmA20 + M19 > EmU20 + M19
    kneighbour*EmA20*M19
R631:
    M20 + A19 > U20 + A19
    kneighbour*M20*A19
R632:
    EmM20 + A19 > EmU20 + A19
    kneighbour*EmM20*A19
R633:
    M20 + EmA19 > U20 + EmA19
    kneighbour*M20*EmA19
R634:
    U20 + A19 > A20 + A19
    kneighbour*U20*A19
R635:
    EmU20 + A19 > EmA20 + A19
    kneighbour*EmU20*A19
R636:
    U20 + EmA19 > A20 + EmA19
    kneighbour*U20*EmA19
R637:
    EmM1 + M2 > M1 + EmM2
    kdif*EmM1*M2
R638:
    EmM1 + U2 > M1 + EmU2
    kdif*EmM1*U2
R639:
    EmM1 + A2 > M1 + EmA2
    kdif*EmM1*A2
R640:
    EmU1 + M2 > U1 + EmM2
    kdif*EmU1*M2
R641:
    EmU1 + U2 > U1 + EmU2
    kdif*EmU1*U2
R642:
    EmU1 + A2 > U1 + EmA2
    kdif*EmU1*A2
R643:
    EmA1 + M2 > A1 + EmM2
    kdif*EmA1*M2
R644:
    EmA1 + U2 > A1 + EmU2
    kdif*EmA1*U2
R645:
    EmA1 + A2 > A1 + EmA2
    kdif*EmA1*A2
R646:
    EmM2 + M3 > M2 + EmM3
    kdif*EmM2*M3
R647:
    EmM2 + U3 > M2 + EmU3
    kdif*EmM2*U3
R648:
    EmM2 + A3 > M2 + EmA3
    kdif*EmM2*A3
R649:
    EmU2 + M3 > U2 + EmM3
    kdif*EmU2*M3
R650:
    EmU2 + U3 > U2 + EmU3
    kdif*EmU2*U3
R651:
    EmU2 + A3 > U2 + EmA3
    kdif*EmU2*A3
R652:
    EmA2 + M3 > A2 + EmM3
    kdif*EmA2*M3
R653:
    EmA2 + U3 > A2 + EmU3
    kdif*EmA2*U3
R654:
    EmA2 + A3 > A2 + EmA3
    kdif*EmA2*A3
R655:
    EmM3 + M4 > M3 + EmM4
    kdif*EmM3*M4
R656:
    EmM3 + U4 > M3 + EmU4
    kdif*EmM3*U4
R657:
    EmM3 + A4 > M3 + EmA4
    kdif*EmM3*A4
R658:
    EmU3 + M4 > U3 + EmM4
    kdif*EmU3*M4
R659:
    EmU3 + U4 > U3 + EmU4
    kdif*EmU3*U4
R660:
    EmU3 + A4 > U3 + EmA4
    kdif*EmU3*A4
R661:
    EmA3 + M4 > A3 + EmM4
    kdif*EmA3*M4
R662:
    EmA3 + U4 > A3 + EmU4
    kdif*EmA3*U4
R663:
    EmA3 + A4 > A3 + EmA4
    kdif*EmA3*A4
R664:
    EmM4 + M5 > M4 + EmM5
    kdif*EmM4*M5
R665:
    EmM4 + U5 > M4 + EmU5
    kdif*EmM4*U5
R666:
    EmM4 + A5 > M4 + EmA5
    kdif*EmM4*A5
R667:
    EmU4 + M5 > U4 + EmM5
    kdif*EmU4*M5
R668:
    EmU4 + U5 > U4 + EmU5
    kdif*EmU4*U5
R669:
    EmU4 + A5 > U4 + EmA5
    kdif*EmU4*A5
R670:
    EmA4 + M5 > A4 + EmM5
    kdif*EmA4*M5
R671:
    EmA4 + U5 > A4 + EmU5
    kdif*EmA4*U5
R672:
    EmA4 + A5 > A4 + EmA5
    kdif*EmA4*A5
R673:
    EmM5 + M6 > M5 + EmM6
    kdif*EmM5*M6
R674:
    EmM5 + U6 > M5 + EmU6
    kdif*EmM5*U6
R675:
    EmM5 + A6 > M5 + EmA6
    kdif*EmM5*A6
R676:
    EmU5 + M6 > U5 + EmM6
    kdif*EmU5*M6
R677:
    EmU5 + U6 > U5 + EmU6
    kdif*EmU5*U6
R678:
    EmU5 + A6 > U5 + EmA6
    kdif*EmU5*A6
R679:
    EmA5 + M6 > A5 + EmM6
    kdif*EmA5*M6
R680:
    EmA5 + U6 > A5 + EmU6
    kdif*EmA5*U6
R681:
    EmA5 + A6 > A5 + EmA6
    kdif*EmA5*A6
R682:
    EmM6 + M7 > M6 + EmM7
    kdif*EmM6*M7
R683:
    EmM6 + U7 > M6 + EmU7
    kdif*EmM6*U7
R684:
    EmM6 + A7 > M6 + EmA7
    kdif*EmM6*A7
R685:
    EmU6 + M7 > U6 + EmM7
    kdif*EmU6*M7
R686:
    EmU6 + U7 > U6 + EmU7
    kdif*EmU6*U7
R687:
    EmU6 + A7 > U6 + EmA7
    kdif*EmU6*A7
R688:
    EmA6 + M7 > A6 + EmM7
    kdif*EmA6*M7
R689:
    EmA6 + U7 > A6 + EmU7
    kdif*EmA6*U7
R690:
    EmA6 + A7 > A6 + EmA7
    kdif*EmA6*A7
R691:
    EmM7 + M8 > M7 + EmM8
    kdif*EmM7*M8
R692:
    EmM7 + U8 > M7 + EmU8
    kdif*EmM7*U8
R693:
    EmM7 + A8 > M7 + EmA8
    kdif*EmM7*A8
R694:
    EmU7 + M8 > U7 + EmM8
    kdif*EmU7*M8
R695:
    EmU7 + U8 > U7 + EmU8
    kdif*EmU7*U8
R696:
    EmU7 + A8 > U7 + EmA8
    kdif*EmU7*A8
R697:
    EmA7 + M8 > A7 + EmM8
    kdif*EmA7*M8
R698:
    EmA7 + U8 > A7 + EmU8
    kdif*EmA7*U8
R699:
    EmA7 + A8 > A7 + EmA8
    kdif*EmA7*A8
R700:
    EmM8 + M9 > M8 + EmM9
    kdif*EmM8*M9
R701:
    EmM8 + U9 > M8 + EmU9
    kdif*EmM8*U9
R702:
    EmM8 + A9 > M8 + EmA9
    kdif*EmM8*A9
R703:
    EmU8 + M9 > U8 + EmM9
    kdif*EmU8*M9
R704:
    EmU8 + U9 > U8 + EmU9
    kdif*EmU8*U9
R705:
    EmU8 + A9 > U8 + EmA9
    kdif*EmU8*A9
R706:
    EmA8 + M9 > A8 + EmM9
    kdif*EmA8*M9
R707:
    EmA8 + U9 > A8 + EmU9
    kdif*EmA8*U9
R708:
    EmA8 + A9 > A8 + EmA9
    kdif*EmA8*A9
R709:
    EmM9 + M10 > M9 + EmM10
    kdif*EmM9*M10
R710:
    EmM9 + U10 > M9 + EmU10
    kdif*EmM9*U10
R711:
    EmM9 + A10 > M9 + EmA10
    kdif*EmM9*A10
R712:
    EmU9 + M10 > U9 + EmM10
    kdif*EmU9*M10
R713:
    EmU9 + U10 > U9 + EmU10
    kdif*EmU9*U10
R714:
    EmU9 + A10 > U9 + EmA10
    kdif*EmU9*A10
R715:
    EmA9 + M10 > A9 + EmM10
    kdif*EmA9*M10
R716:
    EmA9 + U10 > A9 + EmU10
    kdif*EmA9*U10
R717:
    EmA9 + A10 > A9 + EmA10
    kdif*EmA9*A10
R718:
    EmM10 + M11 > M10 + EmM11
    kdif*EmM10*M11
R719:
    EmM10 + U11 > M10 + EmU11
    kdif*EmM10*U11
R720:
    EmM10 + A11 > M10 + EmA11
    kdif*EmM10*A11
R721:
    EmU10 + M11 > U10 + EmM11
    kdif*EmU10*M11
R722:
    EmU10 + U11 > U10 + EmU11
    kdif*EmU10*U11
R723:
    EmU10 + A11 > U10 + EmA11
    kdif*EmU10*A11
R724:
    EmA10 + M11 > A10 + EmM11
    kdif*EmA10*M11
R725:
    EmA10 + U11 > A10 + EmU11
    kdif*EmA10*U11
R726:
    EmA10 + A11 > A10 + EmA11
    kdif*EmA10*A11
R727:
    EmM11 + M12 > M11 + EmM12
    kdif*EmM11*M12
R728:
    EmM11 + U12 > M11 + EmU12
    kdif*EmM11*U12
R729:
    EmM11 + A12 > M11 + EmA12
    kdif*EmM11*A12
R730:
    EmU11 + M12 > U11 + EmM12
    kdif*EmU11*M12
R731:
    EmU11 + U12 > U11 + EmU12
    kdif*EmU11*U12
R732:
    EmU11 + A12 > U11 + EmA12
    kdif*EmU11*A12
R733:
    EmA11 + M12 > A11 + EmM12
    kdif*EmA11*M12
R734:
    EmA11 + U12 > A11 + EmU12
    kdif*EmA11*U12
R735:
    EmA11 + A12 > A11 + EmA12
    kdif*EmA11*A12
R736:
    EmM12 + M13 > M12 + EmM13
    kdif*EmM12*M13
R737:
    EmM12 + U13 > M12 + EmU13
    kdif*EmM12*U13
R738:
    EmM12 + A13 > M12 + EmA13
    kdif*EmM12*A13
R739:
    EmU12 + M13 > U12 + EmM13
    kdif*EmU12*M13
R740:
    EmU12 + U13 > U12 + EmU13
    kdif*EmU12*U13
R741:
    EmU12 + A13 > U12 + EmA13
    kdif*EmU12*A13
R742:
    EmA12 + M13 > A12 + EmM13
    kdif*EmA12*M13
R743:
    EmA12 + U13 > A12 + EmU13
    kdif*EmA12*U13
R744:
    EmA12 + A13 > A12 + EmA13
    kdif*EmA12*A13
R745:
    EmM13 + M14 > M13 + EmM14
    kdif*EmM13*M14
R746:
    EmM13 + U14 > M13 + EmU14
    kdif*EmM13*U14
R747:
    EmM13 + A14 > M13 + EmA14
    kdif*EmM13*A14
R748:
    EmU13 + M14 > U13 + EmM14
    kdif*EmU13*M14
R749:
    EmU13 + U14 > U13 + EmU14
    kdif*EmU13*U14
R750:
    EmU13 + A14 > U13 + EmA14
    kdif*EmU13*A14
R751:
    EmA13 + M14 > A13 + EmM14
    kdif*EmA13*M14
R752:
    EmA13 + U14 > A13 + EmU14
    kdif*EmA13*U14
R753:
    EmA13 + A14 > A13 + EmA14
    kdif*EmA13*A14
R754:
    EmM14 + M15 > M14 + EmM15
    kdif*EmM14*M15
R755:
    EmM14 + U15 > M14 + EmU15
    kdif*EmM14*U15
R756:
    EmM14 + A15 > M14 + EmA15
    kdif*EmM14*A15
R757:
    EmU14 + M15 > U14 + EmM15
    kdif*EmU14*M15
R758:
    EmU14 + U15 > U14 + EmU15
    kdif*EmU14*U15
R759:
    EmU14 + A15 > U14 + EmA15
    kdif*EmU14*A15
R760:
    EmA14 + M15 > A14 + EmM15
    kdif*EmA14*M15
R761:
    EmA14 + U15 > A14 + EmU15
    kdif*EmA14*U15
R762:
    EmA14 + A15 > A14 + EmA15
    kdif*EmA14*A15
R763:
    EmM15 + M16 > M15 + EmM16
    kdif*EmM15*M16
R764:
    EmM15 + U16 > M15 + EmU16
    kdif*EmM15*U16
R765:
    EmM15 + A16 > M15 + EmA16
    kdif*EmM15*A16
R766:
    EmU15 + M16 > U15 + EmM16
    kdif*EmU15*M16
R767:
    EmU15 + U16 > U15 + EmU16
    kdif*EmU15*U16
R768:
    EmU15 + A16 > U15 + EmA16
    kdif*EmU15*A16
R769:
    EmA15 + M16 > A15 + EmM16
    kdif*EmA15*M16
R770:
    EmA15 + U16 > A15 + EmU16
    kdif*EmA15*U16
R771:
    EmA15 + A16 > A15 + EmA16
    kdif*EmA15*A16
R772:
    EmM16 + M17 > M16 + EmM17
    kdif*EmM16*M17
R773:
    EmM16 + U17 > M16 + EmU17
    kdif*EmM16*U17
R774:
    EmM16 + A17 > M16 + EmA17
    kdif*EmM16*A17
R775:
    EmU16 + M17 > U16 + EmM17
    kdif*EmU16*M17
R776:
    EmU16 + U17 > U16 + EmU17
    kdif*EmU16*U17
R777:
    EmU16 + A17 > U16 + EmA17
    kdif*EmU16*A17
R778:
    EmA16 + M17 > A16 + EmM17
    kdif*EmA16*M17
R779:
    EmA16 + U17 > A16 + EmU17
    kdif*EmA16*U17
R780:
    EmA16 + A17 > A16 + EmA17
    kdif*EmA16*A17
R781:
    EmM17 + M18 > M17 + EmM18
    kdif*EmM17*M18
R782:
    EmM17 + U18 > M17 + EmU18
    kdif*EmM17*U18
R783:
    EmM17 + A18 > M17 + EmA18
    kdif*EmM17*A18
R784:
    EmU17 + M18 > U17 + EmM18
    kdif*EmU17*M18
R785:
    EmU17 + U18 > U17 + EmU18
    kdif*EmU17*U18
R786:
    EmU17 + A18 > U17 + EmA18
    kdif*EmU17*A18
R787:
    EmA17 + M18 > A17 + EmM18
    kdif*EmA17*M18
R788:
    EmA17 + U18 > A17 + EmU18
    kdif*EmA17*U18
R789:
    EmA17 + A18 > A17 + EmA18
    kdif*EmA17*A18
R790:
    EmM18 + M19 > M18 + EmM19
    kdif*EmM18*M19
R791:
    EmM18 + U19 > M18 + EmU19
    kdif*EmM18*U19
R792:
    EmM18 + A19 > M18 + EmA19
    kdif*EmM18*A19
R793:
    EmU18 + M19 > U18 + EmM19
    kdif*EmU18*M19
R794:
    EmU18 + U19 > U18 + EmU19
    kdif*EmU18*U19
R795:
    EmU18 + A19 > U18 + EmA19
    kdif*EmU18*A19
R796:
    EmA18 + M19 > A18 + EmM19
    kdif*EmA18*M19
R797:
    EmA18 + U19 > A18 + EmU19
    kdif*EmA18*U19
R798:
    EmA18 + A19 > A18 + EmA19
    kdif*EmA18*A19
R799:
    EmM19 + M20 > M19 + EmM20
    kdif*EmM19*M20
R800:
    EmM19 + U20 > M19 + EmU20
    kdif*EmM19*U20
R801:
    EmM19 + A20 > M19 + EmA20
    kdif*EmM19*A20
R802:
    EmU19 + M20 > U19 + EmM20
    kdif*EmU19*M20
R803:
    EmU19 + U20 > U19 + EmU20
    kdif*EmU19*U20
R804:
    EmU19 + A20 > U19 + EmA20
    kdif*EmU19*A20
R805:
    EmA19 + M20 > A19 + EmM20
    kdif*EmA19*M20
R806:
    EmA19 + U20 > A19 + EmU20
    kdif*EmA19*U20
R807:
    EmA19 + A20 > A19 + EmA20
    kdif*EmA19*A20
R808:
    EmM2 + M1 > M2 + EmM1
    kdif*EmM2*M1
R809:
    EmM2 + U1 > M2 + EmU1
    kdif*EmM2*U1
R810:
    EmM2 + A1 > M2 + EmA1
    kdif*EmM2*A1
R811:
    EmU2 + M1 > U2 + EmM1
    kdif*EmU2*M1
R812:
    EmU2 + U1 > U2 + EmU1
    kdif*EmU2*U1
R813:
    EmU2 + A1 > U2 + EmA1
    kdif*EmU2*A1
R814:
    EmA2 + M1 > A2 + EmM1
    kdif*EmA2*M1
R815:
    EmA2 + U1 > A2 + EmU1
    kdif*EmA2*U1
R816:
    EmA2 + A1 > A2 + EmA1
    kdif*EmA2*A1
R817:
    EmM3 + M2 > M3 + EmM2
    kdif*EmM3*M2
R818:
    EmM3 + U2 > M3 + EmU2
    kdif*EmM3*U2
R819:
    EmM3 + A2 > M3 + EmA2
    kdif*EmM3*A2
R820:
    EmU3 + M2 > U3 + EmM2
    kdif*EmU3*M2
R821:
    EmU3 + U2 > U3 + EmU2
    kdif*EmU3*U2
R822:
    EmU3 + A2 > U3 + EmA2
    kdif*EmU3*A2
R823:
    EmA3 + M2 > A3 + EmM2
    kdif*EmA3*M2
R824:
    EmA3 + U2 > A3 + EmU2
    kdif*EmA3*U2
R825:
    EmA3 + A2 > A3 + EmA2
    kdif*EmA3*A2
R826:
    EmM4 + M3 > M4 + EmM3
    kdif*EmM4*M3
R827:
    EmM4 + U3 > M4 + EmU3
    kdif*EmM4*U3
R828:
    EmM4 + A3 > M4 + EmA3
    kdif*EmM4*A3
R829:
    EmU4 + M3 > U4 + EmM3
    kdif*EmU4*M3
R830:
    EmU4 + U3 > U4 + EmU3
    kdif*EmU4*U3
R831:
    EmU4 + A3 > U4 + EmA3
    kdif*EmU4*A3
R832:
    EmA4 + M3 > A4 + EmM3
    kdif*EmA4*M3
R833:
    EmA4 + U3 > A4 + EmU3
    kdif*EmA4*U3
R834:
    EmA4 + A3 > A4 + EmA3
    kdif*EmA4*A3
R835:
    EmM5 + M4 > M5 + EmM4
    kdif*EmM5*M4
R836:
    EmM5 + U4 > M5 + EmU4
    kdif*EmM5*U4
R837:
    EmM5 + A4 > M5 + EmA4
    kdif*EmM5*A4
R838:
    EmU5 + M4 > U5 + EmM4
    kdif*EmU5*M4
R839:
    EmU5 + U4 > U5 + EmU4
    kdif*EmU5*U4
R840:
    EmU5 + A4 > U5 + EmA4
    kdif*EmU5*A4
R841:
    EmA5 + M4 > A5 + EmM4
    kdif*EmA5*M4
R842:
    EmA5 + U4 > A5 + EmU4
    kdif*EmA5*U4
R843:
    EmA5 + A4 > A5 + EmA4
    kdif*EmA5*A4
R844:
    EmM6 + M5 > M6 + EmM5
    kdif*EmM6*M5
R845:
    EmM6 + U5 > M6 + EmU5
    kdif*EmM6*U5
R846:
    EmM6 + A5 > M6 + EmA5
    kdif*EmM6*A5
R847:
    EmU6 + M5 > U6 + EmM5
    kdif*EmU6*M5
R848:
    EmU6 + U5 > U6 + EmU5
    kdif*EmU6*U5
R849:
    EmU6 + A5 > U6 + EmA5
    kdif*EmU6*A5
R850:
    EmA6 + M5 > A6 + EmM5
    kdif*EmA6*M5
R851:
    EmA6 + U5 > A6 + EmU5
    kdif*EmA6*U5
R852:
    EmA6 + A5 > A6 + EmA5
    kdif*EmA6*A5
R853:
    EmM7 + M6 > M7 + EmM6
    kdif*EmM7*M6
R854:
    EmM7 + U6 > M7 + EmU6
    kdif*EmM7*U6
R855:
    EmM7 + A6 > M7 + EmA6
    kdif*EmM7*A6
R856:
    EmU7 + M6 > U7 + EmM6
    kdif*EmU7*M6
R857:
    EmU7 + U6 > U7 + EmU6
    kdif*EmU7*U6
R858:
    EmU7 + A6 > U7 + EmA6
    kdif*EmU7*A6
R859:
    EmA7 + M6 > A7 + EmM6
    kdif*EmA7*M6
R860:
    EmA7 + U6 > A7 + EmU6
    kdif*EmA7*U6
R861:
    EmA7 + A6 > A7 + EmA6
    kdif*EmA7*A6
R862:
    EmM8 + M7 > M8 + EmM7
    kdif*EmM8*M7
R863:
    EmM8 + U7 > M8 + EmU7
    kdif*EmM8*U7
R864:
    EmM8 + A7 > M8 + EmA7
    kdif*EmM8*A7
R865:
    EmU8 + M7 > U8 + EmM7
    kdif*EmU8*M7
R866:
    EmU8 + U7 > U8 + EmU7
    kdif*EmU8*U7
R867:
    EmU8 + A7 > U8 + EmA7
    kdif*EmU8*A7
R868:
    EmA8 + M7 > A8 + EmM7
    kdif*EmA8*M7
R869:
    EmA8 + U7 > A8 + EmU7
    kdif*EmA8*U7
R870:
    EmA8 + A7 > A8 + EmA7
    kdif*EmA8*A7
R871:
    EmM9 + M8 > M9 + EmM8
    kdif*EmM9*M8
R872:
    EmM9 + U8 > M9 + EmU8
    kdif*EmM9*U8
R873:
    EmM9 + A8 > M9 + EmA8
    kdif*EmM9*A8
R874:
    EmU9 + M8 > U9 + EmM8
    kdif*EmU9*M8
R875:
    EmU9 + U8 > U9 + EmU8
    kdif*EmU9*U8
R876:
    EmU9 + A8 > U9 + EmA8
    kdif*EmU9*A8
R877:
    EmA9 + M8 > A9 + EmM8
    kdif*EmA9*M8
R878:
    EmA9 + U8 > A9 + EmU8
    kdif*EmA9*U8
R879:
    EmA9 + A8 > A9 + EmA8
    kdif*EmA9*A8
R880:
    EmM10 + M9 > M10 + EmM9
    kdif*EmM10*M9
R881:
    EmM10 + U9 > M10 + EmU9
    kdif*EmM10*U9
R882:
    EmM10 + A9 > M10 + EmA9
    kdif*EmM10*A9
R883:
    EmU10 + M9 > U10 + EmM9
    kdif*EmU10*M9
R884:
    EmU10 + U9 > U10 + EmU9
    kdif*EmU10*U9
R885:
    EmU10 + A9 > U10 + EmA9
    kdif*EmU10*A9
R886:
    EmA10 + M9 > A10 + EmM9
    kdif*EmA10*M9
R887:
    EmA10 + U9 > A10 + EmU9
    kdif*EmA10*U9
R888:
    EmA10 + A9 > A10 + EmA9
    kdif*EmA10*A9
R889:
    EmM11 + M10 > M11 + EmM10
    kdif*EmM11*M10
R890:
    EmM11 + U10 > M11 + EmU10
    kdif*EmM11*U10
R891:
    EmM11 + A10 > M11 + EmA10
    kdif*EmM11*A10
R892:
    EmU11 + M10 > U11 + EmM10
    kdif*EmU11*M10
R893:
    EmU11 + U10 > U11 + EmU10
    kdif*EmU11*U10
R894:
    EmU11 + A10 > U11 + EmA10
    kdif*EmU11*A10
R895:
    EmA11 + M10 > A11 + EmM10
    kdif*EmA11*M10
R896:
    EmA11 + U10 > A11 + EmU10
    kdif*EmA11*U10
R897:
    EmA11 + A10 > A11 + EmA10
    kdif*EmA11*A10
R898:
    EmM12 + M11 > M12 + EmM11
    kdif*EmM12*M11
R899:
    EmM12 + U11 > M12 + EmU11
    kdif*EmM12*U11
R900:
    EmM12 + A11 > M12 + EmA11
    kdif*EmM12*A11
R901:
    EmU12 + M11 > U12 + EmM11
    kdif*EmU12*M11
R902:
    EmU12 + U11 > U12 + EmU11
    kdif*EmU12*U11
R903:
    EmU12 + A11 > U12 + EmA11
    kdif*EmU12*A11
R904:
    EmA12 + M11 > A12 + EmM11
    kdif*EmA12*M11
R905:
    EmA12 + U11 > A12 + EmU11
    kdif*EmA12*U11
R906:
    EmA12 + A11 > A12 + EmA11
    kdif*EmA12*A11
R907:
    EmM13 + M12 > M13 + EmM12
    kdif*EmM13*M12
R908:
    EmM13 + U12 > M13 + EmU12
    kdif*EmM13*U12
R909:
    EmM13 + A12 > M13 + EmA12
    kdif*EmM13*A12
R910:
    EmU13 + M12 > U13 + EmM12
    kdif*EmU13*M12
R911:
    EmU13 + U12 > U13 + EmU12
    kdif*EmU13*U12
R912:
    EmU13 + A12 > U13 + EmA12
    kdif*EmU13*A12
R913:
    EmA13 + M12 > A13 + EmM12
    kdif*EmA13*M12
R914:
    EmA13 + U12 > A13 + EmU12
    kdif*EmA13*U12
R915:
    EmA13 + A12 > A13 + EmA12
    kdif*EmA13*A12
R916:
    EmM14 + M13 > M14 + EmM13
    kdif*EmM14*M13
R917:
    EmM14 + U13 > M14 + EmU13
    kdif*EmM14*U13
R918:
    EmM14 + A13 > M14 + EmA13
    kdif*EmM14*A13
R919:
    EmU14 + M13 > U14 + EmM13
    kdif*EmU14*M13
R920:
    EmU14 + U13 > U14 + EmU13
    kdif*EmU14*U13
R921:
    EmU14 + A13 > U14 + EmA13
    kdif*EmU14*A13
R922:
    EmA14 + M13 > A14 + EmM13
    kdif*EmA14*M13
R923:
    EmA14 + U13 > A14 + EmU13
    kdif*EmA14*U13
R924:
    EmA14 + A13 > A14 + EmA13
    kdif*EmA14*A13
R925:
    EmM15 + M14 > M15 + EmM14
    kdif*EmM15*M14
R926:
    EmM15 + U14 > M15 + EmU14
    kdif*EmM15*U14
R927:
    EmM15 + A14 > M15 + EmA14
    kdif*EmM15*A14
R928:
    EmU15 + M14 > U15 + EmM14
    kdif*EmU15*M14
R929:
    EmU15 + U14 > U15 + EmU14
    kdif*EmU15*U14
R930:
    EmU15 + A14 > U15 + EmA14
    kdif*EmU15*A14
R931:
    EmA15 + M14 > A15 + EmM14
    kdif*EmA15*M14
R932:
    EmA15 + U14 > A15 + EmU14
    kdif*EmA15*U14
R933:
    EmA15 + A14 > A15 + EmA14
    kdif*EmA15*A14
R934:
    EmM16 + M15 > M16 + EmM15
    kdif*EmM16*M15
R935:
    EmM16 + U15 > M16 + EmU15
    kdif*EmM16*U15
R936:
    EmM16 + A15 > M16 + EmA15
    kdif*EmM16*A15
R937:
    EmU16 + M15 > U16 + EmM15
    kdif*EmU16*M15
R938:
    EmU16 + U15 > U16 + EmU15
    kdif*EmU16*U15
R939:
    EmU16 + A15 > U16 + EmA15
    kdif*EmU16*A15
R940:
    EmA16 + M15 > A16 + EmM15
    kdif*EmA16*M15
R941:
    EmA16 + U15 > A16 + EmU15
    kdif*EmA16*U15
R942:
    EmA16 + A15 > A16 + EmA15
    kdif*EmA16*A15
R943:
    EmM17 + M16 > M17 + EmM16
    kdif*EmM17*M16
R944:
    EmM17 + U16 > M17 + EmU16
    kdif*EmM17*U16
R945:
    EmM17 + A16 > M17 + EmA16
    kdif*EmM17*A16
R946:
    EmU17 + M16 > U17 + EmM16
    kdif*EmU17*M16
R947:
    EmU17 + U16 > U17 + EmU16
    kdif*EmU17*U16
R948:
    EmU17 + A16 > U17 + EmA16
    kdif*EmU17*A16
R949:
    EmA17 + M16 > A17 + EmM16
    kdif*EmA17*M16
R950:
    EmA17 + U16 > A17 + EmU16
    kdif*EmA17*U16
R951:
    EmA17 + A16 > A17 + EmA16
    kdif*EmA17*A16
R952:
    EmM18 + M17 > M18 + EmM17
    kdif*EmM18*M17
R953:
    EmM18 + U17 > M18 + EmU17
    kdif*EmM18*U17
R954:
    EmM18 + A17 > M18 + EmA17
    kdif*EmM18*A17
R955:
    EmU18 + M17 > U18 + EmM17
    kdif*EmU18*M17
R956:
    EmU18 + U17 > U18 + EmU17
    kdif*EmU18*U17
R957:
    EmU18 + A17 > U18 + EmA17
    kdif*EmU18*A17
R958:
    EmA18 + M17 > A18 + EmM17
    kdif*EmA18*M17
R959:
    EmA18 + U17 > A18 + EmU17
    kdif*EmA18*U17
R960:
    EmA18 + A17 > A18 + EmA17
    kdif*EmA18*A17
R961:
    EmM19 + M18 > M19 + EmM18
    kdif*EmM19*M18
R962:
    EmM19 + U18 > M19 + EmU18
    kdif*EmM19*U18
R963:
    EmM19 + A18 > M19 + EmA18
    kdif*EmM19*A18
R964:
    EmU19 + M18 > U19 + EmM18
    kdif*EmU19*M18
R965:
    EmU19 + U18 > U19 + EmU18
    kdif*EmU19*U18
R966:
    EmU19 + A18 > U19 + EmA18
    kdif*EmU19*A18
R967:
    EmA19 + M18 > A19 + EmM18
    kdif*EmA19*M18
R968:
    EmA19 + U18 > A19 + EmU18
    kdif*EmA19*U18
R969:
    EmA19 + A18 > A19 + EmA18
    kdif*EmA19*A18
R970:
    EmM20 + M19 > M20 + EmM19
    kdif*EmM20*M19
R971:
    EmM20 + U19 > M20 + EmU19
    kdif*EmM20*U19
R972:
    EmM20 + A19 > M20 + EmA19
    kdif*EmM20*A19
R973:
    EmU20 + M19 > U20 + EmM19
    kdif*EmU20*M19
R974:
    EmU20 + U19 > U20 + EmU19
    kdif*EmU20*U19
R975:
    EmU20 + A19 > U20 + EmA19
    kdif*EmU20*A19
R976:
    EmA20 + M19 > A20 + EmM19
    kdif*EmA20*M19
R977:
    EmA20 + U19 > A20 + EmU19
    kdif*EmA20*U19
R978:
    EmA20 + A19 > A20 + EmA19
    kdif*EmA20*A19
R979:
    M10 > EmM10
    kon*M10
R980:
    U10 > EmU10
    kon*U10
R981:
    A10 > EmA10
    kon*A10

# InitPar
knoise = 1.0
kneighbour = .0
kenz = 5.0
kon = 1.0
koff = 0.1
kdif = 0.6
kenz_neigh = 6.0

# InitVar
M1=0
EmM1=1
U1=0
EmU1=0
A1=0
EmA1=0
M2=0
EmM2=0
U2=0
EmU2=0
A2=0
EmA2=1
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
U5=0
EmU5=0
A5=1
EmA5=0
M6=0
EmM6=0
U6=0
EmU6=0
A6=0
EmA6=1
M7=0
EmM7=1
U7=0
EmU7=0
A7=0
EmA7=0
M8=0
EmM8=1
U8=0
EmU8=0
A8=0
EmA8=0
M9=0
EmM9=1
U9=0
EmU9=0
A9=0
EmA9=0
M10=0
EmM10=0
U10=0
EmU10=0
A10=0
EmA10=1
M11=0
EmM11=0
U11=0
EmU11=1
A11=0
EmA11=0
M12=0
EmM12=0
U12=0
EmU12=0
A12=1
EmA12=0
M13=0
EmM13=0
U13=0
EmU13=0
A13=1
EmA13=0
M14=0
EmM14=1
U14=0
EmU14=0
A14=0
EmA14=0
M15=0
EmM15=0
U15=1
EmU15=0
A15=0
EmA15=0
M16=0
EmM16=0
U16=1
EmU16=0
A16=0
EmA16=0
M17=0
EmM17=0
U17=0
EmU17=0
A17=0
EmA17=1
M18=1
EmM18=0
U18=0
EmU18=0
A18=0
EmA18=0
M19=1
EmM19=0
U19=0
EmU19=0
A19=0
EmA19=0
M20=0
EmM20=0
U20=0
EmU20=0
A20=0
EmA20=1
"""
