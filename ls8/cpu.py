"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.PC = 0
        self.IR = None
        self.FL = None
        self.MAR = None
        self.MDR = None
        self.ram = [None] * 256
        self.reg = [0] * 8
        self.running = True
        self.sp = 7

        LDI = 130
        MUL = 162
        PRN = 71
        HLT = 1
        PUSH = 69
        POP = 70
        ADD = 160
        CALL = 80
        RET = 17
        CMP = 167
        JEQ = 85
        JNE = 86
        JMP = 84

        self.branchtable = {}
        self.branchtable[LDI] = self.ldi
        self.branchtable[ADD] = self.add 
        self.branchtable[MUL] = self.mul 
        self.branchtable[PRN] = self.prn 
        self.branchtable[HLT] = self.hlt 
        self.branchtable[PUSH] = self.push 
        self.branchtable[POP] = self.pop 
        self.branchtable[CALL] = self.call 
        self.branchtable[RET] = self.ret 
        self.branchtable[CMP] = self.cmp 
        self.branchtable[JEQ] = self.jeq 
        self.branchtable[JNE] = self.jne 
        self.branchtable[JMP] = self.jmp 

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("usage: file ls8.py")
            sys.exit(1)

        filename = sys.argv[1];
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()

                    if num == '':
                        continue

                    val = int(num, 2)
                    self.ram[address] = val
                    address += 1
        except FileNotFoundError:
            print("File not found")
            sys.exit(1)


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            self.FL = 0x00
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = self.FL | 0b00000001
            if self.reg[reg_a] < self.reg[reg_b]:
                self.FL = self.FL | 0b00000100
            if self.reg[reg_a] > self.reg[reg_b]:
                self.FL = self.FL | 0b00000010
        elif op == "ADD":
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] = self.reg[reg_a] % self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            self.IR = self.ram_read(self.PC)
            self.branchtable[self.IR]()

    def ram_read(self, address):
        self.MAR = address
        self.MDR = self.ram[self.MAR]
        return self.MDR

    def ram_write(self, address, value):
        self.MAR = address
        self.MDR = value
        self.ram[self.MAR] = self.MDR

    def ldi(self):
        operanda = self.ram_read(self.PC+1)
        opperandb = self.ram_read(self.PC+2)
        self.reg[operanda] = opperandb
        self.PC += 3

    def add(self):
        opperanda = self.ram_read(self.PC+1)
        opperandb = self.ram_read(self.PC+2)
        self.alu('ADD', opperanda, opperandb)
        self.PC += 3

    def mul(self):
        opperanda = self.ram_read(self.PC+1)
        opperandb = self.ram_read(self.PC+2)
        self.alu('MUL', opperanda, opperandb)
        self.PC += 3

    def prn(self):
        opperanda = self.ram_read(self.PC+1)
        print(self.reg[opperanda])
        self.PC += 2

    def hlt(self):
        self.running = False

    def push(self):
        register = self.ram_read(self.PC+1)
        value = self.reg[register]
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = value
        self.PC += 2

    def pop(self):
        register = self.ram_read(self.PC+1)
        value = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        self.reg[register] = value
        self.PC += 2

    def call(self):
        register = self.ram_read(self.PC+1)
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.PC + 2)
        self.PC = self.reg[register]

    def ret(self):
        self.PC = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def cmp(self):
        register_1 = self.ram_read(self.PC+1)
        register_2 = self.ram_read(self.PC+2)
        self.alu('CMP', register_1, register_2)
        self.PC += 3

    def jmp(self):
        register_1 = self.ram_read(self.PC+1)
        opperanda = self.reg[register_1]
        self.PC = opperanda

    def jeq(self):
        register_1 = self.ram_read(self.PC+1)
        operanda = self.reg[register_1]
        if self.FL == 1:
            self.PC = operanda
        else:
            self.PC += 2

    def jne(self):
        register_1 = self.ram_read(self.PC+1)
        operanda = self.reg[register_1]
        if self.FL is not 1:
            self.PC = operanda
        else:
            self.PC += 2
            