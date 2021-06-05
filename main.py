"""
自我約束開發規範 :
1. 因為 regex 的問題，引號用雙引號
2. 變數命名用駝峰式寫法
3. 多寫註解
"""
# 要讀取的檔案名稱
fileName = "XE_OK_02.ASM"

# List File 檔案名稱
listFileName = "out.lst"

# Obj File 檔案名稱
objFileName = "out.obj"

# SIC OpCode 參考檔案名稱
sicFileName = "sicOpCode.json"

# SIC/XE OpCode 參考檔案名稱
sicXEFileName = "sicXEOpCode.json"

# OpCode Format 參考檔案名稱
opCodeFormatName = "opCodeFormat.json"

# 引入必要 Library
from os import EX_TEMPFAIL
import re
import Process, Read, Calculate, Write

"""
建立必要的 "容器"
1. labelAddress : 標籤與 PC 的對應
2. objectCode : Object Code 表
3. missObj : 還沒有 Obj Code 的迷途羔羊
4. literalList : 維護 Literal 有多少的表
5. literalPC : Literal 與 PC 對應 (after LTORG or END)
6. literalAddr : Literal 與 Addr 對應 (after LTORG or END)
"""
labelAddress = dict()
objectCode = dict()
missObj = list()
literalList = list()
literalPC = dict()
literalAddr = dict()

# 讀取 opCode 字典檔 (JSON 格式)
opCodeDict1 = Read.readJSONFile(sicFileName)
opCodeDict2 = Read.readJSONFile(sicXEFileName)

# 合併 opCode 字典檔
opCodeDict = Process.mergeDict(opCodeDict1, opCodeDict2)

# 開啟 OpCode Foramt 參照檔案
opCodeFormat = Read.readJSONFile(opCodeFormatName)

"""
定義 Regex 語法
(感謝 @Mikucat 提供靈感)
- 運用 Regex 的群組概念
- 完整語句
    - `(?:\..*|(?:(^[A-Za-z][A-Za-z0-9]*) +| +)(?: +(\+?[A-Za-z]+))(?:\r?\n| +([=@#]?[A-Za-z0-9',]*)))`
- 分三個區域
    - 標籤部份 : `(?:\..*|(?:(^[A-Za-z][A-Za-z0-9]*) +| +)`
        - 第一個字必須英文字母，後面隨意
        - 必須要在開頭
        - 但因為有可能沒有標籤，所以上面的規則用口語化表示：
            - 如果前面是空格，匹配掉但是不當群組
            - 如果前面有英文字母，繼續匹配直到後面接到不是空格為止
        - 如果匹配到註解句點的部份，那就全部匹配掉
    - 指令部份 : `(?: +(\+?[A-Za-z]+))`
        - 前面一定要有空格，緊貼英文字母的開頭可能會有 `+` 表示 extended 模式
        - 中間是英文字母，SIC/XE指令沒有數字或底線
        - 空格匹配，但是不當群組
    - 指令參數部份 : `(?:\r?\n| +([=@#]?[A-Za-z0-9',]*)))`
        - 批配換行不分組 (例如 RSUB 打完之後馬上換行)
        - 或是批配空格，緊貼英文字母的部份批配 `#` (直接取值) 或 `@` (相對取值) 或 `=` (直接賦值)
        - 中間匹配英文字母或數字
    - 註解部份
        - 會匹配掉，但是都不當群組
        - 註解後面接什麼字都行
- 2021/05/26 : 因為發現在撰寫 List file 時需要匹配註解行，因此寫了新規則
    - `(^\..*)|(^ +\..*)` : 開頭有至少一個空格再英文句號 或 開頭就是英文句號的**就是註解行**
"""
regex = re.compile(r"(?:\..*|(?:(^[A-Za-z][A-Za-z0-9]*) +| +)(?: +(\+?[A-Za-z]+))(?:\r?\n| +([=@#]?[A-Za-z0-9',]*)))")
regex_space = re.compile(r"(^\..*)|(^ +\..*)")

# Init
jump = None
pcCounter = None
bRegLabel = "0"
baseLabelStr = None
haveBase = False
literalCount = 0

