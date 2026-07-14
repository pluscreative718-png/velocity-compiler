from typing import List, Tuple, Dict, Set
from .cfg_graph import ControlFlowGraph
from .analysis import AnalysisManager
from .ir_nodes import PhiInstruction, AssignInstruction, UnconditionalJump, ConditionalJump

class ParallelCopyResolver:
    @classmethod
    def resolve_moves(cls, moves: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        src_map = {dest: src for src, dest in moves}
        resolved: List[Tuple[str, str]] = []
        done: Set[str] = set()
        visiting: Set[str] = set()
        tmp_counter = 0
        def emit_copy(dest: str):
            nonlocal tmp_counter
            if dest in done: return
            if dest in visiting:
                tmp_reg = f"tmp_ssa_{tmp_counter}"
                tmp_counter += 1
                resolved.append((dest, tmp_reg))
                for d, s in list(src_map.items()):
                    if s == dest: src_map[d] = tmp_reg
                return
            if dest in src_map:
                visiting.add(dest)
                emit_copy(src_map[dest])
                visiting.remove(dest)
            if dest in src_map:
                resolved.append((src_map[dest], dest))
                done.add(dest)
        for dest in list(src_map.keys()): emit_copy(dest)
        return resolved

class SSADestructor:
    @classmethod
    def lower(cls, am: AnalysisManager) -> bool:
        cfg = am.cfg
        changed = False
        for block in cfg.blocks:
            phi_nodes = [i for i in block.instructions if isinstance(i, PhiInstruction)]
            if not phi_nodes: continue
            pred_moves: Dict[int, List[Tuple[str, str]]] = {}
            for phi in phi_nodes:
                for pred_id, source_value in phi.operands:
                    pred_moves.setdefault(pred_id, []).append((source_value, phi.result))
            for pred_id, moves in pred_moves.items():
                predecessor = next(b for b in cfg.blocks if b.block_id == pred_id)
                safe_sequence = ParallelCopyResolver.resolve_moves(moves)
                terminator = None
                if predecessor.instructions and isinstance(predecessor.instructions[-1], (UnconditionalJump, ConditionalJump)):
                    terminator = predecessor.instructions.pop()
                for src, dest in safe_sequence:
                    predecessor.instructions.append(AssignInstruction(value=src, result=dest))
                if terminator: predecessor.instructions.append(terminator)
            block.instructions = [i for i in block.instructions if not isinstance(i, PhiInstruction)]
            changed = True
        return changed
