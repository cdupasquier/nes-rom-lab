# utils/ppu_framebuilder.py
import numpy as np
from PIL import Image
import streamlit as st
import time
import random
from utils.nes_palette import NES_PALETTE, DEMO_PALETTES


# === Fonctions de base inchangées ===
def decode_chr(chr_data: bytes):
    """
    Décode la CHR-ROM en tuiles 8x8.
    Si aucune donnée n’est présente (CHR-RAM), on crée une CHR simulée.
    """
    # 💡 Cas sans CHR-ROM : génération d'une CHR factice
    if len(chr_data) == 0:
        st.markdown("""
        <div style="background-color:#2a1f00;border-left:6px solid #ffb347;
        padding:12px 18px;border-radius:8px;color:#ffcc66;
        font-family:'JetBrains Mono', monospace;margin-bottom:10px;">
        ⚠️ <strong>CHR-ROM absente — Jeu utilisant une CHR-RAM</strong><br>
        Une <strong>CHR simulée</strong> de 8 Ko est générée pour la démonstration.
        </div>
        """, unsafe_allow_html=True)

        fake_chr = np.zeros((8192,), dtype=np.uint8)
        for i in range(0, len(fake_chr), 16):
            tile = (i // 16) % 256
            for j in range(8):
                fake_chr[i + j] = ((tile >> (j % 8)) & 0xFF)
                fake_chr[i + 8 + j] = ((~tile >> (j % 8)) & 0xFF)
        chr_data = fake_chr.tobytes()

    # === Décodage standard des tuiles NES ===
    total_tiles = len(chr_data) // 16
    tiles = []
    for i in range(total_tiles):
        tile_bytes = chr_data[i*16:(i+1)*16]
        low = np.frombuffer(tile_bytes[:8], dtype=np.uint8)
        high = np.frombuffer(tile_bytes[8:], dtype=np.uint8)
        tile = np.zeros((8, 8), dtype=np.uint8)
        for y in range(8):
            for x in range(8):
                lo_bit = (low[y] >> (7 - x)) & 1
                hi_bit = (high[y] >> (7 - x)) & 1
                tile[y, x] = lo_bit + (hi_bit << 1)
        tiles.append(tile)

    # ✅ On renvoie toujours au moins quelques tuiles
    if len(tiles) == 0:
        st.warning("Aucune tuile décodée — CHR invalide ou vide.")
    return tiles


def build_name_table(width=32, height=30, total_tiles=256):
    table = np.zeros((height, width), dtype=np.uint16)
    for y in range(height):
        for x in range(width):
            base = (x * 11 + y * 7) % total_tiles
            table[y, x] = (base + (x ^ y) * 2) % total_tiles
    return table


def build_attribute_table(width=32, height=30):
    attr = np.zeros((height // 2, width // 2), dtype=np.uint8)
    for y in range(attr.shape[0]):
        for x in range(attr.shape[1]):
            attr[y, x] = (x + y * 2) % 4
    return attr


def build_sprites(total_tiles=256, num_sprites=8):
    sprites = []
    for _ in range(num_sprites):
        tile_id = random.randint(0, total_tiles - 1)
        x = random.randint(0, 240)
        y = random.randint(0, 200)
        palette_shift = random.randint(0, 3)
        sprites.append({"id": tile_id, "x": x, "y": y, "shift": palette_shift})
    return sprites


# === Boucle d’animation NES simplifiée ===
def render_ppu_frame(chr_data: bytes):
    st.header("🧩 Écran NES animé (Fond + Sprites + Scroll)")

    if len(chr_data) == 0:
        st.warning("⚠️ Aucune CHR-ROM détectée — génération d’une CHR simulée en mémoire.")

    # Palette principale
    palette_name = st.selectbox(
        "🎨 Palette principale NES :",
        list(DEMO_PALETTES.keys()),
        key="ppu_frame_palette"
    )
    indices = DEMO_PALETTES[palette_name]
    base_palette = NES_PALETTE[indices]

    # Décodage des tuiles
    tiles = decode_chr(chr_data)
    total_tiles = len(tiles)
    if total_tiles == 0:
        st.warning("Aucune tuile trouvée.")
        return

    # Tables
    name_table = build_name_table(total_tiles=total_tiles)
    attribute_table = build_attribute_table()

    # Paramètres d’animation
    enable_sprites = st.checkbox("👾 Activer couche Sprite")
    num_sprites = st.slider("Nombre de sprites", 4, 32, 8)
    animate = st.checkbox("🌀 Activer animation / scroll")
    speed = st.slider("Vitesse d’animation (ms)", 30, 200, 80, 10)

    placeholder = st.empty()

    sprites = build_sprites(total_tiles, num_sprites)

    for frame_i in range(200 if animate else 1):
        scroll_x = frame_i % 16 if animate else 0
        scroll_y = (frame_i // 4) % 8 if animate else 0

        h, w = name_table.shape
        frame = np.zeros((h * 8, w * 8, 3), dtype=np.uint8)

        # --- Fond ---
        for ty in range(h):
            for tx in range(w):
                tile_index = int(name_table[ty, tx]) % total_tiles
                tile = tiles[tile_index]
                attr_x, attr_y = tx // 2, ty // 2
                sub_palette_index = attribute_table[attr_y, attr_x]
                local_palette = np.roll(base_palette, sub_palette_index, axis=0)
                frame[ty*8:(ty+1)*8, tx*8:(tx+1)*8] = local_palette[tile]

        # --- Sprites ---
        if enable_sprites:
            for s in sprites:
                tile = tiles[s["id"]]
                sprite_palette = np.roll(base_palette, s["shift"], axis=0)
                sprite_img = sprite_palette[tile]
                mask = tile > 0
                # petit mouvement NES-like
                s["x"] = (s["x"] + random.choice([-1, 0, 1])) % 248
                s["y"] = (s["y"] + random.choice([-1, 0, 1])) % 232
                sy, sx = s["y"], s["x"]
                for y in range(8):
                    for x in range(8):
                        if mask[y, x]:
                            frame[sy + y, sx + x] = sprite_img[y, x]

        # --- Scroll (caméra) ---
        viewport = frame[scroll_y:scroll_y+240, scroll_x:scroll_x+256]
        img = Image.fromarray(viewport, mode="RGB").resize((512, 480), Image.NEAREST)
        placeholder.image(img, caption=f"🕹️ Frame {frame_i:03d}", use_container_width=True)

        if animate:
            time.sleep(speed / 1000.0)

    st.info("""
    💡 L’écran NES fait défiler le décor par translation de la caméra,  
    et le PPU redessine les sprites chaque frame (~60 fps sur console réelle).
    """)
