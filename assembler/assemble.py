import argparse
from dataclasses import dataclass
from operator import contains
import os
import pathlib
import sys
import typing
import shutil


@dataclass
class FileProps:
    """Class for tracking properties of a file"""
    name: str
    path: os.path
    fullPath: os.path


def main():
    # Obtain input and output file names/locations/paths
    inputFile, outputFile = argParse()

    # Validate assembly file exsists
    if not os.path.exists(inputFile.fullPath):
        printErr("[ERROR] File '" + inputFile.fullPath + "' not found!")
        printErr("\tAborting assembly process....\n")
        exit()

    # Create an intermediate file for processing
    tempName = pathlib.Path(outputFile.fullPath).stem + ".tmp"
    intermediateFile = FileProps(tempName, outputFile.path, os.path.join(outputFile.path, tempName))
    shutil.copyfile(inputFile.fullPath, intermediateFile.fullPath)

    # Simplify intermediate file to known format
    # print("Re-formatting file...")
    stripFile(intermediateFile.fullPath)

    # link labels in the intermediate file
    # print("Linking labels...")
    labelLink(intermediateFile.fullPath)

    # Convert intermediate file to machine code
    # print("Assembling file...")
    assemble(intermediateFile.fullPath, outputFile.fullPath)

    print("Finsihed assembling: " + outputFile.name + "!\n")


# Function for converting the intermediate file to machine code and parsing instructions
def assemble(intermediateFile: os.path, outputFile: os.path):
    # At this point in the process, all mnemonics left in the file should strictly be instructions
    # or set directives at the end of the file. Thus all that's left is to parse instructions and
    # convert them to their proper machine code

    # Read all lines of file and store in array for easy modification
    lines = readFile(intermediateFile)

    # Create an array that represents the CPU's RAM to store the program in
    program = ['00'] * 16

    # Store the last address of the program section of RAM, useful for detecting erroneous 'set' writes to program data
    programEndAddress = 0

    # Assemble the file line by line
    for address, line in enumerate(lines):
        programEndAddress, program = convertInstruction(line, address, programEndAddress, program)
    
    # Write the final program RAM to the output file
    file = open(outputFile, 'w')

    # Write header
    file.write('v3.0 hex words plain\n')

    # Write program
    for line in program:
        file.write(line + " ")

    file.close()
          

# Function for converting an instruction to it's machinecode representation and validating it
# Returns the modified program array as we need the full array for the 'set' directives
def convertInstruction(line: str, address: int, programEndAddress: int, program: typing.List[int]) -> typing.Tuple[int, typing.List[str]]:
    # Get the mnemonic from the line
    mnemonic = line.split(None, 1)[0]
    machineCode = ''

    # Error on reserved instructions
    if 'res' in mnemonic.lower():
        printErr("[ERROR] Instruction '" + mnemonic + "' is reserved and should not be used!")
        printErr("\tAborting assembly process....\n")
        exit()

    # map mnemonics to machine code
    match mnemonic.lower():
        case 'nop':
            machineCode = generateMachineCode(int('0000', 2), line)

        case 'lda':
            machineCode = generateMachineCode(int('0001', 2), line, 1, [range(0, 16)])

        case 'add':
            machineCode = generateMachineCode(int('0010', 2), line, 1, [range(0, 16)])

        case 'sub':
            machineCode = generateMachineCode(int('0011', 2), line, 1, [range(0, 16)])

        case 'sta':
            machineCode = generateMachineCode(int('0100', 2), line, 1, [range(0, 16)])

        case 'ldi':
            machineCode = generateMachineCode(int('0101', 2), line, 1, [range(0, 8)])

        case 'jmp':
            machineCode = generateMachineCode(int('0110', 2), line, 1, [range(0, 16)])

        case 'jc':
            machineCode = generateMachineCode(int('0111', 2), line, 1, [range(0,16)])

        case 'jz':
            machineCode = generateMachineCode(int('1000', 2), line, 1, [range(0,16)])


        case 'res6':
            machineCode = generateMachineCode(int('1001', 2), line)
        case 'res7':
            machineCode = generateMachineCode(int('1010', 2), line)
        case 'res8':
            machineCode = generateMachineCode(int('1011', 2), line)
        case 'res9':
            machineCode = generateMachineCode(int('1100', 2), line)


        case 'clr':
            machineCode = generateMachineCode(int('1101', 2), line)

        case 'out':
            machineCode = generateMachineCode(int('1110', 2), line)

        case 'hlt':
            machineCode = generateMachineCode(int('1111', 2), line)

        # Take care of the assembly directive 'set'
        case 'set':
            validateNumArgs(line, 2)
            args = validateArgs(line, [range(0, 16), range(0, 256)])
            setAddress, value = int(''.join(('0x', args[:1])), 16), int(''.join(('0x', args[1:3])), 16)

            # Perform a simple check to make sure the 'set' directive is not overwritting program data
            if setAddress in range(0, programEndAddress+1):
                printErr("[ERROR] Set directive attempting to overwrite program memroy!")
                printErr("\tAttempted wrtie address: " + str(setAddress))
                printErr("\tProgram memory address range: " + str(range(0,programEndAddress+1)) + "\n")
                printErr("\tAborting assembly process....\n")
                exit()

            # Finish 'set' directive
            program[setAddress] = f'{value:02x}'
            return programEndAddress, program

        case _:
            printErr("[ERROR] Instruction '" + mnemonic + "' is not valid!")
            printErr("\tAborting assembly process....\n")
            exit()
    
    # Update the program RAM and end address
    programEndAddress = address
    # program[address] = int(''.join(('0x', machineCode)), 16)
    program[address] = machineCode
    return programEndAddress, program


