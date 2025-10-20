# utils/minimap.py
import numpy as np
import base64, io
from PIL import Image
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

ZONES = [
    (0x0000, 0x07FF, (0, 180, 0), "RAM"),
    (0x0800, 0x1FFF, (0, 120, 0), "Mirrors RAM"),
    (0x2000, 0x2007, (0, 100, 255), "PPU Regs"),
    (0x2008, 0x3FFF, (0, 60, 180), "Mirrors PPU"),
    (0x4000, 0x4017, (255, 150, 0), "APU & IO"),
    (0x4018, 0x401F, (90, 90, 90), "Test"),
    (0x4020, 0x5FFF, (180, 0, 180), "Expansion"),
    (0x6000, 0x7FFF, (150, 80, 0), "SRAM"),
    (0x8000, 0xFFFF, (200, 0, 0), "PRG ROM"),
]

def addr_to_x(addr, width):
    return int((addr / 0xFFFF) * (width - 1))

def render_memory_minimap(cpu, executed_addrs, width=1024, height=28, zoom_bytes=256):
    """Génère HTML image + legend (non-interactive)."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for s, e, color, _ in ZONES:
        xs, xe = addr_to_x(s, width), addr_to_x(e, width)
        img[:, xs:xe] = color

    for addr in executed_addrs:
        x = addr_to_x(addr, width)
        img[:, x] = [255, 200, 80]

    x_pc = addr_to_x(cpu.pc, width)
    img[:, max(0, x_pc - 1):x_pc + 2] = [0, 255, 255]

    pil = Image.fromarray(img.astype('uint8'), 'RGB')
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    ticks = [0x0000, 0x2000, 0x4000, 0x6000, 0x8000, 0xA000, 0xC000, 0xE000, 0xFFFF]
    tick_labels = "".join([
        f"<span style='display:inline-block;width:{width/len(ticks):.1f}px;text-align:center;color:#888;font-size:10px;'>${t:04X}</span>"
        for t in ticks
    ])

    html = f"""
    <div style="text-align:center;">
        <img src='data:image/png;base64,{b64}' style='border-radius:4px;width:{width}px;height:{height}px'>
        <div style="font-size:11px;color:#aaa;margin-top:4px;">
            🟩 RAM 🟦 PPU 🟧 APU 🟪 Expansion 🟫 SRAM 🔴 ROM 🟠 Exécuté 🔹 PC
        </div>
        <div style="font-size:10px;margin-top:2px;">{tick_labels}</div>
    </div>
    """
    return html


def display_memory_map(prg_data: bytes, chr_data: bytes, header: bytes):
    """Affiche une vue pédagogique et visuelle de la structure mémoire d'une ROM NES."""
    st.markdown("## 🗺️ Carte mémoire NES — Comprendre la structure")

    st.markdown("""
    Une ROM NES n’est pas qu’un simple fichier :  
    c’est une **mini carte électronique** découpée en zones bien précises.

    Chaque partie joue un rôle essentiel :
    - 📘 **Header** — l’étiquette du jeu : il indique la taille, le format et les options.  
    - ⚙️ **PRG-ROM** — le cerveau : c’est le code du jeu, lu par le processeur **6502**.  
    - 🎨 **CHR-ROM** — la mémoire graphique : elle contient les tuiles, les sprites et les décors.  

    > 💡 Ces segments sont toujours présents (dans cet ordre) et permettent à l’émulateur
    > de savoir où commence le code et où se trouvent les images.
    """)

    # Calculs des tailles
    total_size = len(header) + len(prg_data) + len(chr_data)
    header_ratio = len(header) / total_size
    prg_ratio = len(prg_data) / total_size
    chr_ratio = len(chr_data) / total_size

    # --- Garantir que le header reste visible ---
    min_ratio = 0.02  # 2 % minimum d’affichage visuel
    sizes = [max(header_ratio, min_ratio), prg_ratio, chr_ratio]
    # Renormaliser pour garder un total de 1
    sizes = [s / sum(sizes) for s in sizes]

    # --- Diagramme horizontal ---
    st.markdown("### 🧩 Structure interne de la ROM")

    fig, ax = plt.subplots(figsize=(8, 1))
    segments = ["Header", "PRG-ROM", "CHR-ROM"]
    colors = ["#4B8BBE", "#FFD43B", "#306998"]

    # Fond
    ax.barh([0], [1], color="#222")

    start = 0
    for label, size, color in zip(segments, sizes, colors):
        ax.barh([0], [size], left=[start], color=color, edgecolor="black", label=label)
        start += size

    # --- Annotation flèche pour le Header ---
    ax.annotate(
        "Header (16 octets)",
        xy=(sizes[0] / 2, 0),
        xytext=(0.1, 0.4),
        textcoords='axes fraction',
        arrowprops=dict(arrowstyle="->", color="#4B8BBE", lw=1.5),
        fontsize=9,
        color="#4B8BBE",
        fontweight='bold'
    )

    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.6),
        ncol=3,
        frameon=False
    )

    # --- Ajustements visuels ---
    fig.suptitle("Structure binaire d'une ROM NES", fontsize=12, y=1.25)
    fig.subplots_adjust(top=0.55)  # laisse de la place pour le titre
    st.pyplot(fig)

    # --- Explication détaillée ---
    st.markdown("""
    ### 🔍 Lecture du schéma

    | Couleur | Section | Contenu typique | Rôle dans la console |
    |:--|:--|:--|:--|
    | 🟦 Bleu | **Header (16 octets)** | Signature `NES<1A>`, tailles, flags | Identifie le format du jeu |
    | 🟨 Jaune | **PRG-ROM** | Code machine (processeur 6502) | Logique du jeu, gestion du score, ennemis, etc. |
    | 🟦 Foncé | **CHR-ROM** | Données graphiques compressées | Tuiles, sprites et textures du jeu |

    Ces trois zones forment ensemble le "corps" d’une cartouche NES :
    le processeur lit le code dans la PRG-ROM et le **PPU** (chip graphique)
    lit les tuiles dans la CHR-ROM pour afficher l’image.
    """)

    # --- JSON technique ---
    st.markdown("### 📊 Détails techniques du fichier")
    st.json({
        "Taille totale": f"{total_size} octets",
        "Header": f"{len(header)} octets",
        "PRG-ROM": f"{len(prg_data)} octets",
        "CHR-ROM": f"{len(chr_data)} octets"
    })

    st.caption("""
    🧭 Cette visualisation t’aide à **relier le contenu du fichier .NES** à son fonctionnement réel :  
    chaque octet correspond à une portion du jeu (logique, graphismes ou métadonnées).
    """)

    # --- BONUS : carte RAM CPU ---
    st.markdown("---")
    st.markdown("### 🧠 Carte mémoire CPU NES (en fonctionnement)")

    st.markdown("""
    Lorsque la console tourne, la mémoire est organisée ainsi :
    """)

    html = render_memory_minimap(
        cpu=type("CPU", (), {"pc": 0x8000}),
        executed_addrs=[],
        width=1024,
        height=28
    )
    st.components.v1.html(html, height=80)

    st.markdown("""
    | Couleur | Zone mémoire | Rôle dans la NES | Description détaillée |
    |:--|:--|:--|:--|
    | 🟩 **Vert** | **RAM interne (0x0000–0x07FF)** | Mémoire de travail du processeur | Sert de carnet temporaire au CPU : positions des objets, scores, états des ennemis, etc. Réinitialisée à chaque démarrage. |
    | 🟦 **Bleu** | **PPU (0x2000–0x3FFF)** | Unité graphique (Picture Processing Unit) | Permet au processeur d’envoyer des ordres au moteur vidéo : affichage des sprites, palettes, scrolling et fond d’écran. |
    | 🟧 **Orange** | **APU / I/O (0x4000–0x401F)** | Son et périphériques | Regroupe la partie audio (APU) et la lecture des manettes, boutons et extensions physiques. |
    | 🟪 **Violet** | **Expansion (0x4020–0x5FFF)** | Modules spécifiques à certaines cartouches | Certaines cartouches embarquent leur propre matériel : puces d’extension, mémoire spéciale, coprocesseur, etc. |
    | 🟫 **Marron** | **SRAM (0x6000–0x7FFF)** | Sauvegarde du joueur | Zone mémoire facultative pour stocker les sauvegardes, souvent alimentée par une pile interne. |
    | 🔴 **Rouge** | **PRG-ROM (0x8000–0xFFFF)** | Code du jeu | Contient le programme principal (processeur 6502). C’est ici que résident les instructions du jeu et la logique complète. |
    | 🔹 **Cyan** | **PC (Program Counter)** | Curseur d’exécution | Indique la position actuelle dans la mémoire où le CPU lit la prochaine instruction. Défile au rythme du processeur. |
    """)

    st.info("""
    🧩 Cette “minimap mémoire” te montre comment le processeur NES parcourt la mémoire :
    il lit dans la **ROM rouge** les instructions, écrit temporairement en **RAM verte**,  
    et échange des données avec les **zones bleues** pour le rendu graphique.
    """)

