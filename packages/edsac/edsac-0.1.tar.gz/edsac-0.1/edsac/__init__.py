#!/usr/bin/env python3
# coding: utf-8

__version__ = '0.1'

import sys

CLOOKUP = {
    int('00000', 2) : 'P',  
    int('00001', 2) : 'Q',  
    int('00010', 2) : 'W',  
    int('00011', 2) : 'E',  
    int('00100', 2) : 'R',  
    int('00101', 2) : 'T',  
    int('00110', 2) : 'Y',  
    int('00111', 2) : 'U',  
    int('01000', 2) : 'I',  
    int('01001', 2) : 'O',  
    int('01010', 2) : 'J',  
    int('01011', 2) : '#',  # PI ~ π
    int('01100', 2) : 'S',  
    int('01101', 2) : 'Z',  
    int('01110', 2) : 'K',  
    int('01111', 2) : '*',  # ASTRISK ~ *
    int('10000', 2) : '.',  # row of Blank tape
    int('10001', 2) : 'F',  
    int('10010', 2) : '@',  # THETA ~ θ
    int('10011', 2) : 'D',  
    int('10100', 2) : '!',  # PHI ~ ɸ
    int('10101', 2) : 'H',  
    int('10110', 2) : 'N',  
    int('10111', 2) : 'M',  
    int('11000', 2) : '&',  # DELTA ~ ∆
    int('11001', 2) : 'L',  
    int('11010', 2) : 'X',  
    int('11011', 2) : 'G',  
    int('11100', 2) : 'A',  
    int('11101', 2) : 'B',  
    int('11110', 2) : 'C',  
    int('11111', 2) : 'V',  
}

FLOOKUP = {
    int('00000', 2) : '0',  
    int('00001', 2) : '1',  
    int('00010', 2) : '2',  
    int('00011', 2) : '3',  
    int('00100', 2) : '4',  
    int('00101', 2) : '5',  
    int('00110', 2) : '6',  
    int('00111', 2) : '7',  
    int('01000', 2) : '8',  
    int('01001', 2) : '9',  
    int('01010', 2) : ' ',  
    int('01011', 2) : '#',  # PI ~ π
    int('01100', 2) : '\"', 
    int('01101', 2) : '+',  
    int('01110', 2) : '(',  
    int('01111', 2) : '*',  # ASTRISK ~ *
    int('10000', 2) : '.',  # row of Blank tape
    int('10001', 2) : '$',  
    int('10010', 2) : '@',  # THETA ~ θ
    int('10011', 2) : ';',  
    int('10100', 2) : '!',  # PHI ~ ɸ
    int('10101', 2) : '£',  
    int('10110', 2) : ',',  
    int('10111', 2) : '.',  
    int('11000', 2) : '&',  # DELTA ~ ∆
    int('11001', 2) : ')',  
    int('11010', 2) : '/',  
    int('11011', 2) : '#',  
    int('11100', 2) : '-',  
    int('11101', 2) : '?',  
    int('11110', 2) : ':',  
    int('11111', 2) : '=',  
}

# INSTRUCTION_SIZE = 17 # total instruction length
INITIALORDER1MARGIN = 31

