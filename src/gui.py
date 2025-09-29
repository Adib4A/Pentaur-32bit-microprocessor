import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from control_unit import ControlUnit
from pipeline import Pipeline
import logging
import re
import os

# GUI class to create and manage the simulator interface
class ProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pentaur ( 32-bit Pentium Microprocessor Simulator ) ")
        self.control_unit = ControlUnit()
        self.pipeline = Pipeline(self.control_unit)
        self.step_mode = False
        self.current_instruction_index = 0
        self.instructions = []
        self.labels = {}
        self.setup_gui()
        logging.info("GUI initialized")

    def setup_gui(self):
        """Set up the GUI layout with all components and buttons."""
        # Configure main window grid
        self.root.minsize(900, 700)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=4)
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)

        # Set up menu bar
        self.menu_bar = tk.Menu(self.root, font=("Arial", 11), borderwidth=1, relief="ridge", bg="lightgray")
        self.root.config(menu=self.menu_bar)

        # Program menu
        self.program_menu = tk.Menu(self.menu_bar, tearoff=0, font=("Arial", 10))
        self.menu_bar.add_cascade(label="Program", menu=self.program_menu)
        self.program_menu.add_command(label="Save Program", command=self.save_program, accelerator="Ctrl+S")
        self.program_menu.add_command(label="Load Program", command=self.load_program, accelerator="Ctrl+O")

        # Log menu
        self.log_menu = tk.Menu(self.menu_bar, tearoff=0, font=("Arial", 10))
        self.menu_bar.add_cascade(label="Log", menu=self.log_menu)
        self.log_menu.add_command(label="Open processor.log", command=self.open_log, accelerator="Ctrl+L")
        self.log_menu.add_command(label="Clear processor.log", command=self.clear_log, accelerator="Ctrl+Shift+L")

        # Instruction menu
        self.instruction_menu = tk.Menu(self.menu_bar, tearoff=0, font=("Arial", 10))
        self.menu_bar.add_cascade(label="Instruction", menu=self.instruction_menu)
        self.instruction_menu.add_command(label="Run", command=self.run_instructions, accelerator="Ctrl+R")
        self.instruction_menu.add_command(label="Step", command=self.step_instruction, accelerator="Ctrl+T")
        self.instruction_menu.add_command(label="Reset", command=self.reset_program, accelerator="Ctrl+Shift+R")

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0, font=("Arial", 10))
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Show Help", command=self.show_help, accelerator="Ctrl+H")

        # About menu
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0, font=("Arial", 10))
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)
        self.about_menu.add_command(label="Show About", command=self.show_about, accelerator="Ctrl+I")

        # Bind keyboard shortcuts
        self.root.bind("<Control-s>", lambda e: self.save_program())
        self.root.bind("<Control-o>", lambda e: self.load_program())
        self.root.bind("<Control-l>", lambda e: self.open_log())
        self.root.bind("<Control-Shift-L>", lambda e: self.clear_log())
        self.root.bind("<Control-r>", lambda e: self.run_instructions())
        self.root.bind("<Control-t>", lambda e: self.step_instruction())
        self.root.bind("<Control-Shift-R>", lambda e: self.reset_program())
        self.root.bind("<Control-h>", lambda e: self.show_help())
        self.root.bind("<Control-i>", lambda e: self.show_about())

        # Pipeline visualization canvas
        self.canvas_frame = ttk.LabelFrame(self.root, text="Microprocessor Components Visualization")
        self.canvas_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.canvas = tk.Canvas(self.canvas_frame, width=420, height=520, bg="white")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)

        # Draw pipeline stages
        self.components = {
            "Fetch": self.canvas.create_rectangle(10, 10, 390, 100, fill="lightblue", tags="Fetch"),
            "Decode": self.canvas.create_rectangle(10, 110, 390, 200, fill="lightblue", tags="Decode"),
            "Execute": self.canvas.create_rectangle(10, 210, 390, 300, fill="lightblue", tags="Execute"),
            "Memory": self.canvas.create_rectangle(10, 310, 390, 400, fill="lightblue", tags="Memory"),
            "Writeback": self.canvas.create_rectangle(10, 410, 390, 500, fill="lightblue", tags="Writeback"),
        }
        self.canvas.create_text(200, 50, text="Fetch", font=("Arial", 15), tags="Fetch")
        self.canvas.create_text(200, 155, text="Decode", font=("Arial", 15), tags="Decode")
        self.canvas.create_text(200, 260, text="Execute", font=("Arial", 15), tags="Execute")
        self.canvas.create_text(200, 355, text="Memory", font=("Arial", 15), tags="Memory")
        self.canvas.create_text(200, 460, text="Writeback", font=("Arial", 15), tags="Writeback")

        # Instruction input and output frame
        self.io_frame = ttk.LabelFrame(self.root, text="Instruction Input and Output")
        self.io_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.io_frame.grid_rowconfigure(0, weight=1)
        self.io_frame.grid_rowconfigure(1, weight=1)
        self.io_frame.grid_columnconfigure(0, weight=1)

        # Input frame with buttons and text
        self.input_frame = ttk.Frame(self.io_frame)
        self.input_frame.grid(row=0, column=0, padx=0, pady=5, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=0)
        self.input_frame.grid_columnconfigure(1, weight=1)
        self.input_frame.grid_rowconfigure(1, weight=1)

        # Add Run and Step buttons above the input text
        self.button_frame = ttk.Frame(self.input_frame)
        self.button_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.run_button = ttk.Button(self.button_frame, text="Run", command=self.run_instructions)
        self.run_button.grid(row=0, column=0, padx=(0, 5), pady=2)
        self.step_button = ttk.Button(self.button_frame, text="Step", command=self.step_instruction)
        self.step_button.grid(row=0, column=1, padx=(5, 0), pady=2)

        # Line numbers and input text box
        self.line_numbers = tk.Text(self.input_frame, height=15, width=4, wrap="none", state="disabled", font=("Courier", 10), bg="lightgray")
        self.line_numbers.grid(row=1, column=0, sticky="nsw")
        self.input_text = tk.Text(self.input_frame, height=15, width=46, wrap="none", font=("Courier", 10))
        self.input_text.grid(row=1, column=1, sticky="nsew")

        # Input scrollbar
        self.input_scrollbar = ttk.Scrollbar(self.io_frame, orient='vertical', command=self._sync_scroll)
        self.input_scrollbar.grid(row=0, column=1, sticky='ns')
        self.input_text.configure(yscrollcommand=self._sync_scroll_set)
        self.line_numbers.configure(yscrollcommand=self._sync_scroll_set)

        # Bind input text events
        self.input_text.bind("<KeyRelease>", self._update_line_numbers)
        self.input_text.bind("<MouseWheel>", self._sync_mousewheel)
        self.line_numbers.bind("<MouseWheel>", self._sync_mousewheel)
        self._update_line_numbers(None)

        # Output text box
        self.output_text = tk.Text(self.io_frame, height=15, width=50, state="disabled")
        self.output_text.grid(row=1, column=0, padx=0, pady=5, sticky="nsew")
        self.output_scrollbar = ttk.Scrollbar(self.io_frame, orient='vertical', command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=self.output_scrollbar.set)
        self.output_scrollbar.grid(row=1, column=1, sticky='ns')

        # Left panel for registers, segments, and flags
        self.left_panel = ttk.Frame(self.root)
        self.left_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_panel.grid_rowconfigure(0, weight=2)
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Register status display
        self.register_frame = ttk.LabelFrame(self.left_panel, text="Register Status")
        self.register_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.register_labels = {}
        for i, reg in enumerate(sorted(self.control_unit.register_file.registers)):
            val = self.control_unit.register_file.read(reg)
            label = ttk.Label(self.register_frame, text=f"{reg}: {val} (0x{val:08X})")
            label.grid(row=i // 4, column=i % 4, padx=30, pady=1, sticky='w')
            self.register_labels[reg] = label

        # Segment registers display
        self.segment_frame = ttk.LabelFrame(self.left_panel, text="Segment Registers")
        self.segment_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.segment_labels = {}
        segment_list = list(self.control_unit.segment_regs.segments.keys())
        for i, seg in enumerate(segment_list):
            base = self.control_unit.segment_regs.get_base(seg)
            label = ttk.Label(self.segment_frame, text=f"{seg}: {base} (0x{base:08X})")
            label.grid(row=i // 3, column=i % 3, padx=30, pady=1, sticky='w')
            self.segment_labels[seg] = label

        # Flags display
        self.flags_frame = ttk.LabelFrame(self.left_panel, text="Flags")
        self.flags_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.flags_labels = {}
        flag_list = ['ZF', 'SF', 'CF', 'OF']
        for i, flag in enumerate(flag_list):
            value = getattr(self.control_unit.flags, flag)
            label = ttk.Label(self.flags_frame, text=f"{flag}: {int(value)}")
            label.grid(row=i // 2, column=i % 2, padx=10, pady=1, sticky='w')
            self.flags_labels[flag] = label

        # Memory display table
        self.memory_frame = ttk.LabelFrame(self.root, text="Memory (non-zero)")
        self.memory_frame.grid(row=1, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        self.memory_tree = ttk.Treeview(self.memory_frame, columns=("addr_dec", "addr_hex", "val_dec", "val_hex"), show='headings', height=12)
        self.memory_tree.heading("addr_dec", text="Addr(dec)")
        self.memory_tree.heading("addr_hex", text="Addr(hex)")
        self.memory_tree.heading("val_dec", text="Value(dec)")
        self.memory_tree.heading("val_hex", text="Value(hex)")
        self.memory_tree.column("addr_dec", width=70, anchor="center")
        self.memory_tree.column("addr_hex", width=90, anchor="center")
        self.memory_tree.column("val_dec", width=80, anchor="center")
        self.memory_tree.column("val_hex", width=90, anchor="center")
        self.memory_tree.grid(row=0, column=0, sticky="nsew")
        self.memory_frame.grid_rowconfigure(0, weight=1)
        self.memory_frame.grid_columnconfigure(0, weight=1)
        self.memory_scrollbar = ttk.Scrollbar(self.memory_frame, orient='vertical', command=self.memory_tree.yview)
        self.memory_tree.configure(yscrollcommand=self.memory_scrollbar.set)
        self.memory_scrollbar.grid(row=0, column=1, sticky='ns')

    def reset_program(self):
        """Reset the simulator to initial state."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset the simulator? This will clear input, output, registers, segments, flags, and memory."):
            self.input_text.delete("1.0", tk.END)
            self._update_line_numbers(None)
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.config(state="disabled")
            self.control_unit = ControlUnit()
            self.pipeline = Pipeline(self.control_unit)
            self.instructions = []
            self.labels = {}
            self.current_instruction_index = 0
            self.step_mode = False
            for stage in self.components:
                self.update_component_color(stage, "lightblue")
            self._update_register_display()
            self._update_segment_display()
            self._update_memory_display()
            logging.info("Simulator reset by user")

    def _sync_scroll(self, *args):
        """Synchronize scrolling between input text and line numbers."""
        self.input_text.yview(*args)
        self.line_numbers.yview(*args)

    def _sync_scroll_set(self, first, second):
        """Update scrollbar position and sync text widgets."""
        self.input_scrollbar.set(first, second)
        self._sync_scroll('moveto', first)
        return 'break'

    def _sync_mousewheel(self, event):
        """Handle mouse wheel scrolling for input text and line numbers."""
        self.input_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.line_numbers.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return 'break'

    def _update_line_numbers(self, event):
        """Update line numbers display based on input text."""
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        num_lines = int(self.input_text.index('end-1c').split('.')[0])
        line_nums = '\n'.join(str(i) for i in range(1, num_lines + 1))
        self.line_numbers.insert("1.0", line_nums)
        self.line_numbers.config(state="disabled")
        self.line_numbers.yview_moveto(self.input_text.yview()[0])

    def show_help(self):
        """Display the help window with detailed usage instructions."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - 32-bit Pentium Microprocessor Simulator")
        help_window.minsize(600, 400)
        text_frame = tk.Frame(help_window)
        text_frame.pack(padx=10, pady=10, fill="both", expand=True)
        help_text = tk.Text(text_frame, wrap="word", height=20, width=70)
        help_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=help_text.yview)
        help_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        help_content = """
32-bit Pentium Microprocessor Simulator - Comprehensive User Guide

1. Introduction
The 32-bit Pentium Microprocessor Simulator is an educational tool designed to emulate a simplified 32-bit Pentium processor architecture. It allows users to write, load, execute, and debug assembly-like instructions in a graphical environment. The simulator models key components such as the Arithmetic Logic Unit (ALU), register file, segment registers, memory, flags, and a 5-stage instruction pipeline (Fetch, Decode, Execute, Memory, Writeback). This guide provides a complete overview of the interface, supported instructions, usage instructions, and troubleshooting tips.

Built using Python and Tkinter, the simulator supports 32-bit operations, segmented memory addressing, and basic I/O ports. It is intended for learning purposes and does not replicate all features of a real Pentium processor.

2. User Interface Overview
The graphical interface is divided into several sections for ease of use:

- Menu Bar (Top):
  - Program: Save or load assembly programs (Ctrl+S / Ctrl+O).
  - Log: Open or clear the processor.log file (Ctrl+L / Ctrl+Shift+L).
  - Instruction: Run all instructions (Ctrl+R), step through one instruction at a time (Ctrl+T), or reset the simulator (Ctrl+Shift+R).
  - Help: Display this guide (Ctrl+H).
  - About: Show application information (Ctrl+I).

- Pipeline Visualization (Left Top):
  - A canvas displaying the 5 pipeline stages. Stages highlight in green during execution to illustrate instruction flow.

- Instruction Input and Output (Right Top):
  - Input Box: Enter assembly instructions line by line. Line numbers are shown on the left. Supports scrolling.
  - Run and Step Buttons: Quick access to execute all instructions or step through them.
  - Output Box: Displays execution logs, results, errors, and stage-by-stage details.

- State Monitoring (Bottom Left):
  - Register Status: Shows values of general-purpose registers (R0-R7) and SP in decimal and hexadecimal.
  - Segment Registers: Displays base addresses of CS, DS, ES, SS, FS, GS in decimal and hexadecimal.
  - Flags: Indicates status of ZF (Zero), SF (Sign), CF (Carry), and OF (Overflow) as 0 or 1.

- Memory Display (Bottom Right):
  - A table listing non-zero memory locations with addresses and values in decimal and hexadecimal. Scrollable for large memory views.

The window is resizable, and components adjust accordingly.

3. Supported Instructions
The simulator supports a subset of assembly instructions for arithmetic, logical, memory, control flow, stack, and I/O operations. Instructions are case-insensitive for opcodes but registers are uppercase (e.g., R0). Immediates can be decimal or hexadecimal (prefix 0x). Comments use ; or // and are ignored. Labels for jumps are supported (e.g., label: instruction).

Below is a list of all supported instructions with syntax and examples:

- MOV dest, src: Copy value from src (register or immediate) to dest register.
  Example: MOV R0, 0x42  ; R0 = 66 (hex)
           MOV R1, R0   ; R1 = R0

- ADD dest, src1, src2: Add src1 and src2, store in dest. Sets flags.
  Example: ADD R2, R0, R1  ; R2 = R0 + R1
           ADD R3, R2, 10  ; R3 = R2 + 10

- SUB dest, src1, src2: Subtract src2 from src1, store in dest. Sets flags.
  Example: SUB R4, R3, R2  ; R4 = R3 - R2
           SUB R5, R4, 5   ; R5 = R4 - 5

- AND dest, src1, src2: Bitwise AND of src1 and src2, store in dest. Sets flags.
  Example: AND R6, R0, R1  ; R6 = R0 & R1
           AND R7, R6, 0xFF ; R7 = R6 & 255

- OR dest, src1, src2: Bitwise OR.
  Example: OR R0, R1, R2   ; R0 = R1 | R2

- XOR dest, src1, src2: Bitwise XOR.
  Example: XOR R1, R2, R3  ; R1 = R2 ^ R3

- NOT dest, src: Bitwise NOT of src, store in dest.
  Example: NOT R2, R1      ; R2 = ~R1

- SHL dest, src1, src2: Shift src1 left by src2 bits.
  Example: SHL R3, R0, 2   ; R3 = R0 << 2

- SHR dest, src1, src2: Shift right.
  Example: SHR R4, R3, 1   ; R4 = R3 >> 1

- ROL dest, src1, src2: Rotate left.
  Example: ROL R5, R4, 3   ; R5 = R4 rotated left by 3 bits

- ROR dest, src1, src2: Rotate right.
  Example: ROR R6, R5, 2   ; R6 = R5 rotated right by 2 bits

- INC dest, src: Increment src by 1, store in dest.
  Example: INC R7, R6      ; R7 = R6 + 1

- DEC dest, src: Decrement src by 1.
  Example: DEC R0, R7      ; R0 = R7 - 1

- CMP src1, src2: Compare src1 and src2 (subtract without storing). Sets flags for jumps.
  Example: CMP R1, R2      ; Sets ZF if R1 == R2, CF if R1 < R2

- LOAD dest, offset: Load from memory [DS:offset] to dest.
  Example: LOAD R3, 0x10   ; R3 = memory at DS base + 16

- STORE src, offset: Store src to memory [DS:offset].
  Example: STORE R4, 0x20  ; memory at DS base + 32 = R4

- MOVSEG seg, base: Set segment register base.
  Example: MOVSEG DS, 0x1000  ; DS base = 4096

- PUSH src: Push src to stack [SS:SP], decrement SP by 4.
  Example: PUSH R5         ; Stack push R5

- POP dest: Pop from stack to dest, increment SP by 4.
  Example: POP R6          ; R6 = pop from stack

- IN dest, port: Read from I/O port to dest.
  Example: IN R7, 0x10     ; R7 = port 16 value (simulated)

- OUT src, port: Write src to I/O port.
  Example: OUT R0, 0x20    ; Port 32 = R0

- JMP label: Unconditional jump to label.
  Example: JMP loop

- JE label: Jump if equal (ZF=1).
  Example: JE equal

- JNE label: Jump if not equal (ZF=0).
  Example: JNE notequal

- JG label: Jump if greater (not CF and not ZF, unsigned).
  Example: JG greater

- JL label: Jump if less (CF=1, unsigned).
  Example: JL less

Notes:
- Registers: R0-R7, SP.
- Segments: CS, DS, ES, SS, FS, GS (default DS for data, SS for stack).
- Labels: Defined as label: followed by instruction.
- Flags: Updated by arithmetic/logical ops for conditional jumps.

4. Getting Started: How to Use the Simulator
Step 1: Launch the Application
- Run the script: python pentium32bit.py.
- The GUI will open with empty input and default state (all registers/memory/flags zeroed).

Step 2: Entering Instructions
- In the Instruction Input box (top-right), type instructions line by line.
- Example program to test basic operations:
  MOVSEG DS, 0x0000      ; Set DS base to 0
  MOV R0, 10             ; R0 = 10
  MOV R1, 20             ; R1 = 20
  ADD R2, R0, R1         ; R2 = 30
  STORE R2, 0x10         ; Memory[0x10] = 30
  LOAD R3, 0x10          ; R3 = 30
  CMP R2, R3             ; Compare (ZF=1)
  JE end                 ; Jump if equal
  INC R4, R4             ; Not reached
end: MOV R5, 999          ; R5 = 999
- Blank lines and comments (; or //) are ignored.

Step 3: Executing Instructions
- Run (Ctrl+R or Run button): Executes all instructions sequentially. Pipeline stages animate in green.
- Step (Ctrl+T or Step button): Executes one instruction at a time, showing each pipeline stage.
- Reset (Ctrl+Shift+R): Clears everything to initial state after confirmation.

Step 4: Monitoring Execution
- Output Box: Shows step-by-step results, flags updates, and errors.
- Registers/Segments/Flags: Update after each instruction.
- Memory Table: Shows non-zero entries; refresh after execution.
- Pipeline Canvas: Highlights active stages.

Step 5: Program Management
- Save Program (Ctrl+S): Save input to .txt or .asm file.
- Load Program (Ctrl+O): Load from file into input box.

Step 6: Logging
- All actions logged to processor.log in the script directory.
- Open Log (Ctrl+L): View in default editor.
- Clear Log (Ctrl+Shift+L): Clear file after confirmation.

5. Advanced Features and Tips
- Memory Addressing: Physical address = segment base + offset (mod 2^32). Use MOVSEG to set bases.
- Stack Operations: Set SS and SP first (e.g., MOVSEG SS, 0x1000; MOV SP, 0x100).
- Jumps: Labels must be defined; infinite loops possible but use Step to debug.
- I/O Ports: Simulated as a dictionary; values persist until reset.
- Error Handling: Invalid ops/registers/memory show in output/log.
- Performance: For large programs, use Run; Step for debugging.
- Best Practices: Start with simple code, check flags/memory after ops, use hex for addresses.

6.Chartres Cathedral, France

6. Limitations and Troubleshooting
- Memory: Limited to 128KB; no paging/protection.
- Pipeline: Simplified; no hazards, branching stalls.
- Flags: Basic implementation; unsigned comparisons for JG/JL.
- Troubleshooting:
  - Errors in output? Check syntax/register names.
  - No output? Ensure instructions are valid/non-blank.
  - Crashes? Check processor.log for details.
  - Contact: For issues, refer to source code or developer.

This simulator is for educational use. Explore, experiment, and learn microprocessor concepts!
        """
        help_text.insert(tk.END, help_content)
        help_text.config(state="disabled")
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def show_about(self):
        """Display the about window."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About - 32-bit Pentium Microprocessor Simulator")
        about_window.minsize(300, 200)
        text_frame = tk.Frame(about_window)
        text_frame.pack(padx=10, pady=10, fill="both", expand=True)
        about_text = tk.Text(text_frame, wrap="word", height=20, width=70)
        about_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=about_text.yview)
        about_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        about_content = """
Hello my friend...

This project was written by AmirAbas AdibAnsari for the final project of the Microprocessor and Assembly Language course in September 2025, with the aim of creating a 32-bit Pentium microprocessor simulator named Pentaur.  

Good luck!
        """
        about_text.insert(tk.END, about_content)
        about_text.config(state="disabled")
        close_button = ttk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)

    def update_component_color(self, stage, color):
        """Update the color of a pipeline stage in the canvas."""
        try:
            self.canvas.itemconfig(self.components[stage], fill=color)
            self.root.update_idletasks()
        except KeyError:
            logging.error(f"Invalid stage {stage} for visualization")
            raise ValueError(f"Visualization error: Stage {stage} not found")

    def _update_segment_display(self):
        """Update segment registers and flags display."""
        for seg, label in self.segment_labels.items():
            base = self.control_unit.segment_regs.get_base(seg)
            label.config(text=f"{seg}: {base} (0x{base:08X})")
        for flag, label in self.flags_labels.items():
            value = getattr(self.control_unit.flags, flag)
            label.config(text=f"{flag}: {int(value)}")

    def clear_log(self):
        """Clear the processor.log file after user confirmation."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the contents of processor.log?"):
            try:
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor.log'), 'w') as f:
                    f.write('')
                messagebox.showinfo("Success", "processor.log cleared successfully")
                logging.info("processor.log cleared by user")
                logging.basicConfig(
                    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor.log'),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    force=True
                )
                logging.info("Logging reinitialized after clearing processor.log")
            except Exception as e:
                messagebox.showerror("Error", f"Error clearing processor.log: {str(e)}")
                logging.error(f"Error clearing processor.log: {str(e)}")

    def open_log(self):
        """Open the processor.log file in the default editor."""
        try:
            log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor.log')
            if os.name == 'nt':
                os.startfile(log_file_path)
            elif os.name == 'posix':
                os.system(f"open {log_file_path}" if 'darwin' in os.uname().sysname.lower() else f"xdg-open {log_file_path}")
            logging.info("processor.log opened by user")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening processor.log: {str(e)}")
            logging.error(f"Error opening processor.log: {str(e)}")

    def parse_labels(self):
        """Parse labels from instructions for jump operations."""
        self.labels = {}
        temp_instructions = []
        for line in self.instructions:
            match = re.match(r'^\s*(\w+)\s*:\s*(.*)$', line)
            if match:
                label = match.group(1)
                instruction = match.group(2).strip()
                if instruction:
                    temp_instructions.append(instruction)
                    self.labels[label] = len(temp_instructions) - 1
                else:
                    self.labels[label] = len(temp_instructions)
            else:
                temp_instructions.append(line)
        self.instructions = temp_instructions
        self.control_unit.labels = self.labels

    def step_instruction(self):
        """Execute one instruction with pipeline visualization."""
        try:
            lines = self.input_text.get("1.0", tk.END).splitlines()
            self.instructions = [line for line in lines if re.sub(r'\s*(;.*|//.*)$', '', line).strip()]
            self.parse_labels()
            if not self.instructions:
                messagebox.showinfo("Info", "No valid instructions to step through.")
                return
            if self.current_instruction_index >= len(self.instructions):
                self.current_instruction_index = 0
            self.step_mode = True
            self.output_text.config(state="normal")
            if self.output_text.get("1.0", tk.END).strip() == "":
                self.output_text.insert(tk.END, f"Log file location: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor.log')}\n")
            self._step_next_instruction()
        except Exception as e:
            self.output_text.config(state="normal")
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            self.output_text.config(state="disabled")
            messagebox.showerror("Error", f"Error stepping instruction: {str(e)}")
            logging.error(f"Error stepping instruction: {str(e)}")

    def _step_next_instruction(self):
        """Execute the next instruction in step mode."""
        if self.current_instruction_index >= len(self.instructions):
            self.output_text.insert(tk.END, "All instructions executed.\n")
            self.output_text.config(state="disabled")
            logging.info("All instructions executed in step mode")
            return

        instruction = self.instructions[self.current_instruction_index]
        self.pipeline.clear_state()
        self.current_instruction = instruction
        self.output_text.insert(tk.END, f"Stepping instruction #{self.current_instruction_index + 1}: {instruction}\n")
        self.update_component_color("Fetch", "lightgreen")
        self.output_text.insert(tk.END, f"Stage Fetch for {instruction}\n")
        self.pipeline.perform_stage("Fetch", None)
        self.root.after(300, lambda: self._after_fetch_step(instruction))

    def _after_fetch_step(self, instruction):
        """Handle post-fetch stage in step mode."""
        self.update_component_color("Fetch", "lightblue")
        self.update_component_color("Decode", "lightgreen")
        self.output_text.insert(tk.END, f"Stage Decode for {instruction}\n")
        try:
            parsed = self.control_unit.decode_instruction(instruction)
            if parsed[0] is None:
                self.output_text.insert(tk.END, "Skipped (no-op or blank)\n")
                self.update_component_color("Decode", "lightblue")
                self.current_instruction_index += 1
                return
            self.current_parsed = parsed
            self.pipeline.perform_stage("Decode", parsed)
            self.root.after(300, lambda: self._after_decode_step(instruction))
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            self.update_component_color("Decode", "lightblue")
            logging.error(f"Error executing instruction '{instruction}': {str(e)}")
            self.current_instruction_index += 1

    def _after_decode_step(self, instruction):
        """Handle post-decode stage in step mode."""
        self.update_component_color("Decode", "lightblue")
        op, dest, src1, src2 = self.current_parsed
        remaining_stages = self.pipeline.get_remaining_stages(op)
        self.remaining_stages = remaining_stages
        self.remaining_index = 0
        if not remaining_stages:
            self._finish_instruction()
            return
        self._animate_remaining_step()

    def _animate_remaining_step(self):
        """Animate remaining pipeline stages in step mode."""
        if self.remaining_index < len(self.remaining_stages):
            stage = self.remaining_stages[self.remaining_index]
            self.update_component_color(stage, "lightgreen")
            self.output_text.insert(tk.END, f"Stage {stage} for {self.current_instruction}\n")
            self.pipeline.perform_stage(stage, self.current_parsed)
            last_result = self.pipeline.results[-1] if self.pipeline.results else None
            if last_result:
                self.output_text.insert(tk.END, f"Result: {last_result}\n")
            self.root.after(300, lambda s=stage: self._end_remaining_stage_step(s))
        else:
            self._finish_instruction()

    def _end_remaining_stage_step(self, stage):
        """End a pipeline stage in step mode."""
        self.update_component_color(stage, "lightblue")
        self.remaining_index += 1
        if self.remaining_index < len(self.remaining_stages):
            self.root.after(100, self._animate_remaining_step)
        else:
            self._finish_instruction()

    def _finish_instruction(self):
        """Complete instruction execution and update state."""
        logging.info(f"Executed: {self.current_instruction}")
        self._log_full_state(self.current_instruction)
        self._update_register_display()
        self._update_segment_display()
        self._update_memory_display()
        self.output_text.insert(tk.END, f"Instruction completed.\n")
        self.current_instruction_index += 1
        if self.control_unit.jump_to is not None:
            self.current_instruction_index = self.control_unit.jump_to
            self.control_unit.jump_to = None
        if not self.step_mode:
            self.root.after(200, self._run_next_instruction)

    def run_instructions(self):
        """Execute all instructions with pipeline visualization."""
        try:
            lines = self.input_text.get("1.0", tk.END).splitlines()
            self.instructions = [line for line in lines if re.sub(r'\s*(;.*|//.*)$', '', line).strip()]
            self.parse_labels()
            if not self.instructions:
                self.output_text.insert(tk.END, "No valid instructions to run.\n")
                self.output_text.config(state="disabled")
                logging.info("No valid instructions provided")
                messagebox.showinfo("Info", "No valid instructions to run.")
                return
            self.current_instruction_index = 0
            self.step_mode = False
            self.output_text.config(state="normal")
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Log file location: {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processor.log')}\n")
            self._run_next_instruction()
        except Exception as e:
            self.output_text.config(state="normal")
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            self.output_text.config(state="disabled")
            messagebox.showerror("Error", f"Error executing instructions: {str(e)}")
            logging.error(f"Error executing instructions: {str(e)}")

    def _run_next_instruction(self):
        """Execute the next instruction in run mode."""
        if self.current_instruction_index >= len(self.instructions):
            self.output_text.insert(tk.END, "Instructions executed successfully\n")
            self.output_text.config(state="disabled")
            logging.info("Instructions executed successfully")
            return

        instruction = self.instructions[self.current_instruction_index]
        self.pipeline.clear_state()
        self.current_instruction = instruction
        self.output_text.insert(tk.END, f"Running instruction #{self.current_instruction_index + 1}: {instruction}\n")
        self.update_component_color("Fetch", "lightgreen")
        self.output_text.insert(tk.END, f"Stage Fetch for {instruction}\n")
        self.pipeline.perform_stage("Fetch", None)
        self.root.after(300, lambda: self._after_fetch(instruction))

    def _after_fetch(self, instruction):
        """Handle post-fetch stage in run mode."""
        self.update_component_color("Fetch", "lightblue")
        self.update_component_color("Decode", "lightgreen")
        self.output_text.insert(tk.END, f"Stage Decode for {instruction}\n")
        try:
            parsed = self.control_unit.decode_instruction(instruction)
            if parsed[0] is None:
                self.output_text.insert(tk.END, "Skipped (no-op or blank)\n")
                self.update_component_color("Decode", "lightblue")
                self.current_instruction_index += 1
                self.root.after(200, self._run_next_instruction)
                return
            self.current_parsed = parsed
            self.pipeline.perform_stage("Decode", parsed)
            self.root.after(300, lambda: self._after_decode(instruction))
        except Exception as e:
            self.output_text.insert(tk.END, f"Error: {str(e)}\n")
            self.update_component_color("Decode", "lightblue")
            logging.error(f"Error executing instruction '{instruction}': {str(e)}")
            self.current_instruction_index += 1
            self.root.after(200, self._run_next_instruction)

    def _after_decode(self, instruction):
        """Handle post-decode stage in run mode."""
        self.update_component_color("Decode", "lightblue")
        op, dest, src1, src2 = self.current_parsed
        remaining_stages = self.pipeline.get_remaining_stages(op)
        self.remaining_stages = remaining_stages
        self.remaining_index = 0
        if not remaining_stages:
            self._finish_instruction()
            return
        self._animate_remaining()

    def _animate_remaining(self):
        """Animate remaining pipeline stages in run mode."""
        if self.remaining_index < len(self.remaining_stages):
            stage = self.remaining_stages[self.remaining_index]
            self.update_component_color(stage, "lightgreen")
            self.output_text.insert(tk.END, f"Stage {stage} for {self.current_instruction}\n")
            self.pipeline.perform_stage(stage, self.current_parsed)
            last_result = self.pipeline.results[-1] if self.pipeline.results else None
            if last_result:
                self.output_text.insert(tk.END, f"Result: {last_result}\n")
            self.root.after(300, lambda s=stage: self._end_remaining_stage(s))
        else:
            self._finish_instruction()

    def _end_remaining_stage(self, stage):
        """End a pipeline stage in run mode."""
        self.update_component_color(stage, "lightblue")
        self.remaining_index += 1
        if self.remaining_index >= len(self.remaining_stages):
            self._finish_instruction()
        else:
            self.root.after(100, self._animate_remaining)

    def _update_register_display(self):
        """Update register display with current values."""
        for reg, label in self.register_labels.items():
            val = self.control_unit.register_file.read(reg)
            label.config(text=f"{reg}: {val} (0x{val:08X})")

    def _update_memory_display(self):
        """Update memory table with non-zero values."""
        for item in self.memory_tree.get_children():
            self.memory_tree.delete(item)
        mem = self.control_unit.memory.memory
        for addr, val in enumerate(mem):
            if val != 0:
                self.memory_tree.insert("", "end", values=(str(addr), f"0x{addr:08X}", str(val), f"0x{val:08X}"))

    def _log_full_state(self, instruction):
        """Log the full processor state after an instruction."""
        regs = ", ".join([f"{r}={self.control_unit.register_file.read(r)}(0x{self.control_unit.register_file.read(r):08X})" for r in self.control_unit.register_file.registers])
        segs = ", ".join([f"{s}=0x{self.control_unit.segment_regs.get_base(s):08X}" for s in self.control_unit.segment_regs.segments])
        flags = ", ".join([f"{f}={int(getattr(self.control_unit.flags, f))}" for f in ['ZF', 'SF', 'CF', 'OF']])
        mem_entries = [f"0x{addr:08X}={val}(0x{val:08X})" for addr, val in enumerate(self.control_unit.memory.memory) if val != 0]
        logging.info(f"STATE after '{instruction}': Registers: {regs}; Segments: {segs}; Flags: {flags}; Memory: {';'.join(mem_entries)}")

    def save_program(self):
        """Save the input program to a file."""
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("Assembly files", "*.asm")])
            if file_path:
                with open(file_path, "w") as f:
                    f.write(self.input_text.get("1.0", tk.END))
                messagebox.showinfo("Success", "Program saved successfully")
                logging.info(f"Program saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving program: {str(e)}")
            logging.error(f"Error saving program: {str(e)}")

    def load_program(self):
        """Load a program from a file into the input text."""
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("Assembly files", "*.asm")])
            if file_path:
                with open(file_path, "r") as f:
                    self.input_text.delete("1.0", tk.END)
                    self.input_text.insert("1.0", f.read())
                messagebox.showinfo("Success", "Program loaded successfully")
                logging.info(f"Program loaded from {file_path}")
                self.current_instruction_index = 0
                self.instructions = []
                self._update_line_numbers(None)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading program: {str(e)}")
            logging.error(f"Error loading program: {str(e)}")