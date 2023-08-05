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
    M2 > U2
    knoise*M2
R11:
    EmM2 > EmU2
    knoise*EmM2
R12:
    U2 > A2
    knoise*U2
R13:
    A2 > U2
    knoise*A2
R14:
    EmA2 > EmU2
    knoise*EmA2
R15:
    EmM2 > M2
    koff*EmM2
R16:
    EmU2 > U2
    koff*EmU2
R17:
    EmA2 > A2
    koff*EmA2
R18:
    EmU2 > EmM2
    kenz*EmU2
R19:
    M3 > U3
    knoise*M3
R20:
    EmM3 > EmU3
    knoise*EmM3
R21:
    U3 > A3
    knoise*U3
R22:
    A3 > U3
    knoise*A3
R23:
    EmA3 > EmU3
    knoise*EmA3
R24:
    EmM3 > M3
    koff*EmM3
R25:
    EmU3 > U3
    koff*EmU3
R26:
    EmA3 > A3
    koff*EmA3
R27:
    EmU3 > EmM3
    kenz*EmU3
R28:
    M4 > U4
    knoise*M4
R29:
    EmM4 > EmU4
    knoise*EmM4
R30:
    U4 > A4
    knoise*U4
R31:
    A4 > U4
    knoise*A4
R32:
    EmA4 > EmU4
    knoise*EmA4
R33:
    EmM4 > M4
    koff*EmM4
R34:
    EmU4 > U4
    koff*EmU4
R35:
    EmA4 > A4
    koff*EmA4
R36:
    EmU4 > EmM4
    kenz*EmU4
R37:
    M5 > U5
    knoise*M5
R38:
    EmM5 > EmU5
    knoise*EmM5
R39:
    U5 > A5
    knoise*U5
R40:
    A5 > U5
    knoise*A5
R41:
    EmA5 > EmU5
    knoise*EmA5
R42:
    EmM5 > M5
    koff*EmM5
R43:
    EmU5 > U5
    koff*EmU5
R44:
    EmA5 > A5
    koff*EmA5
R45:
    EmU5 > EmM5
    kenz*EmU5
R46:
    M6 > U6
    knoise*M6
R47:
    EmM6 > EmU6
    knoise*EmM6
R48:
    U6 > A6
    knoise*U6
R49:
    A6 > U6
    knoise*A6
R50:
    EmA6 > EmU6
    knoise*EmA6
R51:
    EmM6 > M6
    koff*EmM6
R52:
    EmU6 > U6
    koff*EmU6
R53:
    EmA6 > A6
    koff*EmA6
R54:
    EmU6 > EmM6
    kenz*EmU6
R55:
    M7 > U7
    knoise*M7
R56:
    EmM7 > EmU7
    knoise*EmM7
R57:
    U7 > A7
    knoise*U7
R58:
    A7 > U7
    knoise*A7
R59:
    EmA7 > EmU7
    knoise*EmA7
R60:
    EmM7 > M7
    koff*EmM7
R61:
    EmU7 > U7
    koff*EmU7
R62:
    EmA7 > A7
    koff*EmA7
R63:
    EmU7 > EmM7
    kenz*EmU7
R64:
    M8 > U8
    knoise*M8
R65:
    EmM8 > EmU8
    knoise*EmM8
R66:
    U8 > A8
    knoise*U8
R67:
    A8 > U8
    knoise*A8
R68:
    EmA8 > EmU8
    knoise*EmA8
R69:
    EmM8 > M8
    koff*EmM8
R70:
    EmU8 > U8
    koff*EmU8
R71:
    EmA8 > A8
    koff*EmA8
R72:
    EmU8 > EmM8
    kenz*EmU8
R73:
    M9 > U9
    knoise*M9
R74:
    EmM9 > EmU9
    knoise*EmM9
R75:
    U9 > A9
    knoise*U9
R76:
    A9 > U9
    knoise*A9
R77:
    EmA9 > EmU9
    knoise*EmA9
R78:
    EmM9 > M9
    koff*EmM9
R79:
    EmU9 > U9
    koff*EmU9
R80:
    EmA9 > A9
    koff*EmA9
R81:
    EmU9 > EmM9
    kenz*EmU9
R82:
    M10 > U10
    knoise*M10
R83:
    EmM10 > EmU10
    knoise*EmM10
R84:
    U10 > A10
    knoise*U10
R85:
    A10 > U10
    knoise*A10
R86:
    EmA10 > EmU10
    knoise*EmA10
R87:
    EmM10 > M10
    koff*EmM10
R88:
    EmU10 > U10
    koff*EmU10
R89:
    EmA10 > A10
    koff*EmA10
R90:
    EmU10 > EmM10
    kenz*EmU10
R91:
    M11 > U11
    knoise*M11
R92:
    EmM11 > EmU11
    knoise*EmM11
R93:
    U11 > A11
    knoise*U11
R94:
    A11 > U11
    knoise*A11
R95:
    EmA11 > EmU11
    knoise*EmA11
R96:
    EmM11 > M11
    koff*EmM11
R97:
    EmU11 > U11
    koff*EmU11
R98:
    EmA11 > A11
    koff*EmA11
R99:
    EmU11 > EmM11
    kenz*EmU11
R100:
    M12 > U12
    knoise*M12
R101:
    EmM12 > EmU12
    knoise*EmM12
R102:
    U12 > A12
    knoise*U12
R103:
    A12 > U12
    knoise*A12