class Memory(object):
    
    
    def __init__(self, size, repr):
        """
        repr := how to represent the memory map/table?
            1. show order
            2. show content
        """
        self.repr = repr
        # EDSAC I : size = 512
        # EDSAC II: size = 1024
        self.size = size
        # internal use, for Memory table representation
        self.tableSize = size + int(size / 8)
        self.order = [ "{0} {1} {2}".format('P', 0, 'S') ] * size
        self.content = [ 0 ] * size
        # 40 : constant / overwritten
        # 41 : reserved for contant zero
        # 42 : reserved for origin of current routine
        # 43 : reserved for constant one
        # 44 - 55 : reserved for use by programmer ("present parameters")
        # self.content[41] = 0
        # self.content[43] = 1
        self.initialOrders1()
    
    
    def initialOrders1(self):
        self.order[0] = "{0} {1} {2}".format('T', 0, 'S')
        self.order[1] = "{0} {1} {2}".format('H', 2, 'S') 
        self.order[2] = "{0} {1} {2}".format('T', 0, 'S')
        self.order[3] = "{0} {1} {2}".format('E', 6, 'S')
        self.order[4] = "{0} {1} {2}".format('P', 1, 'S')
        self.content[4] = 2
        self.order[5] = "{0} {1} {2}".format('P', 5, 'S')
        self.content[5] = 10
        self.order[6] = "{0} {1} {2}".format('T', 0, 'S')
        self.order[7] = "{0} {1} {2}".format('I', 0, 'S')
        self.order[8] = "{0} {1} {2}".format('A', 0, 'S')
        self.order[9] = "{0} {1} {2}".format('R', 16, 'S')
        self.order[10] = "{0} {1} {2}".format('T', 0, 'S')
        self.order[11] = "{0} {1} {2}".format('I', 2, 'S')
        self.order[12] = "{0} {1} {2}".format('A', 2, 'S')
        self.order[13] = "{0} {1} {2}".format('S', 5, 'S')
        self.order[14] = "{0} {1} {2}".format('E', 21, 'S')
        self.order[15] = "{0} {1} {2}".format('T', 3, 'S')
        self.order[16] = "{0} {1} {2}".format('V', 1, 'S')
        self.order[17] = "{0} {1} {2}".format('L', 8, 'S')
        self.order[18] = "{0} {1} {2}".format('A', 2, 'S')
        self.order[19] = "{0} {1} {2}".format('T', 1, 'S')
        self.order[20] = "{0} {1} {2}".format('E', 11, 'S')
        self.order[21] = "{0} {1} {2}".format('R', 4, 'S')
        self.order[22] = "{0} {1} {2}".format('A', 1, 'S')
        self.order[23] = "{0} {1} {2}".format('L', 0, 'S')
        self.order[24] = "{0} {1} {2}".format('A', 0, 'S')
        self.order[25] = "{0} {1} {2}".format('T', 31, 'S')
        self.order[26] = "{0} {1} {2}".format('A', 25, 'S')
        self.order[27] = "{0} {1} {2}".format('A', 4, 'S')
        self.order[28] = "{0} {1} {2}".format('U', 25, 'S')
        self.order[29] = "{0} {1} {2}".format('S', 31, 'S')
        self.order[30] = "{0} {1} {2}".format('G', 6, 'S')
        self.order[31] = "{0} {1} {2}".format('P', 0, 'S')
        # self.order[] = "{0} {1} {2}".format('P', 0, 'S')
    
    
    def __str__(self):
        width = 8
        output = "-" * 110
        output += "\nEDSAC Memory:\n\n"
        
        # Table header
        for i in range(width*2+2):
            if (i == 0): output += "          |"
            if (i < width): output += "{0:{a}{w}} |".format(i, a='>', w=9)
            elif (i == width): output += "\n"
            else: output += "{0:-{a}{w}}".format("+", a='>', w=11)
        
        # Table content
        j = 0
        for i in range(self.tableSize):
            # column 1
            if (i % (width+1) == 0):
                # if (i == 0): output += "\nR {0:{a}{w}}|".format(i, a='<', w=8)
                # else: output += "\nR {0:{a}{w}}|".format(i-1, a='<', w=8)
                if (i == 0):
                    output += "\nR {0:{a}4}+{1:{a}}|".format(j, " " * (8 - 4 - len(str(i))), a='>')
                else:
                    if (len(str(i)) == 1):
                        output += "\nR {0:{a}4}+{1:{a}}|".format(j, " " * (8 - 4 - len(str(i))), a='>')
                    elif (len(str(i)) == 2):
                        output += "\nR {0:{a}4}+{1:{a}}|".format(j, " " * (8 - 3 - len(str(i))), a='>')
                    elif (len(str(i)) == 3):
                        output += "\nR {0:{a}4}+{1:{a}}|".format(j, " " * (8 - 2 - len(str(i))), a='>')
                    elif (len(str(i)) == 4):
                        output += "\nR {0:{a}4}+{1:{a}}|".format(j, " " * (8 - 1 - len(str(i))), a='>')
            # other columns
            else:
                if (i % (width+1) == 0):
                    output += "{0:<{w}}|".format(j, w=10)
                #output += "{0:>{w}}|".format(j, w=10)#self.content[j], w=10)
                if self.repr == 1:
                    output += "{0:>{w}}|".format(self.order[j], w=10)
                elif self.repr == 2:
                    output += "{0:>{w}}|".format(self.content[j], w=10)
                j += 1
                
        output += "\n"
        output += "-" * 110
        return output



