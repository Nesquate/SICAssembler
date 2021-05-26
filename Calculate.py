def addPcCounter(pcCounter, jump):
    pcCounter = int(pcCounter, 16)
    pcCounter = pcCounter + jump
    pcCounter = format(pcCounter, "X")
    return pcCounter