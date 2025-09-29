from alu import ALU, Operation
from registers import RegisterFile, SegmentRegisters, Flags
from memory import Memory
import logging
import re

# Control unit class to manage instruction execution
class ControlUnit:
    def __init__(self):
        self.alu = ALU()
        self.register_file = RegisterFile()
        self.memory = Memory()
        self.segment_regs = SegmentRegisters()
        self.flags = Flags()
        self.ports = {}  # Simulated I/O ports
        self.labels = {}  # Jump labels
        self.jump_to = None  # Jump target index

    def decode_instruction(self, instruction):
        """Parse and validate an instruction."""
        try:
            parts = [part.replace(',', '') for part in instruction.strip().split()]
            if not parts:
                return None, None, None, None
            op = parts[0].upper()
            if op not in [e.value for e in Operation]:
                raise ValueError(f"Instruction {op} is not valid")
            op = Operation(op)
            if op in [Operation.MOV, Operation.MOVSEG, Operation.NOT, Operation.INC, Operation.DEC, Operation.LOAD, Operation.STORE, Operation.IN, Operation.OUT, Operation.CMP]:
                if len(parts) != 3:
                    raise ValueError(f"{op.value} instruction requires two arguments")
                if op == Operation.LOAD:
                    return op, parts[1].upper(), parts[2], None
                elif op == Operation.STORE:
                    return op, parts[2], parts[1].upper(), None
                elif op == Operation.IN:
                    dest = parts[1].upper()
                    src1 = parts[2]
                    return op, dest, src1, None
                elif op == Operation.OUT:
                    src1 = parts[1].upper()
                    dest = parts[2]
                    return op, dest, src1, None
                elif op == Operation.CMP:
                    src1 = parts[1].upper() if parts[1].upper() in self.register_file.registers else parts[1]
                    src2 = parts[2].upper() if parts[2].upper() in self.register_file.registers else parts[2]
                    return op, None, src1, src2
                elif op in [Operation.NOT, Operation.INC, Operation.DEC]:
                    dest = parts[1].upper()
                    src1 = parts[2].upper() if parts[2].upper() in self.register_file.registers else parts[2]
                    return op, dest, src1, None
                elif op == Operation.MOV:
                    dest = parts[1].upper()
                    src1 = parts[2].upper() if parts[2].upper() in self.register_file.registers else parts[2]
                    return op, dest, src1, None
                elif op == Operation.MOVSEG:
                    dest = parts[1].upper()
                    if dest not in self.segment_regs.segments:
                        raise ValueError(f"Invalid segment register {dest}")
                    src1 = parts[2]
                    return op, dest, src1, None
            elif op in [Operation.PUSH, Operation.POP]:
                if len(parts) != 2:
                    raise ValueError(f"{op.value} instruction requires one argument")
                if op == Operation.PUSH:
                    src1 = parts[1].upper() if parts[1].upper() in self.register_file.registers else parts[1]
                    return op, None, src1, None
                elif op == Operation.POP:
                    dest = parts[1].upper()
                    return op, dest, None, None
            elif op in [Operation.ADD, Operation.SUB, Operation.AND, Operation.OR, Operation.XOR, Operation.SHL, Operation.SHR, Operation.ROL, Operation.ROR]:
                if len(parts) != 4:
                    raise ValueError(f"{op.value} instruction requires three arguments")
                dest = parts[1].upper()
                src1 = parts[2].upper() if parts[2].upper() in self.register_file.registers else parts[2]
                src2 = parts[3].upper() if parts[3].upper() in self.register_file.registers else parts[3]
                return op, dest, src1, src2
            elif op in [Operation.JMP, Operation.JE, Operation.JNE, Operation.JG, Operation.JL]:
                if len(parts) != 2:
                    raise ValueError(f"{op.value} instruction requires one argument (label)")
                dest = parts[1]
                if dest not in self.labels:
                    raise ValueError(f"Label {dest} not found")
                return op, dest, None, None
        except Exception as e:
            raise ValueError(f"Error parsing instruction: {str(e)}")

    def execute_instruction(self, op, dest, src1, src2):
        """Execute a decoded instruction and return result string."""
        logging.info(f"Executing instruction: {op} {dest} {src1} {src2}")
        try:
            if op == Operation.MOV:
                value = self.register_file.read(src1) if src1 in self.register_file.registers else int(src1, 0)
                self.register_file.write(dest, value)
                return f"{op.value} {dest}, {src1}"
            elif op in [Operation.ADD, Operation.SUB, Operation.AND, Operation.OR, Operation.XOR, Operation.SHL, Operation.SHR, Operation.ROL, Operation.ROR]:
                val1 = self.register_file.read(src1) if src1 in self.register_file.registers else int(src1, 0)
                val2 = self.register_file.read(src2) if src2 in self.register_file.registers else int(src2, 0)
                result = self.alu.execute(op, val1, val2)
                self.flags.set_flags(result, op, val1, val2)
                self.register_file.write(dest, result)
                return f"{op.value} {dest}, {src1}, {src2} -> {result}"
            elif op in [Operation.NOT, Operation.INC, Operation.DEC]:
                val1 = self.register_file.read(src1) if src1 in self.register_file.registers else int(src1, 0)
                result = self.alu.execute(op, val1, 0)
                self.flags.set_flags(result, op, val1, 1 if op in [Operation.INC, Operation.DEC] else 0)
                self.register_file.write(dest, result)
                return f"{op.value} {dest}, {src1} -> {result}"
            elif op == Operation.LOAD:
                offset = int(src1, 0)
                segment_base = self.segment_regs.get_base('DS')
                physical_address = self.memory.compute_physical_address(segment_base, offset)
                value = self.memory.read(physical_address)
                self.register_file.write(dest, value)
                return f"{op.value} {dest}, [DS:{offset}] -> {value} (phys: 0x{physical_address:08X})"
            elif op == Operation.STORE:
                offset = int(dest, 0)
                segment_base = self.segment_regs.get_base('DS')
                physical_address = self.memory.compute_physical_address(segment_base, offset)
                value = self.register_file.read(src1)
                self.memory.write(physical_address, value)
                return f"{op.value} [DS:{offset}], {src1} (phys: 0x{physical_address:08X})"
            elif op == Operation.MOVSEG:
                value = int(src1, 0)
                self.segment_regs.set_base(dest, value)
                return f"{op.value} {dest}, {src1}"
            elif op == Operation.PUSH:
                sp = self.register_file.read('SP')
                physical_address = self.memory.compute_physical_address(self.segment_regs.get_base('SS'), sp - 4)
                value = self.register_file.read(src1) if src1 in self.register_file.registers else int(src1, 0)
                self.memory.write(physical_address, value)
                self.register_file.write('SP', sp - 4)
                return f"{op.value} {src1} (addr: 0x{physical_address:08X})"
            elif op == Operation.POP:
                sp = self.register_file.read('SP')
                physical_address = self.memory.compute_physical_address(self.segment_regs.get_base('SS'), sp)
                value = self.memory.read(physical_address)
                self.register_file.write(dest, value)
                self.register_file.write('SP', sp + 4)
                return f"{op.value} {dest} <- [{physical_address}] {value}"
            elif op == Operation.IN:
                port = int(src1, 0)
                value = self.ports.get(port, 0)
                self.register_file.write(dest, value)
                return f"{op.value} {dest}, port {src1} -> {value}"
            elif op == Operation.OUT:
                port = int(dest, 0)
                value = self.register_file.read(src1)
                self.ports[port] = value
                return f"{op.value} {src1}, port {dest}"
            elif op == Operation.CMP:
                val1 = self.register_file.read(src1) if src1 in self.register_file.registers else int(src1, 0)
                val2 = self.register_file.read(src2) if src2 in self.register_file.registers else int(src2, 0)
                result = self.alu.execute(op, val1, val2)
                self.flags.set_flags(result, op, val1, val2)
                return f"{op.value} {src1}, {src2}"
            elif op in [Operation.JMP, Operation.JE, Operation.JNE, Operation.JG, Operation.JL]:
                condition = False
                if op == Operation.JMP:
                    condition = True
                elif op == Operation.JE:
                    condition = self.flags.ZF
                elif op == Operation.JNE:
                    condition = not self.flags.ZF
                elif op == Operation.JG:
                    condition = not self.flags.CF and not self.flags.ZF
                elif op == Operation.JL:
                    condition = self.flags.CF
                if condition:
                    self.jump_to = self.labels[dest]
                return f"{op.value} {dest} {'taken' if condition else 'not taken'}"
        except ValueError as e:
            raise ValueError(f"Execution error: {str(e)}")