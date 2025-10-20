# utils/disasm.py
from .opcodes import LOCAL_OPCODES, load_local_table
import streamlit as st

NES_LOCAL_OPCODES = load_local_table()

def disassemble_full(cpu, start, count=32):
    """
    Désassemble en utilisant NES_LOCAL_OPCODES or session opcode_table or LOCAL_OPCODES.
    """
    mem = cpu.memory
    tab = NES_LOCAL_OPCODES or st.session_state.get("opcode_table_full", {}) or LOCAL_OPCODES
    out = []
    pc = start & 0xFFFF
    for _ in range(count):
        opcode = mem[pc]
        if opcode in tab:
            mnemo, mode = tab[opcode]
            size = cpu.instruction_size.get(opcode, 1) if hasattr(cpu, "instruction_size") else 1
            if size == 1:
                op_str = ""
            elif size == 2:
                val = mem[(pc + 1) & 0xFFFF]
                if mode and "imm" in mode:
                    op_str = f" #${val:02X}"
                else:
                    op_str = f" ${val:02X}"
            else:
                lo = mem[(pc + 1) & 0xFFFF]
                hi = mem[(pc + 2) & 0xFFFF]
                addr = lo | (hi << 8)
                op_str = f" ${addr:04X}"
            out.append(f"${pc:04X}: {mnemo}{op_str}")
            pc = (pc + size) & 0xFFFF
            continue
        # fallback
        size = 1
        if hasattr(cpu, "instruction_size"):
            size = cpu.instruction_size.get(opcode, 1)
        if size == 1:
            out.append(f"${pc:04X}: .db ${opcode:02X}")
            pc = (pc + 1) & 0xFFFF
        elif size == 2:
            val = mem[(pc + 1) & 0xFFFF]
            out.append(f"${pc:04X}: OPC${opcode:02X} ${val:02X}")
            pc = (pc + 2) & 0xFFFF
        else:
            lo = mem[(pc + 1) & 0xFFFF]
            hi = mem[(pc + 2) & 0xFFFF]
            addr = lo | (hi << 8)
            out.append(f"${pc:04X}: OPC${opcode:02X} ${addr:04X}")
            pc = (pc + 3) & 0xFFFF
    return "\n".join(out)


def colorize_disasm(disasm_text: str, current_pc: int):
    import re
    lines = re.findall(r"\$[0-9A-F]{4}:[^$]*", disasm_text, re.IGNORECASE)
    if not lines:
        lines = disasm_text.splitlines()

    html_lines = []
    line_num = 1
    for line in lines:
        line = line.strip()
        if not line:
            continue
        addr = line.split(":")[0].strip()
        if f"${current_pc:04X}" in addr:
            line_html = (
                f"<span style='color:#ffaa00;font-weight:bold;'>➜</span> "
                f"<span style='background-color:#ffaa0044; padding:2px 4px; border-radius:3px;'>{line}</span>"
            )
        else:
            line_html = f"&nbsp;&nbsp;&nbsp;{line}"
        for key, color in {
            "JSR": "#4fa3ff", "JMP": "#4fa3ff",
            "BRK": "#ff4f4f", "RTS": "#ff4f4f", "RTI": "#ff4f4f",
            "LDA": "#00d084", "STA": "#ffb14f", "LDX": "#4fffad", "LDY": "#4fffad",
            "ADC": "#ff66cc", "SBC": "#ff66cc", "CMP": "#ffcc00",
            "BEQ": "#00ccff", "BNE": "#00ccff", "BCC": "#00ccff", "BCS": "#00ccff",
            "BMI": "#00ccff", "BPL": "#00ccff", "BVS": "#00ccff", "BVC": "#00ccff",
            "NOP": "#999999"
        }.items():
            if key in line_html:
                line_html = line_html.replace(key, f"<span style='color:{color}; font-weight:600;'>{key}</span>")
        html_lines.append(f"<span style='color:#555;'>{line_num:>4}</span> │ {line_html}<br>")
        line_num += 1

    return f"""
    <div style="
        font-family: JetBrains Mono, Consolas, monospace;
        font-size: 13px;
        color: #ddd;
        background-color: #111;
        padding: 12px 8px;
        border-radius: 8px;
        line-height: 1.4em;
        white-space: pre;
        overflow-y: auto;
        max-height: 420px;
        border-left: 3px solid #333;
        box-shadow: inset 0 0 8px #000;
    ">
    {''.join(html_lines)}
    </div>
    """


def show_disassembly(start, end):
    """
    Affiche un désassemblage coloré d'une plage mémoire dans Streamlit (fallback demo).
    If you have cpu.memory available, adapt to read real bytes.
    """
    import streamlit as st
    disasm = []
    import numpy as np
    for addr in range(start, end, 3):
        opcode = np.random.choice(["LDA", "STA", "ADC", "CMP", "NOP", "LDY", "BNE", "BEQ", "SBC"])
        disasm.append((addr, opcode))
    html_lines = []
    for addr, opcode in disasm:
        color = {
            "LDA": "#00ff00",
            "STA": "#ffb300",
            "ADC": "#ff6060",
            "CMP": "#ffaa00",
            "BNE": "#00bfff",
            "BEQ": "#0099ff",
            "NOP": "#777777",
            "LDY": "#aaffaa",
            "SBC": "#ff4444",
        }.get(opcode, "#cccccc")
        html_lines.append(f"<div style='font-family:monospace;color:{color};'>${addr:04X}: <b>{opcode}</b></div>")
    st.markdown(
        f"""
        <div style='border:1px solid #333;padding:8px;border-radius:6px;background-color:#111;'>
            <h4 style='color:#ffcc00;'>🧩 Désassemblage : ${start:04X} → ${end:04X}</h4>
            {''.join(html_lines)}
        </div>
        """,
        unsafe_allow_html=True
    )


def is_probable_code(cpu, start_addr, length=64):
    valid_count = 0
    for i in range(length):
        byte = cpu.memory[(start_addr + i) & 0xFFFF]
        if byte in LOCAL_OPCODES:
            valid_count += 1
    return (valid_count / length) > 0.5
