# utils/ppu_rom_viewer.py
import numpy as np
from PIL import Image
import streamlit as st
from utils.nes_palette import NES_PALETTE, DEMO_PALETTES


def decode_chr(chr_data: bytes):
    """
    Décode la CHR-ROM en tuiles 8x8.
    Si la ROM utilise de la CHR-RAM (aucune donnée présente),
    on crée un espace vide pour conserver la cohérence pédagogique.
    """
    # 🧠 Cas 1 : aucune donnée graphique trouvée (CHR-RAM)
    if len(chr_data) == 0:
        st.markdown("""
        <div style="
            background-color:#2a1f00;
            border-left:6px solid #ffb347;
            padding:16px 20px;
            border-radius:8px;
            color:#ffcc66;
            font-family:'JetBrains Mono', monospace;
            margin-bottom:20px;
        ">
        ⚠️ <strong>CHR-ROM absente — Jeu utilisant une CHR-RAM</strong><br><br>
        Ce type de cartouche NES ne contient **aucune donnée graphique intégrée**.  
        Les tuiles sont générées dynamiquement en RAM par le CPU au démarrage du jeu.<br><br>
        💡 Un espace graphique vierge de 8 Ko est créé à titre pédagogique.
        </div>
        """, unsafe_allow_html=True)

        # On crée une fausse zone CHR de 8 Ko (512 tuiles de 16 octets)
        chr_data = bytes(8192)

    # 🧱 Décodage standard des tuiles CHR (8×8)
    total_tiles = len(chr_data) // 16
    tiles = []
    for i in range(total_tiles):
        t = np.zeros((8, 8), dtype=np.uint8)
        low = np.frombuffer(chr_data[i*16:i*16+8], dtype=np.uint8)
        high = np.frombuffer(chr_data[i*16+8:i*16+16], dtype=np.uint8)
        for y in range(8):
            for x in range(8):
                lo = (low[y] >> (7 - x)) & 1
                hi = (high[y] >> (7 - x)) & 1
                t[y, x] = lo + (hi << 1)
        tiles.append(t)

    return tiles


# === Construction de Name Table simulée réaliste ===
def build_name_table(theme="mario", width=32, height=30):
    """Construit une table de tuiles NES imitant une scène connue."""
    table = np.zeros((height, width), dtype=np.uint16)

    if theme == "mario":
        for y in range(height):
            for x in range(width):
                if y > 25:
                    table[y, x] = 80 + (x % 4)  # sol
                elif y > 20:
                    table[y, x] = 64 + (x // 2) % 4  # briques
                elif y == 10 and x % 8 == 0:
                    table[y, x] = 100  # nuage
                else:
                    table[y, x] = 0  # ciel
    elif theme == "zelda":
        for y in range(height):
            for x in range(width):
                if y == 0 or y == height-1 or x == 0 or x == width-1:
                    table[y, x] = 32  # mur
                elif (x + y) % 7 == 0:
                    table[y, x] = 48  # arbre
                else:
                    table[y, x] = 16  # sol
    elif theme == "metroid":
        for y in range(height):
            for x in range(width):
                if y > 25:
                    table[y, x] = 96 + (x % 8)
                elif (x * y) % 11 == 0:
                    table[y, x] = 72
                else:
                    table[y, x] = 40
    else:
        table[:, :] = np.random.randint(0, 128, (height, width))
    return table


def render_rom_scene(chr_data: bytes):
    """Affiche un écran NES reconstruit avec une Name Table thématique."""
    st.header("🎮 Reconstruction d’un écran NES réaliste")

    # ⚠️ Gestion CHR-RAM : message + génération automatique
    if len(chr_data) == 0:
        st.markdown("""
        <div style="
            background-color:#2a1f00;
            border-left:6px solid #ffb347;
            padding:16px 20px;
            border-radius:8px;
            color:#ffcc66;
            font-family:'JetBrains Mono', monospace;
            margin-bottom:20px;
        ">
        ⚠️ <strong>CHR-ROM absente — Jeu utilisant une CHR-RAM</strong><br><br>
        Ce jeu ne contient aucune donnée graphique.  
        Le processeur NES écrit les tuiles à la volée dans la mémoire vidéo (VRAM).  
        💡 Pour cette démo, une <strong>CHR-ROM simulée</strong> de 8 Ko est affichée.
        </div>
        """, unsafe_allow_html=True)
                # 🔧 Génération d'une CHR de secours avec motifs visibles
        fake_chr = np.zeros((8192,), dtype=np.uint8)
        for i in range(0, len(fake_chr), 16):
            tile = (i // 16) % 256
            for j in range(8):
                # motif diagonal simple pour visualiser quelque chose
                fake_chr[i + j] = ((tile >> (j % 8)) & 0xFF)
                fake_chr[i + 8 + j] = ((~tile >> (j % 8)) & 0xFF)
        chr_data = fake_chr.tobytes()

    # Sélection du thème et de la palette
    theme = st.selectbox("🕹️ Thème à simuler :", ["mario", "zelda", "metroid"])
    palette_name = st.selectbox(
        "🎨 Palette NES à utiliser :",
        list(DEMO_PALETTES.keys()),
        key=f"palette_{theme}_scene"
    )
    indices = DEMO_PALETTES[palette_name]
    palette = NES_PALETTE[indices]

    # Décodage + construction
    tiles = decode_chr(chr_data)
    table = build_name_table(theme=theme)
    height, width = table.shape

    frame = np.zeros((height * 8, width * 8, 3), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            idx = table[y, x] % len(tiles)
            frame[y*8:(y+1)*8, x*8:(x+1)*8] = palette[tiles[idx]]

    img = Image.fromarray(frame, mode="RGB").resize((512, 480), Image.NEAREST)
    st.image(img, caption=f"Écran simulé — thème : {theme}", use_container_width=True)

    # 🧠 Explications pédagogiques
    st.markdown(f"""
    ### 🧠 Explication
    Ce rendu simule une vraie scène NES :
    - **{theme.capitalize()}** applique une structure logique (sol, mur, ciel, obstacles).
    - Chaque tuile provient directement de la **CHR-ROM** (ou CHR-RAM simulée).
    - Le PPU assemble ces tuiles pour composer le décor final.

    💡 Essaie de changer de palette ou de thème pour observer comment les teintes influencent l’ambiance du jeu !
    """)

    st.info("""
    🪄 Ce mode ne lit pas une ROM complète : il réutilise les tuiles CHR  
    et les agence selon un schéma typique d’un jeu NES pour visualiser le fonctionnement du PPU.
    """)
