import Calculate

# 合併 Dictionary
# 讀進來的 JSON 檔案可以轉化為 Python 的 Dictionary
# 但是在實做上我只會檢查一個 Dict ，所以需要合併
def mergeDict(dict1, dict2):
    merged = {**dict1, **dict2}
    return merged

def checkExtendMode(command):
    commandList = list(command)
    # 如果字首有 + 那就是 ExtendMode，否則就不是
    if commandList[0] == "+":
        return True
    else:
        return False

# 檢查 arg 的開頭是否包含符號
def checkArgMode(arg):
    argList = list(arg)
    if argList[0] == "#":
        return 1
    elif argList[0] == "@":
        return 2
    elif argList[0] == "=":
        return 3
    else:
        return 0

# 去掉 + 、@ 或 # 號
def controlLabel(command):
    commandList = list(command) # 字串轉成一個一個字元的 List
    tempList = list() # 暫時的 List
    for i in range(1, len(commandList)):
        tempList.append(commandList[i]) # 合併到暫時的 List
    toString = ''.join(tempList) # 合併 List 變字串
    return toString

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
        return toString, int(len(toString)/2)
    
    if splitString[0] == "x" or splitString[0] == "X":
        return splitString[1], int(len(splitString[1])/2)
    
    return arg, 3

def processWORD(word):
    # arg 要轉成 16 進位且要 6 byte
    address = int(word)
    address = format(address, "06X")
    jump = 3
    return address, jump

def processFormat(command, arg, extendMode, opCodeFormat):
    # TODO : 改寫成 SIC/XE 時，要判斷指令格式來決定 pcCounter 的加減

    # 初始化變數
    register = None
    jump = 3
    
    # 如果遇到逗點 => 切割成 arg 和 register
    # arg 也可以是 register，總而言之就是切成兩個部份
    if arg is not None and ',' in arg:
        spiltString = arg.split(',')
        arg = spiltString[0]
        register = spiltString[1]
    
    # 判斷指令格式
    # 如果 Format = 3，看一下是否有 extendMode (有的話變 4)
    # 如果 Format = 2， jump = 2
    # 如果 Format = 1， jump = 1
    if opCodeFormat[command] == 3:
        if extendMode == True:
            jump = 4
        else:
            jump = 3
    if opCodeFormat[command] == 2:
        jump = 2
    if opCodeFormat[command] == 1:
        jump = 1

    return jump, arg, register

# 處理 Format 2 的地址問題
def processFormat2(arg, register):
    registerDict = {
        "A" : "0",
        "X" : "1",
        "L" : "2",
        "B" : "3",
        "S" : "4",
        "T" : "5",
        "F" : "6"
    }
    # 如果存在於 Register Dict 裡面，直接拿出來取值
    if arg in registerDict.keys():
        argCode = registerDict[arg]
    # Register 這個變數有可能是存放純數字 (如 SHIFTL)
    # 所以如果找不到的話
    # 如果有數字，就直接把該數字轉成 16 進位
    # 否則填 0 處理
    if register in registerDict.keys():
        regCode = registerDict[register]
    elif register != None:
        regCode = int(register, 16)
        regCode = format(regCode, "X")
    else:
        regCode = "0"
    
    return argCode+regCode

# 處理 opCode ni 定址問題
def opCodeXEProcess(opCode, argMode):
    if argMode == 0:
        opCode = Calculate.addHex(opCode, 3)
    elif argMode == 1:
        opCode = Calculate.addHex(opCode, 1)
    elif argMode == 2:
        opCode = Calculate.addHex(opCode, 2)
    else:
        return opCode
    return opCode

# 處理直接取值(#)的問題
def immediatelyValue(address):
    address = int(address) # 字串轉整數
    address = format(address, "04X") # 10 進位整數轉成 16 進位 4 位整數並轉成字串
    return address



# 將尚未產生 ObjCode 的部份轉為 ObjCode
def transMissObjToObjCode(missObj, opCodeDict, objectCode, labelAddress, bRegLabel):
    # TODO : 改寫成 SIC/XE 時，要判斷的不只有 Index
    for missDict in missObj:
        opCode = opCodeDict[missDict['opCode']]
        address = labelAddress[missDict['label']]
        argMode = missDict['argMode']
        pcCounter = missDict['nowPC']
        jump = missDict['nowJump']
        extendMode = missDict['extendMode']
        
        # 處理 Index 
        if missDict['index'] == 1:
            address = Calculate.calXRegister(address)
        
        # 處理 argMode
        opCode = opCode = opCodeXEProcess(opCode, argMode)
        # # Debug
        # if argMode == 1:
        #     print(address)
        #     print(pcCounter)

        # 處理 address bpe 的問題
        if address != "":
            address = Calculate.calAddress(address, pcCounter, jump, bRegLabel, extendMode)
        
        address = opCode + address
        objectCode[missDict['nowPC']] = address
    # 排序 objectCode
    sortedObjCode = dict()
    for i in sorted(objectCode.keys()):
        sortedObjCode[i] = objectCode[i]
    return sortedObjCode

# 將目前無法產生 ObjCode 的行列加入列表中
def addMissObj(pcCounter, command, arg, missObj, index, argMode, extendMode, jump):
    tempdict = dict()
    tempdict['nowPC'] = pcCounter
    tempdict['opCode'] = command
    tempdict['label'] = arg
    tempdict['argMode'] = argMode
    tempdict['nowJump'] = jump
    
    # 判斷無法產生的 ObjCode 是否需要 Index 處理
    # TODO : 改寫成 SIC/XE 時，要判斷的不只有 Index
    if index == True:
        tempdict['index'] = 1
    else:
        tempdict['index'] = 0
    # 判斷是否需要 extendMode 處理
    if extendMode == True:
        tempdict['extendMode'] = 1
    else:
        tempdict['extendMode'] = 0
    missObj.append(tempdict)