from typing import Set, Dict, List
from .analysis import AnalysisManager
from .ir_nodes import IRInstruction

class SSADCE:
    SIDE_EFFECT_TYPES = ("CallPluginInstruction", "UnconditionalJump", "ConditionalJump")
    @classmethod
    def optimize(cls, am: AnalysisManager) -> bool:
        cfg = am.cfg
        definitions: Dict[str, IRInstruction] = {}
        live_instructions: Set[int] = set()
        for block in cfg.blocks:
            for instr in block.instructions:
                definition = instr.defines()
                if definition: definitions[definition] = instr
        worklist: List[IRInstruction] = []
        for block in cfg.blocks:
            for instr in block.instructions:
                if instr.__class__.__name__ in cls.SIDE_EFFECT_TYPES:
                    worklist.append(instr)
        while worklist:
            instr = worklist.pop()
            if id(instr) in live_instructions: continue
            live_instructions.add(id(instr))
            for use in instr.uses():
                if use in definitions:
                    defining_instr = definitions[use]
                    if id(defining_instr) not in live_instructions: worklist.append(defining_instr)
        changed = False
        for block in cfg.blocks:
            original_count = len(block.instructions)
            block.instructions = [i for i in block.instructions if id(i) in live_instructions or i.defines() is None]
            if len(block.instructions) != original_count: changed = True
        return changed