R104:
    EmA12 > EmU12
    knoise*EmA12
R105:
    EmM12 > M12
    koff*EmM12
R106:
    EmU12 > U12
    koff*EmU12
R107:
    EmA12 > A12
    koff*EmA12
R108:
    EmU12 > EmM12
    kenz*EmU12
R109:
    M13 > U13
    knoise*M13
R110:
    EmM13 > EmU13
    knoise*EmM13
R111:
    U13 > A13
    knoise*U13
R112:
    A13 > U13
    knoise*A13
R113:
    EmA13 > EmU13
    knoise*EmA13
R114:
    EmM13 > M13
    koff*EmM13
R115:
    EmU13 > U13
    koff*EmU13
R116:
    EmA13 > A13
    koff*EmA13
R117:
    EmU13 > EmM13
    kenz*EmU13
R118:
    M14 > U14
    knoise*M14
R119:
    EmM14 > EmU14
    knoise*EmM14
R120:
    U14 > A14
    knoise*U14
R121:
    A14 > U14
    knoise*A14
R122:
    EmA14 > EmU14
    knoise*EmA14
R123:
    EmM14 > M14
    koff*EmM14
R124:
    EmU14 > U14
    koff*EmU14
R125:
    EmA14 > A14
    koff*EmA14
R126:
    EmU14 > EmM14
    kenz*EmU14
R127:
    M15 > U15
    knoise*M15
R128:
    EmM15 > EmU15
    knoise*EmM15
R129:
    U15 > A15
    knoise*U15
R130:
    A15 > U15
    knoise*A15
R131:
    EmA15 > EmU15
    knoise*EmA15
R132:
    EmM15 > M15
    koff*EmM15
R133:
    EmU15 > U15
    koff*EmU15
R134:
    EmA15 > A15
    koff*EmA15
R135:
    EmU15 > EmM15
    kenz*EmU15
R136:
    M16 > U16
    knoise*M16
R137:
    EmM16 > EmU16
    knoise*EmM16
R138:
    U16 > A16
    knoise*U16
R139:
    A16 > U16
    knoise*A16
R140:
    EmA16 > EmU16
    knoise*EmA16
R141:
    EmM16 > M16
    koff*EmM16
R142:
    EmU16 > U16
    koff*EmU16
R143:
    EmA16 > A16
    koff*EmA16
R144:
    EmU16 > EmM16
    kenz*EmU16
R145:
    M17 > U17
    knoise*M17
R146:
    EmM17 > EmU17
    knoise*EmM17
R147:
    U17 > A17
    knoise*U17
R148:
    A17 > U17
    knoise*A17
R149:
    EmA17 > EmU17
    knoise*EmA17
R150:
    EmM17 > M17
    koff*EmM17
R151:
    EmU17 > U17
    koff*EmU17
R152:
    EmA17 > A17
    koff*EmA17
R153:
    EmU17 > EmM17
    kenz*EmU17
R154:
    M18 > U18
    knoise*M18
R155:
    EmM18 > EmU18
    knoise*EmM18
R156:
    U18 > A18
    knoise*U18
R157:
    A18 > U18
    knoise*A18
R158:
    EmA18 > EmU18
    knoise*EmA18
R159:
    EmM18 > M18
    koff*EmM18
R160:
    EmU18 > U18
    koff*EmU18
R161:
    EmA18 > A18
    koff*EmA18
R162:
    EmU18 > EmM18
    kenz*EmU18
R163:
    M19 > U19
    knoise*M19
R164:
    EmM19 > EmU19
    knoise*EmM19
R165:
    U19 > A19
    knoise*U19
R166:
    A19 > U19
    knoise*A19
R167:
    EmA19 > EmU19
    knoise*EmA19
R168:
    EmM19 > M19
    koff*EmM19
R169:
    EmU19 > U19
    koff*EmU19
R170:
    EmA19 > A19
    koff*EmA19
R171:
    EmU19 > EmM19
    kenz*EmU19
R172:
    M20 > U20
    knoise*M20
R173:
    EmM20 > EmU20
    knoise*EmM20
R174:
    U20 > A20
    knoise*U20
R175:
    A20 > U20
    knoise*A20
R176:
    EmA20 > EmU20
    knoise*EmA20
R177:
    EmM20 > M20
    koff*EmM20
R178:
    EmU20 > U20
    koff*EmU20
R179:
    EmA20 > A20
    koff*EmA20
R180:
    EmU20 > EmM20
    kenz*EmU20
R181:
    EmM1 + M2 > M1 + EmM2
    kdif*EmM1*M2
R182:
    EmM1 + U2 > M1 + EmU2
    kdif*EmM1*U2
R183:
    EmM1 + A2 > M1 + EmA2
    kdif*EmM1*A2
R184:
    EmU1 + M2 > U1 + EmM2
    kdif*EmU1*M2
R185:
    EmU1 + U2 > U1 + EmU2
    kdif*EmU1*U2
R186:
    EmU1 + A2 > U1 + EmA2
    kdif*EmU1*A2
R187:
    EmA1 + M2 > A1 + EmM2
    kdif*EmA1*M2
R188:
    EmA1 + U2 > A1 + EmU2
    kdif*EmA1*U2
R189:
    EmA1 + A2 > A1 + EmA2
    kdif*EmA1*A2
R190:
    EmM2 + M3 > M2 + EmM3
    kdif*EmM2*M3
