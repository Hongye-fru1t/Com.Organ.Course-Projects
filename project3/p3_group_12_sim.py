# Simulator and Assembler by ECE366 Project3 Group12
# take instructions as input, convert it to machine code
# take machine code as input to run the simulator


def simulate(MC, Instr, Nsteps, debug_mode, Memory):
    PC = 0              # Program-counter
    DIC = 0
    TotalCycle = 0
    Reg = [0, 0, 0, 0]     # 4 registers, init to all 0
    print("******** Simulation starts *********")
    finished = False
    while not finished:
        fetch = MC[PC]
        fetch = fetch[1:]
        DIC += 1
        if debug_mode:
            print(fetch)
            print(Instr[PC])
            print()
        if fetch[0:3] == "000":  # init
            MUX = [0, 1, 6, 108]
            R = int(fetch[3:5],2)
            MUXindex = int(fetch[5:7],2)
            imm = MUX[MUXindex]
            Reg[R] = imm
            PC += 1
            TotalCycle += 2
        elif fetch[0:3] == "001":  # ld
            Rx = int(fetch[3:5], 2)
            Ry = int(fetch[5:7], 2)
            Reg[Rx] = Memory[Reg[Ry]]
            PC += 1
            TotalCycle += 5
        elif fetch[0:3] == "010":  # st
            Rx = int(fetch[3:5], 2)
            Ry = int(fetch[5:7], 2)
            Memory[Reg[Ry]] = Reg[Rx]
            PC += 1
            TotalCycle += 4
        elif fetch[0:3] == "011":  # add
            Rx = int(fetch[3:5], 2)
            Ry = int(fetch[5:7], 2)
            Reg[Rx] = Reg[Rx] + Reg[Ry]
            PC += 1
            TotalCycle += 4
        elif fetch[0:3] == "100":  # jpu1
            MUX = [9, 6, 24, 18]
            Rx = int(fetch[3], 2)
            Ry = 2 + int(fetch[4], 2)
            imm = MUX[int(fetch[5:7], 2)]
            if Reg[Rx] < Reg[Ry]:
                PC = imm
            else:
                PC += 1
            TotalCycle += 3
        elif fetch[0:3] == "101":  # jpu2
            MUX = [14,8,27]
            Rx = 2 + int(fetch[3],2)
            Ry = int(fetch[4],2)
            imm = MUX[int(fetch[5:7],2)]
            if Reg[Rx] < Reg[Ry]:
                PC = imm
            else:
                PC += 1
            TotalCycle += 3
        elif fetch[0:5] == "11100":   # subR3
            Ry = int(fetch[5:7],2)
            Reg[3] = Reg[3] - Reg[Ry]
            PC += 1
            TotalCycle += 4
        elif fetch[0:5] == "11101":   # inc
            Rx = int(fetch[5:7],2)
            Reg[Rx] = Reg[Rx] + 1
            PC += 1
            TotalCycle += 4
        elif fetch == "1111110":      # R3x6
            Reg[3] = Reg[3]*6
            PC += 1
            TotalCycle += 4
        elif fetch == "1111111":      # score
            Rx = Reg[3]
            Ry = Reg[1]
            binRx = bin(Rx).replace('0b','')
            binRy = bin(Ry).replace('0b','')

            some0 = ''
            for i in range(16-len(binRx)):
                some0 += '0'
            binRx = some0 + binRx

            some0 = ''
            for i in range(16-len(binRy)):
                some0 += '0'
            binRy = some0 + binRy

            score = 0
            for i in range(0, 16):
                if binRx[i] == binRy[i]:
                    score += 1
            Reg[3] = score
            PC += 1
            TotalCycle += 4

        if PC == len(MC):
            finished = True
        if debug_mode:
            if (DIC % Nsteps) == 0:  # print stats every Nsteps
                print("Registers R0-R3: ", Reg)
                print("Program Counter : ", PC)
                input("Press any key to continue")
                print()
        else:
            continue

    print("******** Simulation finished *********")
    print("Dynamic Instr Count: ", DIC)
    print("Total Cycle Count:   ", TotalCycle)
    print("Registers R0-R3:     ", Reg)
    print("Data Memory :")
    for i in range(0,6):
        print('Addr '+str(i)+": HEX:"+format(Memory[i], "016b")+"   DEC: "+str(Memory[i]))


