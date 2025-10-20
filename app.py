# app.py — NES ROM Lab (version pédagogique complète sans upload)
import streamlit as st
import hashlib, zlib, os
from utils import (
    edu_helpers,
    chr,
    disasm,
    cpu_manager,
    minimap,
    ppu_scroll,
    ppu_viewer,
    nes_emulator,
)

# === CONFIGURATION GLOBALE ===
st.set_page_config(
    page_title="🧠 NES ROM Lab",
    page_icon="🎮",
    layout="wide"
)

st.title("🧬 NES ROM Lab — Exploration pédagogique des ROMs Nintendo")

# === CHARGEMENT AUTOMATIQUE DE LA ROM PAR DÉFAUT ===
DEFAULT_ROM_PATH = os.path.join("roms", "SMB3.nes")

# --- Initialisation de l’état global ---
if "rom_loaded" not in st.session_state:
    st.session_state.rom_loaded = False
    st.session_state.rom_name = None
    st.session_state.header = {}
    st.session_state.prg_data = b""
    st.session_state.chr_data = b""

# --- BANDEAU LATÉRAL ---
st.sidebar.header("📂 Chargement de la ROM")
if not os.path.exists(DEFAULT_ROM_PATH):
    st.sidebar.error("❌ Aucune ROM détectée.\nPlace `SMB3.nes` dans le dossier `/roms` pour lancer la démo.")
    st.stop()

# ✅ Supprimer tout composant d’upload
st.sidebar.markdown("""
<div style="
    background-color:#101010;
    color:#ccc;
    padding:10px;
    border-radius:8px;
    border-left:4px solid #00cc66;
    margin-bottom:10px;">
    🎮 <b>Mode démo activé :</b><br>
    Chargement automatique de <b>Super Mario Bros 3</b>.<br>
    <i>(Chargement verrouillé — aucun import possible)</i>
</div>
""", unsafe_allow_html=True)

# --- Chargement automatique de la ROM ---
if not st.session_state.rom_loaded:
    with open(DEFAULT_ROM_PATH, "rb") as f:
        rom_data = f.read()

    header = rom_data[:16]
    prg_size = header[4] * 16384
    chr_size = header[5] * 8192

    prg_data = rom_data[16:16 + prg_size]
    chr_data = rom_data[16 + prg_size:16 + prg_size + chr_size]

    st.session_state.rom_loaded = True
    st.session_state.rom_name = "Super Mario Bros 3 (démo)"
    st.session_state.header = header
    st.session_state.prg_data = prg_data
    st.session_state.chr_data = chr_data

st.sidebar.success("🎮 ROM chargée : Super Mario Bros 3 (mode démo)")

# === Données globales ===
rom_name = st.session_state.rom_name
header = st.session_state.header
prg_data = st.session_state.prg_data
chr_data = st.session_state.chr_data

# --- Calcul des empreintes ---
sha1 = hashlib.sha1(prg_data + chr_data).hexdigest()
crc32 = f"{zlib.crc32(prg_data + chr_data) & 0xffffffff:08X}"

# --- Paramètres du header ---
prg_size = header[4] * 16384 if header else 0
chr_size = header[5] * 8192 if header else 0
trainer = bool(header[6] & 0b100) if header else False

# === BANDEAU D’INFORMATION ROM ===
st.markdown(f"""
<div style="background-color:#101010;padding:10px 20px;border-left:6px solid #4CAF50;
border-radius:8px;margin-bottom:15px;">
<h4 style="color:#4CAF50;margin-bottom:5px;">🎮 ROM actuellement chargée</h4>
<p style="color:#ddd;margin:0;">
<b>Nom :</b> {rom_name}<br>
<b>PRG-ROM :</b> {prg_size//1024} Ko |
<b>CHR-ROM :</b> {chr_size//1024} Ko |
<b>SHA1 :</b> {sha1[:10]}... |
<b>CRC32 :</b> {crc32}
</p>
</div>
""", unsafe_allow_html=True)

