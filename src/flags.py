from operation import Operation

# Define Flags class to manage processor flags (ZF, SF, CF, OF)
class Flags:
    def __init__(self):
        self.ZF = False  # Zero Flag
        self.SF = False  # Sign Flag
        self.CF = False  # Carry Flag
        self.OF = False  # Overflow Flag

    def set_flags(self, result, op, operand1, operand2):
        """Set flags based on ALU operation result."""
        result = result & 0xFFFFFFFF
        self.ZF = result == 0
        self.SF = (result & 0x80000000) != 0
        self.CF = False
        self.OF = False
        if op in [Operation.ADD, Operation.SUB, Operation.CMP, Operation.INC, Operation.DEC]:
            if op == Operation.ADD or op == Operation.INC:
                self.CF = (operand1 + (operand2 if op != Operation.INC else 1)) > 0xFFFFFFFF
                self.OF = (((operand1 ^ (operand2 if op != Operation.INC else 1)) & 0x80000000) == 0) and ((operand1 ^ result) & 0x80000000 != 0)
            elif op == Operation.SUB or op == Operation.DEC or op == Operation.CMP:
                self.CF = operand1 < (operand2 if op != Operation.DEC else 1)
                self.OF = (((operand1 ^ (operand2 if op != Operation.DEC else 1)) & 0x80000000) != 0) and ((operand1 ^ result) & 0x80000000 != 0)
        elif op in [Operation.AND, Operation.OR, Operation.XOR, Operation.NOT]:
            self.CF = False
            self.OF = False
        elif op in [Operation.SHL, Operation.SHR]:
            self.CF = (operand1 & (1 << (31 if op == Operation.SHL else 0))) != 0
        elif op in [Operation.ROL, Operation.ROR]:
            self.CF = (result & 1) != 0
