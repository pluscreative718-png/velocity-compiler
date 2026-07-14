import pytest
from automation_engine.cfg import BasicBlock
from automation_engine.cfg_graph import ControlFlowGraph
from automation_engine.analysis import AnalysisManager
from automation_engine.ir_nodes import AssignInstruction, BinaryOpInstruction, CallPluginInstruction
from automation_engine.ssa_constprop import SSAConstantPropagation

def test_constant_propagation_folding():
    b0 = BasicBlock(0)
    b1 = BasicBlock(1)
    b0.instructions = [BinaryOpInstruction("+", 10, 20, "x_1")]
    b1.instructions = [AssignInstruction("x_1", "x_2"), CallPluginInstruction((1,0), ["x_2"])]
    b0.successors = [b1]
    b1.predecessors = [b0]
    cfg = ControlFlowGraph(b0, [b0, b1])
    am = AnalysisManager(cfg)
    SSAConstantPropagation.analyze_and_fold(am)
    assert am.state.constant_values.values["x_1"] == 30
