from typing import Dict, Set
from .analysis import AnalysisManager
from .ir_nodes import AssignInstruction

class SSACopyPropagation:
    @classmethod
    def optimize(cls, am: AnalysisManager) -> bool:
        cfg = am.cfg
        aliases: Dict[str, str] = {}
        changed = False
        for block in cfg.blocks:
            for instr in block.instructions:
                if isinstance(instr, AssignInstruction) and isinstance(instr.value, str):
                    aliases[instr.result] = instr.value
        def resolve(name: str) -> str:
            visited: Set[str] = set()
            while name in aliases and name not in visited:
                visited.add(name)
                name = aliases[name]
            return name
        for key in list(aliases.keys()): aliases[key] = resolve(aliases[key])
        for block in cfg.blocks:
            for instr in block.instructions:
                for use in list(instr.uses()):
                    if use in aliases:
                        replacement = aliases[use]
                        if replacement != use:
                            instr.replace_use(use, replacement)
                            changed = True
        if changed:
            for block in cfg.blocks:
                block.instructions = [i for i in block.instructions if not (isinstance(i, AssignInstruction) and i.result in aliases)]
        return changed
