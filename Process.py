def processBYTE(arg):
    # TODO : 如果讀到 BYTE ，讀讀看 Group 3 是 X、C
    # X : 直接把 16 進位拿出來當地址
    # C : 裡面的東西要先轉成 16 進位
    return arg

def processWORD(word):
    # TODO : Group 3 要轉成 16 進位且要 6 byte
    address = str(word)
    jump = 3
    return address, jump

def processFormat(command, arg):
    # TODO : 改寫成 SIC/XE 時，要判斷指令格式來決定 pcCounter 的加減
    # TODO : 處理逗點問題
    return 3, arg, None

def transMissObjToObjCode(missObj, opCodeDict, objectCode, labelAddress):
    for missDict in missObj:
        opCode = opCodeDict[missDict['opCode']]
        address = labelAddress[missDict['label']]
        address = opCode + address
        objectCode[missDict['nowPC']] = address
    # 排序 objectCode
    sortedObjCode = dict()
    for i in sorted(objectCode.keys()):
        sortedObjCode[i] = objectCode[i]
    return sortedObjCode

def addMissObj(pcCounter, command, arg, missObj):
    tempdict = dict()
    tempdict['nowPC'] = pcCounter
    tempdict['opCode'] = command
    tempdict['label'] = arg
    missObj.append(tempdict)