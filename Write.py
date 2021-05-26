def genListFile(outFileName, objectCode, text, regex, regex_space):
    """
    產生 List File
    只有START行、註解行、END行不需要 obj code 和 PC (前面直接空 16 格)
    """
    counter = 0
    dictKey = list(objectCode.keys()) # 開一個 PC List 待會用來找 Obj Code
    with open(outFileName, "w") as outFile:
        for line in text:
            lineList = list(line)
            match = regex.search(line)
            match_space = regex_space.search(line)
            command = match.group(2)
            # 如果知道是 START 行或 END 行，就直接大空格
            if (command == "START") or (command == "END"):
                outFile.write("                ")
                outFile.write(line)
            # 如果是註解行，一樣大空格處理
            elif match_space != None:
                outFile.write("                ")
                outFile.write(line)
            # 否則直接寫出 PC 與 Obj Code
            else:
                outFile.write(dictKey[counter]) # 寫入 PC
                # 數空格
                for i in range(len(dictKey[counter]), 8):
                    outFile.write(" ")
                outFile.write(objectCode[dictKey[counter]]) # 寫入 Obj Code
                # 數空格
                for i in range(len(objectCode[dictKey[counter]]), 8):
                    outFile.write(" ")
                outFile.write(line)
                counter+=1