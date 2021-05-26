import Calculate

def processBYTE(arg):
    # 如果讀到 BYTE ，讀讀看 Group 3 是 X、C
    # X : 直接把 16 進位拿出來當地址
    # C : 裡面的東西要先轉成 16 進位
    splitString = arg.split("'")
    if splitString[0] == "c" or splitString[0] == "C":
        tempChars = list()
        for a in splitString[1]:
            a = ord(a)
            a = format(a, "X")
            tempChars.append(a)
        toString = ''.join(tempChars)
        return toString
    if splitString[0] == "x" or splitString[0] == "X":
        return splitString[1]
    return arg

def processWORD(word):
    # TODO : arg 要轉成 16 進位且要 6 byte
    address = str(word)
    jump = 3
    return address, jump

def processFormat(command, arg):
    # TODO : 改寫成 SIC/XE 時，要判斷指令格式來決定 pcCounter 的加減
    if ',' in arg:
        spiltString = arg.split(',')
        arg = spiltString[0]
        register = spiltString[1]
        return 3, arg, register
    return 3, arg, None

# 將尚未產生 ObjCode 的部份轉為 ObjCode
def transMissObjToObjCode(missObj, opCodeDict, objectCode, labelAddress):
    # TODO : 改寫成 SIC/XE 時，要判斷的不只有 Index
    for missDict in missObj:
        opCode = opCodeDict[missDict['opCode']]
        address = labelAddress[missDict['label']]
        if missDict['index'] == 1:
            address = Calculate.calXRegister(address)
        address = opCode + address
        objectCode[missDict['nowPC']] = address
    # 排序 objectCode
    sortedObjCode = dict()
    for i in sorted(objectCode.keys()):
        sortedObjCode[i] = objectCode[i]
    return sortedObjCode

# 將目前無法產生 ObjCode 的行列加入列表中
def addMissObj(pcCounter, command, arg, missObj, index):
    tempdict = dict()
    tempdict['nowPC'] = pcCounter
    tempdict['opCode'] = command
    tempdict['label'] = arg
    # 判斷無法產生的 ObjCode 是否需要 Index 處理
    # TODO : 改寫成 SIC/XE 時，要判斷的不只有 Index
    if index == True:
        tempdict['index'] = 1
    else:
        tempdict['index'] = 0
    missObj.append(tempdict)