from typing import List, Tuple, Any, Optional

class IRInstruction:
    def uses(self) -> List[str]: return []
    def defines(self) -> Optional[str]: return None
    def replace_use(self, old: str, new: str) -> None: pass
    def replace_def(self, new: str) -> None: pass

class AssignInstruction(IRInstruction):
    def __init__(self, value: Any, result: str):
        self.value = value
        self.result = result
    def uses(self) -> List[str]: return [self.value] if isinstance(self.value, str) else []
    def defines(self) -> Optional[str]: return self.result
    def replace_use(self, old: str, new: str) -> None:
        if self.value == old: self.value = new
    def replace_def(self, new: str) -> None: self.result = new
    def __repr__(self): return f"{self.result} = ASSIGN {self.value}"

class BinaryOpInstruction(IRInstruction):
    def __init__(self, op: str, left: Any, right: Any, result: str):
        self.op, self.left, self.right, self.result = op, left, right, result
    def uses(self) -> List[str]:
        u = []
        if isinstance(self.left, str): u.append(self.left)
        if isinstance(self.right, str): u.append(self.right)
        return u
    def defines(self) -> Optional[str]: return self.result
    def replace_use(self, old: str, new: str) -> None:
        if self.left == old: self.left = new
        if self.right == old: self.right = new
    def replace_def(self, new: str) -> None: self.result = new
    def __repr__(self): return f"{self.result} = {self.op} {self.left}, {self.right}"

class PhiInstruction(IRInstruction):
    def __init__(self, original_name: str):
        self.original_name = original_name
        self.result: Optional[str] = None
        self.operands: List[Tuple[int, str]] = []
    def uses(self) -> List[str]: return [var for _, var in self.operands]
    def defines(self) -> Optional[str]: return self.result
    def replace_use(self, old: str, new: str) -> None:
        self.operands = [(b, new if v == old else v) for b, v in self.operands]
    def replace_def(self, new: str) -> None: self.result = new
    def __repr__(self):
        ops_str = ", ".join([f"B{b}: {v}" for b, v in self.operands])
        res = self.result if self.result else self.original_name
        return f"{res} = PHI({ops_str if ops_str else self.original_name})"

class CallPluginInstruction(IRInstruction):
    def __init__(self, plugin_cmd: Tuple[int, int], args: List[Any]):
        self.plugin_id, self.cmd_id, self.args = plugin_cmd[0], plugin_cmd[1], args
    def uses(self) -> List[str]: return [a for a in self.args if isinstance(a, str)]
    def replace_use(self, old: str, new: str) -> None:
        self.args = [new if a == old else a for a in self.args]
    def __repr__(self): return f"CALL_PLUG ({self.plugin_id}, {self.cmd_id}), {self.args}"

class UnconditionalJump(IRInstruction):
    def __init__(self, target_block_id: int):
        self.target_block_id = target_block_id
    def __repr__(self): return f"JUMP -> B{self.target_block_id}"

class ConditionalJump(IRInstruction):
    def __init__(self, condition: str, true_block_id: int, false_block_id: int):
        self.condition = condition
        self.true_block_id = true_block_id
        self.false_block_id = false_block_id
    def uses(self) -> List[str]: return [self.condition]
    def replace_use(self, old: str, new: str) -> None:
        if self.condition == old: self.condition = new
    def __repr__(self): return f"IF {self.condition} GOTO B{self.true_block_id} ELSE GOTO B{self.false_block_id}"
