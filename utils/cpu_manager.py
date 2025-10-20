# cpu_manager.py
from py65.devices.mpu6502 import MPU
import streamlit as st
import numpy as np
from utils import disasm

def init_cpu(prg_data: bytes, prg_size: int, reset_vector: int):
    """
    Initialise et retourne un CPU MPU avec le PRG-ROM mappé à 0x8000..0xFFFF.
    """
    cpu = MPU()

    try:
        if prg_size == 16 * 1024:
            cpu.memory[0x8000:0x8000 + prg_size] = prg_data
            cpu.memory[0xC000:0xC000 + prg_size] = prg_data
        else:
            length = min(prg_size, 0x8000)
            cpu.memory[0x8000:0x8000 + length] = prg_data[:length]
    except Exception:
        cpu.memory[0x8000:0x8000 + min(prg_size, 0x8000)] = prg_data[:min(prg_size, 0x8000)]

    cpu.pc = reset_vector
    return cpu


def run_steps(session_state: dict, n: int = 1):
    """
    Exécute n instructions sur le CPU stocké dans session_state["cpu"].
    Met à jour session_state['trace'], 'steps', 'executed_addrs', 'halted'.
    """
    if "cpu" not in session_state:
        return

    cpu = session_state["cpu"]
    if "trace" not in session_state:
        session_state["trace"] = []
    if "executed_addrs" not in session_state:
        session_state["executed_addrs"] = set()
    if "steps" not in session_state:
        session_state["steps"] = 0
    if "halted" not in session_state:
        session_state["halted"] = False

    last_pc = cpu.pc
    for _ in range(n):
        if session_state["halted"]:
            break
        pc = cpu.pc
        opcode = cpu.memory[pc]
        try:
            cpu.step()
        except Exception as e:
            session_state["trace"].append(f"⚠️ Erreur exécution: {e}")
            session_state["halted"] = True
            break

        session_state["trace"].append(f"${pc:04X}: OPC=${opcode:02X}  A={cpu.a:02X} X={cpu.x:02X} Y={cpu.y:02X} SP={cpu.sp:02X}")
        session_state["steps"] += 1

        session_state["executed_addrs"].add(last_pc)
        session_state["executed_addrs"].add(cpu.pc)
        last_pc = cpu.pc

        if opcode == 0x00:  # BRK
            session_state["trace"].append("🟥 BRK rencontré — arrêt du CPU.")
            session_state["halted"] = True
            break

    # ensure PC added for minimap
    session_state["executed_addrs"].add(cpu.pc)

import streamlit as st
import numpy as np
from . import disasm