class EDSAC(object):
    
    def __init__(self, memorySize, memoryRepr):
        self.memory = Memory(size=memorySize, repr=memoryRepr)
                                # binary representation
        self.scr            = 0 # [0] * 10 # Sequence Control Register
        self.orderTank      = 0 # [0] * 17
        self.multiplier     = 0 # [0] * 35
        self.multiplicand   = 0 # [0] * 35
        self.accumulator    = 0 # [0] * 71
        
        self.programCounter = 31
        self.jump           = 0
        
        self.lastCharacterOutput = ''
        self.output = ""
        self.programLength = INITIALORDER1MARGIN
        
        self.teleprinter = "letter"
    
    
    def __str__(self):
        output = "\n"
        output += "-" * 110
        output += "\n"
        output += "{0:27}DECIMAL  BINARY\n".format(" ")
        output += "{0:>26} {1:<6}   {2:0>10}\n".format("Sequence Control Register:", self.scr, bin(self.scr)[2:])
        output += "{0:>26} {1:<6}   {2:0>17}\n".format("Order Tank:", self.orderTank, bin(self.orderTank)[2:])
        output += "{0:>26} {1:<6}   {2:0>35}\n".format("Multiplier:", self.multiplier, bin(self.multiplier)[2:])
        output += "{0:>26} {1:<6}   {2:0>35}\n".format("Multiplicand:", self.multiplicand, bin(self.multiplicand)[2:])
        output += "{0:>26} {1:<6}   {2:0>71}".format("Accumulator:", self.accumulator, bin(self.accumulator)[2:])
        return output
    
    
    def load(self, opcode, address, postfix):
        if address == None:
            address = 0
        self.memory.order[self.programLength] = "{0} {1} {2}".format(opcode, address, postfix)
        if      opcode == 'P': self.memory.content[self.programLength] = int(address)
        elif    opcode == '#': self.memory.content[self.programLength] = 11
        elif    opcode == '@': self.memory.content[self.programLength] = 18
        elif    opcode == '!': self.memory.content[self.programLength] = 20
        elif    opcode == '&': self.memory.content[self.programLength] = 24
        self.programLength += 1
    
    
    def execute(self, instruction):
        opcode, address, postfix = instruction.split(' ')
        address = int(address)
        # print("DEBUG", instruction)
        # print("DEBUG {0} {1} {2}".format(opcode, address, postfix))
        if      opcode == 'A': self.accumulator += self.memory.content[address]
        elif    opcode == 'S': self.accumulator -= self.memory.content[address]
        elif    opcode == 'H': self.multiplier = self.memory.content[address]
        elif    opcode == 'V': self.accumulator += self.memory.content[address] * self.multiplier
        elif    opcode == 'N': self.accumulator -= self.memory.content[address] * self.multiplier
        elif    opcode == 'T':
            self.memory.content[address] = self.accumulator
            self.accumulator = 0
        elif    opcode == 'U': self.memory.content[address] = self.accumulator
        elif    opcode == 'C':
            self.accumulator += self.memory.content[address] & self.multiplier
            # print("DEBUG {0} = {1} & {2}".format(self.accumulator, self.memory.content[address], self.multiplier))
        elif    opcode == 'R':
            if postfix == 'S':
                self.accumulator = self.accumulator >> address
            elif postfix == 'L':
                addressInBin = bin(address)[2:]
                addressInBin = addressInBin + "1"
                addressInDec = int(addressInBin, 2)
                self.accumulator = self.accumulator >> addressInDec
        elif    opcode == 'L':
            if postfix == 'S':
                self.accumulator = self.accumulator << address
            elif postfix == 'L':
                addressInBin = bin(address)[2:]
                addressInBin = addressInBin + "1"
                addressInDec = int(addressInBin, 2)
                self.accumulator = self.accumulator << addressInDec
        elif    opcode == 'E': 
            if self.accumulator >= 0:
                self.programCounter = address - 1
        elif    opcode == 'G': 
            if self.accumulator < 0:
                self.programCounter = address - 1
        elif    opcode == 'I': pass
        elif    opcode == 'O':
            # print self.memory.content[address]
            n = self.memory.content[address]
            n = bin(n)[2:]
            n = n[:5]
            self.io(n)
        elif    opcode == 'F': pass
                               # read the last character output for verification (never used)
        elif    opcode == 'X': pass # noop
        elif    opcode == 'Y':
            self.accumulator = self.accumulator << 34
            self.accumulator = self.accumulator >> 34
        elif    opcode == 'Z': 
            sys.stdout.write("\a") # make beep sound
            sys.stdout.flush()
        elif    opcode == '#': # shift teleprinter to figure
            self.teleprinter = "figure"
        elif    opcode == '*': # shift teleprinter to letter (default)
            self.teleprinter = "letter"
        elif    opcode == '!': # space
            self.io('10100')
        elif    opcode == '&': # line feed
            self.io('11000')
        else: pass
    
    
    def io(self, data):
        c = ''
        if self.teleprinter == "letter":
            c = CLOOKUP[int(data,2)]
        elif self.teleprinter == "figure":
            c = FLOOKUP[int(data,2)]
            
        # print("DEBUG C is",c)
        
        if c == '@': # carriage return
            self.output += "\n"
        elif c == '.': # row of blank tape
            self.output += "\n\n"
        elif c == '!': # space
            self.output += " "
        elif c == '&': # line feed
            pass
        elif c == '#': # figure shift
            pass
            # self.teleprinter = "figure"
        elif c == '*': # letter shift
            pass
            # self.teleprinter = "letter"
        # elif c == ' ' or c == " ":
        #     pass
        else:
            self.output += c
        self.lastCharacterOutput = c
  

