from typing import Dict, List, Any, Optional
from .opcode import Opcode
from .bytecode import BytecodeInstruction
from .plugin_host import PluginHost

class VirtualMachine:
    def __init__(self, plugin_host: Optional[PluginHost] = None):
        self.registers: Dict[str, Any] = {}
        self.program: Dict[int, List[BytecodeInstruction]] = {}
        self.current_block: int = 0
        self.instruction_pointer: int = 0
        self.running: bool = False
        self.plugin_host: PluginHost = plugin_host if plugin_host else PluginHost()
    def resolve(self, operand: Any) -> Any:
        if isinstance(operand, str) and operand.startswith("r"): return self.registers.get(operand, 0)
        return operand
    def load_program(self, compiled_blocks: Dict[int, List[BytecodeInstruction]], entry_id: int = 0):
        self.program = compiled_blocks
        self.current_block = entry_id
        self.instruction_pointer = 0
        self.registers.clear()
    def execute(self):
        self.running = True
        while self.running:
            if self.current_block not in self.program: break
            block = self.program[self.current_block]
            if self.instruction_pointer >= len(block): break
            instr = block[self.instruction_pointer]
            jumped = self.dispatch(instr)
            if not jumped: self.instruction_pointer += 1
    def dispatch(self, instr: BytecodeInstruction) -> bool:
        op, args = instr.opcode, instr.operands
        if op == Opcode.LOAD_CONST: self.registers[args[0]] = args[1]
        elif op == Opcode.MOVE: self.registers[args[0]] = self.registers[args[1]]
        elif op == Opcode.ADD: self.registers[args[0]] = self.resolve(args[1]) + self.resolve(args[2])
        elif op == Opcode.SUB: self.registers[args[0]] = self.resolve(args[1]) - self.resolve(args[2])
        elif op == Opcode.MUL: self.registers[args[0]] = self.resolve(args[1]) * self.resolve(args[2])
        elif op == Opcode.CMP_EQ: self.registers[args[0]] = self.resolve(args[1]) == self.resolve(args[2])
        elif op == Opcode.JUMP:
            self.current_block = int(args[0][1:])
            self.instruction_pointer = 0
            return True
        elif op == Opcode.JUMP_IF:
            if self.resolve(args[0]): self.current_block = int(args[1][1:])
            else: self.current_block = int(args[2][1:])
            self.instruction_pointer = 0
            return True
        elif op == Opcode.CALL_PLUGIN:
            self.plugin_host.call(args[0], args[1], [self.resolve(x) for x in args[2:]])
        elif op == Opcode.HALT:
            self.running = False
            return True
        return False
