from typing import Counter
import Calculate, GenCards

# 印空格後接下去
def printSpace(listFile, line):
    listFile.write("                ")
    listFile.write(line)

# 寫出 T 卡片
def printTCard(objFile, startT, lenT, command, counter, dictKey, objectCode):
    # Obj : 產出 T 卡片
    # 如果 startT 沒有值，代表新的 T 卡片產出
    if startT == None and (command != "RESW" and command != "RESB"):
        startT = dictKey[counter]
        # print("Start T : {}".format(startT))
        lenT += len(objectCode[dictKey[counter]]) # 讀到之後，算一下長度

    # 如果 lenT = 0 (代表根本沒有開始) 然後後面又接了 RESW 或 RESB
    # => 什麼都不要做
    elif lenT == 0 and (command == "RESB" or command == "RESW"):
        pass
    else:
        # 如果 command 不等於 RESW 或， RESB，計算長度直到 30 為止
        if (command != "RESW" and command != "RESB") and command != "BYTE":
            if (lenT + len(objectCode[dictKey[counter]])) <= 60: 
                lenT += len(objectCode[dictKey[counter]])
        
        # 如果是 BYTE， 因為長度不一定是固定 3 Bytes，直接結束並產生 T 卡片
        elif command == "BYTE":
            # print("BYTE end!")
            endT = dictKey[counter]
            # print("End T : {}".format(endT))
            # print("------")

            # Obj : 產出 T 卡片    
            GenCards.genTCard(objFile, startT, endT, lenT, objectCode)

            # 重置 : 新的 T 卡片開始
            lenT = 0
            startT = None
        
        # 否則紀錄上一個的地址，然後開始印出 T 卡片
        else:
            # print("REXX end!")
            endT = dictKey[counter-1]
            # print("End T : {}".format(endT))
            # print("------")
            
            # Obj : 產出 T 卡片
            GenCards.genTCard(objFile, startT, endT, lenT, objectCode)
            
            # 重置 : 新的 T 卡片開始
            lenT = 0
            startT = None
        # 如果長度 >= 60，結束
        # 紀錄地址，然後開始印出 T 卡片
        if lenT <= 60 and ((lenT + len(objectCode[dictKey[counter]])) > 60):
            # print("Early end!")
            endT = dictKey[counter]
            # print("End T : {}".format(endT))
            # print("------")

            # Obj : 產出 T 卡片    
            GenCards.genTCard(objFile, startT, endT, lenT, objectCode)

            # 重置 : 新的 T 卡片開始
            lenT = 0
            startT = None

    return startT, lenT

# 印出 Literal
def printLiteral(listFile, literalPC, counter, dictKey, literalAddr, objectCode):
    listFile.write(dictKey[counter]) # 寫入 PC
    # 數空格
    for i in range(len(dictKey[counter]), 8):
        listFile.write(" ")

    listFile.write(objectCode[dictKey[counter]]) # 寫入 Obj Code
    # 數空格
    for i in range(len(objectCode[dictKey[counter]]), 8):
        listFile.write(" ")

    literal = literalPC[dictKey[counter]] 
    address = literalAddr[literal]

    # 寫 * 號
    listFile.write("*")

    # 空七格
    for j in range(1, 8):
        listFile.write(" ")

    # 寫 Literal
    listFile.write(literal)
    # 換行
    listFile.write(("\n"))

def genFile(objFileName, listFileName, labelAddress, objectCode, text, regex, regex_space, literalPC, literalAddr):
    """
    產生 List File
    只有START行、註解行、END行不需要 obj code 和 PC (前面直接空 16 格)

    產生 Obj File
    START 行產生 H 卡片
    END 行產生 E 卡片

    其他 (不包含 RESW 與 RESB) 則產生 T 卡片

    TODO : 改寫成 SIC/XE 時，寫 M 卡片
    """
    # 初始化
    literalCounter = 0
    counter = 0 # List : 計算印到第幾個 Obj Code
    dictKey = list(objectCode.keys()) # 開一個 PC List 待會用來找 Obj Code

    # Obj : 找出起點位置 和 計算終點位置
    startAt = dictKey[0]
    startAtInt = int(startAt, 16)
    startAt = format(startAtInt, "06X")
    endAtInt = int(dictKey[-1], 16) + Calculate.calObjSize(objectCode[dictKey[-1]])
    endAt = format(endAtInt, "06X")

    # Obj : 計算程式長度
    lengthInt = endAtInt - startAtInt
    length = format(lengthInt, "06X")

    # Obj : T 卡片紀錄開始位置
    startT = None # 先用 None 代表目前沒有值
    # Obj : T 卡片紀錄長度
    lenT = 0

    with open(listFileName, "w") as listFile:
        with open(file=objFileName, mode="w") as objFile:
            for line in text:
                lineList = list(line)

                match = regex.search(line)
                match_space = regex_space.search(line)
                
                label = match.group(1)
                command = match.group(2)
                arg = match.group(3)

                
                # List : 如果知道是 START 行或 END 行，就直接大空格
                if (command == "START"):
                    printSpace(listFile, line)
                    # Obj : 產出 H 卡片
                    GenCards.genHCard(objFile, label, startAt, length)

                elif (command == "END"):
                    printSpace(listFile, line)
                    listFile.write("\n") # 換行一下
                    # 印出剩下的賦值
                    if literalCounter > 0:
                        printLiteral(listFile, literalPC, counter, dictKey, literalAddr, objectCode)
                    
                    endArgAddress = labelAddress[arg]
                    # Obj : 產出最後的 T 卡片 (如果 lenT < 60 的話)
                    if startT != None and lenT < 60:
                        # print("END end!")
                        if counter <= len(dictKey) - 1:
                            endT = dictKey[counter]
                            # print("End T : {}".format(endT))
                            # print("------")

                            # Obj : 產出 T 卡片    
                            GenCards.genTCard(objFile, startT, endT, lenT, objectCode)
                        else:
                            print("BUG")

                    # Obj : 產出 E 卡片
                    GenCards.genECard(objFile, endArgAddress)
                
                # List : 如果是註解行，一樣大空格處理
                elif match_space != None:
                    printSpace(listFile, line)
                
                # 如果是 EQU，整行大空格
                elif command == "EQU":
                    printSpace(listFile, line)

                # 如果是 BASE，整行大空格
                elif command == "BASE":
                    printSpace(listFile, line)

                # 如果是 LTORG， LTORG 整行大空格，並且把賦值往下寫
                # Obj : 幫忙產出 T 卡片
                elif command == "LTORG":
                    printSpace(listFile, line)
                    # 印出賦值
                    printLiteral(listFile, literalPC, counter, dictKey, literalAddr, objectCode)
                    
                    counter+=1
                
                # List : 否則直接寫出 PC 與 Obj Code
                else:
                    listFile.write(dictKey[counter]) # 寫入 PC
                    # 數空格
                    for i in range(len(dictKey[counter]), 8):
                        listFile.write(" ")
                    
                    listFile.write(objectCode[dictKey[counter]]) # 寫入 Obj Code
                    # 數空格
                    for i in range(len(objectCode[dictKey[counter]]), 8):
                        listFile.write(" ")
                    
                    listFile.write(line) # 寫入 asm 的內容
                    
                    # # Obj : 產出 T 卡片
                    startT, lenT = printTCard(objFile, startT, lenT, command, counter, dictKey, objectCode)
                    

                    counter+=1