R191:
    EmM2 + U3 > M2 + EmU3
    kdif*EmM2*U3
R192:
    EmM2 + A3 > M2 + EmA3
    kdif*EmM2*A3
R193:
    EmU2 + M3 > U2 + EmM3
    kdif*EmU2*M3
R194:
    EmU2 + U3 > U2 + EmU3
    kdif*EmU2*U3
R195:
    EmU2 + A3 > U2 + EmA3
    kdif*EmU2*A3
R196:
    EmA2 + M3 > A2 + EmM3
    kdif*EmA2*M3
R197:
    EmA2 + U3 > A2 + EmU3
    kdif*EmA2*U3
R198:
    EmA2 + A3 > A2 + EmA3
    kdif*EmA2*A3
R199:
    EmM3 + M4 > M3 + EmM4
    kdif*EmM3*M4
R200:
    EmM3 + U4 > M3 + EmU4
    kdif*EmM3*U4
R201:
    EmM3 + A4 > M3 + EmA4
    kdif*EmM3*A4
R202:
    EmU3 + M4 > U3 + EmM4
    kdif*EmU3*M4
R203:
    EmU3 + U4 > U3 + EmU4
    kdif*EmU3*U4
R204:
    EmU3 + A4 > U3 + EmA4
    kdif*EmU3*A4
R205:
    EmA3 + M4 > A3 + EmM4
    kdif*EmA3*M4
R206:
    EmA3 + U4 > A3 + EmU4
    kdif*EmA3*U4
R207:
    EmA3 + A4 > A3 + EmA4
    kdif*EmA3*A4
R208:
    EmM4 + M5 > M4 + EmM5
    kdif*EmM4*M5
R209:
    EmM4 + U5 > M4 + EmU5
    kdif*EmM4*U5
R210:
    EmM4 + A5 > M4 + EmA5
    kdif*EmM4*A5
R211:
    EmU4 + M5 > U4 + EmM5
    kdif*EmU4*M5
R212:
    EmU4 + U5 > U4 + EmU5
    kdif*EmU4*U5
R213:
    EmU4 + A5 > U4 + EmA5
    kdif*EmU4*A5
R214:
    EmA4 + M5 > A4 + EmM5
    kdif*EmA4*M5
R215:
    EmA4 + U5 > A4 + EmU5
    kdif*EmA4*U5
R216:
    EmA4 + A5 > A4 + EmA5
    kdif*EmA4*A5
R217:
    EmM5 + M6 > M5 + EmM6
    kdif*EmM5*M6
R218:
    EmM5 + U6 > M5 + EmU6
    kdif*EmM5*U6
R219:
    EmM5 + A6 > M5 + EmA6
    kdif*EmM5*A6
R220:
    EmU5 + M6 > U5 + EmM6
    kdif*EmU5*M6
R221:
    EmU5 + U6 > U5 + EmU6
    kdif*EmU5*U6
R222:
    EmU5 + A6 > U5 + EmA6
    kdif*EmU5*A6
R223:
    EmA5 + M6 > A5 + EmM6
    kdif*EmA5*M6
R224:
    EmA5 + U6 > A5 + EmU6
    kdif*EmA5*U6
R225:
    EmA5 + A6 > A5 + EmA6
    kdif*EmA5*A6
R226:
    EmM6 + M7 > M6 + EmM7
    kdif*EmM6*M7
R227:
    EmM6 + U7 > M6 + EmU7
    kdif*EmM6*U7
R228:
    EmM6 + A7 > M6 + EmA7
    kdif*EmM6*A7
R229:
    EmU6 + M7 > U6 + EmM7
    kdif*EmU6*M7
R230:
    EmU6 + U7 > U6 + EmU7
    kdif*EmU6*U7
R231:
    EmU6 + A7 > U6 + EmA7
    kdif*EmU6*A7
R232:
    EmA6 + M7 > A6 + EmM7
    kdif*EmA6*M7
R233:
    EmA6 + U7 > A6 + EmU7
    kdif*EmA6*U7
R234:
    EmA6 + A7 > A6 + EmA7
    kdif*EmA6*A7
R235:
    EmM7 + M8 > M7 + EmM8
    kdif*EmM7*M8
R236:
    EmM7 + U8 > M7 + EmU8
    kdif*EmM7*U8
R237:
    EmM7 + A8 > M7 + EmA8
    kdif*EmM7*A8
R238:
    EmU7 + M8 > U7 + EmM8
    kdif*EmU7*M8
R239:
    EmU7 + U8 > U7 + EmU8
    kdif*EmU7*U8
R240:
    EmU7 + A8 > U7 + EmA8
    kdif*EmU7*A8
R241:
    EmA7 + M8 > A7 + EmM8
    kdif*EmA7*M8
R242:
    EmA7 + U8 > A7 + EmU8
    kdif*EmA7*U8
R243:
    EmA7 + A8 > A7 + EmA8
    kdif*EmA7*A8
R244:
    EmM8 + M9 > M8 + EmM9
    kdif*EmM8*M9
R245:
    EmM8 + U9 > M8 + EmU9
    kdif*EmM8*U9
R246:
    EmM8 + A9 > M8 + EmA9
    kdif*EmM8*A9
R247:
    EmU8 + M9 > U8 + EmM9
    kdif*EmU8*M9
R248:
    EmU8 + U9 > U8 + EmU9
    kdif*EmU8*U9
