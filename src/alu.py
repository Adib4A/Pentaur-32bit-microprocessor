from operation import Operation

# ALU class to perform arithmetic and logical operations
class ALU:
    def execute(self, op, operand1, operand2):
        """Execute the specified ALU operation, ensuring 32-bit results."""
        if op == Operation.ADD:
            return (operand1 + operand2) & 0xFFFFFFFF
        elif op == Operation.SUB:
            return (operand1 - operand2) & 0xFFFFFFFF
        elif op == Operation.MOV:
            return operand2 & 0xFFFFFFFF
        elif op == Operation.AND:
            return (operand1 & operand2) & 0xFFFFFFFF
        elif op == Operation.OR:
            return (operand1 | operand2) & 0xFFFFFFFF
        elif op == Operation.XOR:
            return (operand1 ^ operand2) & 0xFFFFFFFF
        elif op == Operation.NOT:
            return (~operand1) & 0xFFFFFFFF
        elif op == Operation.SHL:
            return (operand1 << operand2) & 0xFFFFFFFF
        elif op == Operation.SHR:
            return (operand1 >> operand2) & 0xFFFFFFFF
        elif op == Operation.ROL:
            return ((operand1 << operand2) | (operand1 >> (32 - operand2))) & 0xFFFFFFFF
        elif op == Operation.ROR:
            return ((operand1 >> operand2) | (operand1 << (32 - operand2))) & 0xFFFFFFFF
        elif op == Operation.INC:
            return (operand1 + 1) & 0xFFFFFFFF
        elif op == Operation.DEC:
            return (operand1 - 1) & 0xFFFFFFFF
        elif op == Operation.CMP:
            return (operand1 - operand2) & 0xFFFFFFFF
        else:
            raise ValueError(f"Operation {op} is not supported")
