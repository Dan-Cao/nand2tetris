// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

    @8192 // size of screen memory map
    D=A
    @n
    M=D // n = 8K

(START)
    @i
    M=0 // i = 0
    
    @SCREEN
    D=A
    @address
    M=D  // address = 16384 (base address of the Hack screen)
    
    @fill
    M=-1  // default to black
    @KBD
    D=M
    @PAINT
    D;JGT // don't set to white if key pressed
    @fill
    M=0

(PAINT)
    @i
    D=M
    @n
    D=D-M
    @START
    D;JGE // if i>=n goto START
    
    // fill selected 16 pixels
    @fill
    D=M
    @address
    A=M
    M=D // RAM[address] = fill
    
    @i
    M=M+1 // i = i +1
    @address
    M=M+1 // address = address + 1
    
    @PAINT
    0;JMP