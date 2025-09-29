# Memory class to simulate a flat 128KB memory
class Memory:
    def __init__(self, size=0x20000):
        self.memory = [0] * size  # Initialize 128KB memory

    def read(self, physical_address):
        """Read 32-bit value from memory."""
        if 0 <= physical_address < len(self.memory):
            return self.memory[physical_address]
        raise ValueError(f"Physical memory address {physical_address} is invalid (max: {len(self.memory)-1})")

    def write(self, physical_address, value):
        """Write 32-bit value to memory."""
        if 0 <= physical_address < len(self.memory):
            self.memory[physical_address] = value & 0xFFFFFFFF
        else:
            raise ValueError(f"Physical memory address {physical_address} is invalid (max: {len(self.memory)-1})")

    def compute_physical_address(self, segment_base, offset):
        """Compute physical address from segment base and offset."""
        return (segment_base + offset) & 0xFFFFFFFF