R249:
    EmU8 + A9 > U8 + EmA9
    kdif*EmU8*A9
R250:
    EmA8 + M9 > A8 + EmM9
    kdif*EmA8*M9
R251:
    EmA8 + U9 > A8 + EmU9
    kdif*EmA8*U9
R252:
    EmA8 + A9 > A8 + EmA9
    kdif*EmA8*A9
R253:
    EmM9 + M10 > M9 + EmM10
    kdif*EmM9*M10
R254:
    EmM9 + U10 > M9 + EmU10
    kdif*EmM9*U10
R255:
    EmM9 + A10 > M9 + EmA10
    kdif*EmM9*A10
R256:
    EmU9 + M10 > U9 + EmM10
    kdif*EmU9*M10
R257:
    EmU9 + U10 > U9 + EmU10
    kdif*EmU9*U10
R258:
    EmU9 + A10 > U9 + EmA10
    kdif*EmU9*A10
R259:
    EmA9 + M10 > A9 + EmM10
    kdif*EmA9*M10
R260:
    EmA9 + U10 > A9 + EmU10
    kdif*EmA9*U10
R261:
    EmA9 + A10 > A9 + EmA10
    kdif*EmA9*A10
R262:
    EmM10 + M11 > M10 + EmM11
    kdif*EmM10*M11
R263:
    EmM10 + U11 > M10 + EmU11
    kdif*EmM10*U11
R264:
    EmM10 + A11 > M10 + EmA11
    kdif*EmM10*A11
R265:
    EmU10 + M11 > U10 + EmM11
    kdif*EmU10*M11
R266:
    EmU10 + U11 > U10 + EmU11
    kdif*EmU10*U11
R267:
    EmU10 + A11 > U10 + EmA11
    kdif*EmU10*A11
R268:
    EmA10 + M11 > A10 + EmM11
    kdif*EmA10*M11
R269:
    EmA10 + U11 > A10 + EmU11
    kdif*EmA10*U11
R270:
    EmA10 + A11 > A10 + EmA11
    kdif*EmA10*A11
R271:
    EmM11 + M12 > M11 + EmM12
    kdif*EmM11*M12
R272:
    EmM11 + U12 > M11 + EmU12
    kdif*EmM11*U12
R273:
    EmM11 + A12 > M11 + EmA12
    kdif*EmM11*A12
R274:
    EmU11 + M12 > U11 + EmM12
    kdif*EmU11*M12
R275:
    EmU11 + U12 > U11 + EmU12
    kdif*EmU11*U12
R276:
    EmU11 + A12 > U11 + EmA12
    kdif*EmU11*A12
R277:
    EmA11 + M12 > A11 + EmM12
    kdif*EmA11*M12
R278:
    EmA11 + U12 > A11 + EmU12
    kdif*EmA11*U12
R279:
    EmA11 + A12 > A11 + EmA12
    kdif*EmA11*A12
R280:
    EmM12 + M13 > M12 + EmM13
    kdif*EmM12*M13
R281:
    EmM12 + U13 > M12 + EmU13
    kdif*EmM12*U13
R282:
    EmM12 + A13 > M12 + EmA13
    kdif*EmM12*A13
R283:
    EmU12 + M13 > U12 + EmM13
    kdif*EmU12*M13
R284:
    EmU12 + U13 > U12 + EmU13
    kdif*EmU12*U13
R285:
    EmU12 + A13 > U12 + EmA13
    kdif*EmU12*A13
R286:
    EmA12 + M13 > A12 + EmM13
    kdif*EmA12*M13
R287:
    EmA12 + U13 > A12 + EmU13
    kdif*EmA12*U13
R288:
    EmA12 + A13 > A12 + EmA13
    kdif*EmA12*A13
R289:
    EmM13 + M14 > M13 + EmM14
    kdif*EmM13*M14
R290:
    EmM13 + U14 > M13 + EmU14
    kdif*EmM13*U14
R291:
    EmM13 + A14 > M13 + EmA14
    kdif*EmM13*A14
R292:
    EmU13 + M14 > U13 + EmM14
    kdif*EmU13*M14
R293:
    EmU13 + U14 > U13 + EmU14
    kdif*EmU13*U14
R294:
    EmU13 + A14 > U13 + EmA14
    kdif*EmU13*A14
R295:
    EmA13 + M14 > A13 + EmM14
    kdif*EmA13*M14
R296:
    EmA13 + U14 > A13 + EmU14
    kdif*EmA13*U14
R297:
    EmA13 + A14 > A13 + EmA14
    kdif*EmA13*A14
R298:
    EmM14 + M15 > M14 + EmM15
    kdif*EmM14*M15
R299:
    EmM14 + U15 > M14 + EmU15
    kdif*EmM14*U15
R300:
    EmM14 + A15 > M14 + EmA15
    kdif*EmM14*A15
R301:
    EmU14 + M15 > U14 + EmM15
    kdif*EmU14*M15
R302:
    EmU14 + U15 > U14 + EmU15
    kdif*EmU14*U15
R303:
    EmU14 + A15 > U14 + EmA15
    kdif*EmU14*A15
R304:
    EmA14 + M15 > A14 + EmM15
    kdif*EmA14*M15
R305:
    EmA14 + U15 > A14 + EmU15
    kdif*EmA14*U15
R306:
    EmA14 + A15 > A14 + EmA15
    kdif*EmA14*A15
R307:
    EmM15 + M16 > M15 + EmM16
    kdif*EmM15*M16
