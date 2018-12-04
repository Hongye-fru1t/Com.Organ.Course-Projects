.data
T: .word 0xABCDEF23
best_matching_score: .word -1 # best score = ? within [0, 32]
best_matching_count: .word -1 # how many patterns achieve the best score? 
Pattern_Array: .word 0xF, 0xFF, 0xFFF, 0xFFFF, 0xFFFFF, 0xFFFFFF, 0xFFFFFFF, 0xFFFFFFFF, 0xEEEEEEEE, 0xDDDDDDDD, 0xCCCCCCCC, 0xBBBBBBBB, 0x77777777, 0x33333333, 0xAAAAAAAA, 0xFFFF0000, 0xFFFF, 0xCCCCCCCC, 0x66666666, 0x99999999

.text
	lw $8, 0x2000($0)
	addi $10,$0,0x200C
	addi $16,$0,20    # exit traversal flag
	
	addi $17,$17,-1   # the greatest matching score
	addi $15,$15,0    # the greatest score counter

traversal:
	lw $13,0x0($10)
	xor $13,$13,$8
	
	# count 1's in a 32bit number
	xori $13,$13,0xFFFFFFFF
	srl $14,$13,1
	andi $13,$13,0x55555555   # imm used as filters to count 1's in a 32-bit binary number
	andi $14,$14,0x55555555
	addu $13,$13,$14
	
	srl $14,$13,2
	andi $13,$13,0x33333333
	andi $14,$14,0x33333333
	addu $13,$13,$14
	
	srl $14,$13,4
	andi $13,$13,0x07070707
	andi $14,$14,0x07070707
	addu $13,$13,$14
	
	srl $14,$13,8
	andi $13,$13,0x000F000F
	andi $14,$14,0x000F000F
	addu $13,$13,$14

	srl $14,$13,16
	andi $13,$13,0x0000001F
	andi $14,$14,0x0000001F
	addu $13,$13,$14         # the number of 1's is stored in $13

count_out:
	beq $17,$13,equal	#if both of the two scores are equal
	slt $18,$17,$13
	beq $18,$0,pass         # if current score is greater than biggest score
	
greater:			# if current score is greater than biggest score
	add $17,$0,$13     # save the biggest score
	addi $15,$0,1	   # set the counter to 1
	j pass
equal:
	addi $15,$15,1
pass:
	addi $10,$10,4    # prepare for next iteration
	
	addi $16,$16,-1
	beq $16,$0,trave_out
	j traversal
	
trave_out:
	sw $17,0x2004($0)  # save the greatest matching score
	sw $15,0x2008($0)  # save the matching numbers
