from dataclasses import dataclass, field
from typing import Set, List, Tuple
from .cfg_graph import ControlFlowGraph
from .analysis import AnalysisManager
from .ir_nodes import ConditionalJump, UnconditionalJump

@dataclass
class CFGMutationResult:
    removed_blocks: Set[int] = field(default_factory=set)
    removed_edges: List[Tuple[int, int]] = field(default_factory=list)

class ConditionalPruner:
    @classmethod
    def optimize(cls, am: AnalysisManager) -> Tuple[bool, CFGMutationResult]:
        cfg = am.cfg
        mutation = CFGMutationResult()
        if not am.state.constant_values: return False, mutation
        constants = am.state.constant_values.values
        any_changes = False
        for block in cfg.blocks:
            if not block.instructions: continue
            terminator = block.instructions[-1]
            if isinstance(terminator, ConditionalJump):
                cond = terminator.condition
                has_const, const_val = cls._get_constant_value(cond, constants)
                if has_const:
                    surviving_target = terminator.true_block_id if const_val else terminator.false_block_id
                    dead_target = terminator.false_block_id if const_val else terminator.true_block_id
                    block.instructions[-1] = UnconditionalJump(target_block_id=surviving_target)
                    dead_block = next(b for b in cfg.blocks if b.block_id == dead_target)
                    if dead_block in block.successors: block.successors.remove(dead_block)
                    if block in dead_block.predecessors: dead_block.predecessors.remove(block)
                    mutation.removed_edges.append((block.block_id, dead_target))
                    any_changes = True
        if any_changes: cls._clean_unreachable_blocks(cfg, mutation)
        return any_changes, mutation
    @staticmethod
    def _get_constant_value(cond: any, constants: dict) -> Tuple[bool, any]:
        if isinstance(cond, (bool, int)): return True, bool(cond)
        if str(cond) in constants: return True, bool(constants[str(cond)])
        return False, None
    @classmethod
    def _clean_unreachable_blocks(cls, cfg: ControlFlowGraph, mutation: CFGMutationResult) -> None:
        reachable: Set[int] = set()
        worklist = [cfg.entry_block.block_id]
        while worklist:
            curr_id = worklist.pop(0)
            if curr_id not in reachable:
                reachable.add(curr_id)
                curr_block = next(b for b in cfg.blocks if b.block_id == curr_id)
                for succ in curr_block.successors: worklist.append(succ.block_id)
        all_ids = {b.block_id for b in cfg.blocks}
        unreachable_ids = all_ids - reachable
        if unreachable_ids:
            cfg.blocks = [b for b in cfg.blocks if b.block_id not in unreachable_ids]
            mutation.removed_blocks.update(unreachable_ids)
