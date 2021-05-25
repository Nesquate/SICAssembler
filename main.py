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
import re, json

"""
建立必要的 "容器"
1. labelAddress : 標籤與 PC 的對應
2. objectCode : Object Code 表
3. missObj : 還沒有 Obj Code 的迷途羔羊
"""
labelAddress = dict()
objectCode = dict()
missObj = list()

# 讀 SIC Op Code 檔案
with open(file=sicFileName, mode="r") as jsonFile:
    jsonContent = jsonFile.read()
    sicOpCodeDict = json.loads(jsonContent)

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
        match = regex.search(line)
        # 如果 Group 是 START ，Group 1 為程式名稱，Group 2 為記憶體起始位置 (PC 起始位 )
        if match.group(2) == "START":
            # TODO : 處理 Group 3 沒有 match 到的例外
            programName = match.group(1)
            pcCounter = match.group(3)
        else:
            # 如果有標籤，紀錄當下 PC Counter 以及維護標籤表
            if match.group(1) is not None:
                labelAddress[match.group(1)] = pcCounter
            
            print(pcCounter)
            # 如果 Group 2 讀到 WORD ，將 Group 3 的數字變成地址
            # TODO : Group 3 要轉成 16 進位且要 6 byte
            if match.group(2) == "WORD":
                address = str(match.group(3))
                jump = 3
            # TODO : 如果讀到 BYTE ，讀讀看 Group 3 是 X、C
            # X : 直接把 16 進位拿出來當地址
            # C : 裡面的東西要先轉成 16 進位
            elif match.group(2) == "BYTE":
                address = match.group(3)
                objectCode[pcCounter] = address
            # 讀到 RESW ，就把後面的數字 * 3 往下加
            elif match.group(2) == "RESW":
                jump = int(match.group(3), 16) * 3
                print("RESW : {}".format(jump)) # Debug
            # 讀到 RESB ，直接把裡面的數字拿來加
            elif match.group(2) == "RESB":
                jump = int(match.group(3))
                print("RESB: {}".format(jump)) # Debug
            else:
                # TODO : 改寫成 SIC/XE 時，要判斷指令格式來決定 pcCounter 的加減
                # TODO : 改寫成 SIC/XE 時，判斷指令前先判斷前面有沒有符號
                # 如果 Group 2 讀出來的指令存在於 sicOpCodeDict
                if match.group(2) in sicOpCodeDict.keys():
                    # print("NowOpCode : {}".format(opCode)) # Debug
                    jump = 3
                    # 如果 Group 3 的標籤存在於標籤表，讀出地址，並且與 opCode 合併，且加入 Obj Code 對應表
                    if match.group(3) in labelAddress.keys():
                        # TODO : 處理逗點問題
                        # 如果標籤存在於標籤表，但是裡面的值為空，則一樣加入 missObj
                        if labelAddress[match.group(3)] != "":
                            opCode = str(sicOpCodeDict[match.group(2)])
                            address = str(labelAddress[match.group(3)])
                            address = opCode + address
                            objectCode[pcCounter] = address
                        else:
                            tempdict = dict()
                            tempdict['nowPC'] = pcCounter
                            tempdict['opCode'] = match.group(2)
                            tempdict['label'] = match.group(3)
                            missObj.append(tempdict)
                    # 否則加入labelAddress對應 (先使用空白值當值)，且加入 missObj
                    else:
                        labelAddress[match.group(3)] = ""
                        tempdict = dict()
                        tempdict['nowPC'] = pcCounter
                        tempdict['opCode'] = match.group(2)
                        tempdict['label'] = match.group(3)
                        missObj.append(tempdict)
            
            # 處理 pcCounter 16 進位問題
            pcCounter = int(pcCounter, 16)
            pcCounter = pcCounter + jump
            pcCounter = format(pcCounter, "X")
            jump = 3 # Reset

# 處理沒有馬上產生 Obj Code 的列
for missDict in missObj:
    opCode = sicOpCodeDict[missDict['opCode']]
    address = labelAddress[missDict['label']]
    address = opCode + address
    objectCode[missDict['nowPC']] = address

# 排序 objectCode
sortedObjCode = dict()
for i in sorted(objectCode.keys()):
    sortedObjCode[i] = objectCode[i]

print("Label and Address : ")
print(labelAddress)
print("obj Code :")
print(sortedObjCode)
# print("No Obj Code list :")
# print(missObj)

