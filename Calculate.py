# 計算 PC，會需要進行字串處理
def addPcCounter(pcCounter, jump):
    pcCounter = int(pcCounter, 16)
    pcCounter = pcCounter + jump
    pcCounter = format(pcCounter, "04X") # PC 補 4 位
    return pcCounter

def calXRegister(address):
    # 計算當 X Register 被識別出來時，計算地址
    splitString = list(address)
    head = int(splitString[0], 16)
    head = head + 8 # X = 1，所以要加 8
    splitString[0] = format(head, "X")
    address = ''.join(splitString)
    return address

def calObjSize(objCode):
    return int(len(objCode) / 2)