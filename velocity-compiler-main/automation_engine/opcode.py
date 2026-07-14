from enum import IntEnum

class Opcode(IntEnum):
    LOAD_CONST  = 0x01
    MOVE        = 0x02
    ADD         = 0x10
    SUB         = 0x11
    MUL         = 0x12
    CMP_EQ      = 0x13
    JUMP        = 0x20
    JUMP_IF     = 0x21
    CALL_PLUGIN = 0x30
    HALT        = 0xFF
