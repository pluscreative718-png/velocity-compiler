from typing import List, Any
from .opcode import Opcode

class BytecodeInstruction:
    def __init__(self, opcode: Opcode, operands: List[Any]):
        self.opcode = opcode
        self.operands = operands
    def encode(self) -> List[Any]:
        return [int(self.opcode), *self.operands]
    def __repr__(self) -> str:
        return f"{self.opcode.name:<12} [ {', '.join(map(str, self.operands))} ]"