# === Navigation principale ===
tabs = st.tabs([
    "🎮 Introduction",
    "⚙️ CPU & Architecture",
    "🎨 Graphismes (CHR-ROM)",
    "🧩 Graphismes (PPU)",
    "📦 Format iNES",
    "🧱 Matériel & mémoire",
    "🕹️ Émulation simplifiée",
    "🧠 Reconstruction Frame NES",
    "🎮 Reconstruction NES",
    "ℹ️ À propos"
])

# -----------------------------------------------------------------
# 🕹️ ONGLET 1 — INTRODUCTION
# -----------------------------------------------------------------
with tabs[0]:
    edu_helpers.intro()
    edu_helpers.explain_octet_lifecycle()

# -----------------------------------------------------------------
# ⚙️ ONGLET 2 — ARCHITECTURE & CPU
# -----------------------------------------------------------------
with tabs[1]:
    edu_helpers.explain_cpu_basics()
    st.markdown("---")
    st.markdown("### 🔍 Exemple de désassemblage simplifié (PRG-ROM)")
    cpu_manager.show_cpu_interface(prg_data)
    st.markdown("---")
    cpu_manager.show_cpu_step_interface(prg_data)

# -----------------------------------------------------------------
# 🎨 ONGLET 3 — GRAPHISMES
# -----------------------------------------------------------------
with tabs[2]:
    edu_helpers.explain_ppu_concept()
    st.markdown("---")
    st.markdown("### 🧱 Analyse des tuiles CHR")
    subtab1, subtab2 = st.tabs(["📊 Vue d’ensemble", "🔬 Décomposition d’une tuile"])
    with subtab1:
        edu_helpers.explain_chr_tiles(chr_data)
    with subtab2:
        edu_helpers.show_chr_tile_detail(chr_data)

# -----------------------------------------------------------------
# 🧩 ONGLET 4 — PPU 
# -----------------------------------------------------------------
with tabs[3]:
    st.markdown("### 🧩 PPU — Visualiseur graphique")
    subtab1, subtab2 = st.tabs(["🧱 Planche CHR complète", "🌀 Scrolling NES"])
    with subtab1:
        ppu_viewer.show_ppu_viewer(chr_data)
    with subtab2:
        ppu_scroll.show_ppu_scroller(chr_data)

# -----------------------------------------------------------------
# 📦 ONGLET 5 — STRUCTURE iNES
# -----------------------------------------------------------------
with tabs[4]:
    st.header("📦 Structure interne du format iNES")
    edu_helpers.explain_ines_header(prg_size, chr_size, trainer, header)
    edu_helpers.explain_integrity(sha1, crc32)

# -----------------------------------------------------------------
# 🗺️ ONGLET 6 — MINIMAP
# -----------------------------------------------------------------
with tabs[5]:
    st.header("🧱 Matériel & mémoire — Vue d'ensemble de la console NES")
    minimap.display_memory_map(prg_data, chr_data, header)
    edu_helpers.show_memory_bus_diagram()
    edu_helpers.show_frame_cycle_overview()
    edu_helpers.show_vram_explanation()
    edu_helpers.show_sprites_explanation()
    st.markdown("---")
    edu_helpers.show_sync_explanation()
    edu_helpers.show_apu_explanation()
    st.markdown("---")
    edu_helpers.show_cartridge_explanation()
    edu_helpers.show_advanced_mappers()

# -----------------------------------------------------------------
# 🕹️ ONGLET 7 — ÉMULATION SIMPLIFIÉE
# -----------------------------------------------------------------
with tabs[6]:
    nes_emulator.run_emulator(prg_data, chr_data)

# -----------------------------------------------------------------
# 🧠 ONGLET 8 — RECONSTRUCTION FRAME NES
# -----------------------------------------------------------------
with tabs[7]:
    from utils import ppu_framebuilder
    ppu_framebuilder.render_ppu_frame(chr_data)

# -----------------------------------------------------------------
# 🎮 ONGLET 9 — RECONSTRUCTION NES
# -----------------------------------------------------------------
with tabs[8]:
    import utils.ppu_rom_viewer as rom_viewer
    rom_viewer.render_rom_scene(chr_data)


