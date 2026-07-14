from typing import List
from .ir_nodes import IRInstruction

class BasicBlock:
    def __init__(self, block_id: int, name: str = ""):
        self.block_id = block_id
        self.name = name
        self.instructions: List[IRInstruction] = []
        self.successors: List['BasicBlock'] = []
        self.predecessors: List['BasicBlock'] = []
    def __repr__(self):
        return f"BasicBlock(id={self.block_id}, name='{self.name}', instrs={len(self.instructions)})"