R308:
    EmM15 + U16 > M15 + EmU16
    kdif*EmM15*U16
R309:
    EmM15 + A16 > M15 + EmA16
    kdif*EmM15*A16
R310:
    EmU15 + M16 > U15 + EmM16
    kdif*EmU15*M16
R311:
    EmU15 + U16 > U15 + EmU16
    kdif*EmU15*U16
R312:
    EmU15 + A16 > U15 + EmA16
    kdif*EmU15*A16
R313:
    EmA15 + M16 > A15 + EmM16
    kdif*EmA15*M16
R314:
    EmA15 + U16 > A15 + EmU16
    kdif*EmA15*U16
R315:
    EmA15 + A16 > A15 + EmA16
    kdif*EmA15*A16
R316:
    EmM16 + M17 > M16 + EmM17
    kdif*EmM16*M17
R317:
    EmM16 + U17 > M16 + EmU17
    kdif*EmM16*U17
R318:
    EmM16 + A17 > M16 + EmA17
    kdif*EmM16*A17
R319:
    EmU16 + M17 > U16 + EmM17
    kdif*EmU16*M17
R320:
    EmU16 + U17 > U16 + EmU17
    kdif*EmU16*U17
R321:
    EmU16 + A17 > U16 + EmA17
    kdif*EmU16*A17
R322:
    EmA16 + M17 > A16 + EmM17
    kdif*EmA16*M17
R323:
    EmA16 + U17 > A16 + EmU17
    kdif*EmA16*U17
R324:
    EmA16 + A17 > A16 + EmA17
    kdif*EmA16*A17
R325:
    EmM17 + M18 > M17 + EmM18
    kdif*EmM17*M18
R326:
    EmM17 + U18 > M17 + EmU18
    kdif*EmM17*U18
R327:
    EmM17 + A18 > M17 + EmA18
    kdif*EmM17*A18
R328:
    EmU17 + M18 > U17 + EmM18
    kdif*EmU17*M18
R329:
    EmU17 + U18 > U17 + EmU18
    kdif*EmU17*U18
R330:
    EmU17 + A18 > U17 + EmA18
    kdif*EmU17*A18
R331:
    EmA17 + M18 > A17 + EmM18
    kdif*EmA17*M18
R332:
    EmA17 + U18 > A17 + EmU18
    kdif*EmA17*U18
R333:
    EmA17 + A18 > A17 + EmA18
    kdif*EmA17*A18
R334:
    EmM18 + M19 > M18 + EmM19
    kdif*EmM18*M19
R335:
    EmM18 + U19 > M18 + EmU19
    kdif*EmM18*U19
R336:
    EmM18 + A19 > M18 + EmA19
    kdif*EmM18*A19
R337:
    EmU18 + M19 > U18 + EmM19
    kdif*EmU18*M19
R338:
    EmU18 + U19 > U18 + EmU19
    kdif*EmU18*U19
R339:
    EmU18 + A19 > U18 + EmA19
    kdif*EmU18*A19
R340:
    EmA18 + M19 > A18 + EmM19
    kdif*EmA18*M19
R341:
    EmA18 + U19 > A18 + EmU19
    kdif*EmA18*U19
R342:
    EmA18 + A19 > A18 + EmA19
    kdif*EmA18*A19
R343:
    EmM19 + M20 > M19 + EmM20
    kdif*EmM19*M20
R344:
    EmM19 + U20 > M19 + EmU20
    kdif*EmM19*U20
R345:
    EmM19 + A20 > M19 + EmA20
    kdif*EmM19*A20
R346:
    EmU19 + M20 > U19 + EmM20
    kdif*EmU19*M20
R347:
    EmU19 + U20 > U19 + EmU20
    kdif*EmU19*U20
R348:
    EmU19 + A20 > U19 + EmA20
    kdif*EmU19*A20
R349:
    EmA19 + M20 > A19 + EmM20
    kdif*EmA19*M20
R350:
    EmA19 + U20 > A19 + EmU20
    kdif*EmA19*U20
R351:
    EmA19 + A20 > A19 + EmA20
    kdif*EmA19*A20
R352:
    EmM2 + M1 > M2 + EmM1
    kdif*EmM2*M1
R353:
    EmM2 + U1 > M2 + EmU1
    kdif*EmM2*U1
R354:
    EmM2 + A1 > M2 + EmA1
    kdif*EmM2*A1
R355:
    EmU2 + M1 > U2 + EmM1
    kdif*EmU2*M1
R356:
    EmU2 + U1 > U2 + EmU1
    kdif*EmU2*U1
R357:
    EmU2 + A1 > U2 + EmA1
    kdif*EmU2*A1
R358:
    EmA2 + M1 > A2 + EmM1
    kdif*EmA2*M1
R359:
    EmA2 + U1 > A2 + EmU1
    kdif*EmA2*U1
R360:
    EmA2 + A1 > A2 + EmA1
    kdif*EmA2*A1
R361:
    EmM3 + M2 > M3 + EmM2
    kdif*EmM3*M2
R362:
    EmM3 + U2 > M3 + EmU2
    kdif*EmM3*U2
R363:
    EmM3 + A2 > M3 + EmA2
    kdif*EmM3*A2
R364:
    EmU3 + M2 > U3 + EmM2
    kdif*EmU3*M2
R365:
    EmU3 + U2 > U3 + EmU2
    kdif*EmU3*U2