def show_cpu_interface(prg_data: bytes):
    """Interface pédagogique de découverte du CPU 6502 et du désassemblage NES."""

    st.subheader("⚙️ Processeur 6502 — Cœur de la NES")

    st.markdown("""
    ### 🧠 Les bases — Comment pense le processeur 6502

    Le **MOS 6502** est un petit processeur 8 bits, le cœur de la console NES.  
    On peut l’imaginer comme un chef d’orchestre minuscule : il lit le programme,  
    exécute les instructions les unes après les autres et déplace les données en mémoire.

    ---

    #### ⚙️ Architecture simplifiée

    | Élément | Rôle dans le processeur | Exemple concret |
    |:--|:--|:--|
    | **8 bits** | Taille des données manipulées — le processeur ne comprend que les nombres de 0 à 255. | `LDA #$20` charge la valeur 32 (0x20) dans un registre. |
    | **Registre A (Accumulateur)** | C’est la “main droite” du CPU. Presque toutes les opérations passent par lui : addition, comparaison, transfert. | `LDA`, `ADC`, `STA` |
    | **Registres X et Y** | Petits registres d’index utilisés pour parcourir la mémoire ou décaler des positions. | `LDX #$05` puis `LDA $2000,X` |
    | **Registre P (Processor Status)** | Contient **des drapeaux** qui indiquent l’état du CPU : Zéro (Z), Négatif (N), Retenue (Carry), etc. | Après `LDA #$00`, le flag Z est activé. |
    | **PC (Program Counter)** | L’adresse mémoire de la **prochaine instruction** à exécuter. Il avance automatiquement. | Si `PC = $8000`, la prochaine lecture sera à `$8001`. |
    | **SP (Stack Pointer)** | Pointeur de pile : une petite zone de sauvegarde temporaire pour les sous-programmes et interruptions. | Lors d’un `JSR`, le CPU pousse l’adresse de retour sur la pile. |

    ---

    #### 💡 Ce qu’il faut retenir

    - Le 6502 ne fait qu’**une seule chose à la fois** (8 bits par 8 bits).  
    - Il lit le code, exécute, met à jour ses registres et recommence.  
    - La **mémoire** est son terrain de jeu : tout ce qu’il fait, il le lit ou l’écrit dedans.

    > 🧩 Une ROM NES n’est rien d’autre qu’un grand cahier d’instructions binaires  
    > que ce petit processeur lit, interprète et transforme en jeu vivant à l’écran.
    """)

    # --- Tabs pédagogiques ---
    tab1, tab2 = st.tabs(["📜 Désassemblage interactif", "🔍 Explications pédagogiques"])

    # ------------------------------------------------------------------
    # Onglet 1 : Désassemblage interactif
    # ------------------------------------------------------------------
    with tab1:
        st.markdown("### 📜 Désassemblage interactif du code PRG-ROM")

        st.caption("""
        💡 Le désassemblage consiste à **traduire le binaire machine**
        en instructions lisibles (`LDA`, `STA`, `JSR`, etc.).
        """)

        # === Interface utilisateur ===
        start_addr = st.number_input(
            "Adresse de départ (hex):",
            min_value=0x0000, max_value=len(prg_data),
            value=0x0000, step=0x0010
        )
        count = st.slider("Nombre d’instructions à afficher :", 16, 128, 32)

        # --- Simulation mémoire CPU ---
        class DummyCPU:
            def __init__(self, data):
                import numpy as np
                self.memory = np.frombuffer(data, dtype=np.uint8)
                self.instruction_size = {}

        cpu = DummyCPU(prg_data)

        # --- Désassemblage ---
        disasm_text = disasm.disassemble_full(cpu, start_addr, count=count)
        current_pc = start_addr
        html = disasm.colorize_disasm(disasm_text, current_pc)

        # === Rendu HTML isolé ===
        with st.container():
            st.components.v1.html(html, height=500, scrolling=True)

        # === Légende pédagogique ===
        st.markdown("""
        <div style="
            margin-top:8px;
            padding:10px 14px;
            background-color:#1a1a1a;
            border-left:4px solid #444;
            border-radius:6px;
            color:#ccc;
            font-family:'JetBrains Mono', monospace;
            font-size:13px;
            line-height:1.5em;
        ">
        🧩 Les <strong>opcodes colorés</strong> indiquent la nature des instructions :<br>
        <span style="color:#00d084;">LDA</span> = chargement • 
        <span style="color:#ffb14f;">STA</span> = stockage • 
        <span style="color:#4fa3ff;">JSR/JMP</span> = saut • 
        <span style="color:#ff4f4f;">BRK/RTS</span> = fin / retour • 
        <span style="color:#00ccff;">BNE/BEQ/BCC</span> = branchements conditionnels
        </div>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # Onglet 2 : Explications pédagogiques
    # ------------------------------------------------------------------
    with tab2:
        st.markdown("### 🔍 Anatomie d’une instruction 6502")

        st.markdown("""
        Chaque instruction du processeur suit un schéma simple :

        | Élément | Description | Exemple |
        |----------|--------------|----------|
        | **Opcode** | Code machine (1 octet) indiquant l'opération | `LDA` |
        | **Mode d’adressage** | Façon dont l’instruction lit la mémoire | `#imm`, `$addr`, `(addr,X)` |
        | **Opérande** | La donnée ou adresse concernée | `#$20`, `$0600` |

        ### 🧮 Exemple :
        ```
        $8000: LDA #$20
        ```
        > Charge la valeur **$20** (32 en décimal) dans l’accumulateur `A`.

        ### 📊 Types d’instructions
        - **Transfert** (`LDA`, `STA`, `LDX`, `LDY`)
        - **Arithmétique** (`ADC`, `SBC`, `INC`, `DEC`)
        - **Logique** (`AND`, `ORA`, `EOR`)
        - **Sauts / branchements** (`JMP`, `JSR`, `BNE`, `BEQ`, `RTS`)
        - **Contrôle / drapeaux** (`CLC`, `SEC`, `SEI`, `CLI`, `NOP`)
        """)

        st.info("""
        🧠 Le désassembleur convertit donc une suite d’octets en texte compréhensible.  
        En analysant les motifs (`JSR`, `LDA`, `STA`...), on peut reconstruire  
        le comportement du jeu original.
        """)
        
        
class SimpleCPU:
    """Simulation pédagogique ultra simplifiée du processeur MOS 6502."""
    def __init__(self, data: bytes):
        self.memory = np.frombuffer(data, dtype=np.uint8)
        self.pc = 0x0000
        self.a = 0
        self.x = 0
        self.y = 0
        self.sp = 0xFF
        self.p = 0b00100000  # Flag par défaut (bit 5 toujours à 1)
        self.last_instr = ""

    def step(self):
        """Exécute une instruction fictive (simulation pédagogique, non complète)."""
        opcode = int(self.memory[self.pc])
        self.last_instr = disasm.disassemble_full(self, self.pc, 1)
        self.pc = (self.pc + 1) & 0xFFFF  # incrémente le PC
        self.a = (self.a + opcode) & 0xFF  # petite opération bidon
        return self.last_instr

    def dump_registers(self):
        """Retourne un dictionnaire des registres actuels."""
        return {
            "PC": f"${self.pc:04X}",
            "A": f"${self.a:02X}",
            "X": f"${self.x:02X}",
            "Y": f"${self.y:02X}",
            "SP": f"${self.sp:02X}",
            "P (flags)": f"{self.p:08b}"
        }

# --------------------------------------------------------------
# INTERFACE STREAMLIT
# --------------------------------------------------------------

def show_cpu_step_interface(prg_data: bytes):
    """Interface interactive : CPU 6502 simulé pas à pas."""
    st.header("🧮 Simulation CPU Step-by-Step (MOS 6502)")

    if "cpu" not in st.session_state:
        st.session_state["cpu"] = SimpleCPU(prg_data)

    cpu = st.session_state["cpu"]

    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.subheader("📊 Registres actuels")
        st.json(cpu.dump_registers())

        if st.button("▶️ Exécuter une instruction"):
            last = cpu.step()
            st.session_state["last_instr"] = last
            st.toast("Instruction exécutée !", icon="⚙️")

        if st.button("⏹️ Réinitialiser CPU"):
            st.session_state["cpu"] = SimpleCPU(prg_data)
            st.session_state["last_instr"] = disasm.disassemble_full(st.session_state["cpu"], 0, 8)
            st.success("CPU remis à zéro.")

    with col2:
        st.subheader("📜 Désassemblage")
        disasm_text = st.session_state.get("last_instr", disasm.disassemble_full(cpu, 0, 8))
        html = disasm.colorize_disasm(disasm_text, cpu.pc)
        st.markdown(html, unsafe_allow_html=True)

    st.caption("""
    💡 Cette simulation n’exécute pas le code réel,  
    mais reproduit le comportement du CPU pour t’aider à visualiser le **cycle d’exécution** :
    lecture → décodage → exécution → incrément du compteur de programme.  

    🧠 **Astuce pédagogique :**
    - Premier clic sur ⏹️ → *reset partiel* (seuls les registres sont réinitialisés)  
    - Second clic consécutif → *reset complet* (CPU et mémoire reviennent à $0000)
    """)