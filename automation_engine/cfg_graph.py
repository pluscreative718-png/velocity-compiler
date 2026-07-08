from typing import List
from .cfg import BasicBlock

class ControlFlowGraph:
    def __init__(self, entry_block: BasicBlock, blocks: List[BasicBlock]):
        self.entry_block = entry_block
        self.blocks = blocks