R366:
    EmU3 + A2 > U3 + EmA2
    kdif*EmU3*A2
R367:
    EmA3 + M2 > A3 + EmM2
    kdif*EmA3*M2
R368:
    EmA3 + U2 > A3 + EmU2
    kdif*EmA3*U2
R369:
    EmA3 + A2 > A3 + EmA2
    kdif*EmA3*A2
R370:
    EmM4 + M3 > M4 + EmM3
    kdif*EmM4*M3
R371:
    EmM4 + U3 > M4 + EmU3
    kdif*EmM4*U3
R372:
    EmM4 + A3 > M4 + EmA3
    kdif*EmM4*A3
R373:
    EmU4 + M3 > U4 + EmM3
    kdif*EmU4*M3
R374:
    EmU4 + U3 > U4 + EmU3
    kdif*EmU4*U3
R375:
    EmU4 + A3 > U4 + EmA3
    kdif*EmU4*A3
R376:
    EmA4 + M3 > A4 + EmM3
    kdif*EmA4*M3
R377:
    EmA4 + U3 > A4 + EmU3
    kdif*EmA4*U3
R378:
    EmA4 + A3 > A4 + EmA3
    kdif*EmA4*A3
R379:
    EmM5 + M4 > M5 + EmM4
    kdif*EmM5*M4
R380:
    EmM5 + U4 > M5 + EmU4
    kdif*EmM5*U4
R381:
    EmM5 + A4 > M5 + EmA4
    kdif*EmM5*A4
R382:
    EmU5 + M4 > U5 + EmM4
    kdif*EmU5*M4
R383:
    EmU5 + U4 > U5 + EmU4
    kdif*EmU5*U4
R384:
    EmU5 + A4 > U5 + EmA4
    kdif*EmU5*A4
R385:
    EmA5 + M4 > A5 + EmM4
    kdif*EmA5*M4
R386:
    EmA5 + U4 > A5 + EmU4
    kdif*EmA5*U4
R387:
    EmA5 + A4 > A5 + EmA4
    kdif*EmA5*A4
R388:
    EmM6 + M5 > M6 + EmM5
    kdif*EmM6*M5
R389:
    EmM6 + U5 > M6 + EmU5
    kdif*EmM6*U5
R390:
    EmM6 + A5 > M6 + EmA5
    kdif*EmM6*A5
R391:
    EmU6 + M5 > U6 + EmM5
    kdif*EmU6*M5
R392:
    EmU6 + U5 > U6 + EmU5
    kdif*EmU6*U5
R393:
    EmU6 + A5 > U6 + EmA5
    kdif*EmU6*A5
R394:
    EmA6 + M5 > A6 + EmM5
    kdif*EmA6*M5
R395:
    EmA6 + U5 > A6 + EmU5
    kdif*EmA6*U5
R396:
    EmA6 + A5 > A6 + EmA5
    kdif*EmA6*A5
R397:
    EmM7 + M6 > M7 + EmM6
    kdif*EmM7*M6
R398:
    EmM7 + U6 > M7 + EmU6
    kdif*EmM7*U6
R399:
    EmM7 + A6 > M7 + EmA6
    kdif*EmM7*A6
R400:
    EmU7 + M6 > U7 + EmM6
    kdif*EmU7*M6
R401:
    EmU7 + U6 > U7 + EmU6
    kdif*EmU7*U6
R402:
    EmU7 + A6 > U7 + EmA6
    kdif*EmU7*A6
R403:
    EmA7 + M6 > A7 + EmM6
    kdif*EmA7*M6
R404:
    EmA7 + U6 > A7 + EmU6
    kdif*EmA7*U6
R405:
    EmA7 + A6 > A7 + EmA6
    kdif*EmA7*A6
R406:
    EmM8 + M7 > M8 + EmM7
    kdif*EmM8*M7
R407:
    EmM8 + U7 > M8 + EmU7
    kdif*EmM8*U7
R408:
    EmM8 + A7 > M8 + EmA7
    kdif*EmM8*A7
R409:
    EmU8 + M7 > U8 + EmM7
    kdif*EmU8*M7
R410:
    EmU8 + U7 > U8 + EmU7
    kdif*EmU8*U7
R411:
    EmU8 + A7 > U8 + EmA7
    kdif*EmU8*A7
R412:
    EmA8 + M7 > A8 + EmM7
    kdif*EmA8*M7
R413:
    EmA8 + U7 > A8 + EmU7
    kdif*EmA8*U7
R414:
    EmA8 + A7 > A8 + EmA7
    kdif*EmA8*A7
R415:
    EmM9 + M8 > M9 + EmM8
    kdif*EmM9*M8
R416:
    EmM9 + U8 > M9 + EmU8
    kdif*EmM9*U8
R417:
    EmM9 + A8 > M9 + EmA8
    kdif*EmM9*A8
R418:
    EmU9 + M8 > U9 + EmM8
    kdif*EmU9*M8
R419:
    EmU9 + U8 > U9 + EmU8
    kdif*EmU9*U8
R420:
    EmU9 + A8 > U9 + EmA8
    kdif*EmU9*A8
R421:
    EmA9 + M8 > A9 + EmM8
    kdif*EmA9*M8
R422:
    EmA9 + U8 > A9 + EmU8
    kdif*EmA9*U8
R423:
    EmA9 + A8 > A9 + EmA8
    kdif*EmA9*A8
