import numpy as np
from PIL import Image
import streamlit as st
from utils.nes_palette import NES_PALETTE, DEMO_PALETTES, GAME_PALETTES


# === Génération du fond à partir des tuiles CHR ===
def generate_background(chr_data: bytes, palette, tiles_per_row=16, zoom=2):
    """Crée une mosaïque 2D de toutes les tuiles CHR-ROM (ou simulée)."""
    # === Cas CHR-ROM absente (ROM avec CHR-RAM) ===
    if len(chr_data) == 0:
        st.markdown("""
        <div style="background-color:#1e1e1e;padding:10px 15px;border-left:6px solid #ffb347;
        border-radius:8px;font-family:'JetBrains Mono',monospace;color:#ffd966;margin-bottom:10px;">
        ⚠️ <b>Aucune CHR-ROM détectée</b> — le jeu utilise probablement une <b>CHR-RAM</b>.<br>
        Une mosaïque graphique simulée est générée automatiquement pour visualisation.
        </div>
        """, unsafe_allow_html=True)

        # Génère une fausse CHR avec 8 Ko de données variées
        fake_chr = np.zeros((8192,), dtype=np.uint8)
        for i in range(0, len(fake_chr), 16):
            pattern = (i // 32) % 256
            for j in range(8):
                fake_chr[i + j] = ((pattern >> (j % 8)) & 0xFF)
                fake_chr[i + 8 + j] = ((~pattern >> (j % 8)) & 0xFF)
        chr_data = fake_chr.tobytes()

    # === Décodage standard des tuiles NES ===
    total_tiles = len(chr_data) // 16
    tiles_per_row = max(8, tiles_per_row)
    rows = (total_tiles + tiles_per_row - 1) // tiles_per_row
    mosaic = np.zeros((rows * 8, tiles_per_row * 8), dtype=np.uint8)

    for i in range(total_tiles):
        tile_bytes = chr_data[i * 16:(i + 1) * 16]
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

    # Application de la palette NES
    rgb = palette[mosaic]
    full_img = Image.fromarray(rgb, mode="RGB").resize(
        (mosaic.shape[1] * zoom, mosaic.shape[0] * zoom),
        Image.NEAREST
    )
    return full_img


# === Interface principale ===
def show_ppu_scroller(chr_data: bytes):
    """Simulation interactive du scrolling NES (PPU)."""
    st.header("🌀 Simulation de scrolling NES (PPU)")

    # 🔹 Explication pédagogique
    st.markdown("""
    Le **PPU** (Picture Processing Unit) de la NES est le cœur du rendu visuel.  
    Il ne redessine pas tout à chaque image — il fait **défiler une petite fenêtre (256×240 px)**  
    sur une grande carte mémoire remplie de tuiles.

    > 💡 Imagine une **caméra** qui se déplace sur une grande fresque peinte :  
    > tu ne vois qu'une petite partie à la fois, mais la fresque complète est bien plus large.
    """)

    # --- Fusion palettes générales + jeux réels ---
    all_palettes = {**DEMO_PALETTES}
    for game, sections in GAME_PALETTES.items():
        for section_name, indices in sections.items():
            all_palettes[f"🎮 {game} — {section_name}"] = indices

    # --- Sélecteur interactif ---
    palette_name = st.selectbox(
        "🎨 Palette NES à utiliser :",
        list(all_palettes.keys()),
        key="ppu_scroll_palette"
    )
    indices = all_palettes[palette_name]
    palette = NES_PALETTE[indices]

    st.caption(f"💡 Palette active : **{palette_name}** — indices {indices}")

    # --- Contrôles de zoom et disposition ---
    zoom = st.slider("Zoom (×)", 1, 6, 3)
    tiles_per_row = st.slider("Nombre de tuiles par ligne :", 16, 32, 24)

    # Génération de la mosaïque
    background = generate_background(chr_data, palette, tiles_per_row=tiles_per_row, zoom=zoom)
    if background is None:
        return

    bg_width, bg_height = background.size

    # === Contrôles de scrolling ===
    st.markdown("### 🎮 Contrôle du défilement")
    scroll_x = st.slider("📜 Défilement horizontal", 0, max(0, bg_width - 256), 0)
    scroll_y = st.slider("📜 Défilement vertical", 0, max(0, bg_height - 240), 0)

    # === Rendu de la fenêtre visible ===
    viewport = background.crop((scroll_x, scroll_y, scroll_x + 256, scroll_y + 240))
    st.image(viewport, caption="🪄 Fenêtre visible (256×240 pixels NES)", use_container_width=True)

    # === Visualisation ASCII ===
    st.subheader("🧠 Visualisation du principe de caméra")

    camera_ascii = f"""
    ```
    ┌──────────────────────────────────────────────┐
    │                🌍 Name Table (grande carte)  │
    │----------------------------------------------│
    │   ←────────────── {bg_width//zoom}px ───────────────→
    │
    │      ┌────────────────────────────┐
    │      │         📺 Écran NES       │
    │      │      (256×240 pixels)      │
    │      └────────────────────────────┘
    │             ↑
    │        Caméra du PPU
    │   (scroll_x={scroll_x}, scroll_y={scroll_y})
    └──────────────────────────────────────────────┘
    ```
    """

    st.code(camera_ascii, language="text")

    # === Explications pédagogiques ===
    st.caption("""
    💡 La NES déplace simplement la “caméra” sur la grande carte de tuiles.  
    Quand `scroll_x` augmente, la fenêtre glisse vers la droite, et de nouvelles tuiles apparaissent.
    """)
    st.info("""
    🎓 **À retenir :**
    - La **CHR-ROM** contient les tuiles graphiques brutes (formes).
    - Le **PPU** assemble ces tuiles dans une grande carte mémoire (Name Table).
    - L’écran n’affiche qu’une **fenêtre 256×240 pixels** sur cette carte.
    - Le **scrolling** = déplacer cette fenêtre, pas redessiner toute la scène !
    """)
