import typing


# Define Micro-code bits
HLT = int('100000000000000000000000', 2)
MI  = int('10000000000000000000000', 2)
RI  = int('1000000000000000000000', 2)
RO  = int('100000000000000000000', 2)
II  = int('10000000000000000000', 2)
IO  = int('1000000000000000000', 2)
AI  = int('100000000000000000', 2)
AO  = int('10000000000000000', 2)
BI  = int('1000000000000000', 2)
BO  = int('100000000000000', 2)
EO  = int('10000000000000', 2)
SO  = int('1000000000000', 2)
FI  = int('100000000000', 2)
OI  = int('10000000000', 2)
OC  = int('1000000000', 2)
O2  = int('100000000', 2)
CE  = int('10000000', 2)
CI  = int('1000000', 2)
CO  = int('100000', 2)
JC  = int('10000', 2)
JZ  = int('1000', 2)

NXT = int('1', 2)

# Define Instructions
instructions = {
    "NOP":   int('0000', 2),
    "LDA":   int('0001', 2),
    "ADD":   int('0010', 2),
    "SUB":   int('0011', 2),
    "STA":   int('0100', 2),
    "LDI":   int('0101', 2),
    "JMP":   int('0110', 2),
    "JC":    int('0111', 2),
    "JZ":    int('1000', 2),

    "RES6":  int('1001', 2),
    "RES7":  int('1010', 2),
    "RES8":  int('1011', 2),
    "RES9":  int('1100', 2),

    "CLR":   int('1101', 2),
    "OUT":   int('1110', 2),
    "HLT":   int('1111', 2),
}

# Define Micro-steps
t0 = int('000', 2)
t1 = int('001', 2)
t2 = int('010', 2)
t3 = int('011', 2)
t4 = int('100', 2)
t5 = int('101', 2)
t6 = int('110', 2)
t7 = int('111', 2)
t = [t0, t1, t2, t3, t4, t5, t6, t7]

# Define Fetch Cycles
FETCH = [CO|MI, RO|II|CE]


# Generate the micro-code ROM
# 
# Micro-code ROM Addressing scheme:
#   i i i i t t t
#   where:
#       i -> is the binary representation of the instruction
#       t -> is the current micro-code step
# 
def main():
    file = open("./microcode-rom", 'w')
    file.write("v3.0 hex words plain\n")

    for mnemonic in instructions:

        # Binary representation of the mnemonic
        instruction = instructions[mnemonic]

        # Treat reserved instructions as NOP
        if "RES" in mnemonic:
            Write_NOP(instruction, file)
            continue

        match mnemonic:

            case "NOP":
                Write_NOP(instruction, file)

            case "LDA":
                Write_LDA(instruction, file)

            case "ADD":
                Write_ADD(instruction, file)

            case "SUB":
                Write_SUB(instruction, file)

            case "STA":
                Write_STA(instruction, file)
            
            case "LDI":
                Write_LDI(instruction, file)

            case "JMP":
                Write_JMP(instruction, file)

            case "JC":
                Write_JC(instruction, file)
            
            case "JZ":
                Write_JZ(instruction, file)
            

            case "RES6":
                Write_RES6(instruction, file)
            
            case "RES7":
                Write_RES7(instruction, file)
            
            case "RES8":
                Write_RES8(instruction, file)

            case "RES9":
                Write_RES9(instruction, file)

            
            case "CLR":
                Write_CLR(instruction, file)
            
            case "OUT":
                Write_OUT(instruction, file)

            case "HLT":
                Write_HLT(instruction, file)

            case _:
                print("Warning: No case for instruction -> " + mnemonic)
                Write_NOP(instruction, file)

    file.close()


# Generate NOP Micro-code for an instruction
def Write_NOP(instruction: int, file: typing.TextIO):
    file.writelines(Gen_Microcode(instruction, NXT))
    
# Generate LDA Micro-code for an instruction
def Write_LDA(instruction: int, file: typing.TextIO):
    i2 = IO|MI
    i3 = RO|AI

    file.writelines(Gen_Microcode(instruction, i2, i3))

