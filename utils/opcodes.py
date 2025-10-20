# utils/opcodes.py
import json
from pathlib import Path

LOCAL_OPCODES = {
    0x00: ("BRK", "impl"), 0x01: ("ORA", "indx"), 0x05: ("ORA", "zp"), 0x06: ("ASL", "zp"),
    0x08: ("PHP", "impl"), 0x09: ("ORA", "imm"), 0x0A: ("ASL", "acc"), 0x0D: ("ORA", "abs"),
    0x0E: ("ASL", "abs"), 0x10: ("BPL", "rel"), 0x11: ("ORA", "indy"), 0x15: ("ORA", "zpx"),
    0x16: ("ASL", "zpx"), 0x18: ("CLC", "impl"), 0x20: ("JSR", "abs"), 0x21: ("AND", "indx"),
    0x24: ("BIT", "zp"), 0x25: ("AND", "zp"), 0x26: ("ROL", "zp"), 0x28: ("PLP", "impl"),
    0x29: ("AND", "imm"), 0x2A: ("ROL", "acc"), 0x2C: ("BIT", "abs"), 0x2D: ("AND", "abs"),
    0x2E: ("ROL", "abs"), 0x30: ("BMI", "rel"), 0x38: ("SEC", "impl"), 0x40: ("RTI", "impl"),
    0x48: ("PHA", "impl"), 0x4C: ("JMP", "abs"), 0x60: ("RTS", "impl"), 0x68: ("PLA", "impl"),
    0x69: ("ADC", "imm"), 0x6C: ("JMP", "ind"), 0x70: ("BVS", "rel"), 0x78: ("SEI", "impl"),
    0x85: ("STA", "zp"), 0x86: ("STX", "zp"), 0x88: ("DEY", "impl"), 0x8A: ("TXA", "impl"),
    0x8D: ("STA", "abs"), 0x8E: ("STX", "abs"), 0x90: ("BCC", "rel"), 0x91: ("STA", "indy"),
    0x95: ("STA", "zpx"), 0x98: ("TYA", "impl"), 0x9A: ("TXS", "impl"), 0x9D: ("STA", "absx"),
    0xA0: ("LDY", "imm"), 0xA2: ("LDX", "imm"), 0xA5: ("LDA", "zp"), 0xA9: ("LDA", "imm"),
    0xAD: ("LDA", "abs"), 0xAE: ("LDX", "abs"), 0xB1: ("LDA", "indy"), 0xB5: ("LDA", "zpx"),
    0xB9: ("LDA", "absy"), 0xBD: ("LDA", "absx"), 0xC0: ("CPY", "imm"), 0xC8: ("INY", "impl"),
    0xC9: ("CMP", "imm"), 0xCA: ("DEX", "impl"), 0xD0: ("BNE", "rel"), 0xD8: ("CLD", "impl"),
    0xE0: ("CPX", "imm"), 0xE8: ("INX", "impl"), 0xEA: ("NOP", "impl"), 0xF0: ("BEQ", "rel"),
    0xF8: ("SED", "impl")
}

def load_local_table(path="data/opcodes_nes.json"):
    p = Path(path)
    if not p.exists():
        return {}
    try:
        with p.open("r", encoding="utf-8") as f:
            return {int(k, 16): tuple(v) for k, v in json.load(f).items()}
    except Exception:
        return {}