R424:
    EmM10 + M9 > M10 + EmM9
    kdif*EmM10*M9
R425:
    EmM10 + U9 > M10 + EmU9
    kdif*EmM10*U9
R426:
    EmM10 + A9 > M10 + EmA9
    kdif*EmM10*A9
R427:
    EmU10 + M9 > U10 + EmM9
    kdif*EmU10*M9
R428:
    EmU10 + U9 > U10 + EmU9
    kdif*EmU10*U9
R429:
    EmU10 + A9 > U10 + EmA9
    kdif*EmU10*A9
R430:
    EmA10 + M9 > A10 + EmM9
    kdif*EmA10*M9
R431:
    EmA10 + U9 > A10 + EmU9
    kdif*EmA10*U9
R432:
    EmA10 + A9 > A10 + EmA9
    kdif*EmA10*A9
R433:
    EmM11 + M10 > M11 + EmM10
    kdif*EmM11*M10
R434:
    EmM11 + U10 > M11 + EmU10
    kdif*EmM11*U10
R435:
    EmM11 + A10 > M11 + EmA10
    kdif*EmM11*A10
R436:
    EmU11 + M10 > U11 + EmM10
    kdif*EmU11*M10
R437:
    EmU11 + U10 > U11 + EmU10
    kdif*EmU11*U10
R438:
    EmU11 + A10 > U11 + EmA10
    kdif*EmU11*A10
R439:
    EmA11 + M10 > A11 + EmM10
    kdif*EmA11*M10
R440:
    EmA11 + U10 > A11 + EmU10
    kdif*EmA11*U10
R441:
    EmA11 + A10 > A11 + EmA10
    kdif*EmA11*A10
R442:
    EmM12 + M11 > M12 + EmM11
    kdif*EmM12*M11
R443:
    EmM12 + U11 > M12 + EmU11
    kdif*EmM12*U11
R444:
    EmM12 + A11 > M12 + EmA11
    kdif*EmM12*A11
R445:
    EmU12 + M11 > U12 + EmM11
    kdif*EmU12*M11
R446:
    EmU12 + U11 > U12 + EmU11
    kdif*EmU12*U11
R447:
    EmU12 + A11 > U12 + EmA11
    kdif*EmU12*A11
R448:
    EmA12 + M11 > A12 + EmM11
    kdif*EmA12*M11
R449:
    EmA12 + U11 > A12 + EmU11
    kdif*EmA12*U11
R450:
    EmA12 + A11 > A12 + EmA11
    kdif*EmA12*A11
R451:
    EmM13 + M12 > M13 + EmM12
    kdif*EmM13*M12
R452:
    EmM13 + U12 > M13 + EmU12
    kdif*EmM13*U12
R453:
    EmM13 + A12 > M13 + EmA12
    kdif*EmM13*A12
R454:
    EmU13 + M12 > U13 + EmM12
    kdif*EmU13*M12
R455:
    EmU13 + U12 > U13 + EmU12
    kdif*EmU13*U12
R456:
    EmU13 + A12 > U13 + EmA12
    kdif*EmU13*A12
R457:
    EmA13 + M12 > A13 + EmM12
    kdif*EmA13*M12
R458:
    EmA13 + U12 > A13 + EmU12
    kdif*EmA13*U12
R459:
    EmA13 + A12 > A13 + EmA12
    kdif*EmA13*A12
R460:
    EmM14 + M13 > M14 + EmM13
    kdif*EmM14*M13
R461:
    EmM14 + U13 > M14 + EmU13
    kdif*EmM14*U13
R462:
    EmM14 + A13 > M14 + EmA13
    kdif*EmM14*A13
R463:
    EmU14 + M13 > U14 + EmM13
    kdif*EmU14*M13
R464:
    EmU14 + U13 > U14 + EmU13
    kdif*EmU14*U13
R465:
    EmU14 + A13 > U14 + EmA13
    kdif*EmU14*A13
R466:
    EmA14 + M13 > A14 + EmM13
    kdif*EmA14*M13
R467:
    EmA14 + U13 > A14 + EmU13
    kdif*EmA14*U13
R468:
    EmA14 + A13 > A14 + EmA13
    kdif*EmA14*A13
R469:
    EmM15 + M14 > M15 + EmM14
    kdif*EmM15*M14
R470:
    EmM15 + U14 > M15 + EmU14
    kdif*EmM15*U14
R471:
    EmM15 + A14 > M15 + EmA14
    kdif*EmM15*A14
R472:
    EmU15 + M14 > U15 + EmM14
    kdif*EmU15*M14
R473:
    EmU15 + U14 > U15 + EmU14
    kdif*EmU15*U14
R474:
    EmU15 + A14 > U15 + EmA14
    kdif*EmU15*A14
R475:
    EmA15 + M14 > A15 + EmM14
    kdif*EmA15*M14
R476:
    EmA15 + U14 > A15 + EmU14
    kdif*EmA15*U14
R477:
    EmA15 + A14 > A15 + EmA14
    kdif*EmA15*A14
R478:
    EmM16 + M15 > M16 + EmM15
    kdif*EmM16*M15
R479:
    EmM16 + U15 > M16 + EmU15
    kdif*EmM16*U15
R480:
    EmM16 + A15 > M16 + EmA15
    kdif*EmM16*A15
R481:
    EmU16 + M15 > U16 + EmM15
    kdif*EmU16*M15
R482:
    EmU16 + U15 > U16 + EmU15
    kdif*EmU16*U15
