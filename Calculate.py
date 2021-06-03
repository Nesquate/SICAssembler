# 計算 PC，會需要進行字串處理
def addPcCounter(pcCounter, jump):
    pcCounter = int(pcCounter, 16)
    pcCounter = pcCounter + jump
    pcCounter = format(pcCounter, "04X") # PC 補 4 位
    return pcCounter

# 16 進位加法計算
def addHex(hex, addNumber):
    hex = int(hex, 16)
    hex = hex + addNumber
    hex = format(hex, "02X") # 至少補兩位
    return hex

# 16 進位減法計算，輸出為整數
def subHexOutInt(hex1, hex2):
    """
    return hex1 - hex2
    """
    hex1 = int(hex1, 16)
    hex2 = int(hex2, 16)
    return hex1 - hex2


def calXRegister(address):
    # 計算當 X Register 被識別出來時，計算地址
    splitString = list(address)
    head = int(splitString[0], 16)
    head = head + 8 # X = 1，所以要加 8
    splitString[0] = format(head, "X")
    address = ''.join(splitString)
    return address

def calAddress(address, pcCounter, jump, bRegLabel, extendMode):
    # 處理 Address b、p、e的問題
    # 如果 extendMode == 1，地址直接延伸成六位，開頭+1，然後回傳
    if extendMode == 1:
        address = int(address, 16)
        address = format(address, "06X")
        splitString = list(address)
        head = int(splitString[0], 16)
        head = head + 1 # e = 1， head + 1
        splitString[0] = format(head, "X")
        address = ''.join(splitString)
        return address
    
    splitString = list(address)
    # 先把開頭的 16 進位拿出來
    head = int(splitString[0], 16)

    # 預處理 : 非 head 的部份先提取出來
    tempString = list()
    for i in range(1, len(splitString)):
        tempString.append(splitString[i])
    tempString = ''.join(tempString) # 後面地址轉成字串
    
    # 計算下一個 PC 位置
    nextPC = addPcCounter(pcCounter, jump)

    # 計算差距
    pcRelate = subHexOutInt(tempString, nextPC)

    # 如果 pcRelate >= 0 則可以直接拿 pcRelate 組地址
    if pcRelate >= 0:
        head = head + 2 # PC Relate + 2
        relateString = format(pcRelate, "03X") # 轉十六進位補三位 (字串)
    else: # 如果 pcRelate < 0，則需要用 B Register 的值進行加減
        head = head + 4 # B Register Relate + 4
        bRegRelate = subHexOutInt(tempString, bRegLabel)
        relateString = format(bRegRelate, "03X") # 轉十六進位補三位 (字串)
    
    head = format(head, "X") # 10 進位轉 16 進位
    address = head + relateString # 自處合併
    return address

# 計算共有多少 Byte
def calObjSize(objCode):
    return int(len(objCode) / 2)