# -----------------------------------------------------------------
# ℹ️ ONGLET 10 — À PROPOS
# -----------------------------------------------------------------
with tabs[9]:
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #C32E2E 0%, #E55353 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        text-shadow: 1px 1px 2px #000;
        font-family: 'Press Start 2P', monospace;
        font-size: 15px;">
        🕹️ NES ROM LAB — ABOUT / À PROPOS
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 25px;
        color: #ddd;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.6;
    ">
    <h3 style="color:#FF5555;">🎯 Objectif pédagogique</h3>
    <p>
    <b>NES ROM Lab</b> est une plateforme interactive destinée à explorer la structure interne
    des ROMs <b>Nintendo Entertainment System</b>.<br>
    L’objectif est de rendre accessibles et visuelles les notions de :
    </p>
    <ul>
        <li>Architecture <b>8-bit</b> du processeur <b>MOS 6502</b></li>
        <li>Mémoire <b>PRG-ROM / CHR-ROM</b></li>
        <li>Graphismes gérés par le <b>PPU</b> (Picture Processing Unit)</li>
        <li>Mécanismes de <b>sprites, scrolling, mappers</b></li>
        <li>Analyse du <b>format iNES</b></li>
    </ul>

    <p>💡 Il s’agit d’un <b>outil pédagogique</b> et non d’un émulateur complet.<br>
    Le rendu graphique est simulé à des fins d’apprentissage.</p>

    <hr style="border-color:#333;margin:20px 0;">

    <h3 style="color:#4CAF50;">🧩 Technologies utilisées</h3>
    <ul>
        <li>Python 3.11+</li>
        <li>Streamlit pour l’interface</li>
        <li>NumPy / Pillow pour le traitement graphique</li>
        <li>Code couleur rétro façon Famicom</li>
    </ul>

    <hr style="border-color:#333;margin:20px 0;">

    <h3 style="color:#FFD700;">👤 Auteur</h3>
    <p>
    Développé par <b>Christophe Dupasquier</b><br>
    <i>ICT-MANAGER, passionné de rétro-ingénierie et de pédagogie numérique.</i><br><br>
    “Derrière chaque pixel de Mario, il y a un processeur qui pense en binaire.”
    </p>

    <hr style="border-color:#333;margin:20px 0;">

    <h3 style="color:#66CCFF;">⚖️ Licence & usage</h3>
    <p>
    Ce projet est diffusé à des fins éducatives et non commerciales.<br>
    Aucune ROM protégée n’est incluse.<br>
    ROM par défaut : <b>Super Mario Bros 3 (démo pédagogique)</b>.
    </p>

    <hr style="border-color:#333;margin:20px 0;">

    <h3 style="color:#9999FF;">❤️ Remerciements</h3>
    <ul>
        <li>Communauté <b>NESDev Wiki</b></li>
        <li><b>Nintendo</b> pour sa console légendaire</li>
        <li>Tous les passionnés de rétro-computing</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <script>
      if ("serviceWorker" in navigator) {
        window.addEventListener("load", () => {
          navigator.serviceWorker.register("static/service-worker.js");
        });
      }
    </script>

    <link rel="manifest" href="static/manifest.json">
    """,
    unsafe_allow_html=True
)
    
    
    
# === FOOTER RETRO NES ===
st.markdown("""
<style>
.footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: #0a0a0a;
    color: #7fff7f;
    font-family: 'Courier New', monospace;
    text-align: center;
    font-size: 13px;
    padding: 8px 0;
    border-top: 1px solid #00ff66;
    box-shadow: 0 -2px 8px rgba(0,255,100,0.2);
    z-index: 100;
}
.footer a {
    color: #00ff99;
    text-decoration: none;
}
.footer a:hover {
    text-decoration: underline;
}
</style>

<div class="footer">
    🕹️ <b>NES ROM Lab</b> — Mode démo actif : <b>Super Mario Bros 3</b> | 
    © 2025 <a href="https://github.com/cdupasquier" target="_blank">Christophe Dupasquier</a>
</div>
""", unsafe_allow_html=True)


