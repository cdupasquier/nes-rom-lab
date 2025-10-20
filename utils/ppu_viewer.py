import numpy as np
from PIL import Image
import streamlit as st
from utils.nes_palette import NES_PALETTE, DEMO_PALETTES, GAME_PALETTES

def render_chr_mosaic(chr_data: bytes, tiles_per_row: int = 16, zoom: int = 4):
    """
    Affiche une mosaïque complète de toutes les tuiles CHR-ROM.
    Si aucune CHR n’est présente, on crée une mosaïque simulée (CHR-RAM factice).
    """
    # === Étape 1 : Si pas de CHR-ROM, génération d'une zone graphique simulée ===
    if len(chr_data) == 0:
        st.markdown("""
        <div style="background-color:#222;padding:10px 15px;border-left:6px solid #ffaa33;
        border-radius:8px;font-family:'JetBrains Mono',monospace;color:#ffcc66;margin-bottom:10px;">
        ⚠️ <b>Aucune CHR-ROM détectée</b> — le jeu utilise probablement une <b>CHR-RAM</b>.<br>
        Une mosaïque simulée est générée pour visualisation pédagogique.
        </div>
        """, unsafe_allow_html=True)

        fake_chr = np.zeros((8192,), dtype=np.uint8)
        for i in range(0, len(fake_chr), 16):
            v = (i // 64) % 256
            for j in range(8):
                fake_chr[i + j] = ((v >> (j % 8)) & 0xFF)
                fake_chr[i + 8 + j] = ((~v >> (j % 8)) & 0xFF)
        chr_data = fake_chr.tobytes()

    # === Étape 2 : Décodage normal des tuiles ===
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
        mosaic[r*8:(r+1)*8, c*8:(c+1)*8] = tile

    # === Étape 3 : Fusion palettes (démo + jeux réels) ===
    all_palettes = {**DEMO_PALETTES}
    for game, sections in GAME_PALETTES.items():
        for section_name, indices in sections.items():
            all_palettes[f"🎮 {game} — {section_name}"] = indices

    # === Étape 4 : Sélecteur de palette ===
    palette_name = st.selectbox(
        "🎨 Palette NES à utiliser :",
        list(all_palettes.keys()),
        key="ppu_viewer_palette"
    )
    indices = all_palettes[palette_name]
    palette = NES_PALETTE[indices]

    # === Étape 5 : Rendu final ===
    rgb_image = palette[mosaic]
    img = Image.fromarray(rgb_image, mode="RGB").resize(
        (mosaic.shape[1] * zoom, mosaic.shape[0] * zoom),
        Image.NEAREST
    )

    st.image(img, caption=f"Mosaïque complète des {total_tiles} tuiles CHR", use_container_width=True)

    st.caption(f"💡 Palette active : **{palette_name}** — indices {indices}")
    st.info("""
    🎨 La NES stocke uniquement des indices (0–3) pour chaque pixel.
    Le PPU applique la palette active pour obtenir les vraies couleurs à l’écran.
    """)


def show_ppu_viewer(chr_data: bytes):
    """Interface Streamlit du viewer PPU."""
    st.header("🧩 Visualiseur PPU — Mosaïque graphique")
    st.markdown("""
    Chaque jeu NES contient des **tuiles graphiques 8×8 pixels**,  
    stockées dans la **CHR-ROM**. Ces tuiles forment les sprites, décors, lettres, et ennemis.
    """)

    tiles_per_row = st.slider("Nombre de tuiles par ligne :", 8, 32, 16, step=4)
    zoom = st.slider("Facteur de zoom :", 1, 10, 4)

    render_chr_mosaic(chr_data, tiles_per_row, zoom)

    st.info("""
    🎨 Chaque carré représente une tuile 8×8 issue de la mémoire graphique (CHR).  
    Si aucune CHR-ROM n’est présente, une version simulée est générée pour exploration.
    """)
