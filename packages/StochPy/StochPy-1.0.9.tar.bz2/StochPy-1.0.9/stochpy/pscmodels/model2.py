model = """
R1:
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
    M2 > U2
    knoise*M2
R12:
    EmM2 > EmU2
    knoise*EmM2
R13:
    U2 > A2
    knoise*U2
R14:
    A2 > U2
    knoise*A2
R15:
    EmA2 > EmU2
    knoise*EmA2
R16:
    EmM2 > M2
    koff*EmM2
R17:
    EmU2 > U2
    koff*EmU2
R18:
    EmA2 > A2
    koff*EmA2
R19:
    EmU2 > EmM2
    kenz*EmU2
R20:
    M2 > EmM2
    krec*M2
R21:
    M3 > U3
    knoise*M3
R22:
    EmM3 > EmU3
    knoise*EmM3
R23:
    U3 > A3
    knoise*U3
R24:
    A3 > U3
    knoise*A3
R25:
    EmA3 > EmU3
    knoise*EmA3
R26:
    EmM3 > M3
    koff*EmM3
R27:
    EmU3 > U3
    koff*EmU3
R28:
    EmA3 > A3
    koff*EmA3
R29:
    EmU3 > EmM3
    kenz*EmU3
R30:
    M3 > EmM3
    krec*M3
R31:
    M4 > U4
    knoise*M4
R32:
    EmM4 > EmU4
    knoise*EmM4
R33:
    U4 > A4
    knoise*U4
R34:
    A4 > U4
    knoise*A4
R35:
    EmA4 > EmU4
    knoise*EmA4
R36:
    EmM4 > M4
    koff*EmM4
R37:
    EmU4 > U4
    koff*EmU4
R38:
    EmA4 > A4
    koff*EmA4
R39:
    EmU4 > EmM4
    kenz*EmU4
R40:
    M4 > EmM4
    krec*M4
R41:
    M5 > U5
    knoise*M5
R42:
    EmM5 > EmU5
    knoise*EmM5
R43:
    U5 > A5
    knoise*U5
R44:
    A5 > U5
    knoise*A5
R45:
    EmA5 > EmU5
    knoise*EmA5
R46:
    EmM5 > M5
    koff*EmM5
R47:
    EmU5 > U5
    koff*EmU5
R48:
    EmA5 > A5
    koff*EmA5
R49:
    EmU5 > EmM5
    kenz*EmU5
R50:
    M5 > EmM5
    krec*M5
R51:
    M6 > U6
    knoise*M6
R52:
    EmM6 > EmU6
    knoise*EmM6
R53:
    U6 > A6
    knoise*U6
R54:
    A6 > U6
    knoise*A6
R55:
    EmA6 > EmU6
    knoise*EmA6
R56:
    EmM6 > M6
    koff*EmM6
R57:
    EmU6 > U6
    koff*EmU6
R58:
    EmA6 > A6
    koff*EmA6
R59:
    EmU6 > EmM6
    kenz*EmU6
R60:
    M6 > EmM6
    krec*M6
R61:
    M7 > U7
    knoise*M7
R62:
    EmM7 > EmU7
    knoise*EmM7
R63:
    U7 > A7
    knoise*U7
R64:
    A7 > U7
    knoise*A7
R65:
    EmA7 > EmU7
    knoise*EmA7
R66:
    EmM7 > M7
    koff*EmM7
R67:
    EmU7 > U7
    koff*EmU7
R68:
    EmA7 > A7
    koff*EmA7
R69:
    EmU7 > EmM7
    kenz*EmU7
R70:
    M7 > EmM7
    krec*M7
R71:
    M8 > U8
    knoise*M8
R72:
    EmM8 > EmU8
    knoise*EmM8
R73:
    U8 > A8
    knoise*U8
R74:
    A8 > U8
    knoise*A8
R75:
    EmA8 > EmU8
    knoise*EmA8
R76:
    EmM8 > M8
    koff*EmM8
R77:
    EmU8 > U8
    koff*EmU8
R78:
    EmA8 > A8
    koff*EmA8
R79:
    EmU8 > EmM8
    kenz*EmU8
R80:
    M8 > EmM8
    krec*M8
R81:
    M9 > U9
    knoise*M9
R82:
    EmM9 > EmU9
    knoise*EmM9
R83:
    U9 > A9
    knoise*U9
R84:
    A9 > U9
    knoise*A9
R85:
    EmA9 > EmU9
    knoise*EmA9
R86:
    EmM9 > M9
    koff*EmM9
R87:
    EmU9 > U9
    koff*EmU9
R88:
    EmA9 > A9
    koff*EmA9
R89:
    EmU9 > EmM9
    kenz*EmU9
R90:
    M9 > EmM9
    krec*M9
R91:
    M10 > U10
    knoise*M10
R92:
    EmM10 > EmU10
    knoise*EmM10
R93:
    U10 > A10
    knoise*U10
R94:
    A10 > U10
    knoise*A10
R95:
    EmA10 > EmU10
    knoise*EmA10
R96:
    EmM10 > M10
    koff*EmM10
R97:
    EmU10 > U10
    koff*EmU10
R98:
    EmA10 > A10
    koff*EmA10
R99:
    EmU10 > EmM10
    kenz*EmU10
R100:
    M10 > EmM10
    krec*M10
R101:
    M11 > U11
    knoise*M11
R102:
    EmM11 > EmU11
    knoise*EmM11
R103:
    U11 > A11
    knoise*U11
R104:
    A11 > U11
    knoise*A11
R105:
    EmA11 > EmU11
    knoise*EmA11
R106:
    EmM11 > M11
    koff*EmM11
R107:
    EmU11 > U11
    koff*EmU11
R108:
    EmA11 > A11
    koff*EmA11
R109:
    EmU11 > EmM11
    kenz*EmU11
R110:
    M11 > EmM11
    krec*M11
R111:
    M12 > U12
    knoise*M12
R112:
    EmM12 > EmU12
    knoise*EmM12
R113:
    U12 > A12
    knoise*U12
R114:
    A12 > U12
    knoise*A12
R115:
    EmA12 > EmU12
    knoise*EmA12
R116:
    EmM12 > M12
    koff*EmM12
R117:
    EmU12 > U12
    koff*EmU12
R118:
    EmA12 > A12
    koff*EmA12
R119:
    EmU12 > EmM12
    kenz*EmU12
R120:
    M12 > EmM12
    krec*M12
R121:
    M13 > U13
    knoise*M13
R122:
    EmM13 > EmU13
    knoise*EmM13
R123:
    U13 > A13
    knoise*U13
R124:
    A13 > U13
    knoise*A13
R125:
    EmA13 > EmU13
    knoise*EmA13
R126:
    EmM13 > M13
    koff*EmM13
R127:
    EmU13 > U13
    koff*EmU13
R128:
    EmA13 > A13
    koff*EmA13
R129:
    EmU13 > EmM13
    kenz*EmU13
R130:
    M13 > EmM13
    krec*M13
R131:
    M14 > U14
    knoise*M14
R132:
    EmM14 > EmU14
    knoise*EmM14
R133:
    U14 > A14
    knoise*U14
R134:
    A14 > U14
    knoise*A14
R135:
    EmA14 > EmU14
    knoise*EmA14
R136:
    EmM14 > M14
    koff*EmM14
R137:
    EmU14 > U14
    koff*EmU14
R138:
    EmA14 > A14
    koff*EmA14
R139:
    EmU14 > EmM14
    kenz*EmU14
R140:
    M14 > EmM14
    krec*M14
R141:
    M15 > U15
    knoise*M15
R142:
    EmM15 > EmU15
    knoise*EmM15
R143:
    U15 > A15
    knoise*U15
R144:
    A15 > U15
    knoise*A15
R145:
    EmA15 > EmU15
    knoise*EmA15
R146:
    EmM15 > M15
    koff*EmM15
R147:
    EmU15 > U15
    koff*EmU15
R148:
    EmA15 > A15
    koff*EmA15
R149:
    EmU15 > EmM15
    kenz*EmU15
R150:
    M15 > EmM15
    krec*M15
R151:
    M16 > U16
    knoise*M16
R152:
    EmM16 > EmU16
    knoise*EmM16
R153:
    U16 > A16
    knoise*U16
R154:
    A16 > U16
    knoise*A16
R155:
    EmA16 > EmU16
    knoise*EmA16
R156:
    EmM16 > M16
    koff*EmM16
R157:
    EmU16 > U16
    koff*EmU16
R158:
    EmA16 > A16
    koff*EmA16
R159:
    EmU16 > EmM16
    kenz*EmU16
R160:
    M16 > EmM16
    krec*M16
R161:
    M17 > U17
    knoise*M17
R162:
    EmM17 > EmU17
    knoise*EmM17
R163:
    U17 > A17
    knoise*U17
R164:
    A17 > U17
    knoise*A17
R165:
    EmA17 > EmU17
    knoise*EmA17
R166:
    EmM17 > M17
    koff*EmM17
R167:
    EmU17 > U17
    koff*EmU17
R168:
    EmA17 > A17
    koff*EmA17
R169:
    EmU17 > EmM17
    kenz*EmU17
R170:
    M17 > EmM17
    krec*M17
R171:
    M18 > U18
    knoise*M18
R172:
    EmM18 > EmU18
    knoise*EmM18
R173:
    U18 > A18
    knoise*U18
R174:
    A18 > U18
    knoise*A18
R175:
    EmA18 > EmU18
    knoise*EmA18
R176:
    EmM18 > M18
    koff*EmM18
R177:
    EmU18 > U18
    koff*EmU18
R178:
    EmA18 > A18
    koff*EmA18
R179:
    EmU18 > EmM18
    kenz*EmU18
R180:
    M18 > EmM18
    krec*M18
R181:
    M19 > U19
    knoise*M19
R182:
    EmM19 > EmU19
    knoise*EmM19
R183:
    U19 > A19
    knoise*U19
R184:
    A19 > U19
    knoise*A19
R185:
    EmA19 > EmU19
    knoise*EmA19
R186:
    EmM19 > M19
    koff*EmM19
R187:
    EmU19 > U19
    koff*EmU19
R188:
    EmA19 > A19
    koff*EmA19
R189:
    EmU19 > EmM19
    kenz*EmU19
R190:
    M19 > EmM19
    krec*M19
R191:
    M20 > U20
    knoise*M20
R192:
    EmM20 > EmU20
    knoise*EmM20
R193:
    U20 > A20
    knoise*U20
R194:
    A20 > U20
    knoise*A20
R195:
    EmA20 > EmU20
    knoise*EmA20
R196:
    EmM20 > M20
    koff*EmM20
R197:
    EmU20 > U20
    koff*EmU20
R198:
    EmA20 > A20
    koff*EmA20
R199:
    EmU20 > EmM20
    kenz*EmU20
R200:
    M20 > EmM20
    krec*M20
R201:
    EmM1 + M2 > M1 + EmM2
    kdif*EmM1*M2
R202:
    EmM1 + U2 > M1 + EmU2
    kdif*EmM1*U2
R203:
    EmM1 + A2 > M1 + EmA2
    kdif*EmM1*A2
R204:
    EmU1 + M2 > U1 + EmM2
    kdif*EmU1*M2
R205:
    EmU1 + U2 > U1 + EmU2
    kdif*EmU1*U2
R206:
    EmU1 + A2 > U1 + EmA2
    kdif*EmU1*A2
R207:
    EmA1 + M2 > A1 + EmM2
    kdif*EmA1*M2
R208:
    EmA1 + U2 > A1 + EmU2
    kdif*EmA1*U2
R209:
    EmA1 + A2 > A1 + EmA2
    kdif*EmA1*A2
R210:
    EmM2 + M3 > M2 + EmM3
    kdif*EmM2*M3
R211:
    EmM2 + U3 > M2 + EmU3
    kdif*EmM2*U3
R212:
    EmM2 + A3 > M2 + EmA3
    kdif*EmM2*A3
R213:
    EmU2 + M3 > U2 + EmM3
    kdif*EmU2*M3
R214:
    EmU2 + U3 > U2 + EmU3
    kdif*EmU2*U3
R215:
    EmU2 + A3 > U2 + EmA3
    kdif*EmU2*A3
R216:
    EmA2 + M3 > A2 + EmM3
    kdif*EmA2*M3
R217:
    EmA2 + U3 > A2 + EmU3
    kdif*EmA2*U3
R218:
    EmA2 + A3 > A2 + EmA3
    kdif*EmA2*A3
R219:
    EmM3 + M4 > M3 + EmM4
    kdif*EmM3*M4
R220:
    EmM3 + U4 > M3 + EmU4
    kdif*EmM3*U4
R221:
    EmM3 + A4 > M3 + EmA4
    kdif*EmM3*A4
R222:
    EmU3 + M4 > U3 + EmM4
    kdif*EmU3*M4
R223:
    EmU3 + U4 > U3 + EmU4
    kdif*EmU3*U4
R224:
    EmU3 + A4 > U3 + EmA4
    kdif*EmU3*A4
R225:
    EmA3 + M4 > A3 + EmM4
    kdif*EmA3*M4
R226:
    EmA3 + U4 > A3 + EmU4
    kdif*EmA3*U4
R227:
    EmA3 + A4 > A3 + EmA4
    kdif*EmA3*A4
R228:
    EmM4 + M5 > M4 + EmM5
    kdif*EmM4*M5
R229:
    EmM4 + U5 > M4 + EmU5
    kdif*EmM4*U5
R230:
    EmM4 + A5 > M4 + EmA5
    kdif*EmM4*A5
R231:
    EmU4 + M5 > U4 + EmM5
    kdif*EmU4*M5
R232:
    EmU4 + U5 > U4 + EmU5
    kdif*EmU4*U5
R233:
    EmU4 + A5 > U4 + EmA5
    kdif*EmU4*A5
R234:
    EmA4 + M5 > A4 + EmM5
    kdif*EmA4*M5
R235:
    EmA4 + U5 > A4 + EmU5
    kdif*EmA4*U5
R236:
    EmA4 + A5 > A4 + EmA5
    kdif*EmA4*A5
R237:
    EmM5 + M6 > M5 + EmM6
    kdif*EmM5*M6
R238:
    EmM5 + U6 > M5 + EmU6
    kdif*EmM5*U6
R239:
    EmM5 + A6 > M5 + EmA6
    kdif*EmM5*A6
R240:
    EmU5 + M6 > U5 + EmM6
    kdif*EmU5*M6
R241:
    EmU5 + U6 > U5 + EmU6
    kdif*EmU5*U6
R242:
    EmU5 + A6 > U5 + EmA6
    kdif*EmU5*A6
R243:
    EmA5 + M6 > A5 + EmM6
    kdif*EmA5*M6
R244:
    EmA5 + U6 > A5 + EmU6
    kdif*EmA5*U6
R245:
    EmA5 + A6 > A5 + EmA6
    kdif*EmA5*A6
R246:
    EmM6 + M7 > M6 + EmM7
    kdif*EmM6*M7
R247:
    EmM6 + U7 > M6 + EmU7
    kdif*EmM6*U7
R248:
    EmM6 + A7 > M6 + EmA7
    kdif*EmM6*A7
R249:
    EmU6 + M7 > U6 + EmM7
    kdif*EmU6*M7
R250:
    EmU6 + U7 > U6 + EmU7
    kdif*EmU6*U7
R251:
    EmU6 + A7 > U6 + EmA7
    kdif*EmU6*A7
R252:
    EmA6 + M7 > A6 + EmM7
    kdif*EmA6*M7
R253:
    EmA6 + U7 > A6 + EmU7
    kdif*EmA6*U7
R254:
    EmA6 + A7 > A6 + EmA7
    kdif*EmA6*A7
R255:
    EmM7 + M8 > M7 + EmM8
    kdif*EmM7*M8
R256:
    EmM7 + U8 > M7 + EmU8
    kdif*EmM7*U8
R257:
    EmM7 + A8 > M7 + EmA8
    kdif*EmM7*A8
R258:
    EmU7 + M8 > U7 + EmM8
    kdif*EmU7*M8
R259:
    EmU7 + U8 > U7 + EmU8
    kdif*EmU7*U8
R260:
    EmU7 + A8 > U7 + EmA8
    kdif*EmU7*A8
R261:
    EmA7 + M8 > A7 + EmM8
    kdif*EmA7*M8
R262:
    EmA7 + U8 > A7 + EmU8
    kdif*EmA7*U8
R263:
    EmA7 + A8 > A7 + EmA8
    kdif*EmA7*A8
R264:
    EmM8 + M9 > M8 + EmM9
    kdif*EmM8*M9
R265:
    EmM8 + U9 > M8 + EmU9
    kdif*EmM8*U9
R266:
    EmM8 + A9 > M8 + EmA9
    kdif*EmM8*A9
R267:
    EmU8 + M9 > U8 + EmM9
    kdif*EmU8*M9
R268:
    EmU8 + U9 > U8 + EmU9
    kdif*EmU8*U9
R269:
    EmU8 + A9 > U8 + EmA9
    kdif*EmU8*A9
R270:
    EmA8 + M9 > A8 + EmM9
    kdif*EmA8*M9
R271:
    EmA8 + U9 > A8 + EmU9
    kdif*EmA8*U9
R272:
    EmA8 + A9 > A8 + EmA9
    kdif*EmA8*A9
R273:
    EmM9 + M10 > M9 + EmM10
    kdif*EmM9*M10
R274:
    EmM9 + U10 > M9 + EmU10
    kdif*EmM9*U10
R275:
    EmM9 + A10 > M9 + EmA10
    kdif*EmM9*A10
R276:
    EmU9 + M10 > U9 + EmM10
    kdif*EmU9*M10
R277:
    EmU9 + U10 > U9 + EmU10
    kdif*EmU9*U10
R278:
    EmU9 + A10 > U9 + EmA10
    kdif*EmU9*A10
R279:
    EmA9 + M10 > A9 + EmM10
    kdif*EmA9*M10
R280:
    EmA9 + U10 > A9 + EmU10
    kdif*EmA9*U10
R281:
    EmA9 + A10 > A9 + EmA10
    kdif*EmA9*A10
R282:
    EmM10 + M11 > M10 + EmM11
    kdif*EmM10*M11
R283:
    EmM10 + U11 > M10 + EmU11
    kdif*EmM10*U11
R284:
    EmM10 + A11 > M10 + EmA11
    kdif*EmM10*A11
R285:
    EmU10 + M11 > U10 + EmM11
    kdif*EmU10*M11
R286:
    EmU10 + U11 > U10 + EmU11
    kdif*EmU10*U11
R287:
    EmU10 + A11 > U10 + EmA11
    kdif*EmU10*A11
R288:
    EmA10 + M11 > A10 + EmM11
    kdif*EmA10*M11
R289:
    EmA10 + U11 > A10 + EmU11
    kdif*EmA10*U11
R290:
    EmA10 + A11 > A10 + EmA11
    kdif*EmA10*A11
R291:
    EmM11 + M12 > M11 + EmM12
    kdif*EmM11*M12
R292:
    EmM11 + U12 > M11 + EmU12
    kdif*EmM11*U12
R293:
    EmM11 + A12 > M11 + EmA12
    kdif*EmM11*A12
R294:
    EmU11 + M12 > U11 + EmM12
    kdif*EmU11*M12
R295:
    EmU11 + U12 > U11 + EmU12
    kdif*EmU11*U12
R296:
    EmU11 + A12 > U11 + EmA12
    kdif*EmU11*A12
R297:
    EmA11 + M12 > A11 + EmM12
    kdif*EmA11*M12
R298:
    EmA11 + U12 > A11 + EmU12
    kdif*EmA11*U12
R299:
    EmA11 + A12 > A11 + EmA12
    kdif*EmA11*A12
R300:
    EmM12 + M13 > M12 + EmM13
    kdif*EmM12*M13
R301:
    EmM12 + U13 > M12 + EmU13
    kdif*EmM12*U13
R302:
    EmM12 + A13 > M12 + EmA13
    kdif*EmM12*A13
R303:
    EmU12 + M13 > U12 + EmM13
    kdif*EmU12*M13
R304:
    EmU12 + U13 > U12 + EmU13
    kdif*EmU12*U13
R305:
    EmU12 + A13 > U12 + EmA13
    kdif*EmU12*A13
R306:
    EmA12 + M13 > A12 + EmM13
    kdif*EmA12*M13
R307:
    EmA12 + U13 > A12 + EmU13
    kdif*EmA12*U13
R308:
    EmA12 + A13 > A12 + EmA13
    kdif*EmA12*A13
R309:
    EmM13 + M14 > M13 + EmM14
    kdif*EmM13*M14
R310:
    EmM13 + U14 > M13 + EmU14
    kdif*EmM13*U14
R311:
    EmM13 + A14 > M13 + EmA14
    kdif*EmM13*A14
R312:
    EmU13 + M14 > U13 + EmM14
    kdif*EmU13*M14
R313:
    EmU13 + U14 > U13 + EmU14
    kdif*EmU13*U14
R314:
    EmU13 + A14 > U13 + EmA14
    kdif*EmU13*A14
R315:
    EmA13 + M14 > A13 + EmM14
    kdif*EmA13*M14
R316:
    EmA13 + U14 > A13 + EmU14
    kdif*EmA13*U14
R317:
    EmA13 + A14 > A13 + EmA14
    kdif*EmA13*A14
R318:
    EmM14 + M15 > M14 + EmM15
    kdif*EmM14*M15
R319:
    EmM14 + U15 > M14 + EmU15
    kdif*EmM14*U15
R320:
    EmM14 + A15 > M14 + EmA15
    kdif*EmM14*A15
R321:
    EmU14 + M15 > U14 + EmM15
    kdif*EmU14*M15
R322:
    EmU14 + U15 > U14 + EmU15
    kdif*EmU14*U15
R323:
    EmU14 + A15 > U14 + EmA15
    kdif*EmU14*A15
R324:
    EmA14 + M15 > A14 + EmM15
    kdif*EmA14*M15
R325:
    EmA14 + U15 > A14 + EmU15
    kdif*EmA14*U15
R326:
    EmA14 + A15 > A14 + EmA15
    kdif*EmA14*A15
R327:
    EmM15 + M16 > M15 + EmM16
    kdif*EmM15*M16
R328:
    EmM15 + U16 > M15 + EmU16
    kdif*EmM15*U16
R329:
    EmM15 + A16 > M15 + EmA16
    kdif*EmM15*A16
R330:
    EmU15 + M16 > U15 + EmM16
    kdif*EmU15*M16
R331:
    EmU15 + U16 > U15 + EmU16
    kdif*EmU15*U16
R332:
    EmU15 + A16 > U15 + EmA16
    kdif*EmU15*A16
R333:
    EmA15 + M16 > A15 + EmM16
    kdif*EmA15*M16
R334:
    EmA15 + U16 > A15 + EmU16
    kdif*EmA15*U16
R335:
    EmA15 + A16 > A15 + EmA16
    kdif*EmA15*A16
R336:
    EmM16 + M17 > M16 + EmM17
    kdif*EmM16*M17
R337:
    EmM16 + U17 > M16 + EmU17
    kdif*EmM16*U17
R338:
    EmM16 + A17 > M16 + EmA17
    kdif*EmM16*A17
R339:
    EmU16 + M17 > U16 + EmM17
    kdif*EmU16*M17
R340:
    EmU16 + U17 > U16 + EmU17
    kdif*EmU16*U17
R341:
    EmU16 + A17 > U16 + EmA17
    kdif*EmU16*A17
R342:
    EmA16 + M17 > A16 + EmM17
    kdif*EmA16*M17
R343:
    EmA16 + U17 > A16 + EmU17
    kdif*EmA16*U17
R344:
    EmA16 + A17 > A16 + EmA17
    kdif*EmA16*A17
R345:
    EmM17 + M18 > M17 + EmM18
    kdif*EmM17*M18
R346:
    EmM17 + U18 > M17 + EmU18
    kdif*EmM17*U18
R347:
    EmM17 + A18 > M17 + EmA18
    kdif*EmM17*A18
R348:
    EmU17 + M18 > U17 + EmM18
    kdif*EmU17*M18
R349:
    EmU17 + U18 > U17 + EmU18
    kdif*EmU17*U18
R350:
    EmU17 + A18 > U17 + EmA18
    kdif*EmU17*A18
R351:
    EmA17 + M18 > A17 + EmM18
    kdif*EmA17*M18
R352:
    EmA17 + U18 > A17 + EmU18
    kdif*EmA17*U18
R353:
    EmA17 + A18 > A17 + EmA18
    kdif*EmA17*A18
R354:
    EmM18 + M19 > M18 + EmM19
    kdif*EmM18*M19
R355:
    EmM18 + U19 > M18 + EmU19
    kdif*EmM18*U19
R356:
    EmM18 + A19 > M18 + EmA19
    kdif*EmM18*A19
R357:
    EmU18 + M19 > U18 + EmM19
    kdif*EmU18*M19
R358:
    EmU18 + U19 > U18 + EmU19
    kdif*EmU18*U19
R359:
    EmU18 + A19 > U18 + EmA19
    kdif*EmU18*A19
R360:
    EmA18 + M19 > A18 + EmM19
    kdif*EmA18*M19
R361:
    EmA18 + U19 > A18 + EmU19
    kdif*EmA18*U19
R362:
    EmA18 + A19 > A18 + EmA19
    kdif*EmA18*A19
R363:
    EmM19 + M20 > M19 + EmM20
    kdif*EmM19*M20
R364:
    EmM19 + U20 > M19 + EmU20
    kdif*EmM19*U20
R365:
    EmM19 + A20 > M19 + EmA20
    kdif*EmM19*A20
R366:
    EmU19 + M20 > U19 + EmM20
    kdif*EmU19*M20
R367:
    EmU19 + U20 > U19 + EmU20
    kdif*EmU19*U20
R368:
    EmU19 + A20 > U19 + EmA20
    kdif*EmU19*A20
R369:
    EmA19 + M20 > A19 + EmM20
    kdif*EmA19*M20
R370:
    EmA19 + U20 > A19 + EmU20
    kdif*EmA19*U20
R371:
    EmA19 + A20 > A19 + EmA20
    kdif*EmA19*A20
R372:
    EmM2 + M1 > M2 + EmM1
    kdif*EmM2*M1
R373:
    EmM2 + U1 > M2 + EmU1
    kdif*EmM2*U1
R374:
    EmM2 + A1 > M2 + EmA1
    kdif*EmM2*A1
R375:
    EmU2 + M1 > U2 + EmM1
    kdif*EmU2*M1
R376:
    EmU2 + U1 > U2 + EmU1
    kdif*EmU2*U1
R377:
    EmU2 + A1 > U2 + EmA1
    kdif*EmU2*A1
R378:
    EmA2 + M1 > A2 + EmM1
    kdif*EmA2*M1
R379:
    EmA2 + U1 > A2 + EmU1
    kdif*EmA2*U1
R380:
    EmA2 + A1 > A2 + EmA1
    kdif*EmA2*A1
R381:
    EmM3 + M2 > M3 + EmM2
    kdif*EmM3*M2
R382:
    EmM3 + U2 > M3 + EmU2
    kdif*EmM3*U2
R383:
    EmM3 + A2 > M3 + EmA2
    kdif*EmM3*A2
R384:
    EmU3 + M2 > U3 + EmM2
    kdif*EmU3*M2
R385:
    EmU3 + U2 > U3 + EmU2
    kdif*EmU3*U2
R386:
    EmU3 + A2 > U3 + EmA2
    kdif*EmU3*A2
R387:
    EmA3 + M2 > A3 + EmM2
    kdif*EmA3*M2
R388:
    EmA3 + U2 > A3 + EmU2
    kdif*EmA3*U2
R389:
    EmA3 + A2 > A3 + EmA2
    kdif*EmA3*A2
R390:
    EmM4 + M3 > M4 + EmM3
    kdif*EmM4*M3
R391:
    EmM4 + U3 > M4 + EmU3
    kdif*EmM4*U3
R392:
    EmM4 + A3 > M4 + EmA3
    kdif*EmM4*A3
R393:
    EmU4 + M3 > U4 + EmM3
    kdif*EmU4*M3
R394:
    EmU4 + U3 > U4 + EmU3
    kdif*EmU4*U3
R395:
    EmU4 + A3 > U4 + EmA3
    kdif*EmU4*A3
R396:
    EmA4 + M3 > A4 + EmM3
    kdif*EmA4*M3
R397:
    EmA4 + U3 > A4 + EmU3
    kdif*EmA4*U3
R398:
    EmA4 + A3 > A4 + EmA3
    kdif*EmA4*A3
R399:
    EmM5 + M4 > M5 + EmM4
    kdif*EmM5*M4
R400:
    EmM5 + U4 > M5 + EmU4
    kdif*EmM5*U4
R401:
    EmM5 + A4 > M5 + EmA4
    kdif*EmM5*A4
R402:
    EmU5 + M4 > U5 + EmM4
    kdif*EmU5*M4
R403:
    EmU5 + U4 > U5 + EmU4
    kdif*EmU5*U4
R404:
    EmU5 + A4 > U5 + EmA4
    kdif*EmU5*A4
R405:
    EmA5 + M4 > A5 + EmM4
    kdif*EmA5*M4
R406:
    EmA5 + U4 > A5 + EmU4
    kdif*EmA5*U4
R407:
    EmA5 + A4 > A5 + EmA4
    kdif*EmA5*A4
R408:
    EmM6 + M5 > M6 + EmM5
    kdif*EmM6*M5
R409:
    EmM6 + U5 > M6 + EmU5
    kdif*EmM6*U5
R410:
    EmM6 + A5 > M6 + EmA5
    kdif*EmM6*A5
R411:
    EmU6 + M5 > U6 + EmM5
    kdif*EmU6*M5
R412:
    EmU6 + U5 > U6 + EmU5
    kdif*EmU6*U5
R413:
    EmU6 + A5 > U6 + EmA5
    kdif*EmU6*A5
R414:
    EmA6 + M5 > A6 + EmM5
    kdif*EmA6*M5
R415:
    EmA6 + U5 > A6 + EmU5
    kdif*EmA6*U5
R416:
    EmA6 + A5 > A6 + EmA5
    kdif*EmA6*A5
R417:
    EmM7 + M6 > M7 + EmM6
    kdif*EmM7*M6
R418:
    EmM7 + U6 > M7 + EmU6
    kdif*EmM7*U6
R419:
    EmM7 + A6 > M7 + EmA6
    kdif*EmM7*A6
R420:
    EmU7 + M6 > U7 + EmM6
    kdif*EmU7*M6
R421:
    EmU7 + U6 > U7 + EmU6
    kdif*EmU7*U6
R422:
    EmU7 + A6 > U7 + EmA6
    kdif*EmU7*A6
R423:
    EmA7 + M6 > A7 + EmM6
    kdif*EmA7*M6
R424:
    EmA7 + U6 > A7 + EmU6
    kdif*EmA7*U6
R425:
    EmA7 + A6 > A7 + EmA6
    kdif*EmA7*A6
R426:
    EmM8 + M7 > M8 + EmM7
    kdif*EmM8*M7
R427:
    EmM8 + U7 > M8 + EmU7
    kdif*EmM8*U7
R428:
    EmM8 + A7 > M8 + EmA7
    kdif*EmM8*A7
R429:
    EmU8 + M7 > U8 + EmM7
    kdif*EmU8*M7
R430:
    EmU8 + U7 > U8 + EmU7
    kdif*EmU8*U7
R431:
    EmU8 + A7 > U8 + EmA7
    kdif*EmU8*A7
R432:
    EmA8 + M7 > A8 + EmM7
    kdif*EmA8*M7
R433:
    EmA8 + U7 > A8 + EmU7
    kdif*EmA8*U7
R434:
    EmA8 + A7 > A8 + EmA7
    kdif*EmA8*A7
R435:
    EmM9 + M8 > M9 + EmM8
    kdif*EmM9*M8
R436:
    EmM9 + U8 > M9 + EmU8
    kdif*EmM9*U8
R437:
    EmM9 + A8 > M9 + EmA8
    kdif*EmM9*A8
R438:
    EmU9 + M8 > U9 + EmM8
    kdif*EmU9*M8
R439:
    EmU9 + U8 > U9 + EmU8
    kdif*EmU9*U8
R440:
    EmU9 + A8 > U9 + EmA8
    kdif*EmU9*A8
R441:
    EmA9 + M8 > A9 + EmM8
    kdif*EmA9*M8
R442:
    EmA9 + U8 > A9 + EmU8
    kdif*EmA9*U8
R443:
    EmA9 + A8 > A9 + EmA8
    kdif*EmA9*A8
R444:
    EmM10 + M9 > M10 + EmM9
    kdif*EmM10*M9
R445:
    EmM10 + U9 > M10 + EmU9
    kdif*EmM10*U9
R446:
    EmM10 + A9 > M10 + EmA9
    kdif*EmM10*A9
R447:
    EmU10 + M9 > U10 + EmM9
    kdif*EmU10*M9
R448:
    EmU10 + U9 > U10 + EmU9
    kdif*EmU10*U9
R449:
    EmU10 + A9 > U10 + EmA9
    kdif*EmU10*A9
R450:
    EmA10 + M9 > A10 + EmM9
    kdif*EmA10*M9
R451:
    EmA10 + U9 > A10 + EmU9
    kdif*EmA10*U9
R452:
    EmA10 + A9 > A10 + EmA9
    kdif*EmA10*A9
R453:
    EmM11 + M10 > M11 + EmM10
    kdif*EmM11*M10
R454:
    EmM11 + U10 > M11 + EmU10
    kdif*EmM11*U10
R455:
    EmM11 + A10 > M11 + EmA10
    kdif*EmM11*A10
R456:
    EmU11 + M10 > U11 + EmM10
    kdif*EmU11*M10
R457:
    EmU11 + U10 > U11 + EmU10
    kdif*EmU11*U10
R458:
    EmU11 + A10 > U11 + EmA10
    kdif*EmU11*A10
R459:
    EmA11 + M10 > A11 + EmM10
    kdif*EmA11*M10
R460:
    EmA11 + U10 > A11 + EmU10
    kdif*EmA11*U10
R461:
    EmA11 + A10 > A11 + EmA10
    kdif*EmA11*A10
R462:
    EmM12 + M11 > M12 + EmM11
    kdif*EmM12*M11
R463:
    EmM12 + U11 > M12 + EmU11
    kdif*EmM12*U11
R464:
    EmM12 + A11 > M12 + EmA11
    kdif*EmM12*A11
R465:
    EmU12 + M11 > U12 + EmM11
    kdif*EmU12*M11
R466:
    EmU12 + U11 > U12 + EmU11
    kdif*EmU12*U11
R467:
    EmU12 + A11 > U12 + EmA11
    kdif*EmU12*A11
R468:
    EmA12 + M11 > A12 + EmM11
    kdif*EmA12*M11
R469:
    EmA12 + U11 > A12 + EmU11
    kdif*EmA12*U11
R470:
    EmA12 + A11 > A12 + EmA11
    kdif*EmA12*A11
R471:
    EmM13 + M12 > M13 + EmM12
    kdif*EmM13*M12
R472:
    EmM13 + U12 > M13 + EmU12
    kdif*EmM13*U12
R473:
    EmM13 + A12 > M13 + EmA12
    kdif*EmM13*A12
R474:
    EmU13 + M12 > U13 + EmM12
    kdif*EmU13*M12
R475:
    EmU13 + U12 > U13 + EmU12
    kdif*EmU13*U12
R476:
    EmU13 + A12 > U13 + EmA12
    kdif*EmU13*A12
R477:
    EmA13 + M12 > A13 + EmM12
    kdif*EmA13*M12
R478:
    EmA13 + U12 > A13 + EmU12
    kdif*EmA13*U12
R479:
    EmA13 + A12 > A13 + EmA12
    kdif*EmA13*A12
R480:
    EmM14 + M13 > M14 + EmM13
    kdif*EmM14*M13
R481:
    EmM14 + U13 > M14 + EmU13
    kdif*EmM14*U13
R482:
    EmM14 + A13 > M14 + EmA13
    kdif*EmM14*A13
R483:
    EmU14 + M13 > U14 + EmM13
    kdif*EmU14*M13
R484:
    EmU14 + U13 > U14 + EmU13
    kdif*EmU14*U13
R485:
    EmU14 + A13 > U14 + EmA13
    kdif*EmU14*A13
R486:
    EmA14 + M13 > A14 + EmM13
    kdif*EmA14*M13
R487:
    EmA14 + U13 > A14 + EmU13
    kdif*EmA14*U13
R488:
    EmA14 + A13 > A14 + EmA13
    kdif*EmA14*A13
R489:
    EmM15 + M14 > M15 + EmM14
    kdif*EmM15*M14
R490:
    EmM15 + U14 > M15 + EmU14
    kdif*EmM15*U14
R491:
    EmM15 + A14 > M15 + EmA14
    kdif*EmM15*A14
R492:
    EmU15 + M14 > U15 + EmM14
    kdif*EmU15*M14
R493:
    EmU15 + U14 > U15 + EmU14
    kdif*EmU15*U14
R494:
    EmU15 + A14 > U15 + EmA14
    kdif*EmU15*A14
R495:
    EmA15 + M14 > A15 + EmM14
    kdif*EmA15*M14
R496:
    EmA15 + U14 > A15 + EmU14
    kdif*EmA15*U14
R497:
    EmA15 + A14 > A15 + EmA14
    kdif*EmA15*A14
R498:
    EmM16 + M15 > M16 + EmM15
    kdif*EmM16*M15
R499:
    EmM16 + U15 > M16 + EmU15
    kdif*EmM16*U15
R500:
    EmM16 + A15 > M16 + EmA15
    kdif*EmM16*A15
R501:
    EmU16 + M15 > U16 + EmM15
    kdif*EmU16*M15
R502:
    EmU16 + U15 > U16 + EmU15
    kdif*EmU16*U15
R503:
    EmU16 + A15 > U16 + EmA15
    kdif*EmU16*A15
R504:
    EmA16 + M15 > A16 + EmM15
    kdif*EmA16*M15
R505:
    EmA16 + U15 > A16 + EmU15
    kdif*EmA16*U15
R506:
    EmA16 + A15 > A16 + EmA15
    kdif*EmA16*A15
R507:
    EmM17 + M16 > M17 + EmM16
    kdif*EmM17*M16
R508:
    EmM17 + U16 > M17 + EmU16
    kdif*EmM17*U16
R509:
    EmM17 + A16 > M17 + EmA16
    kdif*EmM17*A16
R510:
    EmU17 + M16 > U17 + EmM16
    kdif*EmU17*M16
R511:
    EmU17 + U16 > U17 + EmU16
    kdif*EmU17*U16
R512:
    EmU17 + A16 > U17 + EmA16
    kdif*EmU17*A16
R513:
    EmA17 + M16 > A17 + EmM16
    kdif*EmA17*M16
R514:
    EmA17 + U16 > A17 + EmU16
    kdif*EmA17*U16
R515:
    EmA17 + A16 > A17 + EmA16
    kdif*EmA17*A16
R516:
    EmM18 + M17 > M18 + EmM17
    kdif*EmM18*M17
R517:
    EmM18 + U17 > M18 + EmU17
    kdif*EmM18*U17
R518:
    EmM18 + A17 > M18 + EmA17
    kdif*EmM18*A17
R519:
    EmU18 + M17 > U18 + EmM17
    kdif*EmU18*M17
R520:
    EmU18 + U17 > U18 + EmU17
    kdif*EmU18*U17
R521:
    EmU18 + A17 > U18 + EmA17
    kdif*EmU18*A17
R522:
    EmA18 + M17 > A18 + EmM17
    kdif*EmA18*M17
R523:
    EmA18 + U17 > A18 + EmU17
    kdif*EmA18*U17
R524:
    EmA18 + A17 > A18 + EmA17
    kdif*EmA18*A17
R525:
    EmM19 + M18 > M19 + EmM18
    kdif*EmM19*M18
R526:
    EmM19 + U18 > M19 + EmU18
    kdif*EmM19*U18
R527:
    EmM19 + A18 > M19 + EmA18
    kdif*EmM19*A18
R528:
    EmU19 + M18 > U19 + EmM18
    kdif*EmU19*M18
R529:
    EmU19 + U18 > U19 + EmU18
    kdif*EmU19*U18
R530:
    EmU19 + A18 > U19 + EmA18
    kdif*EmU19*A18
R531:
    EmA19 + M18 > A19 + EmM18
    kdif*EmA19*M18
R532:
    EmA19 + U18 > A19 + EmU18
    kdif*EmA19*U18
R533:
    EmA19 + A18 > A19 + EmA18
    kdif*EmA19*A18
R534:
    EmM20 + M19 > M20 + EmM19
    kdif*EmM20*M19
R535:
    EmM20 + U19 > M20 + EmU19
    kdif*EmM20*U19
R536:
    EmM20 + A19 > M20 + EmA19
    kdif*EmM20*A19
R537:
    EmU20 + M19 > U20 + EmM19
    kdif*EmU20*M19
R538:
    EmU20 + U19 > U20 + EmU19
    kdif*EmU20*U19
R539:
    EmU20 + A19 > U20 + EmA19
    kdif*EmU20*A19
R540:
    EmA20 + M19 > A20 + EmM19
    kdif*EmA20*M19
R541:
    EmA20 + U19 > A20 + EmU19
    kdif*EmA20*U19
R542:
    EmA20 + A19 > A20 + EmA19
    kdif*EmA20*A19
R543:
    M10 > EmM10
    kon*M10
R544:
    U10 > EmU10
    kon*U10
R545:
    A10 > EmA10
    kon*A10

# InitPar
knoise = 1.0
kenz = 5.0
kon = 1.0
koff = 0.1
kdif = 0.6
krec = 0.1

# InitVar
M1=1
EmM1=0
U1=0
EmU1=0
A1=0
EmA1=0
M2=0
EmM2=0
U2=1
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
U5=1
EmU5=0
A5=0
EmA5=0
M6=0
EmM6=1
U6=0
EmU6=0
A6=0
EmA6=0
M7=0
EmM7=0
U7=1
EmU7=0
A7=0
EmA7=0
M8=0
EmM8=0
U8=0
EmU8=1
A8=0
EmA8=0
M9=0
EmM9=0
U9=0
EmU9=0
A9=0
EmA9=1
M10=1
EmM10=0
U10=0
EmU10=0
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
EmU12=0
A12=0
EmA12=1
M13=0
EmM13=0
U13=1
EmU13=0
A13=0
EmA13=0
M14=0
EmM14=1
U14=0
EmU14=0
A14=0
EmA14=0
M15=0
EmM15=0
U15=0
EmU15=0
A15=1
EmA15=0
M16=0
EmM16=0
U16=0
EmU16=0
A16=0
EmA16=1
M17=0
EmM17=0
U17=0
EmU17=0
A17=0
EmA17=1
M18=0
EmM18=0
U18=0
EmU18=1
A18=0
EmA18=0
M19=0
EmM19=0
U19=0
EmU19=1
A19=0
EmA19=0
M20=0
EmM20=0
U20=0
EmU20=0
A20=0
EmA20=1
"""
