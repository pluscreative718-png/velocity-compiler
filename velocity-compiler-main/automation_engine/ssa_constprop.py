from typing import Dict, Any
from .analysis import AnalysisManager, ConstantPropagationResult
from .ir_nodes import AssignInstruction, BinaryOpInstruction, PhiInstruction

class SSAConstantPropagation:
    @classmethod
    def analyze_and_fold(cls, am: AnalysisManager) -> bool:
        cfg = am.cfg
        constants: Dict[str, Any] = {}
        loop_changed = True
        while loop_changed:
            loop_changed = False
            for block in cfg.blocks:
                for instr in block.instructions:
                    if isinstance(instr, AssignInstruction):
                        if isinstance(instr.value, (int, float, str, bool)): val = instr.value
                        else: val = constants.get(instr.value, None)
                        if val is not None and constants.get(instr.result) != val:
                            constants[instr.result] = val
                            loop_changed = True
                    elif isinstance(instr, BinaryOpInstruction):
                        left = instr.left if isinstance(instr.left, (int, float)) else constants.get(instr.left)
                        right = instr.right if isinstance(instr.right, (int, float)) else constants.get(instr.right)
                        if left is not None and right is not None:
                            res_val = cls._evaluate(instr.op, left, right)
                            if res_val is not None and constants.get(instr.result) != res_val:
                                constants[instr.result] = res_val
                                loop_changed = True
                    elif isinstance(instr, PhiInstruction):
                        incoming_vals = [constants.get(ver) for _, ver in instr.operands]
                        if incoming_vals and all(v is not None for v in incoming_vals):
                            if all(v == incoming_vals[0] for v in incoming_vals):
                                if constants.get(instr.result) != incoming_vals[0]:
                                    constants[instr.result] = incoming_vals[0]
                                    loop_changed = True
        any_changes = False
        for block in cfg.blocks:
            for instr in block.instructions:
                for use in list(instr.uses()):
                    if use in constants:
                        instr.replace_use(use, constants[use])
                        any_changes = True
        am.state.constant_values = ConstantPropagationResult(values=constants)
        return any_changes
    @staticmethod
    def _evaluate(op: str, left: Any, right: Any) -> Any:
        try:
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "==": return left == right
        except: return None
        return None
