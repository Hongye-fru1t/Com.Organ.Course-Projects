import random


def produce_c():
    string = '01'
    buffer = list()
    buffer.append("0000000000000110\n")   # 0x0 = 6
    buffer.append("1011011001000000\n")   # 0x1 = 46656 = 6^6
    buffer.append("0000000000000000\n")
    buffer.append("0000000000000000\n")   # 0x3 = target pattern
    buffer.append("0000000000000000\n")
    buffer.append("0000000000000000\n")
    buffer.append("0000000000000000\n")
    buffer.append("0000000000000000\n")

    for i in range(0, 100):
        line = ''
        for j in range(0, 16):
            seed = random.randint(0, 1)
            line += string[seed]
        line += '\n'
        buffer.append(line)

    with open('patternC.txt', 'w') as c:
        c.writelines(buffer)


def produce_d():  # all the number are produce randomly
    string = '011'    # P(0) = 1/3     P(1) = 2/3
    buffer = list()

    for i in range(0, 8):
        line = ''
        for j in range(0, 16):
            seed = random.randint(0, 2)
            line += string[seed]
        line += '\n'
        buffer.append(line)

    for i in range(0, 100):
        line = ''
        for j in range(0, 16):
            seed = random.randint(0, 2)
            line += string[seed]
        line += '\n'
        buffer.append(line)

    with open('patternD.txt', 'w') as d:
        d.writelines(buffer)


if __name__ == '__main__':
    produce_c()
    produce_d()

