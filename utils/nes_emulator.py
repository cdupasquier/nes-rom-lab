# utils/nes_emulator.py
import numpy as np
import streamlit as st
import time
from PIL import Image
from utils.nes_palette import NES_PALETTE, DEMO_PALETTES


# ================================================================
# 🧠 Simulation pédagogique du CPU 6502
# ================================================================
class MiniNESCPU:
    """Simulation simple du CPU 6502 (boucle d’exécution pédagogique)."""

    def __init__(self, memory):
        self.memory = memory
        self.pc = 0x8000  # Adresse de départ
        self.a = 0        # Accumulateur
        self.x = 0
        self.y = 0
        self.cycle = 0

    def step(self):
        """Exécute une pseudo-instruction pour la démonstration."""
        opcode = self.memory[self.pc % len(self.memory)]
        self.pc = (self.pc + 1) & 0xFFFF
        self.a = (self.a + opcode) & 0xFF
        self.cycle += 1
        return opcode


# ================================================================
# 🎨 Simulation simplifiée du PPU avec rendu CHR-ROM ou simulé
# ================================================================
class MiniPPU:
    """Simulation simplifiée du PPU (rendu CHR-ROM réel ou simulé)."""

    def __init__(self, chr_data: bytes | None):
        # Si aucune CHR-ROM n’est présente, on génère une CHR simulée (motifs)
        if not chr_data or len(chr_data) == 0:
            st.warning("⚠️ Aucune CHR-ROM détectée — génération d’une CHR simulée.")
            fake_chr = np.zeros((8192,), dtype=np.uint8)
            for i in range(0, len(fake_chr), 16):
                val = (i // 32) % 256
                for j in range(8):
                    fake_chr[i + j] = ((val >> (j % 8)) & 0xFF)
                    fake_chr[i + 8 + j] = ((~val >> (j % 8)) & 0xFF)
            self.chr_data = fake_chr.tobytes()
        else:
            self.chr_data = chr_data

        self.framebuffer = np.zeros((240, 256, 3), dtype=np.uint8)
        self.frame = 0

    def render_frame(self, frame_index, palette):
        """Affiche la CHR-ROM comme si la NES balayait l’écran image par image."""
        total_tiles = len(self.chr_data) // 16
        tiles_per_row = 16
        rows = (total_tiles + tiles_per_row - 1) // tiles_per_row

        mosaic = np.zeros((rows * 8, tiles_per_row * 8), dtype=np.uint8)
        for i in range(total_tiles):
            tile_bytes = self.chr_data[i * 16:(i + 1) * 16]
            low = np.frombuffer(tile_bytes[:8], dtype=np.uint8)
            high = np.frombuffer(tile_bytes[8:], dtype=np.uint8)
            tile = np.zeros((8, 8), dtype=np.uint8)
            for y in range(8):
                for x in range(8):
                    lo_bit = (low[y] >> (7 - x)) & 1
                    hi_bit = (high[y] >> (7 - x)) & 1
                    tile[y, x] = lo_bit + (hi_bit << 1)
            r, c = divmod(i, tiles_per_row)
            mosaic[r * 8:(r + 1) * 8, c * 8:(c + 1) * 8] = tile

        # Simulation d’un balayage vertical du PPU
        scroll_y = (frame_index * 4) % max(1, mosaic.shape[0] - 240)
        window = mosaic[scroll_y:scroll_y + 240, :256]
        rgb = palette[window]

        return Image.fromarray(rgb, mode="RGB")


# ================================================================
# 🕹️ Émulation NES simplifiée (CPU + PPU)
# ================================================================
def run_emulator(prg_data: bytes, chr_data: bytes = None, frame_count=120):
    """Boucle principale d'émulation simplifiée NES."""
    st.header("🧠 Émulation simplifiée NES")

    st.markdown("""
    Cette démonstration illustre la **boucle interne** d’une console NES :
    - Le **CPU** (6502) exécute le code machine depuis la PRG-ROM.
    - Le **PPU** (Picture Processing Unit) lit les données graphiques depuis la CHR-ROM.
    - Ensemble, ils produisent les images affichées à l’écran.
    """)

    if "emulating" not in st.session_state:
        st.session_state.emulating = False

    col1, col2 = st.columns([1, 1.3])

    # === Contrôles ===
    with col1:
        st.markdown("### 🎮 Contrôle d’exécution")
        if st.button("▶️ Lancer / Mettre en pause l’émulation"):
            st.session_state.emulating = not st.session_state.emulating

        if st.button("⏹️ Réinitialiser"):
            st.session_state.emulating = False
            st.session_state.cpu_state = None

        st.caption("💡 Le CPU exécute une instruction, le PPU affiche une frame, puis la console attend le signal **VBlank** avant de recommencer.")

        # Sélecteur de palette visuelle
        palette_name = st.selectbox("🎨 Palette NES :", list(DEMO_PALETTES.keys()))
        indices = DEMO_PALETTES[palette_name]
        palette = NES_PALETTE[indices]

    # === Zone d'affichage ===
    with col2:
        st.markdown("### 🧩 Boucle CPU/PPU simplifiée")

        if st.session_state.emulating:
            cpu = MiniNESCPU(np.frombuffer(prg_data, dtype=np.uint8))
            ppu = MiniPPU(chr_data)

            progress = st.progress(0)
            img_placeholder = st.empty()
            cpu_state = st.empty()

            for i in range(frame_count):
                opcode = cpu.step()
                img = ppu.render_frame(i, palette)

                # Affichage image
                img_placeholder.image(
                    img,
                    caption=f"🖼️ Frame {i+1}/{frame_count} — PC=${cpu.pc:04X} — Opcode ${opcode:02X}",
                    use_container_width=True
                )

                # Affichage état CPU
                cpu_state.json({
                    "PC": f"${cpu.pc:04X}",
                    "A": f"${cpu.a:02X}",
                    "X": f"${cpu.x:02X}",
                    "Y": f"${cpu.y:02X}",
                    "Cycle": cpu.cycle
                })

                progress.progress((i + 1) / frame_count)
                time.sleep(0.05)

            st.success("✅ Émulation terminée — boucle complète exécutée.")
        else:
            st.info("Appuie sur ▶️ pour démarrer la simulation.")
