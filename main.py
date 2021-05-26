"""
自我約束開發規範 :
1. 因為 regex 的問題，引號用雙引號
2. 變數命名用駝峰式寫法
3. 多寫註解
"""
# 要讀取的檔案名稱
fileName = "a2.asm"

# SIC OpCode 參考檔案名稱
sicFileName = "sicOpCode.json"

# 引入必要 Library
import re
import Process, Read, Calculate

"""
建立必要的 "容器"
1. labelAddress : 標籤與 PC 的對應
2. objectCode : Object Code 表
3. missObj : 還沒有 Obj Code 的迷途羔羊
"""
labelAddress = dict()
objectCode = dict()
missObj = list()

opCodeDict = Read.readOpCodeFile(sicFileName)

# 讀 ASM 檔案並且做以下操作
with open(file=fileName, mode="r") as file:
    """
    定義 Regex 語法
    - 分三個區域
    - 標籤部份 : `(?:(^[A-Za-z][A-Za-z0-9]*) +| +)`
        - 第一個字必須英文字母，後面隨意
        - 必須要在開頭
        - 但因為有可能沒有標籤，所以上面的規則用口語化表示：
            - 如果前面是空格，匹配掉但是不當群組
            - 如果前面有英文字母，繼續匹配直到後面接到不是空格為止
    - 指令部份 : `(?: +([A-Za-z]+) +)`
        - 前面一定要有空格
        - 中間一定是英文字母，SIC/XE指令沒有數字或底線
        - 空格匹配，但是不當群組
    - 指令參數部份 : `(?: +([A-Za-z0-9',]*) +)`
        - 同指令部份，但是多匹配了引號和逗號
    - 註解部份
        - 會匹配掉，但是都不當群組
        - 註解後面接什麼字都行
    """
    regex = re.compile(r"(?:\..*|(?:(^[A-Za-z][A-Za-z0-9]*) +| +)(?: +([A-Za-z]+) +)(?: +([A-Za-z0-9',]*) +))")
    # 將檔案裡每一行都變成 List 的一部分
    text = file.readlines()
    # 逐行進行判斷
    for line in text:
        # 匹配分成三個群組
        match = regex.search(line)

        """
        命名:
        label = Group 1 ，標籤
        command = Group 2 ，組合語言指令部份
        arg = Group 3 ，指令後方參數
        """
        label = match.group(1)
        command = match.group(2)
        arg = match.group(3)

        # 如果 command 是 START ，label 為程式名稱，ar  為記憶體起始位置 (PC 起始位 )
        if command == "START":
            # TODO : 處理 aarg 沒有 match 到的例外
            programName = label
            pcCounter = arg
        else:
            # 如果有標籤，紀錄當下 PC Counter 以及維護標籤表
            if label is not None:
                labelAddress[label] = pcCounter
            
            # print(pcCounter) # Debug 
            # 如果 command 讀到 WORD ，將 arg 的數字變成地址
            if command == "WORD":
                address, jump = Process.processWORD(arg)
            
            # 如果讀到 BYTE ，讀讀看 arg 是 X、C
            elif command == "BYTE":
                address = Process.processBYTE(arg)
                objectCode[pcCounter] = address
            
            # 讀到 RESW ，就把後面的數字 * 3 往下加
            elif command == "RESW":
                jump = int(arg, 16) * 3
                # print("RESW : {}".format(jump)) # Debug
            
            # 讀到 RESB ，直接把裡面的數字拿來加
            elif command == "RESB":
                jump = int(arg)
                # print("RESB: {}".format(jump)) # Debug
            
            else:
                # TODO : 改寫成 SIC/XE 時，判斷指令前先判斷前面有沒有符號
                # 如果 command 讀出來的指令存在於 sicOpCodeDict
                if command in opCodeDict.keys():
                    # print("NowOpCode : {}".format(opCode)) # Debug
                    
                    # 根據指令格式處理參數
                    jump, arg, register = Process.processFormat(command, arg)

                    # print(arg) # Debug
                    
                    # 如果是 RSUB，因為 RSUB 後面沒 arg ，那就直接組指令即可
                    if command == "RSUB" and arg == "":
                        opCode = str(opCodeDict[command])
                        address = "0000"
                        address = opCode + address
                        objectCode[pcCounter] = address
                    # 如果 arg 的標籤存在於標籤表，讀出地址，並且與 opCode 合併，且加入 Obj Code 對應表
                    elif arg in labelAddress.keys() and command != "RSUB":
                        # 如果標籤存在於標籤表，但是裡面的值為空，則一樣加入 missObj
                        if labelAddress[arg] != "":
                            opCode = str(opCodeDict[command])
                            address = str(labelAddress[arg])
                            # 如果 register 不等於 None (代表有兩個參數)，且 jump != 2 (format 2)，則進行位置運算
                            if jump != 2 and register != None:
                                # print("Pass!") # Debug
                                address = Calculate.calXRegister(address)
                                # print(address) # Debug
                            address = opCode + address
                            objectCode[pcCounter] = address
                        else:
                            Process.addMissObj(pcCounter, command, arg, missObj)
                    # 否則加入 labelAddress 對應 (先使用空白值當值)，且加入 missObj
                    else:
                        labelAddress[arg] = ""
                        Process.addMissObj(pcCounter, command, arg, missObj)
            
            # 處理 pcCounter 16 進位問題
            pcCounter = Calculate.addPcCounter(pcCounter, jump)
            jump = 3 # Reset

# 處理沒有馬上產生 Obj Code 的列
objectCode =  Process.transMissObjToObjCode(missObj, opCodeDict, objectCode, labelAddress)

# Debug
print("Label and Address : ")
print(labelAddress)
print("obj Code :")
print(objectCode)
# print("No Obj Code list :")
# print(missObj)

