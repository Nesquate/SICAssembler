import json

# 讀 SIC Op Code 檔案
def readOpCodeFile(sicFileName):
    with open(file=sicFileName, mode="r") as jsonFile:
        jsonContent = jsonFile.read()
        sicOpCodeDict = json.loads(jsonContent)
        return sicOpCodeDict