from math import log, ceil

mem_space = 1024
Memory = [0 for i in range(mem_space)]

block_used_tag = 0           # for LRU mechanism

class Block:
    def __init__(self, word_num):
        self.info = [0 for i in range(word_num)]
        self.wd_num = word_num
        self.tag = None
        self.vali = 0
        self.used_tag = 0     # for LRU mechanism


class Blocks:
    def __init__(self, way_num, blk_num, wd_num):
        self.way_num = way_num
        self.blk_num = blk_num
        self.wd_num = wd_num
        self.info = []
        for i in range(blk_num):
            tmp_set = [Block(wd_num) for j in range(way_num)]
            self.info.append(tmp_set)

        self.block_bit: int = ceil(log(self.blk_num, 2))
        self.word_bit: int = ceil(log(self.wd_num, 2)) + 2   # in block offset bits
        self.read_num = 0
        self.hit_num = 0

    def __getitem__(self, n):
        return self.info[n]

    def get_blk_index(self, target_mem):
        if type(target_mem) == type(1):
            target_mem = format(target_mem, '032b')
        if target_mem[32 - self.block_bit - self.word_bit: 32 - self.word_bit]:
            return int(target_mem[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)
        else:
            return 0

    def read(self, target_mem, ):
        self.read_num += 1
        global block_used_tag
        block_used_tag += 1
        if type(target_mem) == type(1):
            target_mem = format(target_mem, '032b')

        target_tag = int(target_mem[0: 32 - self.block_bit - self.word_bit], 2)

        if self.blk_num == 1:
            target_block_index = 0
        else:
            target_block_index = int(target_mem[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)

        for i in range(self.way_num):
            # hit
            if target_tag == self[target_block_index][i].tag and self[target_block_index][i].vali == 1:
                self[target_block_index][i].used_tag = block_used_tag
                self.hit_num += 1
                return True
        # miss
        min_tag = 0
        min_index = 0
        for i in range(self.way_num):
            if self[target_block_index][i].vali == 0:
                min_index = i
                break
            if self[target_block_index][i].used_tag < min_tag:
                min_tag = self[target_block_index][i].used_tag
                min_index = i

        self[target_block_index][min_index].tag = target_tag
        # target mem address
        target_mem_address: int = (int(target_mem, 2) - int(target_mem[- self.word_bit:], 2) - 8192) // 4
        self[target_block_index][min_index].info = Memory[target_mem_address: target_mem_address + self.wd_num]
        self[target_block_index][min_index].vali = 1
        self[target_block_index][min_index].used_tag = block_used_tag

        return False

    def get_the_block_need_to_write(self, target_mem):
        if isinstance(target_mem, int):
            target_mem = format(target_mem, '032b')

        target_tag = int(target_mem[0: 32 - self.block_bit - self.word_bit], 2)
        if self.blk_num == 1:
            target_block_index = 0
        else:
            target_block_index = int(target_mem[32 - self.block_bit - self.word_bit: 32 - self.word_bit], 2)

        for i in range(self.way_num):
            # hit
            if target_tag == self[target_block_index][i].tag and self[target_block_index][i].vali == 1:
                return self[target_block_index][i]
        # miss
        min_tag = 0
        min_index = 0
        for i in range(self.way_num):
            if self[target_block_index][i].vali == 0:
                min_index = i
                break
            if self[target_block_index][i].used_tag < min_tag:
                min_tag = self[target_block_index][i].used_tag
                min_index = i

        return self[target_block_index][min_index]

    def show(self):
        if self.way_num == 1:
            for i in range(self.blk_num):
                print("        block", i, ":")
                print("                  valid:", self[i][0].vali)
                print("                  tag  :", format(self[i][0].tag))
                for j in self[i][0].info:
                    if j < 0:
                        j = 2**32 + j
                    print("                  0x" + format(j, '08x'))
        else:
            for i in range(self.blk_num):
                print("         set", i, ":")

                # valid bits
                tmp_string = ''
                for j in range(self.way_num):
                    tmp_string += "                  valid:   " + str(self[i][j].vali)
                print(tmp_string)

                # tags
                tmp_string = ''
                for j in range(self.way_num):
                    tmp_string += "                  tag  :" + str(self[i][j].tag)
                print(tmp_string)

                # content
                for j in range(self.wd_num):
                    tmp_string = ''
                    for k in range(self.way_num):

                        ele = self[i][k].info[j]
                        if ele < 0:
                            ele = 2**32 + ele
                        tmp_string += "                  0x" + format(ele, '08x')
                    print(tmp_string)



def simulate(Instruction, InstructionHex, debugMode):

    Register = [0, 0, 0, 0, 0, 0, 0, 0]    # initialize all values in registers to 0
    # make Memory a global variable
    PC = 0
    DIC = 0

    # multi-cycle
    Cycle = 0
    threeCycles = 0 # frequency of how many instruction takes 3 cycles
    fourCycles = 0  #                                         4 cycles
    fiveCycles = 0  #                                         5 cycles

    # pipeline
    pp_cycle = 4
    lw_use_stall = 0
    brc_flush_stall = 0

    last_write_reg = ''
    last_write_reg_refresh = 0    # 0 -> false, 1 -> true
    compu_used_by_brch = 0

    # cache

    # A. DM, 4 blocks, 4 words each block
    cache_a = Blocks(1, 4, 4)
    # B. DM, 4 blocks, 2 words each block
    cache_b = Blocks(1, 4, 2)

    # C. FA, 4 blocks, 2 words each block
    cache_c = Blocks(4, 1, 2)
    # D. 2way-SA, total 8 blocks, 2 words each block
    cache_d = Blocks(2, 4, 2)
    # E. Customized cache configuration
    print("You can customize your cache configuration:")
    word = int(input("block size(wd):"))
    way = int(input("num of way:"))
    sets = int(input("num of set:"))
    cache_e = Blocks(way, sets, word)

    print("\n======== Starting simulation ========")


    finished = False
    while(not(finished)):

        DIC += 1
        pp_cycle += 1
        fetch = Instruction[PC]

        # Dead loop
        if fetch[0:32] == '00010000000000001111111111111111':
            Cycle += 3
            threeCycles += 1
            finished = True

        # ADD
        elif fetch[0:6] == '000000' and fetch[26:32] == '100000':
            if debugMode:
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" +  InstructionHex[PC] + " :" + "add $" + str(int(fetch[16:21],2)) + ",$" +str(int(fetch[6:11],2)) + ",$" + str(int(fetch[11:16],2)) )
                print("Taking 4 cycles \n")
            PC += 1
            Cycle += 4
            fourCycles += 1
            Register[int(fetch[16:21], 2)] = Register[int(fetch[6:11], 2)] + Register[int(fetch[11:16], 2)]

            last_write_reg = fetch[16:21]
            last_write_reg_refresh = 0

        # SUB
        elif fetch[0:6] == '000000' and fetch[26:32] == '100010':
            if debugMode:
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" + InstructionHex[PC] + " :" + "sub $" + str(int(fetch[16:21], 2)) + ",$" + str(int(fetch[6:11], 2)) + ",$" + str(int(fetch[11:16], 2)))
                print("Taking 4 cycles \n")
            PC += 1
            Cycle += 4
            fourCycles += 1
            Register[int(fetch[16:21], 2)] = Register[int(fetch[6:11], 2)] - Register[int(fetch[11:16], 2)]

            last_write_reg = fetch[16:21]
            last_write_reg_refresh = 0

        # XOR
        elif fetch[0:6] == '000000' and fetch[26:32] == '100110':
            if debugMode:
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" + InstructionHex[PC] + " :" + "xor $" + str(int(fetch[16:21], 2)) + ",$" + str(int(fetch[6:11], 2)) + ",$" + str(int(fetch[11:16], 2)))
                print("Taking 4 cycles \n")
            PC += 1
            Cycle += 4
            fourCycles += 1
            Register[int(fetch[16:21], 2)] = Register[int(fetch[6:11], 2)] ^ Register[int(fetch[11:16], 2)]

            last_write_reg = fetch[16:21]
            last_write_reg_refresh = 0

        # ADDI
        elif(fetch[0:6] == '001000'):
            imm = int(fetch[16:32],2) if fetch[16]=='0' else -(65535 -int(fetch[16:32],2)+1)
            if(debugMode):
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" +  InstructionHex[PC] + " :" + "addi $" + str(int(fetch[16:21],2)) + ",$" +str(int(fetch[6:11],2)) + ",$" + str(imm) )
                print("Taking 4 cycles \n")
            PC += 1
            Cycle += 4
            fourCycles += 1
            Register[int(fetch[11:16], 2)] = Register[int(fetch[6:11], 2)] + imm

            last_write_reg = fetch[11:16]
            last_write_reg_refresh = 0

        # BEQ
        elif(fetch[0:6] == '000100'):
            imm = int(fetch[16:32],2) if fetch[16]=='0' else -(65535 -int(fetch[16:32],2)+1)
            if debugMode:
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" +  InstructionHex[PC] + " :" + "beq $" + str(int(fetch[6:11],2)) + ",$" +str(int(fetch[11:16],2)) + "," + str(imm) )
                print("Taking 3 cycles \n")
            Cycle += 3
            PC += 1
            threeCycles += 1
            if Register[int(fetch[6:11], 2)] == Register[int(fetch[11:16], 2)]:
                PC = PC + imm
                brc_flush_stall += 1

            # computation used by cmp stalls
            if last_write_reg == fetch[6:11] or last_write_reg == fetch[11:16]:
                compu_used_by_brch += 1

        # BNE
        elif fetch[0:6] == '000101':
            imm = int(fetch[16:32],2) if fetch[16]=='0' else -(65535 -int(fetch[16:32],2)+1)
            if debugMode:
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" +  InstructionHex[PC] + " :" + "bne $" + str(int(fetch[6:11],2)) + ",$" +str(int(fetch[11:16],2)) + "," + str(imm) )
                print("Taking 3 cycles \n")
            Cycle += 3
            PC += 1
            threeCycles += 1
            if Register[int(fetch[6:11], 2)] != Register[int(fetch[11:16], 2)]:
                PC = PC + imm
                brc_flush_stall = 1

            # computation used by cmp stalls
            if last_write_reg == fetch[6:11] or last_write_reg == fetch[11:16]:
                compu_used_by_brch += 1

        # SLT
        elif(fetch[0:6] == '000000' and fetch[26:32] == '101010'):
            if(debugMode):
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" +  InstructionHex[PC] + " :" + "slt $" + str(int(fetch[16:21],2)) + ",$" +str(int(fetch[6:11],2)) + ",$" + str(int(fetch[11:16],2)) )
                print("Taking 4 cycles \n")
            Cycle += 4
            PC += 1
            fourCycles += 1
            Register[int(fetch[16:21],2)] = 1 if Register[int(fetch[6:11],2)] < Register[int(fetch[11:16],2)] else 0

            last_write_reg = fetch[16:21]
            last_write_reg_refresh = 0

        # SW
        elif(fetch[0:6] == '101011'):
            #Sanity check for word-addressing
            if ( int(fetch[30:32])%4 != 0 ):
                print("Runtime exception: fetch address not aligned on word boundary. Exiting ")
                print("Instruction causing error:", hex(int(fetch,2)))
                exit()
            imm = int(fetch[16:32],2)
            if(debugMode):
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" +  InstructionHex[PC] + " :" + "sw $" + str(int(fetch[6:11],2)) + "," +str(imm + Register[int(fetch[6:11],2)] - 8192) + "(0x2000)" )
                print("Taking 4 cycles \n")
            PC += 1
            Cycle += 4
            fourCycles += 1
            Memory[(imm + Register[int(fetch[6:11],2)] - 8192) // 4]= Register[int(fetch[11:16],2)] # Store word into memory

        # LW
        elif fetch[0:6] == '100011' :
            # Sanity check for word-addressing
            if int(fetch[30:32]) % 4 != 0:
                print("Runtime exception: fetch address not aligned on word boundary. Exiting ")
                print("Instruction causing error:", hex(int(fetch,2)))
                exit()
            imm = int(fetch[16:32],2)
            target_mem = imm + Register[int(fetch[6:11], 2)]

            if debugMode:
                print("Cycles " + str(Cycle) + ":")
                print("PC =" + str(PC*4) + " Instruction: 0x" + InstructionHex[PC] + " :" + "lw $" + str(int(fetch[6:11],2)) + "," +str(imm + Register[int(fetch[6:11],2)] - 8192) + "(0x2000)" )
                print("Taking 5 cycles \n")

                print("==== Cache Access Log ====")
                print("target mem: 0x" + format(target_mem, "04x"))

                # cache A
                print("A. DM, 4 blocks, 4 words each block")
                target_block_index = cache_a.get_blk_index(target_mem)
                target_block = cache_a.get_the_block_need_to_write(target_mem)
                print("   blk/set to access :", target_block_index)
                print("   valid bit         :", target_block.vali)
                print("   tag               :", target_block.tag)
                hit = cache_a.read(target_mem)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update info : no update ")

                else:
                    print("   cache update info :")
                    cache_a.show()

                # cache B
                print()
                print("B. DM, 4 blocks, 2 words each block")
                target_block_index = cache_b.get_blk_index(target_mem)
                target_block = cache_b.get_the_block_need_to_write(target_mem)
                print("   blk/set to access :", target_block_index)
                print("   valid bit         :", target_block.vali)
                print("   tag               :", target_block.tag)
                hit = cache_b.read(target_mem)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update info : no update ")

                else:
                    print("   cache update info :")
                    cache_b.show()

                print()
                print("C. FA, 4 blocks, 2 words each block")
                target_block_index = cache_c.get_blk_index(target_mem)
                target_block = cache_c.get_the_block_need_to_write(target_mem)
                print("   blk/set to access :", target_block_index)
                print("   valid bit         :", target_block.vali)
                print("   tag               :", target_block.tag)
                hit = cache_c.read(target_mem)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update info : no update ")

                else:
                    print("   cache update info :")
                    cache_c.show()

                print()
                print("D. 2way-SA, total 8 blocks, 2 words each block")
                target_block_index = cache_d.get_blk_index(target_mem)
                target_block = cache_d.get_the_block_need_to_write(target_mem)
                print("   blk/set to access :", target_block_index)
                print("   valid bit         :", target_block.vali)
                print("   tag               :", target_block.tag)
                hit = cache_d.read(target_mem)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update info : no update ")

                else:
                    print("   cache update info :")
                    cache_d.show()

                print()
                print("E. Customized cache configuration ")
                target_block_index = cache_e.get_blk_index(target_mem)
                target_block = cache_e.get_the_block_need_to_write(target_mem)
                print("   blk/set to access :", target_block_index)
                print("   valid bit         :", target_block.vali)
                print("   tag               :", target_block.tag)
                hit = cache_e.read(target_mem)
                print("   hit or not        :", hit)
                if hit:
                    print("   cache update info : no update ")

                else:
                    print("   cache update info :")
                    cache_e.show()
                print("=== Cache Log End ====\n")

            PC += 1
            Cycle += 5
            fiveCycles += 1

            # cache
            # print((imm + Register[int(fetch[6:11], 2)] - 8192) // 4)
            Register[int(fetch[11:16],2)] = Memory[(imm + Register[int(fetch[6:11], 2)] - 8192) // 4]

            last_write_reg = fetch[11:16]
            last_write_reg_refresh = 0

            # for lw-use stalls
            write2reg = fetch[11:16]
            next_instr = Instruction[PC]
            # R-type
            if next_instr[0:6] == '000000':
                if write2reg == next_instr[6:11] or write2reg == next_instr[11:16]:
                    lw_use_stall += 1
            # branch or sw
            elif next_instr[0:6] == '000100' or next_instr[0:6] == '000101' or next_instr[0:6] == '101011':
                if write2reg == next_instr[6:11] or write2reg == next_instr[11:16]:
                    lw_use_stall += 1
            # lw and other I-type
            else:
                if write2reg == next_instr[6:11]:
                    lw_use_stall += 1

        # for computation used by branch cmp stalls
        if last_write_reg:
            if last_write_reg_refresh:
                last_write_reg = ''
            last_write_reg_refresh = 1 - last_write_reg_refresh


    print("======== Finished simulation ========")
    print("PC = " + str(PC * 4))
    print("Registers:   " + ' '.join(["$%d = %d     " % (i, j) for i, j in enumerate(Register)]))
    print("Dynamic instructions count: " + str(DIC))
    print()
    print("For a multi-cycle MIPS CPU:")
    print("    Total # of cycles: " + str(Cycle))
    print("    |-   # of  take 3-cycle instruction: %d" % threeCycles)
    print("    |-   # of  take 4-cycle instruction: %d" % fourCycles)
    print("    |_   # of  take 5-cycle instruction: %d" % fiveCycles)
    print()
    print("For a pipelined MIPS CPU:")
    stalls = lw_use_stall + brc_flush_stall + compu_used_by_brch
    print("    Total # of cycles: %d" % (pp_cycle + stalls))
    print("    Total # of stalls: %d" % stalls)
    print("    |-   # of  lw-use stalls        : %d" % lw_use_stall)
    print("    |-   # of  branch-flush stalls  : %d" % brc_flush_stall)
    print("    |_   # of  compute used by brch : %d" % compu_used_by_brch)
    print()
    print("For cache configuration A:")
    print("    Hit rate: %.2f" % (cache_a.hit_num / cache_a.read_num))
    print("For cache configuration B:")
    print("    Hit rate: %.2f" % (cache_b.hit_num / cache_b.read_num))
    print("For cache configuration C:")
    print("    Hit rate: %.2f" % (cache_c.hit_num / cache_c.read_num))
    print("For cache configuration D:")
    print("    Hit rate: %.2f" % (cache_d.hit_num / cache_d.read_num))
    print("For cache configuration E:")
    print("    Hit rate: %.2f" % (cache_e.hit_num / cache_e.read_num))




def main():
    print("Welcome to ECE366 sample MIPS_sim")
    print("Please choose files to run:")
    print("1) A1.txt    2)A2.txt     3)B1.txt     4)B2.txt")
    program = ['A1.txt', 'A2.txt','B1.txt','B2.txt'][int(input())-1]
    print('please choose mode:')
    debugMode =True if  int(input("1 = debug mode         2 = normal execution\n"))== 1 else False

    I_file = open(program ,"r")
    Instruction = []            # array containing all instructions to execute
    InstructionHex = []
    for line in I_file:
        if (line == "\n" or line[0] =='#'):              # empty lines,comments ignored
            continue
        line = line.replace('\n','')
        InstructionHex.append(line)
        line = format(int(line,16),"032b")
        Instruction.append(line)


    simulate(Instruction, InstructionHex, debugMode)

if __name__ == "__main__":
    main()
