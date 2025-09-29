# Pentaur: 32-bit Pentium Microprocessor Simulator

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)
[![GitHub Issues](https://img.shields.io/github/issues/Adib4A/Pentaur-32bit-microprocessor)](https://github.com/yourusername/pentaur-simulator/issues)

Pentaur is an educational 32-bit microprocessor simulator inspired by the Pentium architecture. It emulates key components of a processor, including ALU operations, registers, segmented memory, flags, and a 5-stage instruction pipeline. Built with Python and Tkinter, it provides a graphical interface for writing, executing, and debugging assembly-like instructions.


## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [About the Author](#about-the-author)

## Overview

Pentaur simulates a simplified 32-bit Pentium microprocessor, allowing users to explore low-level computing concepts through a user-friendly GUI. The simulator supports a subset of assembly instructions for arithmetic, logical, memory, control flow, stack, and I/O operations. It models segmented memory addressing (with segments like CS, DS, ES, SS, FS, GS), a 128KB flat memory space, and basic I/O ports.

The project is modularized into separate files for better maintainability:
- `main.py`: Entry point and logging setup.
- `alu.py`: Arithmetic Logic Unit (ALU) operations.
- `flags.py`: Flags
- `registers.py`: Register file and segment registers.
- `memory.py`: Memory management.
- `control_unit.py`: Instruction decoding and execution.
- `pipeline.py`: 5-stage pipeline simulation.
- `gui.py`: Tkinter-based graphical interface.
- `utils.py`: Utility functions (e.g., log file path).

This tool is ideal for students, educators, and enthusiasts learning about microprocessor architecture, assembly programming, and pipelining.

## Features

- **Instruction Set Support**: Includes operations like MOV, ADD, SUB, AND, OR, XOR, NOT, SHL, SHR, ROL, ROR, INC, DEC, CMP, LOAD, STORE, MOVSEG, PUSH, POP, IN, OUT, JMP, JE, JNE, JG, JL.
- **GUI Interface**: Interactive input for assembly code, real-time output logs, register/segment/flag displays, memory viewer (non-zero entries), and pipeline visualization with color-coded stages.
- **Pipeline Simulation**: 5-stage pipeline (Fetch, Decode, Execute, Memory, Writeback) with step-by-step animation.
- **Memory and Segments**: 128KB memory with segmented addressing; supports physical address calculation.
- **Flags Management**: ZF, SF, CF, OF flags updated based on operations.
- **Logging**: Detailed logs in `processor.log` for debugging.
- **Program Management**: Save/load assembly programs, reset simulator, keyboard shortcuts.
- **Help and About**: Built-in help guide and about section.
- **Modular Design**: Clean separation of concerns for easy extension.

## Prerequisites

- **Python**: Version 3.8 or higher (tested on 3.12).
- **Libraries**: 
  - Tkinter (included in standard Python installations; install `python3-tk` on Ubuntu if missing).
  - No external pip installs required beyond standard library.
- **Operating System**: Windows, Linux, or macOS (GUI works best on Windows/Linux).
- **Hardware**: Basic requirements; no GPU needed.
- **Optional**: For building EXE (e.g., via PyInstaller), additional tools like Pillow for icon conversion.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Adib4A/Pentaur-32bit-microprocessor.git
   cd Pentaur-32bit-microprocessor
   ```

2. No additional installations needed, as the project uses standard Python libraries.

## Usage

### Running the Simulator
1. Navigate to the project directory.
2. Run the main script:
   ```
   python src/main.py
   ```
   - This launches the GUI window.

### Basic Workflow
- **Enter Instructions**: Type assembly code in the input box (e.g., `MOV R0, 10`).
- **Execute**:
  - **Run**: Executes all instructions sequentially (Ctrl+R).
  - **Step**: Executes one instruction at a time with pipeline animation (Ctrl+T).
  - **Reset**: Clears everything (Ctrl+Shift+R).
- **Monitor State**: View registers, segments, flags, and non-zero memory in real-time.
- **Save/Load**: Use menu options to save/load programs (Ctrl+S/Ctrl+O).
- **Logs**: View `processor.log` for detailed execution traces (Ctrl+L to open).

### Example Program
```
MOVSEG DS, 0x0000
MOV R0, 10
MOV R1, 20
ADD R2, R0, R1  ; R2 = 30
STORE R2, 0x10
LOAD R3, 0x10   ; R3 = 30
CMP R2, R3      ; Sets ZF=1
JE end
INC R4, R4      ; Not reached
end: MOV R5, 999
```

### Building Executable (Optional)
To create a standalone EXE:
```
pip install pyinstaller
pyinstaller --onefile --windowed --icon=logo.ico --name Pentaur --add-data "src;src" --hidden-import=tkinter src/main.py
```
Output: `dist/Pentaur.exe`

## Limitations

- **Memory Size**: Limited to 128KB; no virtual memory or paging.
- **Pipeline Simplifications**: No hazard detection, branch prediction, or stalls.
- **Instruction Set**: Subset of Pentium instructions; no floating-point, MMX, or advanced features.
- **Flags**: Basic implementation (unsigned comparisons for JG/JL).
- **I/O**: Simulated ports; no real hardware interaction.
- **Performance**: Not optimized for large programs; Step mode is slow for visualization.
- **Platform**: GUI may have minor rendering issues on some Linux distros without proper Tkinter setup.
- **No Multi-threading**: Single-threaded execution.

## Future Improvements

- **Expanded Instruction Set**: Add more instructions (e.g., MUL, DIV, floating-point).
- **Advanced Pipeline**: Implement data/structural hazards and forwarding.
- **Debugger**: Breakpoints, single-step debugging, and variable watches.
- **Visualization Enhancements**: Interactive memory maps and waveform viewer.
- **Multi-Platform Builds**: Use tools like PyInstaller for macOS/Linux bundles.
- **Testing**: Add unit tests with pytest for core components.
- **Documentation**: API docs with Sphinx and more examples.
- **Extensions**: Support for interrupts, exceptions, or multi-core simulation.

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

Report issues via [GitHub Issues](https://github.com/yourusername/pentaur-simulator/issues).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About the Author

This project was written by AmirAbas AdibAnsari for the final project of the Microprocessor and Assembly Language course in September 2025, with the aim of creating a 32-bit Pentium microprocessor simulator named Pentaur.  
Good luck.
