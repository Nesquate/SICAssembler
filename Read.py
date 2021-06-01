import json

# 讀 Op Code 檔案
def readJSONFile(fileName):
    with open(file=fileName, mode="r") as jsonFile:
        jsonContent = jsonFile.read()
        opCodeDict = json.loads(jsonContent)
        return opCodeDict