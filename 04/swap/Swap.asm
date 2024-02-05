// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

// Put your code here.

@R14 // get the adress of the first element
D=M

//set both min and max to point the same value as the first element
@R1
M=D

@R2
M=D

@R3 //set a counter to check if we finished the array
M=0

(LOOP)
    @R3 //check if we finished the array
    D=M
    @R15
    D=D-M
    @SWAP //if we finished the array swap the min and max
    D;JEQ

    //else (didn't finish the array)

    @R3 //we update the counter
    M=M+1
    D=M-1  //and store the index

    @R14 //we check the adress of the first element
    D=D+M

    @R4 //we save in R4 the updated adress of the next element
    M=D

    A=M
    D=M
    @R1
    A=M
    D=D-M //we check if the current element is less than the min
    @NEW_MIN
    D;JLT //if so, set a new min

    @R4 //we dereference the current element
    A=M
    D=M
    @R2
    A=M
    D=D-M //we check if the current element is greater than the max
    @NEW_MAX
    D;JGT //if so, set a new max

    @LOOP
    0;JMP


(NEW_MIN)
    @R4
    D=M //a pointer to the element we want to switch with

    @R1 //switch to new min
    M=D

    @LOOP
    0;JMP

(NEW_MAX)
    @R4
    D=M

    @R2 //switch to new max
    M=D

    @LOOP
    0;JMP

(SWAP)
    @R1
    A=M
    D=M
    
    @temp
    M=D

    @R2
    A=M
    D=M


    @R1
    A=M
    M=D

    @temp
    D=M

    @R2
    A=M
    M=D

//     @END
//     0;JMP


// (END)
//     @END
//     0;JMP