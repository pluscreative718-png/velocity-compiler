from .analysis import AnalysisManager
from .ir_nodes import PhiInstruction, AssignInstruction

class PhiSimplifier:
    @classmethod
    def optimize(cls, am: AnalysisManager) -> bool:
        cfg = am.cfg
        changed = False
        existing_blocks = {b.block_id for b in cfg.blocks}
        for block in cfg.blocks:
            new_instructions = []
            for instr in block.instructions:
                if isinstance(instr, PhiInstruction):
                    old_operands = instr.operands
                    instr.operands = [(pred, value) for pred, value in instr.operands if pred in existing_blocks]
                    if len(instr.operands) != len(old_operands): changed = True
                    if not instr.operands:
                        changed = True
                        continue
                    if len(instr.operands) == 1:
                        new_instructions.append(AssignInstruction(value=instr.operands[0][1], result=instr.result))
                        changed = True
                        continue
                    values = {value for _, value in instr.operands}
                    if len(values) == 1:
                        new_instructions.append(AssignInstruction(value=next(iter(values)), result=instr.result))
                        changed = True
                        continue
                new_instructions.append(instr)
            block.instructions = new_instructions
        return changed