R483:
    EmU16 + A15 > U16 + EmA15
    kdif*EmU16*A15
R484:
    EmA16 + M15 > A16 + EmM15
    kdif*EmA16*M15
R485:
    EmA16 + U15 > A16 + EmU15
    kdif*EmA16*U15
R486:
    EmA16 + A15 > A16 + EmA15
    kdif*EmA16*A15
R487:
    EmM17 + M16 > M17 + EmM16
    kdif*EmM17*M16
R488:
    EmM17 + U16 > M17 + EmU16
    kdif*EmM17*U16
R489:
    EmM17 + A16 > M17 + EmA16
    kdif*EmM17*A16
R490:
    EmU17 + M16 > U17 + EmM16
    kdif*EmU17*M16
R491:
    EmU17 + U16 > U17 + EmU16
    kdif*EmU17*U16
R492:
    EmU17 + A16 > U17 + EmA16
    kdif*EmU17*A16
R493:
    EmA17 + M16 > A17 + EmM16
    kdif*EmA17*M16
R494:
    EmA17 + U16 > A17 + EmU16
    kdif*EmA17*U16
R495:
    EmA17 + A16 > A17 + EmA16
    kdif*EmA17*A16
R496:
    EmM18 + M17 > M18 + EmM17
    kdif*EmM18*M17
R497:
    EmM18 + U17 > M18 + EmU17
    kdif*EmM18*U17
R498:
    EmM18 + A17 > M18 + EmA17
    kdif*EmM18*A17
R499:
    EmU18 + M17 > U18 + EmM17
    kdif*EmU18*M17
R500:
    EmU18 + U17 > U18 + EmU17
    kdif*EmU18*U17
R501:
    EmU18 + A17 > U18 + EmA17
    kdif*EmU18*A17
R502:
    EmA18 + M17 > A18 + EmM17
    kdif*EmA18*M17
R503:
    EmA18 + U17 > A18 + EmU17
    kdif*EmA18*U17
R504:
    EmA18 + A17 > A18 + EmA17
    kdif*EmA18*A17
R505:
    EmM19 + M18 > M19 + EmM18
    kdif*EmM19*M18
R506:
    EmM19 + U18 > M19 + EmU18
    kdif*EmM19*U18
R507:
    EmM19 + A18 > M19 + EmA18
    kdif*EmM19*A18
R508:
    EmU19 + M18 > U19 + EmM18
    kdif*EmU19*M18
R509:
    EmU19 + U18 > U19 + EmU18
    kdif*EmU19*U18
R510:
    EmU19 + A18 > U19 + EmA18
    kdif*EmU19*A18
R511:
    EmA19 + M18 > A19 + EmM18
    kdif*EmA19*M18
R512:
    EmA19 + U18 > A19 + EmU18
    kdif*EmA19*U18
R513:
    EmA19 + A18 > A19 + EmA18
    kdif*EmA19*A18
R514:
    EmM20 + M19 > M20 + EmM19
    kdif*EmM20*M19
R515:
    EmM20 + U19 > M20 + EmU19
    kdif*EmM20*U19
R516:
    EmM20 + A19 > M20 + EmA19
    kdif*EmM20*A19
R517:
    EmU20 + M19 > U20 + EmM19
    kdif*EmU20*M19
R518:
    EmU20 + U19 > U20 + EmU19
    kdif*EmU20*U19
R519:
    EmU20 + A19 > U20 + EmA19
    kdif*EmU20*A19
R520:
    EmA20 + M19 > A20 + EmM19
    kdif*EmA20*M19
R521:
    EmA20 + U19 > A20 + EmU19
    kdif*EmA20*U19
R522:
    EmA20 + A19 > A20 + EmA19
    kdif*EmA20*A19
R523:
    M10 > EmM10
    kon*M10
R524:
    U10 > EmU10
    kon*U10
R525:
    A10 > EmA10
    kon*A10

# InitPar
knoise = 1.0
kenz = 5.0
kon = 1.0
koff = 0.1
kdif = 0.6

# InitVar
M1=0
EmM1=1
U1=0
EmU1=0
A1=0
EmA1=0
M2=1
EmM2=0
U2=0
EmU2=0
A2=0
EmA2=0
M3=1
EmM3=0
U3=0
EmU3=0
A3=0
EmA3=0
M4=0
EmM4=1
U4=0
EmU4=0
A4=0
EmA4=0
M5=0
EmM5=0
U5=0
EmU5=0
A5=0
EmA5=1
M6=1
EmM6=0
U6=0
EmU6=0
A6=0
EmA6=0
M7=0
EmM7=0
U7=0
EmU7=1
A7=0
EmA7=0
M8=0
EmM8=0
U8=0
EmU8=0
A8=0
EmA8=1
M9=0
EmM9=1
U9=0
EmU9=0
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
EmU11=0
A11=0
EmA11=1
M12=0
EmM12=1
U12=0
EmU12=0
A12=0
EmA12=0
M13=0
EmM13=0
U13=0
EmU13=0
A13=1
EmA13=0
M14=0
EmM14=0
U14=0
EmU14=0
A14=1
EmA14=0
M15=0
EmM15=0
U15=0
EmU15=0
A15=1
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
EmU17=1
A17=0
EmA17=0
M18=1
EmM18=0
U18=0
EmU18=0
A18=0
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
EmU20=0
A20=0
EmA20=1
"""