# This function generates machine code for an instruction
# Instruction   -> nibble representing instruction
# line          -> line of assembly containgin mnemonic and its arguments
# numArgs       -> number of arguments instruction has
# ragnes        -> list of numeric ranges for each argument
# Returns a byte as a string in hex without '0x' that represents the machine code
def generateMachineCode(instruction: int, line: str, numArgs: int = 0, ranges: typing.List[typing.Iterable[int]] = range(0,1)) -> str:
    machineCode = f'{instruction:01x}'
    validateNumArgs(line, numArgs)
    if numArgs > 0:
        machineCode += validateArgs(line, ranges)
        return machineCode

    # We are here if instruction doesn't contain arguments so pad it before returning
    return machineCode + f'{0:01x}'


# Function for validating type of argument
# In this instruction set all arguments have to be integers
# so we will only validate that the integers are in the correct range
# and that the argument is indeed an integer
# Returns all arguments concatenated from left to right as bytes in hex without '0x' in string format
def validateArgs(line: str, ranges: typing.List[typing.Iterable[int]]) -> str:
    args = line.split(None, 1)[1]
    args = args.split()
    numArgs = len(args)

    # Validate that instructions where programmed properly by checinig arg length against list of ranges
    if numArgs != len(ranges):
        printErr("[ERROR] Instruction '" + line.split(None, 1)[0] + "' was not programmatically setup correctly!\n")
        printErr("\tGo back to the program and make sure that the list of ranges matches the expected number of")
        printErr("\tinstruction arguments.\n")
        printErr("\tNumber of arguments: " + str(numArgs))
        printErr("\tNumber of ranges: " + str(len(ranges)) + "\n")
        printErr("\tAborting assembly process....\n")
        exit()
    
    # Make sure all arguments are valid numbers
    for i, arg in enumerate(args):
        try:
            args[i] = int(arg, 16)
        except ValueError:
            printErr("[ERROR] The argument '" + str(arg) + "' is not a valid integer!\n")
            printErr("\tFor the line: " + line)
            printErr("\tAborting assembly process....\n")
            exit()
        
        # Make sure hex representation is correct if user tried to write it without '0x'
        if '0x' not in arg:
            printErr("[ERROR] The argument '" + str(arg) + "' is not a valid hex representation!\n")
            printErr("\tFor the line: " + line)
            printErr("\tAborting assembly process....\n")
            exit()
    
    # Place to save arguments to and return
    convertedArgs = ''
    # Validate argument range
    for i, numRange in enumerate(ranges):
        # The argument must be within its range to be valid
        if int(args[i]) in numRange:
            convertedArgs += f'{args[i]:01x}'
            continue

        # Argument not incorrect range
        printErr("[ERROR] The argument '" + str(args[i]) + "' is not within the " + str(numRange) + "!\n")
        printErr("\tFor the line: " + line + "\n")
        printErr("\tAborting assembly process....\n")
        exit()

    # Done Converting
    return convertedArgs


# Function for getting number of arguments passed to an instruction
def validateNumArgs(line: str, numArgs: int):
    mnemonic = line.split(None, 1)[0]

    # Check if instruction has arguments
    try:
        args = line.split(None, 1)[1]
    except IndexError:
        # Intsruction doesn't have arguments and that's correct
        if numArgs == 0:
            return
        
        # Instruction doesn't have arguments but should have multiple...
        printErr("[ERROR] Instruction '" + mnemonic + "' should have " + str(numArgs) + " argument/s!")
        printErr("\tLine: " + line)
        printErr("\tAborting assembly process....\n")
        exit()
    
    # Instruction has more arguments than it should have, or not enough in some cases
    if len(args.split(None, 1)) != numArgs:
        printErr("[ERROR] Instruction '" + mnemonic + "' should only have " + str(numArgs) + " arguments/!")
        printErr("\tLine: " + line)
        printErr("\tAborting assembly process....\n")
        exit()
    
    # Instruction has correct amount of args if here
    return