def assemble(I, program_dupe):
    if program_dupe != 1 and program_dupe != 2:
        print("Error, unknown program option")
        exit()
    # p3_group_x_p1_imem.txt
    file = open("p3_group_12_p" + str(program_dupe) + "_imem.txt", "w")

    print("******* Assembler Start ********")
    for i in range(len(I)):
        fetch = I[i]
        fetch = fetch.replace("R", "")
        fetch = fetch.replace(" ", "")

        if (fetch[0:4] == "init"):
            fetch = fetch.replace("init", "")
            fetch = fetch.split(",")
            R = format(int(fetch[0]), "02b")
            if (fetch[1] == "6"):
                imm = "10"
            elif (fetch[1] == "108"):
                imm = "11"
            else:
                imm = format(int(fetch[1]), "02b")
            op = "000"
            string = op + R + imm + "\n"
            # file.write(op + R + imm + "\n")

        elif (fetch[0:2] == "ld"):
            fetch = fetch.replace("ld", "")
            fetch = fetch.split(",")
            Rx = format(int(fetch[0]), "02b")
            Ry = format(int(fetch[1]), "02b")
            op = "001"
            string = op + Rx + Ry + "\n"
            # file.write(op + Rx + Ry + "\n")

        elif (fetch[0:2] == "st"):
            fetch = fetch.replace("st", "")
            fetch = fetch.split(",")
            Rx = format(int(fetch[0]), "02b")
            Ry = format(int(fetch[1]), "02b")
            op = "010"
            string = op + Rx + Ry + "\n"
            # file.write(op + Rx + Ry + "\n")

        elif (fetch[0:3] == "add"):
            fetch = fetch.replace("add", "")
            fetch = fetch.split(",")
            Rx = format(int(fetch[0]), "02b")
            Ry = format(int(fetch[1]), "02b")
            op = "011"
            string = op + Rx + Ry + "\n"
            # file.write(op + Rx + Ry + "\n")

        elif (fetch[0:4] == "jpu1"):
            fetch = fetch.replace("jpu1", "")
            fetch = fetch.split(",")
            Rx = format(int(fetch[0]), "01b")
            Ry = format((int(fetch[1]) - 2), "01b")
            if (fetch[2] == "9"):
                imm = "00"
            elif (fetch[2] == "6"):
                imm = "01"
            elif (fetch[2] == "24"):
                imm = "10"
            elif (fetch[2] == "18"):
                imm = "11"
            op = "100"
            string = op + Rx + Ry + imm + "\n"
            # file.write(op + Rx + Ry + imm + "\n")

        elif (fetch[0:4] == "jpu2"):
            fetch = fetch.replace("jpu2", "")
            fetch = fetch.split(",")
            Rx = format((int(fetch[0]) - 2), "01b")
            Ry = format(int(fetch[1]), "01b")
            if (fetch[2] == "14"):
                imm = "00"
            elif (fetch[2] == "8"):
                imm = "01"
            elif (fetch[2] == "27"):
                imm = "10"
            op = "101"
            string = op + Rx + Ry + imm + "\n"
            # file.write(op + Rx + Ry + imm + "\n")
        elif (fetch[0:4] == "sub3"):
            fetch = fetch.replace("sub3", "")
            Rx = format(int(fetch), "02b")
            op = "11100"
            # file.write(op + Rx + "\n")
            string = op + Rx + "\n"
        elif (fetch[0:3] == "inc"):
            fetch = fetch.replace("inc", "")
            Rx = format(int(fetch), "02b")
            op = "11101"
            string = op + Rx + "\n"
            # file.write(op + Rx + "\n")
        elif (fetch[0:3] == "3x6"):
            op = "1111110"
            string = op + "\n"
            # file.write(op + "\n")
        elif (fetch[0:5] == "score"):
            op = "1111111"
            string = op + "\n"
            # file.write(op + "\n")
        elif (fetch[0:4] == "halt"):
            string = "1111100\n"

        oneCount = 0
        for c in string:
            if (c == "1"):
                oneCount = oneCount + 1

        if (oneCount % 2 == 1):
            string = "1" + string
        else:
            string = "0" + string

        file.write(string)
    file.close()
    print("Machine Code already wrote into prog" + str(program_dupe) + "_MachineCode.txt")
    print("******* Assembler End ********")

