
// File name: Box.asm
// Roll Number: 2501410006
// K = 06
// Box: 48 pixels wide and 20 rows tall
// Starting row: 6

(MAIN)

// Check if any key is pressed
@KBD
D=M
@DRAW
D;JNE

// No key pressed: clear the box
@CLEAR
0;JMP


// =================================
// DRAW BLACK BOX
// =================================

(DRAW)

// Starting address = 16384 + (6 * 32) = 16576
@16576
D=A
@R13
M=D

// Set row counter = 20
@20
D=A
@R14
M=D

(DRAW_LOOP)

// First word of the row
@R13
A=M
M=-1

// Move to second word
@R13
M=M+1

// Second word of the row
@R13
A=M
M=-1

// Move to third word
@R13
M=M+1

// Third word of the row
@R13
A=M
M=-1

// Move to the next screen row
// Three words written, add 30 to reach the next row
@30
D=A
@R13
M=D+M

// Decrease row counter
@R14
MD=M-1

@DRAW_LOOP
D;JGT

@MAIN
0;JMP


// =================================
// CLEAR THE BOX
// =================================

(CLEAR)

// Starting address = 16576
@16576
D=A
@R13
M=D

// Set row counter = 20
@20
D=A
@R14
M=D

(CLEAR_LOOP)

// Clear first word
@R13
A=M
M=0

// Move to second word
@R13
M=M+1

// Clear second word
@R13
A=M
M=0

// Move to third word
@R13
M=M+1

// Clear third word
@R13
A=M
M=0

// Move to the next screen row
@30
D=A
@R13
M=D+M

// Decrease row counter
@R14
MD=M-1

@CLEAR_LOOP
D;JGT

@MAIN
0;JMP
