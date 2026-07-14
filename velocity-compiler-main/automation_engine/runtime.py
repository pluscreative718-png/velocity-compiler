from .vm import VirtualMachine

class BytecodeDebugger:
    @staticmethod
    def dump_state(vm: VirtualMachine) -> None:
        print("\n" + "="*35)
        print("⚡ VELOCITY VM INSPECTION TRACE ⚡")
        print("="*35)
        print(f" Execution Position : Block B{vm.current_block}, IP: {vm.instruction_pointer}")
        for reg in sorted(vm.registers.keys()):
            print(f"   {reg:<6} -> {vm.registers[reg]}")
        print("="*35 + "\n")