# Generate ADD Micro-code for an instruction
def Write_ADD(instruction: int, file: typing.TextIO):
    i2 = IO|MI
    i3 = RO|BI
    i4 = EO|AI|FI

    file.writelines(Gen_Microcode(instruction, i2, i3, i4))

# Generate SUB Micro-code for an instruction
def Write_SUB(instruction: int, file: typing.TextIO):
    i2 = IO|MI
    i3 = RO|BI
    i4 = SO|EO|AI|FI

    file.writelines(Gen_Microcode(instruction, i2, i3, i4))

# Generate STA Micro-code for an instruction
def Write_STA(instruction: int, file: typing.TextIO):
    i2 = IO|MI
    i3 = AO|RI

    file.writelines(Gen_Microcode(instruction, i2, i3))

# Generate LDI Micro-code for an instruction
def Write_LDI(instruction: int, file: typing.TextIO):
    i2 = IO|AI

    file.writelines(Gen_Microcode(instruction, i2))

# Generate JMP Micro-code for an instruction
def Write_JMP(instruction: int, file: typing.TextIO):
    i2 = IO|CI

    file.writelines(Gen_Microcode(instruction, i2))

# Generate JC Micro-code for an instruction
def Write_JC(instruction: int, file: typing.TextIO):
    i2 = JC

    file.writelines(Gen_Microcode(instruction, i2))

# Generate JZ Micro-code for an instruction
def Write_JZ(instruction: int, file: typing.TextIO):
    i2 = JZ

    file.writelines(Gen_Microcode(instruction, i2))


# Generate RES6 Micro-code for an instruction
def Write_RES6(instruction: int, file: typing.TextIO):
    i2 = NXT

    file.writelines(Gen_Microcode(instruction, i2))

# Generate RES7 Micro-code for an instruction
def Write_RES7(instruction: int, file: typing.TextIO):
    i2 = NXT
    
    file.writelines(Gen_Microcode(instruction, i2))

# Generate RES8 Micro-code for an instruction
def Write_RES8(instruction: int, file: typing.TextIO):
    i2 = NXT
    
    file.writelines(Gen_Microcode(instruction, i2))

# Generate RES9 Micro-code for an instruction
def Write_RES9(instruction: int, file: typing.TextIO):
    i2 = NXT
    
    file.writelines(Gen_Microcode(instruction, i2))


# Generate CLR Micro-code for an instruction
def Write_CLR(instruction: int, file: typing.TextIO):
    i2 = OC

    file.writelines(Gen_Microcode(instruction, i2))

# Generate OUT Micro-code for an instruction
def Write_OUT(instruction: int, file: typing.TextIO):
    i2 = AO|OI

    file.writelines(Gen_Microcode(instruction, i2))

# Generate HLT Micro-code for an instruction
def Write_HLT(instruction: int, file: typing.TextIO):
    i2 = HLT

    file.writelines(Gen_Microcode(instruction, i2))
    

# Generate Microcode for each specified step for a given instruction
# This function returns the lines needed for writing to the Micro-Code ROM
def Gen_Microcode(instruction: int, i2: int, i3: int = int('00001', 16), i4: int = int('00001', 16), i5: int = int('00001', 16), i6: int = int('00001', 16), i7: int = int('00001', 16)) -> typing.List[str]:
    lines: typing.List[str] = []
    
    for step in t:
        romAddress = "{0:02x}: ".format(int(str(f'{instruction:x}' + f'{t[step]:x}'), 16))
        romAddress = ""

        # Define Fetch Cycle
        if(step == t0 or step == t1):
            microcode = "{0:06x} ".format(FETCH[step])
            lines.append(romAddress + microcode)
            continue

        if step == t2:
            microcode = "{0:06x} ".format(i2)
        elif step == t3:
            microcode = "{0:06x} ".format(i3)
        elif step == t4:
            microcode = "{0:06x} ".format(i4)
        elif step == t5:
            microcode = "{0:06x} ".format(i5)
        elif step == t6:
            microcode = "{0:06x} ".format(i6)
        elif step == t7:
            microcode = "{0:06x}\n".format(i7)
        else:
            print("ERROR: Unknown time step -> " + str(step))
            exit()
            
        lines.append(romAddress + microcode)
    
    return lines


if __name__ == "__main__":
    main()
