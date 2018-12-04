# Project 1   Calculate the result of "6^P mod 17"
# Author: Yihua PU

.data
P: .word 201
R: .word -1           # the result

even_result: .word 1,2,4,8,16,15,13,9
odd_result: .word 6,12,7,14,11,5,10,3
# the steps and ideas about how to 
# caculate these numbers are on my scratch paper attached below.

.text       
	lw $8, 0x2000($0)    # load the P into register
	andi $9,$8,1         #  get the lowest bit of P
	bne $9,$0,odd        #  P is even or odd ?
even:
	andi $8,$8,0xF       # "6^P mod 17" have 16-number-cycle. So P = P mod 16
	sll $8,$8,1          # relative word address = P*2 
	addi $10,$0,0x2008   # the address of even_result array
	add $10,$10,$8	     # the address of answer
	j then
odd:
	andi $8,$8,0xF       # "6^P mod 17" have 16-number-cycle. So P = P mod 16
	addi $8,$8,-1        # relative word address = (P-1)*2 
	sll $8,$8,1
	addi $10,$0,0x2028   # the address of odd_result array
	add $10,$10,$8       # the address of answer
then:
	lw $11,($10)
	sw $11,0x2004($0)
	


