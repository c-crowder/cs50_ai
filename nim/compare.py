nims1 = []
i = 0
with open("nim.py") as nim1:
    for line in nim1:
        i += 1
        if i >= 182:
            nims1.append(line)

nims2 = []
i = 0
with open("nim2.py") as nim2:
    for line in nim2:
        i += 1
        if i >= 152:
            nims2.append(line)

for line in zip(nims1, nims2):
    if line[0] == line[1]:
        print(line[0])
    else:
        break