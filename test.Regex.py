import re
g1 = list()
g2 = list()
g3 = list()

with open("a2.asm", mode="r") as file:
    # 核心匹配功能
    regex = re.compile(r"(?:\..*|(?:(^[A-Za-z][A-Za-z0-9]*) +| +)(?: +([A-Za-z]+) +)(?: +([A-Za-z0-9',]*) +))")
    text = file.readlines()
    for line in text:
        match = regex.search(line)
        if match.group(1) is not None:
            g1.append(match.group(1))
        if match.group(2) is not None:
            g2.append(match.group(2))
        if match.group(1) is not None:
            g3.append(match.group(3))
    print("Labels :", end="")
    print(g1)
    print()
    print("Commands :", end="")
    print(g2)
    print()
    print("Variables : ", end="")
    print(g3)
    print()