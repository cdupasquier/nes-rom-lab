# utils/nes_crt_view.py
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import streamlit as st
import time
from utils.nes_palette import NES_PALETTE, DEMO_PALETTES


def apply_crt_effect(img: Image.Image, intensity=0.4):
    """Ajoute un effet CRT : balayage, légère distorsion et flou."""
    # Convertit en numpy pour traitement
    arr = np.array(img, dtype=np.uint8)

    # Ajoute un motif de lignes horizontales sombres
    for y in range(0, arr.shape[0], 2):
        arr[y, :, :] = (arr[y, :, :] * (1 - intensity)).astype(np.uint8)

    img = Image.fromarray(arr, "RGB")

    # Légère accentuation des couleurs
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.2)

    # Légère mise au flou pour simuler la persistance du phosphore
    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    return img


def render_crt_view(chr_data: bytes, speed=2, palette_name=None):
    """Affiche une animation de défilement horizontal avec effet CRT."""
    st.header("📺 Mode TV — Effet CRT et défilement NES")

    if not chr_data or len(chr_data) == 0:
        st.warning("Aucune donnée CHR-ROM disponible. Charge d’abord une ROM valide.")
        return

    # Palette NES à utiliser
    if not palette_name:
        palette_name = st.selectbox("🎨 Palette NES :", list(DEMO_PALETTES.keys()))
    indices = DEMO_PALETTES[palette_name]
    palette = NES_PALETTE[indices]

    # --- Construction de la mosaïque CHR ---
    total_tiles = len(chr_data) // 16
    tiles_per_row = 16
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

    rgb = palette[mosaic]
    img = Image.fromarray(rgb, "RGB").resize((512, 480), Image.NEAREST)

    # --- Animation de défilement horizontal ---
    scroll_speed = st.slider("📜 Vitesse du défilement", 1, 10, speed)
    enable_crt = st.checkbox("📺 Activer effet CRT", value=True)

    placeholder = st.empty()
    for offset in range(0, img.width - 256, scroll_speed):
        viewport = img.crop((offset, 0, offset + 256, 240))
        if enable_crt:
            viewport = apply_crt_effect(viewport)
        placeholder.image(viewport, caption=f"Défilement horizontal (offset={offset})", use_container_width=True)
        time.sleep(0.05)

    st.success("🎬 Animation terminée (fin du balayage).")