def main():
    Memory = []
    debug_mode = False  # is machine in debug mode?
    Nsteps = 3          # How many cycle to run before output statistics
    Instruction = []    # all instructions will be stored here
    machineInstruction = []

    print("Welcome to ECE366 Project3 Group12 ISA Simulator!")

    # Read in instr and convert to machine code
    print("type 1 for program 1")
    print("type 2 for program 2")
    print("type 3 for both program 1 and program 2")
    program = int(input("Enter which program to run:"))
    if program != 1 and program != 2 and program != 3:
        print("wrong program selection!")
        exit()

    # the code commented below is for the case that the input file is instructions not machine code.
    '''
    if program ==1 or program == 2:
        with open("prog"+str(program)+".txt", "r") as instr_file:
            for line in instr_file:
                if line == "\n" or line[0] == '#' or ':' in line:  # empty lines,comments ignored
                    continue
                # Copy all instruction into a list
                Instruction.append(line.strip())
        print("Calling assembler...")
        assemble(Instruction, program)
        print("Assembling Done.")

    elif program == 3:
        instr1 = []
        instr2 = []
        with open("prog1.txt", "r") as instr_file:
            for line in instr_file:
                if line == "\n" or line[0] == '#' or ':' in line:  # empty lines,comments ignored
                    continue
                # Copy all instruction into a list
                instr1.append(line.strip())

        with open("prog2.txt", "r") as instr_file:
            for line in instr_file:
                if line == "\n" or line[0] == '#' or ':' in line:  # empty lines,comments ignored
                    continue
                # Copy all instruction into a list
                instr2.append(line.strip())
        print("Calling assembler...")
        assemble(instr1, 1)
        assemble(instr2, 2)
        print("Assembling Done.")
    '''

    # read MachineCode
    if program == 1 or program == 2:
        Instruction = []
        with open("p3_group_12_p"+str(program)+"_imem.txt", "r") as f:
            for line in f:
                if line == "\n" or line[0] == '#' or ':' in line:  # empty lines,comments ignored
                    continue
                mc = line.split('#')[0]
                inst = line.split('#')[1]
                machineInstruction.append((mc.strip()))
                Instruction.append((inst.strip()))
    elif program == 3:
        MC1 = []
        MC2 = []
        instr1 = []
        instr2 = []
        with open("p3_group_12_p1_imem.txt", "r") as f:
            for line in f:
                if line == "\n" or line[0] == '#' or ':' in line:  # empty lines,comments ignored
                    continue
                mc = line.split('#')[0]
                inst = line.split('#')[1]
                MC1.append((mc.strip()))
                instr1.append((inst.strip()))
        with open("p3_group_12_p2_imem.txt", "r") as f:
            for line in f:
                if line == "\n" or line[0] == '#' or ':' in line:  # empty lines,comments ignored
                    continue
                mc = line.split('#')[0]
                inst = line.split('#')[1]
                MC2.append((mc.strip()))
                instr2.append((inst.strip()))

    # read Data Memory
    print("Data memory pattern we have:")
    print("1] patternA.txt")
    print("2] patternB.txt")
    print("3] patternC.txt")
    print("4] patternD.txt")
    pattern = int(input("Please select pattern:"))
    if pattern < 1 or pattern > 4:
        print("wrong data pattern selection")
        exit()
    pattern_pool = ['A', 'B', 'C', 'D']
    pattern = pattern_pool[pattern-1]
    with open('pattern'+pattern+'.txt', 'r') as data_file:
        for line in data_file:
            if line == "\n" or line[0] == '#':              # empty lines,comments ignored
                continue
            line = line.strip()
            Memory.append(int(line, 2))


    print("********* Simulator **********")
    print("Simulator has 2 modes: ")
    print(" 1] Normal execution")
    print(" 2] Debug mode")
    simMode = int(input("Please select simulator's mode: "))
    if simMode == 1:
        debug_mode = False
    elif simMode == 2:
        debug_mode = True
        Nsteps = int(input("Debug Mode selected. Please enter # of debugging steps: "))
    else:
        print("Error, unrecognized input. Exiting")
        exit()

    if program == 1 or program == 2:
        simulate(machineInstruction, Instruction, Nsteps, debug_mode, Memory)

    elif program == 3:
        simulate(MC1, instr1, Nsteps, debug_mode, Memory)
        simulate(MC2, instr2, Nsteps, debug_mode, Memory)

    # store the memory back
    data = open("p3_group_12_dmem_"+pattern+'.txt', "w")
    for i in range(len(Memory)):
        data.write(format(Memory[i], "016b"))
        data.write("\n")
    data.close()


if __name__ == "__main__":
    main()
