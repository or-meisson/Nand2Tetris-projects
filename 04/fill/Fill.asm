// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// This program illustrates low-level handling of the screen and keyboard
// devices, as follows.
//
// The program runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.
// 
// Assumptions:
// Your program may blacken and clear the screen's pixels in any spatial/visual
// Order, as long as pressing a key continuously for long enough results in a
// fully blackened screen, and not pressing any key for long enough results in a
// fully cleared screen.
//
// Test Scripts:
// For completeness of testing, test the Fill program both interactively and
// automatically.
// 
// The supplied FillAutomatic.tst script, along with the supplied compare file
// FillAutomatic.cmp, are designed to test the Fill program automatically, as 
// described by the test script documentation.
//
// The supplied Fill.tst script, which comes with no compare file, is designed
// to do two things:
// - Load the Fill.hack program
// - Remind you to select 'no animation', and then test the program
//   interactively by pressing and releasing some keyboard keys

(WHAT_TO_FILL)
@SCREEN
D=A
@0
M=D //PUT IN RAM[0] THE PIXEL NUMBER THAT NEEDS TO BE FILLED




(LOOP)
    @KBD
    D=M

    @PRESSED //BLACK
    D;JNE

    @NOT_PRESSED //WHITE
    D;JEQ


    @LOOP
    0;JMP



(PRESSED) //BLACK

@1
M=-1 //PUT IN RAM[1] WHAT NEEDS TO BE FILL(1111111111111111)
@FILL
0;JMP

(NOT_PRESSED) //WHITE
@1
M=0 //PUT IN RAM[1] WHAT NEEDS TO BE FILL(000000000000000)
@FILL
0;JMP

(FILL)
@1
D=M //D HOLDS EHAT NEEDS TO FILL WITH

@0
A=M
M=D //FILL THE PIXEL WITH WHATS IN RAM[1]



@0
D=M+1
@KBD
D=A-D

@0
M=M+1 //MOVE TO NEXT PIXEL
A=M 
@WHAT_TO_FILL //IF WE GET TO ZERO - WE FINISHED FILLING THE SCREEN
D;JEQ

@FILL //IF NOT WE CONTINUE THE LOOP
0;JMP