# Function for linking labels to where they are referrenced
def labelLink(intermediateFile: os.path):
    # Method of resolving links
    #   Find first label definition
    #   Pop definition from file
    #   Get address for that label
    #   Find all references to that label and replace with address
    #   Repeat for remaining labels

    # Read all lines of files and store in array for easy modification
    lines = readFile(intermediateFile)

    # Get number of labels and run label error detection
    numLabels = 0
    labels = []
    for line in lines:
        if ':' in line:
            numLabels += 1
            labels.append(line.split(':')[0])

            # Check if multiple labels on same line error exists
            if len(line.split(':')) != 2:
                printErr("[ERROR] Multi label definition found on single line!")
                printErr("\t" + line)
                printErr("\tAborting assembly process....\n")
                exit()
            
            # Check that nothing comes after ':'
            if not line.split(':')[1].isspace():
                printErr("[ERROR] Unknown text found aftet label!")
                printErr("\t" + line)
                printErr("\tAborting assembly process....\n")
                exit()
            
            # Check that nothing is before label
            if len(line.split()) != 1:
                printErr("[ERROR] Multiple symbols found before label!")
                printErr("\t" + line)
                printErr("\tAborting assembly process....\n")
                exit()
            
            # Check that label is defined
            if line.split(':')[0] == '':
                printErr("[ERROR] Label not defined!")
                printErr("\t" + line)
                printErr("\tAborting assembly process....\n")
                exit()
            
            # Make sure label is only defined once
            if len(labels) != len(set(labels)):
                printErr("[ERROR] Duplicate label defined!")
                printErr("\t" + line)
                printErr("\tAborting assembly process....\n")
                exit()

    # Perform label linking
    for label in labels:
        # Get address label refrences and remove it from program
        labelAddress = lines.index(label + ":\n")
        lines.pop(labelAddress)

        # Resolve refrences to label
        for i in range(len(lines)):
            if label in lines[i]:
                lines[i] = lines[i].replace(label, hex(labelAddress))

    # Wrtie results to intermeddiate file
    writeFile(intermediateFile, lines)


# Method for striping anything unecessary from input file and converting it to standard format
def stripFile(intermediateFile: os.path):
    # Read all lines of files and store in array for easy modification
    lines = lines = readFile(intermediateFile)

    # Strip Comments
    for i, _ in enumerate(lines):
        if ';' in lines[i]:
            lines[i] = lines[i].split(';', 1)[0]
    
    # Strip empty lines
    tempLines = []
    lines = list(filter(None, lines))
    for i, line in enumerate(lines):
        if line.isspace():
            continue

        tempLine = ''
        for part in line.split():
            tempLine += part + ' '
        tempLine = tempLine.strip() + '\n'
        tempLines.append(tempLine)
    lines = tempLines

    # Set all characters to lowercase
    for i in range(len(lines)):
        lines[i] = lines[i].lower()

    # Move all set directives to end of file and remove the ',' from them
    directives = []
    for i in range(len(lines)-1, -1, -1):
        if lines[i].split()[0] == 'set':
            directives.append(lines[i])
            lines.pop(i)
    
    for i in range(len(directives)):
        lines.append(directives[i].replace(',', ' '))

    # Set all decimal numbers to hex representation
    for i in range(len(lines)):
        tokens = []
        for token in lines[i].split():
            if token.isnumeric():
                tokens.append(hex(int(token)))
                continue
            tokens.append(token)
        
        tempLine = ''
        for token in tokens:
            tempLine += token + ' '
        lines[i] = tempLine.strip() + '\n'
    
    # Wrtie the parsed intermeddiate file
    writeFile(intermediateFile, lines)


# Argument Parsing
def argParse() -> typing.Tuple[FileProps]:
    # Instantiate the parser and parse arguments
    parser = argparse.ArgumentParser(description='The SAP-1 Assembler!')
    parser.add_argument('input_file', type=str, help="The file to assemble")
    parser.add_argument('output_file', type=str, nargs='?', default="out.bin", help="Output file path and name. Default -> out.bin")
    args = parser.parse_args()

    inputFullPath = os.path.abspath(args.input_file)
    outputFullPath = os.path.abspath(args.output_file)

    inputFile = FileProps(os.path.basename(inputFullPath), os.path.dirname(inputFullPath), inputFullPath)
    outputFile = FileProps(os.path.basename(outputFullPath), os.path.dirname(outputFullPath), outputFullPath)
    
    return (inputFile, outputFile)


# Function for reading a file and returning each line as a section of an array
def readFile(filePath: os.path) -> typing.List[str]:
    # Read all lines of files and store in array for easy modification
    file = open(filePath, 'r')

    lines = []
    for line in file:
        lines.append(line)

    file.close()
    return lines


# Function for writing lines to a file
def writeFile(filePath: os.path, lines: typing.List[str]):
    # Wrtie the parsed intermeddiate file
    file = open(filePath, 'w')
    file.writelines(lines)
    file.close()


# Easy error printing
def printErr(msg: str):
    print(msg, file=sys.stderr)


# Easy way to clear screen
def clearScreen():
    os.system('cls' if os.name=='nt' else 'clear')

# Easy printing of FileProps dataclass
def printFileProps(fileProps: FileProps):
    print("File Name: " + fileProps.name)
    print("File Path: " + fileProps.path)
    print("File Full Path: " + fileProps.fullPath + "\n")


if __name__ == "__main__":
    # clearScreen()
    main()
