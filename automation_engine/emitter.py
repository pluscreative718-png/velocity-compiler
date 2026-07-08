from typing import Dict, List, Any
from .cfg_graph import ControlFlowGraph
from .ir_nodes import AssignInstruction, BinaryOpInstruction, CallPluginInstruction, UnconditionalJump, ConditionalJump
from .opcode import Opcode
from .bytecode import BytecodeInstruction

class BytecodeSelector:
    def __init__(self):
        self.register_map: Dict[str, int] = {}
        self.next_reg_id = 0
    def _get_reg(self, var_name: Any) -> Any:
        if not isinstance(var_name, str): return var_name
        if var_name not in self.register_map:
            self.register_map[var_name] = self.next_reg_id
            self.next_reg_id += 1
        return f"r{self.register_map[var_name]}"
    def lower_graph(self, cfg: ControlFlowGraph) -> Dict[int, List[BytecodeInstruction]]:
        compiled_program: Dict[int, List[BytecodeInstruction]] = {}
        for block in cfg.blocks:
            stream: List[BytecodeInstruction] = []
            for instr in block.instructions:
                if isinstance(instr, AssignInstruction):
                    dest = self._get_reg(instr.result)
                    if isinstance(instr.value, (int, float, bool, str)) and not isinstance(instr.value, str):
                        stream.append(BytecodeInstruction(Opcode.LOAD_CONST, [dest, instr.value]))
                    else:
                        stream.append(BytecodeInstruction(Opcode.MOVE, [dest, self._get_reg(instr.value)]))
                elif isinstance(instr, BinaryOpInstruction):
                    dest, left, right = self._get_reg(instr.result), self._get_reg(instr.left), self._get_reg(instr.right)
                    op_map = {"+": Opcode.ADD, "-": Opcode.SUB, "*": Opcode.MUL, "==": Opcode.CMP_EQ}
                    stream.append(BytecodeInstruction(op_map[instr.op], [dest, left, right]))
                elif isinstance(instr, CallPluginInstruction):
                    args = [self._get_reg(arg) for arg in instr.args]
                    stream.append(BytecodeInstruction(Opcode.CALL_PLUGIN, [instr.plugin_id, instr.cmd_id, *args]))
                elif isinstance(instr, UnconditionalJump):
                    stream.append(BytecodeInstruction(Opcode.JUMP, [f"B{instr.target_block_id}"]))
                elif isinstance(instr, ConditionalJump):
                    stream.append(BytecodeInstruction(Opcode.JUMP_IF, [self._get_reg(instr.condition), f"B{instr.true_block_id}", f"B{instr.false_block_id}"]))
            if block.block_id == cfg.blocks[-1].block_id:
                stream.append(BytecodeInstruction(Opcode.HALT, []))
            compiled_program[block.block_id] = stream
        return compiled_program
