from typing import Dict, Set, List
from .cfg_graph import ControlFlowGraph
from .analysis import AnalysisManager
from .ir_nodes import PhiInstruction

class SSAPlacement:
    @classmethod
    def insert_phi_nodes(cls, am: AnalysisManager) -> None:
        cfg = am.cfg
        df_res = am.state.dominance_frontier
        if not df_res: return
        frontier = df_res.frontier
        def_sites: Dict[str, Set[int]] = {}
        for block in cfg.blocks:
            for instr in block.instructions:
                if hasattr(instr, 'result') and instr.result:
                    def_sites.setdefault(instr.result, set()).add(block.block_id)
        for var_name, sites in def_sites.items():
            worklist = list(sites)
            added_phi_blocks: Set[int] = set()
            while worklist:
                node_id = worklist.pop(0)
                for frontier_id in frontier.get(node_id, set()):
                    if frontier_id not in added_phi_blocks:
                        target_block = next(b for b in cfg.blocks if b.block_id == frontier_id)
                        target_block.instructions.insert(0, PhiInstruction(original_name=var_name))
                        added_phi_blocks.add(frontier_id)
                        if frontier_id not in sites:
                            worklist.append(frontier_id)
