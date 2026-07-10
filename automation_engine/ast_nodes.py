from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass(frozen=True)
class SourceSpan:
    filepath: str
    line: int
    start_column: int
    end_column: int
    source_line: str

class SymbolTable:
    def __init__(self, parent: 'SymbolTable' = None):
        self.symbols: Dict[str, Any] = {}
        self.parent = parent

@dataclass
class CompilationContext:
    filepath: str
    source_code: str
    tokens: List[Any] = field(default_factory=list)
    ast: Any = None
    linear_ir: List[Any] = field(default_factory=list)
    cfg: Any = None
    symbol_table: SymbolTable = field(default_factory=SymbolTable)
    has_errors: bool = False
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)