from typing import Dict, List, Optional
from .cfg_graph import ControlFlowGraph
from .ir_nodes import PhiInstruction

class SSARenamer:
    def __init__(self, cfg: ControlFlowGraph, idom_map: Dict[int, Optional[int]]):
        self.cfg = cfg
        self.counters: Dict[str, int] = {}
        self.stacks: Dict[str, List[str]] = {}
        self.dom_children: Dict[int, List[int]] = {b.block_id: [] for b in cfg.blocks}
        for b_id, parent_id in idom_map.items():
            if parent_id is not None:
                self.dom_children[parent_id].append(b_id)
    def _next_version(self, var: str) -> str:
        self.counters[var] = self.counters.get(var, 0) + 1
        ver = f"{var}_{self.counters[var]}"
        self.stacks.setdefault(var, []).append(ver)
        return ver
    def run(self) -> None:
        self._rename_block(self.cfg.entry_block.block_id)
    def _rename_block(self, block_id: int) -> None:
        block = next(b for b in self.cfg.blocks if b.block_id == block_id)
        pushed_variables: List[str] = []
        for instr in block.instructions:
            if isinstance(instr, PhiInstruction):
                orig = instr.original_name
                instr.replace_def(self._next_version(orig))
                pushed_variables.append(orig)
        for instr in block.instructions:
            if isinstance(instr, PhiInstruction): continue
            for use in list(instr.uses()):
                if use in self.stacks and self.stacks[use]:
                    instr.replace_use(use, self.stacks[use][-1])
            def_var = instr.defines()
            if def_var:
                instr.replace_def(self._next_version(def_var))
                pushed_variables.append(def_var)
        for succ in block.successors:
            for instr in succ.instructions:
                if isinstance(instr, PhiInstruction):
                    orig = instr.original_name
                    if orig in self.stacks and self.stacks[orig]:
                        instr.operands.append((block_id, self.stacks[orig][-1]))
        for child_id in self.dom_children[block_id]:
            self._rename_block(child_id)
        for var in pushed_variables:
            if var in self.stacks and self.stacks[var]:
                self.stacks[var].pop()
