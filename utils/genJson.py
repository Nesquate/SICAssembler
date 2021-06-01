# fileName = "sicOpCode.json"
fileName = "sicXEOpCode.json"

# SIC OpCOode
# sicOpcode = {
#     'ADD' : '18',
#     'AND' : '40',
#     'COMP' : '28',
#     'DIV' : '24',
#     'J' : '3C',
#     'JEQ' : '30',
#     'JGT' : '34',
#     'JLT' : '38',
#     'JSUB' : '48',
#     'LDA' : '00',
#     'LDCH' : '50',
#     'LDL' : '08',
#     'LDX' : '04',
#     'MUL' : '20',
#     'OR' : '44',
#     'RD' : 'D8',
#     'RSUB' : '4C',
#     'STA' : '0C',
#     'STCH' : '54',
#     'STL' : '14',
#     'STSW' : 'E8',
#     'STX' : '10',
#     'SUB' : '1C',
#     'TD' : 'E0',
#     'TIX' : '2C',
#     'WD' : 'DC'
# }

# SIC/XE OpCode
sicXEOpcode = {
    'ADDF' : '58',
    'ADDR' : '90',
    'CLEAR' : 'B4',
    'COMPF' : '88',
    'COMPR' : 'A0',
    'DIVF' : '64',
    'DIVR' : '9C',
    'FIX' : 'C4',
    'FLOAT' : 'C0',
    'HIO' : 'F4',
    'LDB' : '68',
    'LDF' : '70',
    'LDS' : '6C',
    'LDT' : '74',
    'LPS' : 'D0',
    'MULF' : '60',
    'MULR' : '98',
    'NORM' : 'C8',
    'RMO' : 'AC',
    'SHIFTL' : 'A4',
    'SHIFTR' : 'A8',
    'SIO' : 'F0',
    'SSK' : 'EC',
    'STB' : '78',
    'STF' : '80',
    'STI' : 'D4',
    'STS' : '7C',
    'STT' : '84',
    'SUBF' : '5C',
    'SUBR' : '94',
    'SVC' : 'B0',
    'TIO' : 'F8',
    'TIXR' : 'B8'
}

import json

with open(file=fileName, mode="w") as file:
    # data = json.dumps(sicOpcode)
    data = json.dumps(sicXEOpcode)
    file.write(data)