# 讀 ASM 檔案並且做以下操作
with open(file=fileName, mode="r") as file:
    # 將檔案裡每一行都變成 List 的一部分
    text = file.readlines()
    # 逐行進行判斷
    for line in text:
        # 匹配分成三個群組
        match = regex.search(line)

        bReg = 0 # 初始化 B 暫存器的數值

        """
        命名:
        label = Group 1 ，標籤
        command = Group 2 ，組合語言指令部份
        arg = Group 3 ，指令後方參數
        """
        label = match.group(1)
        command = match.group(2)
        arg = match.group(3)

        extendMode = False # Extend 模式，預設為 False
        """ 
        判斷 arg 是否有 @ 或 #
        # : 直接取值 
        @ : 間接取值 (類似指標概念)
        = : 直接賦值

        數字意義 :
        argMode = 0 -> 一般標籤模式
        argMode = 1 -> 直接取值模式
        argMode = 2 -> 間接取值模式
        argMode = 3 -> 直接賦值模式
        """
        argMode = 0 # arg 模式，預設為 0

        # 如果 command 是 START ，label 為程式名稱，ar  為記憶體起始位置 (PC 起始位 )
        if command == "START":
            # TODO : 處理 aarg 沒有 match 到的例
            programName = label
            pcCounter = format(int(arg, 16), "04X") # 處理補 4 個位數
            labelAddress[label] = pcCounter
        else:
            # 如果有標籤，紀錄當下 PC Counter 以及維護標籤表
            if label is not None:
                labelAddress[label] = pcCounter
            
            # print(pcCounter) # Debug 
            # 如果 command 讀到 WORD ，將 arg 的數字變成地址
            if command == "WORD":
                address, jump = Process.processWORD(arg)
                objectCode[pcCounter] = address
            
            # 如果讀到 BYTE ，讀讀看 arg 是 X、C
            elif command == "BYTE":
                address, jump = Process.processBYTE(arg)
                objectCode[pcCounter] = address
            
            # 讀到 RESW ，就把後面的數字 * 3 往下加
            elif command == "RESW":
                jump = int(arg) * 3
                # print("RESW : {}".format(jump)) # Debug
                objectCode[pcCounter] = "" # 寫一個空值表示不用產生 ObjCode
            
            # 讀到 RESB ，直接把裡面的數字拿來加
            elif command == "RESB":
                jump = int(arg)
                # print("RESB: {}".format(jump)) # Debug
                objectCode[pcCounter] = "" # 寫一個空值表示不用產生 ObjCode
            
            # TODO: 讀到 EQU ，判斷前後標籤問題
            elif command == "EQU":
                print("Have EQU!")
                continue

            # 讀到 BASE，判斷 BASE 標籤的問題
            # 把 arg 記錄下來，並且分別判斷是標籤還是整數
            elif command == "BASE":
                baseLabelStr = arg
                continue
            
            # TODO : 處理 LTORG 的問題
            elif command == "LTORG" or command == "END":
                # 把 literal 表的值通通讀出來，賦予 PC 後再繼續
                # 因為中間可能會斷掉，所以用個 STOP 作為提醒
                for i in range(literalCount, len(literalList)):
                    infoDict = literalList[i]

                    if infoDict['literal'] == "STOP":
                        continue

                    jump = infoDict['jump']
                    address = infoDict['address']
                    
                    #Debug
                    print("Debug : pcCounter = {}, address = {}".format(pcCounter, address))

                    #加入 PC 與 Literal 對應以方便計算
                    literalPC[pcCounter] = infoDict['literal']

                    #加入 Addr 與 Literal 對應
                    literalAddr[infoDict['literal']] = address
                    
                    labelAddress[address] = pcCounter
                    # objectCode[pcCounter] = address
                    pcCounter = Calculate.addPcCounter(pcCounter, jump)
                    literalCount += 1
                tempDict = dict()
                stopStr = "STOP" + str(literalCount)
                tempDict['literal'] = "STOP"
                literalPC[stopStr] = "STOP"
                literalAddr[stopStr] = "STOP"
                literalList.append(tempDict)
                continue
            
            else:
                # 判斷指令前先判斷前面有沒有符號
                if command is not None:
                    # 判斷指令部份是否有 +
                    extendMode = Process.checkExtendMode(command)
                    # 如果確定為 Extend Mode ，那就去掉開頭
                    if extendMode == True:
                        command = Process.controlLabel(command)

                # 如果 command 讀出來的指令存在於 opCodeDict
                if command in opCodeDict.keys():
                    # print("NowOpCode : {}".format(opCode)) # Debug
                    
                    # 根據指令格式處理參數
                    jump, arg, register = Process.processFormat(command, arg, extendMode, opCodeFormat)

                    # print(arg) # Debug
                    
                    if arg is not None:
                        # 判斷 arg 是否有 @ 或 #
                        argMode = Process.checkArgMode(arg)
                        if argMode != 0:
                            arg = Process.controlLabel(arg)
                    
                    # 如果是 RSUB，因為 RSUB 後面沒 arg ，那就直接組指令即可
                    if command == "RSUB" and (arg == "" or arg is None):
                        opCode = str(opCodeDict[command])
                        address = "0000"
                        address = opCode + address
                        objectCode[pcCounter] = address

                    # 處理 Jump = 2 時，後面地址的問題
                    elif jump == 2:
                        # OpCode 不需要理會 n、i 問題
                        opCode = str(opCodeDict[command])
                        # Debug
                        # print("Arg : {}, Register : {}".format(arg, register))
                        address = Process.processFormat2(arg, register)
                        address = opCode + address
                        objectCode[pcCounter] = address

                    # TODO : 處理 Literal
                    elif argMode == 3:
                        tempDict = dict()
                        tempDict['literal'] = arg
                        
                        # 當 BYTE 轉換，紀錄到 Literal 維護表 (之後用於 LTORG 與 END 的 PC Counter 計算以及 List File 處理用)
                        address, jump = Process.processBYTE(arg)
                        tempDict['address'] = address
                        tempDict['jump'] = jump

                        # 當不重複的時候才要加到 list 上
                        if tempDict not in literalList:
                            literalList.append(tempDict)

                        # 把轉換後的地址丟到 labelAddress
                        labelAddress[arg] = "" # 先用空值處理，到 LTORG 階段會直接賦予 PC

                        # 直接把目前的 command 當作 missObj 處理
                        Process.addMissObj(pcCounter, command, arg, missObj, index, argMode, extendMode, jump)
                    
                    # 如果 arg 的標籤存在於標籤表，讀出地址，並且與 opCode 合併，且加入 Obj Code 對應表
                    elif arg in labelAddress.keys() and command != "RSUB":
                        # 如果標籤存在於標籤表，但是裡面的值為空，或是當前沒有 BASE，則一樣加入 missObj
                        if labelAddress[arg] != "":
                            # BASE : 如果標籤等於被記錄下來當作 BASE 的標籤
                            # 則把 BASE 標籤代表的數值讀出來替換
                            if arg == baseLabelStr:
                                bRegLabel = labelAddress[arg]
                                haveBase = True

                            opCode = str(opCodeDict[command])
                            address = str(labelAddress[arg])

                            # 如果 register 等於 X ，且 jump != 2 (format 2)，則進行位置運算
                            if jump != 2 and register == "X":
                                # print("Pass!") # Debug
                                address = Calculate.calXRegister(address)
                                # print(address) # Debug
                            
                            # 處理 opCode ni (argMode = 2 / 1) 參數的問題
                            opCode = Process.opCodeXEProcess(opCode, argMode)

                            # 處理 address bpe 的問題
                            # 如果有 BASE，那就直接處理，否則也加入 addMissObj 稍後處理
                            if haveBase == True:
                                if extendMode == True:
                                    extendModeInt = 1
                                else:
                                    extendModeInt = 0
                                if address != "":
                                    # Debug
                                    # print("Debug : (A) label = {}, command = {}, arg={}, PC={}".format(label, command, arg, pcCounter))
                                    address = Calculate.calAddress(address, pcCounter, jump, bRegLabel, extendModeInt)

                                address = opCode + address
                                objectCode[pcCounter] = address
                            else:
                                Process.addMissObj(pcCounter, command, arg, missObj, index, argMode, extendMode, jump)
                        else:
                            if jump != 2 and register == "X":
                                index = True
                            else:
                                index = False
                            
                            Process.addMissObj(pcCounter, command, arg, missObj, index, argMode, extendMode, jump)
                    
                    # 否則，非直接取值，加入 labelAddress 對應 (先使用空白值當值)，且加入 missObj
                    # 直接取值 (argMode = 1) 要先處理再放入
                    else:
                        if arg is not None:
                            # 處理直接取值 (argMode = 1) 的問題
                            # 必須先判斷字串是否都是整數 (isdigit())
                            if argMode == 1 and arg.isdigit() == True:
                                arg = Process.immediatelyValue(arg)
                                labelAddress[arg] = arg
                            else:
                                labelAddress[arg] = ""
                                if jump != 2 and register == "X":
                                    index = True
                                else:
                                    index = False
                            
                            Process.addMissObj(pcCounter, command, arg, missObj, index, argMode, extendMode, jump)
            
            # 處理 pcCounter 16 進位問題
            if command != None and (command != "END" or command != "EQU"):
                # Debug
                # print("PC Counter : {}, Jump : {}".format(pcCounter, jump))
                pcCounter = Calculate.addPcCounter(pcCounter, jump)
        # Debug
        # print("NextPCCounter : {}, Command : {}, ExtendMode == {} ; Arg : {}, ArgMode == {}, jump : {}".format(pcCounter, command, extendMode, arg, argMode, jump))
            

# 處理沒有馬上產生 Obj Code 的列
objectCode =  Process.transMissObjToObjCode(missObj, opCodeDict, objectCode, labelAddress, bRegLabel, baseLabelStr, literalPC)

# print(missObj)

# print(objectCode)
# print(literalList)

# # Debug
# # print("Label and Address : ")
# # print(labelAddress)
# # print("No Obj Code list :")
# print(missObj)
# # print("obj Code :")
# # print(objectCode)
# # print(list(objectCode.keys()))

# # 產出 List File 與 Obj File
Write.genFile(objFileName, listFileName, labelAddress, objectCode, text, regex, regex_space, literalPC, literalAddr)