# 計算 PC，會需要進行字串處理
def addPcCounter(pcCounter, jump):
    pcCounter = int(pcCounter, 16)
    pcCounter = pcCounter + jump
    pcCounter = format(pcCounter, "X")
    return pcCounter

def calXRegister(address):
    # TODO : 計算當 X Register 被識別出來時，計算地址
    return address