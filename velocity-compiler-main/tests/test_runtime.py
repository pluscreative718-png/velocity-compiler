import pytest
from automation_engine.opcode import Opcode
from automation_engine.bytecode import BytecodeInstruction
from automation_engine.plugin_host import PluginHost
from automation_engine.vm import VirtualMachine

def test_vm_execution():
    triggered = []
    def mock_plugin(cmd_id, args): triggered.append(args[0])
    host = PluginHost()
    host.register(1, mock_plugin)
    program = {
        0: [
            BytecodeInstruction(Opcode.LOAD_CONST, ["r0", 42]),
            BytecodeInstruction(Opcode.CALL_PLUGIN, [1, 5, "r0"]),
            BytecodeInstruction(Opcode.HALT, [])
        ]
    }
    vm = VirtualMachine(plugin_host=host)
    vm.load_program(program)
    vm.execute()
    assert triggered == [42]
