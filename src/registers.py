from alu import Operation
from flags import Flags

# Register file class to manage general-purpose registers
class RegisterFile:
    def __init__(self):
        self.registers = {f'R{i}': 0 for i in range(8)}  # R0-R7
        self.registers['SP'] = 0  # Stack Pointer

    def read(self, reg):
        """Read value from a register."""
        if reg in self.registers:
            return self.registers[reg]
        raise ValueError(f"Register {reg} does not exist")

    def write(self, reg, value):
        """Write value to a register, ensuring 32-bit bounds."""
        if reg in self.registers:
            self.registers[reg] = value & 0xFFFFFFFF
        else:
            raise ValueError(f"Register {reg} does not exist")

# Segment Registers class to manage segment base addresses
class SegmentRegisters:
    def __init__(self):
        self.segments = {
            'CS': 0x00000000,  # Code Segment
            'DS': 0x00000000,  # Data Segment
            'ES': 0x00000000,  # Extra Segment
            'SS': 0x00000000,  # Stack Segment
            'FS': 0x00000000,  # Extra Segment
            'GS': 0x00000000   # Extra Segment
        }

    def get_base(self, seg):
        """Get base address of a segment."""
        if seg in self.segments:
            return self.segments[seg]
        raise ValueError(f"Segment {seg} does not exist")
    
    def set_base(self, seg, base):
        """Set base address of a segment, ensuring 32-bit bounds."""
        if seg in self.segments:
            self.segments[seg] = base & 0xFFFFFFFF
        else:
            raise ValueError(f"Segment {seg} does not exist")