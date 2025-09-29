from alu import Operation
import logging

# Pipeline class to manage the 5-stage pipeline
class Pipeline:
    def __init__(self, control_unit):
        self.stages = ["Fetch", "Decode", "Execute", "Memory", "Writeback"]
        self.control_unit = control_unit
        self.results = []
        self.parsed = None
        self.alu_result = None
        self.memory_result = None
        self.address = None

    def get_remaining_stages(self, op):
        """Determine remaining pipeline stages for an operation."""
        if op in [Operation.ADD, Operation.SUB, Operation.MOV, Operation.MOVSEG, Operation.AND, Operation.OR, Operation.XOR, Operation.NOT, Operation.SHL, Operation.SHR, Operation.ROL, Operation.ROR, Operation.INC, Operation.DEC, Operation.IN]:
            return ["Execute", "Writeback"]
        elif op == Operation.LOAD:
            return ["Execute", "Memory", "Writeback"]
        elif op in [Operation.STORE, Operation.PUSH, Operation.OUT]:
            return ["Execute", "Memory"]
        elif op == Operation.POP:
            return ["Execute", "Memory", "Writeback"]
        elif op == Operation.CMP:
            return ["Execute"]
        elif op in [Operation.JMP, Operation.JE, Operation.JNE, Operation.JG, Operation.JL]:
            return ["Execute"]
        return []

    def clear_state(self):
        """Reset pipeline state for a new instruction."""
        self.results = []
        self.parsed = None
        self.alu_result = None
        self.memory_result = None
        self.address = None

    def perform_stage(self, stage, parsed):
        """Execute a specific pipeline stage."""
        if parsed is None and stage != "Fetch":
            return
        op, dest, src1, src2 = parsed if parsed else (None, None, None, None)
        try:
            if stage == "Fetch":
                logging.info(f"Performing Fetch stage")
            elif stage == "Decode":
                self.parsed = parsed
                logging.info(f"Performing Decode stage: {op} {dest} {src1} {src2}")
            elif stage == "Execute":
                logging.info(f"Performing Execute stage for {op}")
                if op in [Operation.ADD, Operation.SUB, Operation.AND, Operation.OR, Operation.XOR, Operation.SHL, Operation.SHR, Operation.ROL, Operation.ROR]:
                    val1 = self.control_unit.register_file.read(src1) if src1 in self.control_unit.register_file.registers else int(src1, 0)
                    val2 = self.control_unit.register_file.read(src2) if src2 in self.control_unit.register_file.registers else int(src2, 0)
                    self.alu_result = self.control_unit.alu.execute(op, val1, val2)
                    self.control_unit.flags.set_flags(self.alu_result, op, val1, val2)
                elif op in [Operation.NOT, Operation.INC, Operation.DEC]:
                    val1 = self.control_unit.register_file.read(src1) if src1 in self.control_unit.register_file.registers else int(src1, 0)
                    self.alu_result = self.control_unit.alu.execute(op, val1, 0)
                    self.control_unit.flags.set_flags(self.alu_result, op, val1, 1 if op in [Operation.INC, Operation.DEC] else 0)
                elif op == Operation.MOV:
                    self.alu_result = self.control_unit.register_file.read(src1) if src1 in self.control_unit.register_file.registers else int(src1, 0)
                elif op == Operation.MOVSEG:
                    self.alu_result = int(src1, 0)
                elif op in [Operation.LOAD, Operation.STORE]:
                    if op == Operation.LOAD:
                        offset = int(src1, 0)
                        self.address = self.control_unit.memory.compute_physical_address(self.control_unit.segment_regs.get_base('DS'), offset)
                    else:
                        offset = int(dest, 0)
                        self.address = self.control_unit.memory.compute_physical_address(self.control_unit.segment_regs.get_base('DS'), offset)
                elif op == Operation.PUSH:
                    sp = self.control_unit.register_file.read('SP')
                    self.address = self.control_unit.memory.compute_physical_address(self.control_unit.segment_regs.get_base('SS'), sp - 4)
                    self.alu_result = self.control_unit.register_file.read(src1) if src1 in self.control_unit.register_file.registers else int(src1, 0)
                    self.control_unit.register_file.write('SP', sp - 4)
                elif op == Operation.POP:
                    sp = self.control_unit.register_file.read('SP')
                    self.address = self.control_unit.memory.compute_physical_address(self.control_unit.segment_regs.get_base('SS'), sp)
                    self.control_unit.register_file.write('SP', sp + 4)
                elif op == Operation.IN:
                    port = int(src1, 0)
                    self.alu_result = self.control_unit.ports.get(port, 0)
                elif op == Operation.OUT:
                    port = int(dest, 0)
                    value = self.control_unit.register_file.read(src1)
                    self.control_unit.ports[port] = value
                elif op == Operation.CMP:
                    val1 = self.control_unit.register_file.read(src1) if src1 in self.control_unit.register_file.registers else int(src1, 0)
                    val2 = self.control_unit.register_file.read(src2) if src2 in self.control_unit.register_file.registers else int(src2, 0)
                    self.alu_result = self.control_unit.alu.execute(Operation.SUB, val1, val2)
                    self.control_unit.flags.set_flags(self.alu_result, op, val1, val2)
                elif op in [Operation.JMP, Operation.JE, Operation.JNE, Operation.JG, Operation.JL]:
                    condition = False
                    if op == Operation.JMP:
                        condition = True
                    elif op == Operation.JE:
                        condition = self.control_unit.flags.ZF
                    elif op == Operation.JNE:
                        condition = not self.control_unit.flags.ZF
                    elif op == Operation.JG:
                        condition = not self.control_unit.flags.CF and not self.control_unit.flags.ZF
                    elif op == Operation.JL:
                        condition = self.control_unit.flags.CF
                    if condition:
                        self.control_unit.jump_to = self.control_unit.labels[dest]
            elif stage == "Memory":
                logging.info(f"Performing Memory stage for {op}")
                if op == Operation.LOAD:
                    self.memory_result = self.control_unit.memory.read(self.address)
                elif op == Operation.STORE:
                    value = self.control_unit.register_file.read(src1)
                    self.control_unit.memory.write(self.address, value)
                    result_str = f"{op.value} [{self.address}], {src1}"
                    self.results.append(result_str)
                elif op == Operation.PUSH:
                    self.control_unit.memory.write(self.address, self.alu_result)
                    result_str = f"{op.value} {src1} (addr: 0x{self.address:08X})"
                    self.results.append(result_str)
                elif op == Operation.POP:
                    self.memory_result = self.control_unit.memory.read(self.address)
                elif op == Operation.OUT:
                    pass
            elif stage == "Writeback":
                logging.info(f"Performing Writeback stage for {op}")
                value = None
                if op == Operation.LOAD:
                    value = self.memory_result
                    self.control_unit.register_file.write(dest, value)
                    result_str = f"{op.value} {dest}, [{self.address}] -> {value}"
                    self.results.append(result_str)
                elif op in [Operation.ADD, Operation.SUB, Operation.MOV, Operation.AND, Operation.OR, Operation.XOR, Operation.NOT, Operation.SHL, Operation.SHR, Operation.ROL, Operation.ROR, Operation.INC, Operation.DEC, Operation.IN]:
                    value = self.alu_result
                    self.control_unit.register_file.write(dest, value)
                    if op == Operation.MOV:
                        result_str = f"{op.value} {dest}, {src1}"
                    else:
                        src2_str = src2 if src2 else "0"
                        result_str = f"{op.value} {dest}, {src1}, {src2_str} -> {value}"
                    self.results.append(result_str)
                elif op == Operation.MOVSEG:
                    value = self.alu_result
                    self.control_unit.segment_regs.set_base(dest, value)
                    result_str = f"{op.value} {dest}, {src1}"
                    self.results.append(result_str)
                elif op == Operation.POP:
                    value = self.memory_result
                    self.control_unit.register_file.write(dest, value)
                    result_str = f"{op.value} {dest} <- [{self.address}] {value}"
                    self.results.append(result_str)
                elif op == Operation.CMP:
                    pass
                elif op in [Operation.JMP, Operation.JE, Operation.JNE, Operation.JG, Operation.JL]:
                    pass
                elif op == Operation.OUT:
                    pass
        except Exception as e:
            logging.error(f"Error in stage {stage}: {str(e)}")
            raise ValueError(f"Stage {stage} error: {str(e)}")