"""CPU functionality."""

import sys
HLT = 0b00000001
PRN = 0b01000111
LDI = 0b10000010
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # The Ram will hold the 256 bytes of memory
        self.ram = [0] * 256
        # This should be our counter as we go
        self.pc = 0
        # where we can store values in the reg
        self.reg = [0] * 8
        self.op_hlt = False

        self.reg[7] = 0xF3  # stack pointer
        self.SP = 7

        self.inst = {
            HLT: self.op_halt,
            LDI: self.op_LDI,
            MUL: self.op_mul,
            PRN: self.op_PRN,
        }

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def op_mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)

    def op_halt(self, address, value):
        self.op_hlt = True

    def op_LDI(self, address, value):
        self.reg[address] = value

    def op_PRN(self, address, operand_b):
        print(self.reg[address])

    def load(self, filename):
        """Load a program into memory."""

        address = 0

        with open(filename) as file:
            for line in file:
                comment_split = line.split('#')
                instruction = comment_split[0]

                if instruction == '':
                    continue
                # print(instruction)

                first_bit = instruction[0]

                if first_bit == "0" or first_bit == "1":

                    self.ram[address] = int(instruction[:8], 2)
                    address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        """Some instructions requires up to the next two bytes
        of data after the PC in memory to perform operations on.
        Sometimes the byte value is a register number,
        other times it's a constant value (in the case of LDI).
        Using ram_read(), read the bytes at PC+1 and PC+2
        from RAM into variables operand_a and operand_b in case
        the instruction needs them."""

        # running = True

        while not self.op_hlt:
            # Storeing the result in IR from reading
            # the memory address that is stored in register PC
            IR = self.ram[self.pc]

            # print("IR", IR)
            operand_a = self.ram_read(self.pc + 1)
            # print(operand_a)
            operand_b = self.ram_read(self.pc + 2)

            op_size = IR >> 6
            ins_set = ((IR >> 4) & 0b1) == 1

            # if IR == HLT:
            #     self.op_halt=True
            # elif IR == LDI:
            #     self.reg[operand_a]=operand_b
            #     self.pc += 3
            # elif IR == PRN:
            #     print(self.reg[operand_a])
            #     self.pc += 2
            if IR in self.inst:

                self.inst[IR](operand_a, operand_b)
            elif IR == PUSH:

                self.reg[self.SP] -= 1
                self.ram[self.reg[self.SP]] = self.reg[operand_a]

            elif IR == POP:
                self.reg[operand_a] = self.ram[self.reg[self.SP]]
                self.ram[self.reg[self.SP]] = 0
                self.reg[self.SP] += 1

            elif IR == CALL:
                self.ram[self.reg[self.SP]] = self.reg[operand_a]
                
                self.pc = self.ram[self.reg[self.SP]]
            elif IR == RET:
                self.reg[operand_a] = self.ram[self.reg[self.SP]]
                self.pc = self.reg[operand_a]

            elif IR == JMP:
                self.pc = self.reg[operand_a]

            if not ins_set:
                self.pc += op_size + 1
