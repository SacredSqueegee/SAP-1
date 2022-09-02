# SAP-1
Ben Eaters SAP-1 Implemented by Me.

### Recuirements:
  - Logisim Evolution
  - Python 10+

### What's Included / Project Organization:
The Logisim Evolution circuit file is located in the root directory.

Also in the root directory are ROMs for the Output Control Unit (OCU) and Microcode.
The Microcode ROM has its own python file for generating it.
  - This python file should hopefully make adding more instructions and micro-ops easier

In the documentation folder is a PDF going over the specification for the instructions and micro-code
  - At the end of the document is a more detailed description of the instructions implemented on the CPU

Example code is in the examples folder and includes both assembly and machine code files.

### Background:
I went through and implemented Ben's CPU in Logisim Evolution trying to keep as true to the original architecture as possible. For the most part everything is the same except I kept/added a few extra control lines and instructions. While working on this project I wanted to document everything as much as possible and make adding additional functionality "easier" (you can only add so much functionality with 4 bytes of RAM and 24 control lines). Some of this functionality includes a microcode ROM programmer and an assembler. The goal with these two python programs was to make adding new instructions easier (microcode programmer), and make writing complex programs easier (assembler). The assembler is super basic but does include some nice features. I've added labels and set directives (allow you to set specific addresses in RAM to a value). There is also very basic error checking in the assembler so programmer beware.

### CPU Overview:
The entire CPU is emulated using Logisim Evolution. The microcode was implemented with a hybrid approach. The fetch cycle is hardwired while the instruction execution cycles are accomplished via a microcode ROM. A snippet of this can be seen in the first image below. I did try to document and comment the project as much as possible but kinda got lazy along the way as I wanted to move on to the next iteration. If something doesn't make sense or sounds like I had a stroke in the middle of a sentence let me know and I'll try to clarify and update documentation.

---

### Last but not least there is an assembler written in python in the assembler folder.
  - Running the file with -h or --help should dispaly the usage information
  - Hopefully if you decide to add new instructions/micro-ops it will be somewhat easy to add that in

### More info on the assembler:
  - ';' are treated as comments. Anything after them is completely ignored
  - only one instruction per line
  - instructions can be what ever case you want. 'NoP' is completely valid.
  - argumenst must come after the instruction on the same line. Spaces and tabs do not matter
  - Memory is mapped as such:
    - address 0 is the first line in the file
    - address 16 will be the last line in the file
    - there is no error checking to make sure that your program is only 16 bytes long(over sight on my part, oops...)
  - Labels are supported. To create a label type your label name followed by ':'.
    - labels must be one word.
    - labels can contain numbers.
    - lavels cannot contain spaces
    - To use a label simply insert the labels name without the ':' in place of an instruction
    - labels are essentailly fancy address pointers
    - Ex) jump to label -> JMP labelName
    - technically as labels get resolved to memory addresses, you can use them in instructions such as ADD as the memroy address is a valid number(you probably don't ever want to do that.... but its an option... Well.. Maybe we'll just call it a feature!)
  - 'set' directive. This fancy "instruction" will set any byte in memory to some value
    - The 'set' directive works like this: SET 0xf, 0xff
      - This sets address 15 to 255
      - There are checks in the assembler that wont let you write to the program section of RAM. So don't over write your code with these things.
      - The program section of code is calculated each time and is only the size of how many instructions make up your program.
      - Also, the comma is optional so if you want to use a space you can.
  - There is "some" error checking. it is very minimal and sucky but should keep you from making a few basic mistakes.
    - This is very much a programmer be aware situation
  - One more thing, any integer used can be in decimal or hex. If you want to use hex you must prefix the value with '0x'
    - These are both valid:
      - ADD 0xa
      - ADD 10
  - Oh, and negative numbers are not yet implemented in the assembeler so this would not work:
    - ldi -4
    - ldi -0x4
