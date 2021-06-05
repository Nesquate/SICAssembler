import Calculate

# Obj : 產出 H 卡片
def genHCard(objFile, programName, startAt, length):
    objFile.write("H")
    objFile.write(programName)
    for i in range(len(programName), 6):
        objFile.write(" ") # 補空格
    objFile.write(startAt)
    objFile.write(length)
    objFile.write("\n")

# Obj : 產出 T 卡片
def genTCard(objFile, startAt, endAt, length, objCodeList):
    # 先紀錄開始位置
    nowAt = startAt
    # 先轉成 Int 以方便計算
    nowAtInt = int(startAt, 16)
    endAtInt = int(endAt, 16)

    objFile.write("T")
    objFile.write(format(nowAtInt, "06X"))
    objFile.write(format(int(length/2), "02X"))

    # 當目前PC數字小於等於終點數字時，持續印出
    while nowAtInt <= endAtInt:
        objFile.write(objCodeList[nowAt]) # 先寫入
        
        # 再計算當前 objCode 長度，用來計算接下來 PC 要往下加多少 Byte
        jump = int(len(objCodeList[nowAt]) / 2)

        # 利用計算出來的數字再加回去 nowAt
        nowAt = Calculate.addPcCounter(nowAt, jump)

        # 最後把計算出來的結果轉成整數
        nowAtInt = int(nowAt, 16)

    objFile.write("\n")

# Obj : 產出 E 卡片
def genECard(objFile, endArgAddress):
    objFile.write("E")
    endArgAddrInt = int(endArgAddress, 16)
    endArgAddress = format(endArgAddrInt, "06X")
    objFile.write(endArgAddress)