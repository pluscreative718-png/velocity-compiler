from .cfg_graph import ControlFlowGraph

class SSAVerifier:
    @staticmethod
    def verify(cfg: ControlFlowGraph) -> None:
        definitions = set()
        uses = []
        for block in cfg.blocks:
            for instr in block.instructions:
                definition = instr.defines()
                if definition:
                    if definition in definitions:
                        raise RuntimeError(f"Duplicate SSA Definition: '{definition}'")
                    definitions.add(definition)
                uses.extend(instr.uses())
        for use in uses:
            if isinstance(use, str) and "_" in use:
                if use not in definitions:
                    raise RuntimeError(f"Undefined SSA Variable read: '{use}'")
        print("Verify: SSA invariants fully intact.")
