# utils/edu_helpers.py
import streamlit as st
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image
from utils.disasm import disassemble_full, colorize_disasm
import matplotlib.pyplot as plt
# ---------------------------------------------------
# 🎓 INTRODUCTION GÉNÉRALE
# ---------------------------------------------------

def intro():
    """Introduction générale de l'application."""
    st.markdown("""
    ## 🎮 Bienvenue dans NES ROM Lab

    Plonge dans les entrailles d’un jeu **Nintendo NES** et découvre comment cette console
    de 8 bits transformait quelques octets en aventures inoubliables.

    ### 🎯 Objectif pédagogique
    Tu vas apprendre à :
    - 🧩 **Analyser la structure** du format `.nes` (iNES)
    - 🧱 **Explorer les tuiles graphiques** (CHR-ROM)
    - ⚙️ **Comprendre le processeur 6502**
    - 💾 **Lire le désassemblage du code du jeu**
    - 🎨 **Décoder la palette et le rendu visuel**

    > 💡 Ce n’est pas juste une appli technique, c’est un **laboratoire rétro** :
    > chaque octet ici raconte une part d’histoire de l’informatique.
    """)

# ---------------------------------------------------
# ⚙️ CPU — LE COEUR DU SYSTÈME
# ---------------------------------------------------

def explain_cpu_basics():
    """Explique le fonctionnement du processeur MOS 6502 de la NES."""
    st.header("⚙️ Le processeur MOS 6502 — Le cœur battant de la NES")

    st.markdown("""
    Le **MOS 6502** est un processeur 8 bits d’une simplicité redoutable, 
    cadencé à **1,79 MHz** sur la NES.  
    C’est lui qui exécute le code stocké dans la **PRG-ROM**.

    ### 🧠 Les composants essentiels :
    | Élément | Nom complet | Rôle |
    |:--|:--|:--|
    | **A** | Accumulateur | Sert aux calculs et transferts de données |
    | **X / Y** | Registres d’index | Utilisés pour parcourir la mémoire |
    | **P** | Registre d’état | Contient les drapeaux (Zéro, Négatif, Retenue, etc.) |
    | **PC** | Compteur de programme | Indique l’adresse actuelle d’exécution |
    | **SP** | Pointeur de pile | Gère les appels de fonction et les retours |

    > 💬 Chaque instruction assemble ou déplace des octets en mémoire.
    > En 1 seconde, le CPU peut exécuter plus de **100 000 instructions 8-bit** !

    ### 🧮 Exemple simple
    ```assembly
    LDA #$01   ; charge la valeur 1 dans l’accumulateur
    STA $0200  ; stocke cette valeur en mémoire (adresse 0x0200)
    ```

    > 💡 C’est la base du gameplay : ces opérations contrôlent les mouvements, 
    > les collisions, les scores, tout le moteur du jeu.
    """)

# ---------------------------------------------------
# 🧱 PPU — LE PROCESSEUR GRAPHIQUE
# ---------------------------------------------------

def explain_ppu_concept():
    """Explique le rôle et le fonctionnement du processeur graphique (PPU)."""
    st.header("🧱 Le PPU — L’artiste de la NES")

    st.markdown("""
    Le **PPU (Picture Processing Unit)** est un processeur spécialisé dans l’affichage.  
    Il gère les **sprites**, les **décors**, et les **palettes de couleurs**.

    ### 🎨 Les 3 missions du PPU :
    1. Lire les **tuiles CHR** (graphismes bruts 8×8)
    2. Appliquer une **palette de 4 couleurs**
    3. Afficher le tout **ligne par ligne** à l’écran

    ### 🧩 Composition typique :
    | Élément | Taille | Rôle |
    |:--|:--|:--|
    | **CHR-ROM** | 8 Ko à 64 Ko | Contient les tuiles graphiques brutes |
    | **Palette** | 4 × 4 couleurs | Associe chaque valeur 0–3 à une vraie couleur |
    | **Name Table** | 1 Ko | Spécifie quelles tuiles afficher et où |
    | **Attribute Table** | 64 octets | Contrôle les couleurs par zone de 16×16 pixels |

    > 💡 Le PPU fonctionne comme un puzzle : il assemble des tuiles 8×8
    > en mosaïques plus grandes, pour former l’écran complet (256×240 px).

    🧠 **Anecdote** : les développeurs de l’époque dessinaient leurs graphismes 
    directement en binaire sur du papier quadrillé !
    """)

# ---------------------------------------------------
# 🧬 CYCLE DE VIE D’UN OCTET
# ---------------------------------------------------

def explain_octet_lifecycle():
    """Explique le parcours d’un octet du fichier .NES jusqu’à l’écran."""
    st.header("🧬 Le cycle de vie d’un octet NES")

    st.markdown("""
    Un simple octet passe par plusieurs étapes avant d’apparaître à l’écran.

    | Étape | Composant | Description |
    |:--|:--|:--|
    | 💾 Lecture | **ROM (PRG / CHR)** | L’octet est lu depuis la cartouche |
    | 🧠 Interprétation | **CPU 6502** | Il devient une instruction ou une donnée |
    | 🔁 Circulation | **Bus de données** | Il est échangé entre CPU, RAM et PPU |
    | 🎨 Rendu | **PPU** | Il se transforme en pixel coloré |
    | 👀 Affichage | **Écran CRT** | Il apparaît à l’écran 60 fois par seconde |

    > 💡 Ce ballet électronique se répète **60 fois par seconde**,  
    > créant le mouvement fluide des jeux NES.
    """)

def explain_ines_header(prg_size, chr_size, trainer, header_bytes):
    """Analyse et explique le header iNES d'une ROM NES, sans bloquer l'exécution."""
    import streamlit as st

    st.header("📦 Structure interne du format iNES")
    st.markdown("""
    Le format **iNES** (pour *Nintendo Entertainment System*) décrit la structure binaire d'une ROM NES :
    - Les **16 premiers octets** forment le **header**.
    - Ils indiquent la taille des sections, le type de mirroring, le mapper, etc.
    """)

    # Vérifie la signature magique NES<1A>
    if len(header_bytes) < 16 or header_bytes[:4] != b"NES\x1A":
        st.warning("""
        ⚠️ **Le fichier ne respecte pas entièrement le format standard `iNES`.**

        Cela peut arriver si :
        - La ROM est dans un format ancien (pré-iNES ou format propriétaire)
        - Le fichier est incomplet ou a été modifié
        - C’est une ROM traduite, patchée ou générée par un éditeur tiers

        💡 L’analyse se poursuit quand même à titre pédagogique, mais certaines informations peuvent être incorrectes.
        """)

        # On remplit avec des valeurs par défaut pour éviter un crash
        prg_size = 0
        chr_size = 0
        mapper = 0
        mirroring = "Inconnu"
        trainer = False
    else:
        # Lecture des informations du header
        mapper = (header_bytes[6] >> 4) | (header_bytes[7] & 0xF0)
        mirroring = "Verticale" if header_bytes[6] & 1 else "Horizontale"
        prg_size_kb = prg_size // 1024
        chr_size_kb = chr_size // 1024

        st.markdown("""
        ### 🧠 Décodage du header iNES
        Voici les champs clés interprétés depuis le header binaire :
        """)

        st.json({
            "Signature": header_bytes[:4].decode(errors="replace"),
            "PRG-ROM": f"{prg_size_kb} Ko",
            "CHR-ROM": f"{chr_size_kb} Ko",
            "Mapper": mapper,
            "Mirroring": mirroring,
            "Trainer présent": bool(header_bytes[6] & 0b100),
        })

        st.caption("""
        💡 *Le mapper est une puce intégrée à la cartouche NES.  
        Elle permet d’adresser plus de mémoire et d’ajouter des fonctionnalités spécifiques (bank switching, IRQ, etc.).*
        """)

    # --- Description visuelle du header ---
    st.markdown("### 🧩 Structure binaire (16 octets du header iNES)")

    header_hex = " ".join(f"{b:02X}" for b in header_bytes[:16])
    st.code(header_hex, language="text")

    st.markdown("""
    | Octets | Signification | Détails |
    |:------:|:--------------|:--------|
    | 0–3 | Signature | Doit être `NES<1A>` |
    | 4 | Taille PRG-ROM | En blocs de 16 Ko |
    | 5 | Taille CHR-ROM | En blocs de 8 Ko |
    | 6 | Flags 6 | Mirroring, batterie, trainer, Mapper bas |
    | 7 | Flags 7 | Mapper haut, VS Unisystem, PlayChoice |
    | 8–15 | Extension | Souvent inutilisée ou réservée |
    """)

    st.info("""
    🧱 En résumé :
    - **PRG-ROM** = code exécutable du jeu (processeur 6502)
    - **CHR-ROM** = données graphiques (sprites & décors)
    - **Mapper** = puce mémoire embarquée
    - **Mirroring** = organisation de l’affichage à l’écran (horizontal ou vertical)
    """)

    st.caption("""
    🔍 *Si le header n’est pas conforme, la ROM reste analysable à titre pédagogique —  
    cela ne signifie pas qu’elle est inutilisable dans un émulateur.*
    """)



def explain_integrity(sha1: str, crc32: str):
    """Affiche la section pédagogique sur l’intégrité du fichier NES (SHA1 / CRC32)."""
    import streamlit as st

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔐 Intégrité du fichier")
        st.markdown("""
        Pour s’assurer qu’une **ROM n’a pas été altérée ou corrompue**,  
        on calcule des **empreintes numériques** — un peu comme une **signature ADN** du fichier.

        ### 🧬 SHA-1
        Produit une empreinte unique de 40 caractères pour chaque fichier.  
        Si deux ROMs ont le même SHA-1, elles sont **strictement identiques bit à bit**.

        ### 📦 CRC-32
        Une somme de contrôle historique utilisée dans les fichiers ZIP  
        et les cartouches NES d’origine pour détecter les erreurs.

        > 💡 Ces valeurs servent à vérifier l’**authenticité** du jeu  
        > ou à le comparer à une base de données comme *No-Intro*.
        """)

    with col2:
        st.subheader("📋 Empreintes calculées")
        st.markdown(f"""
        ```json
        {{
            "SHA1": "{sha1}",
            "CRC32": "{crc32}"
        }}
        ```""")

        # --- Vérification No-Intro ---
        match = check_no_intro_match(sha1, crc32)

        # --- Vérification structure iNES ---
        header = st.session_state.get("header")
        prg_size = st.session_state.get("prg_size", 0)
        chr_size = st.session_state.get("chr_size", 0)
        structure_ok = validate_ines_structure(header, prg_size, chr_size) if header else False

        # --- Cas 1 : ROM reconnue ---
        if match:
            st.markdown(f"""
            <div style="
                background-color:#102a12;
                border-left:6px solid #00ff66;
                padding:12px 16px;
                border-radius:6px;
                color:#aaffaa;
                font-family:'JetBrains Mono', monospace;">
                ✅ <strong>ROM reconnue :</strong> <span style="color:#00ff88;">{match}</span><br>
                <span style="color:#66ffcc;">Base :</span> No-Intro locale<br>
                <span style="font-size:13px;color:#99cc99;">(fichier certifié authentique)</span>
            </div>
            """, unsafe_allow_html=True)

        # --- Cas 2 : Structure valide mais non référencée ---
        elif structure_ok:
            st.markdown("""
            <div style="
                background-color:#2b1f00;
                border-left:6px solid #ffb347;
                padding:12px 16px;
                border-radius:6px;
                color:#ffcc66;
                font-family:'JetBrains Mono', monospace;">
                ⚠️ <strong>ROM non répertoriée</strong>, mais structure iNES <strong>valide</strong>.<br>
                <ul style="margin-top:4px;margin-bottom:4px;">
                    <li>Probablement un <em>hack</em> (version modifiée ou traduite)</li>
                    <li>Une <em>édition non officielle</em> ou régionale</li>
                    <li>Ou un <em>prototype</em> / <em>dump alternatif</em></li>
                </ul>
                <span style="font-size:13px;color:#e0c080;">
                💡 Le format iNES est cohérent : la ROM est saine et jouable,<br>
                simplement absente des bases officielles.
                </span>
            </div>
            """, unsafe_allow_html=True)

        # --- Cas 3 : Structure douteuse (ancien comportement) ---
        else:
            st.markdown("""
            <div style="
                background-color:#332200;
                border-left:6px solid #ffcc00;
                padding:12px 16px;
                border-radius:6px;
                color:#ffdd66;
                font-family:'JetBrains Mono', monospace;">
                ⚠️ <strong>ROM non standard ou entête iNES incomplet</strong><br>
                Le fichier ne respecte pas totalement la structure <code>NES&lt;1A&gt;</code>,  
                mais il reste exploitable à des fins pédagogiques.<br><br>
                <ul style="margin-top:4px;margin-bottom:4px;">
                    <li>Header atypique ou version antérieure du format</li>
                    <li>Possiblement un <em>dump</em> brut ou un <em>patch</em> (IPS/UPS)</li>
                </ul>
                💡 <em>L’analyse continue — certaines informations peuvent être incomplètes.</em>
            </div>
            """, unsafe_allow_html=True)

        # --- Note finale ---
        st.caption("""
        🕵️‍♂️ *Le SHA-1 agit comme une empreinte digitale immuable :*  
        modifier un seul octet change complètement sa valeur.
        """)



def check_no_intro_match(sha1: str, crc32: str, dat_path: str = "data/No-Intro-NES.dat"):
    """
    Vérifie si les empreintes de la ROM (SHA1 ou CRC32)
    correspondent à une ROM répertoriée dans la base No-Intro locale (.dat).
    Compatible avec les fichiers XML récents contenant <category> et <rom ...>.
    """
    p = Path(dat_path)
    if not p.exists():
        return None

    try:
        tree = ET.parse(p)
        root = tree.getroot()

        for game in root.findall(".//game"):
            rom = game.find("rom")
            if rom is None:
                continue

            # Récupération des empreintes avec tolérance sur la casse
            rom_sha1 = rom.attrib.get("sha1", "").strip().lower()
            rom_crc32 = rom.attrib.get("crc", "").strip().upper()

            # Comparaison
            if sha1.lower() == rom_sha1 or crc32.upper() == rom_crc32:
                # Retourne un nom lisible
                title = game.attrib.get("name") or game.findtext("description") or "Jeu inconnu"
                return title
    except Exception as e:
        st.warning(f"Erreur lors du chargement du fichier No-Intro : {e}")
    return None

def validate_ines_structure(header: bytes, prg_size: int, chr_size: int):
    """
    Vérifie si le fichier a une structure iNES cohérente :
    - Signature correcte "NES<1A>"
    - Taille PRG/CHR réaliste
    Retourne True si tout semble valide, sinon False.
    """
    if len(header) < 16:
        return False
    if header[:4] != b"NES\x1A":
        return False

    # Vérification tailles typiques
    prg_ok = 1 <= prg_size // 1024 <= 1024  # entre 16 Ko et 1 Mo
    chr_ok = 0 <= chr_size // 1024 <= 512   # jusqu’à 512 Ko
    return prg_ok and chr_ok


# ======================================================
# 🧱 EXPLICATION DES TUILES CHR (corrigée pour CHR-RAM)
# ======================================================
def explain_chr_tiles(chr_data: bytes):
    """Explique et visualise les tuiles graphiques (CHR-ROM) d'une ROM NES, avec fallback CHR simulée."""
    st.header("🧱 CHR — Visualisation des tuiles")

    st.markdown("""
    ### 🧱 Qu’est-ce qu’une tuile CHR ?

    Sur NES, tout le graphisme repose sur de **petites images de 8×8 pixels** appelées **tuiles**  
    (*tiles*). Chaque sprite, chaque lettre, chaque décor est construit à partir de ces briques.
    """)

    # === Si aucune CHR-ROM, créer un motif simulé (CHR-RAM pédagogique) ===
    if not chr_data or len(chr_data) < 16:
        st.warning("""
        ⚠️ Aucune donnée graphique **CHR-ROM** détectée.  
        Ce jeu utilise une **CHR-RAM** (graphismes chargés dynamiquement).  
        💡 Une mosaïque simulée est générée pour démonstration.
        """)

        fake_chr = np.zeros((8192,), dtype=np.uint8)
        for i in range(0, len(fake_chr), 16):
            val = (i // 64) % 256
            for j in range(8):
                fake_chr[i + j] = ((val >> (j % 8)) & 0xFF)
                fake_chr[i + 8 + j] = ((~val >> (j % 8)) & 0xFF)
        chr_data = fake_chr.tobytes()

    # --- Génération des tuiles ---
    tile_count = min(len(chr_data) // 16, 256)
    tiles = []

    for i in range(tile_count):
        tile_bytes = chr_data[i * 16:(i + 1) * 16]
        low = np.frombuffer(tile_bytes[:8], dtype=np.uint8)
        high = np.frombuffer(tile_bytes[8:], dtype=np.uint8)
        tile = np.zeros((8, 8), dtype=np.uint8)
        for y in range(8):
            for x in range(8):
                lo_bit = (low[y] >> (7 - x)) & 1
                hi_bit = (high[y] >> (7 - x)) & 1
                tile[y, x] = lo_bit + (hi_bit << 1)
        tiles.append(tile)

    grid_size = int(np.ceil(np.sqrt(tile_count)))
    tile_size = 8
    canvas = np.zeros((grid_size * tile_size, grid_size * tile_size), dtype=np.uint8)

    for idx, tile in enumerate(tiles):
        y = (idx // grid_size) * tile_size
        x = (idx % grid_size) * tile_size
        canvas[y:y+tile_size, x:x+tile_size] = tile

    img = Image.fromarray(canvas * 85)
    img = img.resize((img.width * 4, img.height * 4), Image.NEAREST)

    st.image(img, caption=f"{tile_count} tuiles CHR (réelles ou simulées)", use_container_width=True)

    st.info("""
    🧩 Chaque tuile NES = 16 octets (8 octets bas + 8 octets hauts) → 64 pixels (4 teintes possibles).  
    Même sans CHR-ROM, la structure reste identique, seule la source des données change (RAM vs ROM).
    """)


# ======================================================
# 🔬 DÉTAIL INTERACTIF D'UNE TUILE
# ======================================================
def show_chr_tile_detail(chr_data: bytes):
    """Affiche une démonstration interactive et colorée du décodage d'une tuile CHR NES, avec fallback CHR simulée."""

    st.subheader("🔬 Décomposition interactive d’une tuile CHR — en couleur NES")

    # === Cas CHR absente ===
    if len(chr_data) == 0:
        st.warning("""
        ⚠️ Aucune donnée graphique CHR-ROM détectée.  
        Une tuile factice est générée pour démonstration.
        """)
        fake_chr = np.zeros((16 * 256,), dtype=np.uint8)
        for i in range(0, len(fake_chr), 16):
            val = (i // 64) % 255
            for j in range(8):
                fake_chr[i + j] = ((val >> (j % 8)) & 0xFF)
                fake_chr[i + 8 + j] = ((~val >> (j % 8)) & 0xFF)
        chr_data = fake_chr.tobytes()

    total_tiles = len(chr_data) // 16
    tile_index = st.slider("🧱 Sélectionne une tuile à analyser :", 0, min(255, total_tiles - 1), 0)

    tile_bytes = chr_data[tile_index * 16 : (tile_index + 1) * 16]
    low = np.frombuffer(tile_bytes[:8], dtype=np.uint8)
    high = np.frombuffer(tile_bytes[8:], dtype=np.uint8)

    tile = np.zeros((8, 8), dtype=np.uint8)
    for y in range(8):
        for x in range(8):
            lo_bit = (low[y] >> (7 - x)) & 1
            hi_bit = (high[y] >> (7 - x)) & 1
            tile[y, x] = lo_bit + (hi_bit << 1)

    nes_palettes = {
        "🎮 Classique (Super Mario Bros.)": [(124, 124, 124), (0, 0, 252), (248, 56, 0), (252, 252, 252)],
        "🌿 Aventure (Zelda)": [(0, 0, 0), (34, 139, 34), (107, 142, 35), (173, 255, 47)],
        "🔥 Énergie (Metroid)": [(0, 0, 0), (180, 50, 0), (255, 100, 0), (255, 200, 0)],
        "🧊 Froid (Mega Man)": [(0, 0, 0), (0, 70, 160), (100, 200, 255), (255, 255, 255)],
        "⚪ Niveaux de gris": [(255, 255, 255), (180, 180, 180), (100, 100, 100), (0, 0, 0)],
    }

    selected_palette = st.selectbox("🎨 Palette de rendu :", list(nes_palettes.keys()))
    palette = np.array(nes_palettes[selected_palette], dtype=np.uint8)

    rgb_tile = palette[tile]
    img = Image.fromarray(rgb_tile, mode="RGB").resize((8 * 20, 8 * 20), Image.NEAREST)

    tab1, tab2, tab3 = st.tabs(["📄 Données brutes", "🔢 Matrice", "🎨 Rendu NES"])

    with tab1:
        st.code("\n".join([f"L{y+1}: {low[y]:08b} | H{y+1}: {high[y]:08b}" for y in range(8)]), language="text")

    with tab2:
        st.write(tile)

    with tab3:
        st.image(img, caption=f"🎨 Tuile {tile_index} — {selected_palette}", use_container_width=True)

    st.caption("""
    💾 Même sans CHR-ROM réelle, la structure 8×8 reste la même :  
    c’est l’illustration du format 2-bitplan NES (2 bits → 4 teintes).
    """)

def show_chr_atlas(chr_data: bytes, cols: int = 16):
    """Affiche toutes les tuiles CHR-ROM sous forme d'un atlas complet."""
    import streamlit as st

    st.subheader("🧱 Vue globale — Planche complète des tuiles CHR")

    tiles = len(chr_data) // 16
    if tiles == 0:
        st.warning("Aucune donnée CHR-ROM détectée.")
        return

    rows = (tiles + cols - 1) // cols
    atlas = np.zeros((rows * 8, cols * 8), dtype=np.uint8)

    for i in range(tiles):
        tile_bytes = chr_data[i*16:(i+1)*16]
        low = np.frombuffer(tile_bytes[:8], dtype=np.uint8)
        high = np.frombuffer(tile_bytes[8:], dtype=np.uint8)
        for y in range(8):
            for x in range(8):
                lo_bit = (low[y] >> (7 - x)) & 1
                hi_bit = (high[y] >> (7 - x)) & 1
                atlas[(i//cols)*8 + y, (i%cols)*8 + x] = lo_bit + (hi_bit << 1)

    # Palette 4 niveaux de gris
    palette = np.array([
        [255, 255, 255],
        [170, 170, 170],
        [85, 85, 85],
        [0, 0, 0]
    ], dtype=np.uint8)

    rgb_atlas = palette[atlas]
    img = Image.fromarray(rgb_atlas, mode="RGB").resize(
        (cols * 8 * 2, rows * 8 * 2),
        Image.NEAREST
    )

    st.image(img, caption=f"Planche complète : {tiles} tuiles ({rows}×{cols})", use_container_width=True)
    st.caption("💡 Chaque bloc 8×8 représente une tuile graphique utilisée dans le jeu.")

def show_memory_bus_diagram():
    """Affiche un schéma pédagogique du bus mémoire NES (CPU, PPU, APU, RAM, ROM)."""
    st.header("🔌 Bus mémoire NES — Les échanges internes")

    st.markdown("""
    La **NES** est construite autour d’un seul processeur principal : le **CPU 6502**.  
    Ce CPU communique avec tout le reste via un **bus mémoire** partagé.

    > 💡 Imagine une autoroute où circulent des données — le bus transporte les octets  
    > entre le processeur, la mémoire, la carte graphique (PPU) et la cartouche.
    """)

    # === Schéma ASCII / HTML stylé ===
    st.markdown("""
    <div style="
        font-family:monospace;
        background:#111;
        color:#ddd;
        padding:16px;
        border-radius:8px;
        line-height:1.5em;
        border-left:4px solid #ffcc00;
    ">
    🧠 <b>CPU (6502)</b>  ←→  🟩 <b>RAM</b>  (données temporaires, variables)<br>
      │<br>
      ├──→  🟦 <b>PPU</b>  (dessine les sprites et décors à l’écran)<br>
      ├──→  🟧 <b>APU</b>  (génère le son, musiques et bruitages)<br>
      ├──→  🟪 <b>IO Ports</b>  (manettes, périphériques)<br>
      └──→  🔴 <b>Cartouche</b>  (PRG-ROM + CHR-ROM)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🧩 Rôle de chaque élément
    | Élément | Description | Type de données |
    |:--|:--|:--|
    | 🧠 **CPU (6502)** | Exécute le code du jeu, lit/écrit dans la mémoire | Instructions, registres |
    | 🟩 **RAM** | Zone temporaire pour les scores, positions, variables | Données volatiles |
    | 🟦 **PPU (Picture Processing Unit)** | Génère les images à l’écran à partir des tuiles CHR | Graphismes |
    | 🟧 **APU (Audio Processing Unit)** | Gère les canaux sonores de la NES | Sons et musiques |
    | 🟪 **Ports I/O** | Interface avec les manettes et périphériques | Entrées utilisateur |
    | 🔴 **Cartouche (ROM)** | Contient le code du jeu (PRG) et les graphismes (CHR) | Données permanentes |
    """)

    st.info("""
    💡 Ce bus mémoire est la “colonne vertébrale” de la NES :  
    chaque cycle d’horloge, le CPU échange des octets avec un composant différent.
    """)

    # === Bonus interactif (simulation pédagogique) ===
    with st.expander("🛰️ Simuler un échange de données"):
        st.markdown("💾 Cette zone te permet de visualiser un transfert sur le bus mémoire NES.")
        components = ["CPU", "PPU", "APU", "RAM", "ROM"]
        src = st.selectbox("📤 Source :", components, key="src_bus")
        dest = st.selectbox("📥 Destination :", components, key="dest_bus")
        data = st.text_input("💽 Donnée envoyée (hex)", "0xA9", key="bus_data")

        if src == dest:
            st.error("⚠️ Impossible : un composant ne peut pas s'envoyer de données à lui-même !")
        else:
            color_map = {
                ("CPU", "PPU"): "#00ccff",
                ("CPU", "APU"): "#ffb347",
                ("CPU", "RAM"): "#00ff99",
                ("CPU", "ROM"): "#ff6666",
                ("PPU", "CPU"): "#33ccff",
                ("APU", "CPU"): "#ff9933",
                ("ROM", "CPU"): "#ff4444",
                ("RAM", "CPU"): "#66ff99"
            }
            color = color_map.get((src, dest), "#cccccc")

            html = f"""
            <div style='
                font-family:monospace;
                background:#111;
                padding:14px;
                border-radius:8px;
                border:2px solid {color};
                color:#ddd;
                margin-top:10px;
                text-align:center;
            '>
                🔁 Transmission sur le bus :  
                <b style='color:{color}'>{src} → {dest}</b>  
                Donnée : <span style='color:#fff;'>{data}</span>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)

            # 💬 Explication contextuelle
            explanations = {
                ("CPU", "PPU"): "Le CPU écrit dans les registres du PPU pour modifier l'affichage (scroll, sprites…).",
                ("CPU", "APU"): "Le CPU envoie des valeurs à l’APU pour jouer des sons et musiques.",
                ("CPU", "RAM"): "Le CPU lit ou écrit des variables temporaires dans la RAM (scores, positions…).",
                ("CPU", "ROM"): "Le CPU lit le code du jeu (PRG-ROM) stocké dans la cartouche.",
                ("PPU", "CPU"): "Le PPU renvoie des signaux de synchronisation (VBlank) au CPU.",
                ("APU", "CPU"): "L’APU signale la fin d’une note ou d’un canal au CPU.",
                ("ROM", "CPU"): "Le CPU lit une instruction ou des données depuis la ROM.",
                ("RAM", "CPU"): "Le CPU lit des données qu’il avait précédemment stockées en RAM."
            }

            if (src, dest) in explanations:
                st.info("🧠 " + explanations[(src, dest)])
            else:
                st.warning("⚙️ Ce type de transfert est peu courant ou réservé à des circuits spéciaux.")
                

def show_frame_cycle_overview():
    """Montre le cycle complet d’un frame NES — coordination CPU/PPU/APU."""
    st.header("🎞️ Cycle d’un frame NES — Synchronisation CPU, PPU et APU")

    st.markdown("""
    Chaque image affichée à l’écran (1 frame) correspond à un **cycle complet**  
    de la console NES : environ **60 images par seconde**.

    > 💡 Pendant qu’une image est affichée, le **CPU** prépare la suivante,  
    > le **PPU** dessine ligne par ligne, et l’**APU** génère le son.
    """)

    st.markdown("""
    <div style="text-align:center;">
        <img src="https://www.emulationonline.com/systems/nes/nes-system-timing/nes_ntsc_video_timing.png"
            width="550"
            style="border-radius:8px; box-shadow:0 0 12px #0003;">
    <p style="color:gray;font-size:13px;">
        Schéma du timing vidéo NTSC de la NES — période active et VBlank
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    👉 Voici un schéma visuel : on voit que la PPU produit **262 lignes** par image, mais seules **240 sont affichées**.  
    La période « VBlank » (vertical blanking) est le moment où la CPU peut mettre à jour les tuiles en mémoire sans effet de “tearing”.  
    """)

    st.markdown("""
    ### 🧮 Répartition du travail
    | Composant | Rôle pendant une frame | Détails |
    |:--|:--|:--|
    | 🧠 **CPU (6502)** | Exécute le code du jeu | Lit/écrit la RAM, met à jour la position des sprites, prépare les commandes graphiques |
    | 🟦 **PPU** | Gère le rendu visuel | Dessine 262 lignes dont 240 visibles, puis génère un signal VBlank (fin d’image) |
    | 🟧 **APU** | Génère le son | Joue les canaux sonores, met à jour les notes et effets audio |
    | 🕹️ **I/O Ports** | Collecte les entrées | Lit les boutons de manette à intervalles réguliers |

    À chaque VBlank (Vertical Blank), le **CPU peut modifier la mémoire vidéo** sans risque  
    de “tearing” : c’est le moment où le PPU ne dessine pas.
    """)

    # === Animation logique ===
    st.subheader("⚙️ Schéma simplifié du déroulement d’une frame")
    st.markdown("""
    ```
    [Début du frame]
        ↓
    CPU → calcule les positions, scores, collisions
        ↓
    PPU → dessine ligne 1 à 240
        ↓
    APU → joue la musique en parallèle
        ↓
    VBlank (pause du rendu)
        ↓
    CPU → met à jour la mémoire graphique
        ↓
    [Frame suivante]
    ```
    """)

    # === Explication finale ===
    st.info("""
    🧠 **À retenir :**  
    - Le **CPU** (6502) et le **PPU** (graphique) fonctionnent en parallèle.  
    - Le **VBlank** est la seule période sûre pour écrire dans la mémoire vidéo.  
    - L’**APU** suit son propre rythme, synchronisé sur les cycles CPU.  
    - La NES répète ce cycle environ **60 fois par seconde** pour animer le jeu.
    """)

    st.caption("""
    ⏱️ 1 frame = ~16,67 ms  
    💾 1 seconde = 60 frames ≈ 60 000 cycles CPU  
    🎮 Et tout cela, avec moins de 2 Ko de RAM !
    """)
    
    
def show_vram_explanation():
    """Explique la structure de la mémoire vidéo (VRAM) et les Name Tables."""
    st.header("🧱 Organisation de la mémoire vidéo (VRAM NES)")

    st.markdown("""
    La **VRAM** de la NES (2 Ko seulement !) est utilisée par le **PPU** pour stocker :
    - Les **Name Tables** → disposition des tuiles à l’écran  
    - Les **Attribute Tables** → couleurs appliquées à chaque bloc  
    - Les **Pattern Tables** → tuiles graphiques (formes 8×8)  
    - Les **Sprite Tables (OAM)** → éléments mobiles comme Mario, Link, etc.

    > 💡 La NES ne dessine pas des pixels individuellement,  
    > elle compose son image à partir de **tuiles** et **palettes**.
    """)

    # --- Affichage graphique VRAM Map ---
    st.markdown("### 🗺️ Carte mémoire du PPU (VRAM Map)")
    st.image(
        "https://bugzmanov.github.io/nes_ebook/images/ch6.1/image_1_ppu_registers_memory.png",
        caption="Carte mémoire PPU : organisation des zones graphiques",
        width=600
    )

    st.markdown("""
    | Adresse | Zone | Contenu | Taille |
    |:---------|:------|:---------|:--------|
    | `$0000–$0FFF` | Pattern Table 0 | Tuiles graphiques (CHR-ROM) | 4 Ko |
    | `$1000–$1FFF` | Pattern Table 1 | Autre banque graphique | 4 Ko |
    | `$2000–$23FF` | Name Table 0 | Carte de fond écran | 1 Ko |
    | `$2400–$27FF` | Name Table 1 | Deuxième écran (scrolling) | 1 Ko |
    | `$3F00–$3F1F` | Palette Table | Couleurs (32 octets) | 32 o |
    | `$3F20–$3FFF` | Mirroring / répétition | Zones redondantes | – |

    Chaque tuile est une **entrée dans la Pattern Table**,  
    et chaque case de la Name Table indique **quelle tuile** afficher à une position donnée.
    """)

    st.subheader("🎨 Exemple : combinaison des tables")
    st.markdown("""
    ```
    Pattern Table (formes) + Palette (couleurs)
        ↓
    Name Table (position des tuiles)
        ↓
    Image finale affichée par la PPU
    ```
    """)

    st.caption("""
    🧠 La NES assemble chaque frame à partir de ces briques.  
    Cette approche permet de grandes cartes de jeu avec très peu de mémoire.
    """)

    st.info("""
    💾 2 Ko de VRAM = un seul écran visible + mirroring pour le scrolling.  
    Pour les grands niveaux (Zelda, Mario), la console utilise **2 Name Tables côte à côte**.
    """)
    
def show_sprites_explanation():
    """Explique la gestion des sprites par la NES (OAM)."""
    st.header("🕹️ Les sprites et la mémoire OAM (Object Attribute Memory)")

    st.markdown("""
    Les **sprites** sont les éléments mobiles du jeu : personnages, ennemis, balles, objets…  
    Chaque sprite est une **tuile 8×8 pixels**, dont la position et la couleur sont stockées
    dans une mémoire spéciale appelée **OAM** (*Object Attribute Memory*).

    > 💡 La NES gère **jusqu’à 64 sprites** en même temps, soit 4 × 64 = 256 octets de données.
    """)

    # --- Illustration ---
    st.image(
        "https://opengameart.org/sites/default/files/Pirate%20Livery%20%26%20Sheet%201.png",
        caption="Exemple de sprites",
        width=500
    )

    # --- Structure de l’OAM ---
    st.markdown("### 🧩 Structure d’un sprite dans la mémoire OAM")
    st.markdown("""
    | Octet | Champ | Description |
    |:--:|:--|:--|
    | 0 | **Y Position** | Position verticale (haut du sprite) |
    | 1 | **Tile Index** | Quelle tuile (dans la CHR-ROM) afficher |
    | 2 | **Attributes** | Palette, flip horizontal/vertical, priorité |
    | 3 | **X Position** | Position horizontale |
    """)

    st.caption("""
    Chaque sprite = 4 octets.  
    → 64 sprites × 4 octets = 256 octets au total dans l’OAM.
    """)

    # --- Détails attributs ---
    st.markdown("### 🎨 Détail des attributs (octet 2)")
    st.markdown("""
    | Bits | Signification |
    |:--|:--|
    | 7 | Priorité (devant ou derrière le décor) |
    | 6 | Flip vertical |
    | 5 | Flip horizontal |
    | 4-2 | Sélection de la palette (0–3) |
    | 1-0 | Non utilisés |
    """)

    # --- Pédagogie ---
    st.info("""
    🧠 Le PPU lit l’OAM à chaque frame pour savoir quels sprites afficher.  
    Si plus de 8 sprites se trouvent sur la même ligne, les suivants sont ignorés — d’où les effets de clignotement visibles dans de nombreux jeux.
    """)

    # --- Exemple visuel ---
    st.markdown("### 📺 Exemple")
    st.image(
        "https://opengameart.org/sites/default/files/popotachars_orig1x_3.png",
        
        width=500
    )

    st.caption("""
    💡 Chaque personnage est en réalité **un assemblage de plusieurs tuiles 8×8**,  
    repositionnées et colorisées par le PPU en temps réel.
    """)

    # --- Conclusion ---
    st.success("""
    🎓 **À retenir :**
    - L’OAM contient les sprites, séparés du fond.
    - 64 sprites max, 8 par ligne → limitation matérielle.
    - Les sprites peuvent être “flippés” horizontalement/verticalement.
    - Leur priorité détermine s’ils apparaissent **devant** ou **derrière** le décor.
    """)

def show_sync_explanation():
    """Explique la synchronisation CPU / PPU et le timing vidéo de la NES."""
    st.header("⏱️ Synchronisation CPU ↔ PPU — Le rythme du rendu NES")

    st.markdown("""
    La **NES** contient deux processeurs principaux :
    - 🧮 Le **CPU 6502**, qui exécute la logique du jeu (~1.79 MHz NTSC)
    - 🖼️ Le **PPU**, qui génère l’image à **60 images/seconde (NTSC)** ou **50 Hz (PAL)**

    Ces deux composants fonctionnent **en parallèle**, mais doivent rester parfaitement synchronisés.
    """)

    st.markdown("""
    ### 🧩 Cycle d’une frame (NTSC)
    1. **240 lignes visibles** : le PPU trace l’image ligne par ligne  
    2. **22 lignes de VBlank** : le PPU arrête le rendu → le CPU peut mettre à jour les sprites et décors  
    3. **Interruption NMI** : signal envoyé au CPU pour indiquer que la frame est terminée
    """)

    # --- Affichage du schéma (redimensionné proprement) ---
    st.markdown("""
    <div style="text-align:center;">
      <img src="https://www.emulationonline.com/systems/nes/nes-system-timing/nes_ntsc_video_timing.png"
           width="600"
           style="border-radius:8px; box-shadow:0 0 10px #0003;">
      <p style="color:gray;font-size:13px;">
        Schéma du timing vidéo NTSC de la NES : période d'affichage (240 lignes) et période VBlank
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 📊 Correspondance CPU ↔ PPU
    | Élément | Cadence approximative | Rôle |
    |:--|:--:|:--|
    | **CPU (6502)** | 1.79 MHz | Exécute la logique du jeu |
    | **PPU** | 5.37 MHz | Génère 3 pixels par cycle CPU |
    | **Frame complète** | 16.67 ms | 262 lignes × 341 points |
    """)

    st.caption("""
    💡 Le CPU et le PPU communiquent via des registres spécifiques ($2000–$2007).  
    Le bon timing entre les deux évite les artefacts visuels (tearing, sprites coupés, etc.).
    """)

    st.info("""
    🧠 **En résumé :**
    - Une frame NES = ~16.7 ms (60 Hz).  
    - Le CPU tourne pendant la phase visible **et** pendant la VBlank.  
    - Le PPU interrompt le CPU à chaque fin d’image (NMI).  
    - Les jeux optimisent le code pour tenir dans le temps imparti de chaque frame.
    """)

    st.success("""
    🔬 Cette compréhension est essentielle pour l’émulation :  
    reproduire le **timing exact** entre CPU et PPU est ce qui fait la différence  
    entre un émulateur fluide et un autre qui “tremble”.
    """)


def show_apu_explanation():
    """Explique le fonctionnement audio de la NES (APU)."""
    st.header("🎶 L’APU — Le processeur sonore de la NES")

    st.markdown("""
    Le **son de la NES** est produit par une puce intégrée appelée **APU** (*Audio Processing Unit*).  
    Elle ne lit pas de fichiers audio : elle **synthétise** le son en temps réel à partir de **formes d’onde mathématiques**.

    ### 🧩 Les 5 canaux sonores :
    | Canal | Type d’onde | Usage typique |
    |:--|:--|:--|
    | Pulse 1 | Onde carrée | Mélodie principale |
    | Pulse 2 | Onde carrée | Harmonie ou effets |
    | Triangle | Onde triangulaire | Basse / batterie |
    | Noise | Bruit aléatoire | Percussions, explosions |
    | DMC | Échantillons PCM | Voix, effets numériques |

    > 💡 Chaque jeu NES composait sa bande-son **en code**, en pilotant directement ces registres audio.
    """)

    # --- Génération de formes d’onde ---
    t = np.linspace(0, 1, 500)
    pulse = np.sign(np.sin(2 * np.pi * 3 * t))
    tri = 2 * np.abs(2 * (t * 3 % 1) - 1) - 1
    noise = np.random.uniform(-1, 1, len(t))
    
    fig, axs = plt.subplots(3, 1, figsize=(6, 3))
    axs[0].plot(t, pulse, color="#ff5555"); axs[0].set_title("Onde carrée (Pulse)")
    axs[1].plot(t, tri, color="#ffaa00"); axs[1].set_title("Onde triangulaire (Triangle)")
    axs[2].plot(t, noise, color="#55aaff"); axs[2].set_title("Bruit (Noise)")
    for ax in axs:
        ax.set_ylim(-1.2, 1.2)
        ax.set_xticks([]); ax.set_yticks([])
    plt.tight_layout()
    st.pyplot(fig)

    st.caption("""
    💡 Ces signaux sont additionnés en temps réel pour créer la musique et les effets sonores du jeu.  
    Modifier la **fréquence**, la **largeur d’impulsion** ou la **période du bruit** change complètement le timbre.
    """)

    # --- Encadré technique ---
    st.info("""
    🧠 **Détails techniques :**
    - Le CPU écrit directement dans les registres `$4000–$4017`.  
    - Chaque canal possède son propre registre de volume et de fréquence.  
    - Le mix final est envoyé sur une sortie mono à ~44 kHz.  
    - Certains jeux (ex. *Castlevania III JPN*) utilisaient des **puces sonores supplémentaires** sur la cartouche !
    """)

    # --- Bonus image ---
    st.markdown("""
    <div style="text-align:center;">
      <img src="https://nathanieltan.github.io/CompArchFinal/apu.png"
           width="550" style="border-radius:8px;box-shadow:0 0 8px #0003;">
      <p style="color:gray;font-size:13px;">Schéma interne simplifié de l’APU NES</p>
    </div>
    """, unsafe_allow_html=True)

    st.success("""
    🎓 **À retenir :**
    - Le son NES est 100 % synthétisé, pas enregistré.  
    - 5 canaux audio indépendants (2 Pulse, 1 Triangle, 1 Noise, 1 DMC).  
    - Le CPU “compose” la musique en écrivant dans la mémoire sonore.  
    - C’est cette contrainte qui donne au son NES sa **personnalité 8-bit unique** !
    """)
    
    
def show_cartridge_explanation():
    """Explique le rôle des cartouches NES et des mappers."""
    st.header("💾 Les cartouches NES — bien plus que de simples ROMs")

    st.markdown("""
    Une **cartouche NES** n’est pas qu’un support de stockage :  
    c’est un **mini-ordinateur** à part entière, avec sa propre logique, parfois même un coprocesseur.

    ### 🧩 Composition typique :
    | Élément | Rôle |
    |:--|:--|
    | **PRG-ROM** | Contient le **code du jeu** (6502) |
    | **CHR-ROM** | Contient les **graphismes** (tuiles, sprites) |
    | **SRAM + Batterie** | Sauvegarde les données du joueur |
    | **Mapper / MMC** | Gère la **banque mémoire**, le **scrolling**, et parfois le **son** |
    """)

    st.image(
        "https://ae01.alicdn.com/kf/Sc5fb7fe0ebdb42a9be62c026f97948a3N.jpg",
        caption="Carte interne d’une cartouche NES",
        width=550
    )

    st.markdown("""
    ### 🧠 Pourquoi des mappers ?
    Le processeur de la NES ne peut adresser que **32 Ko** de code à la fois.  
    Pour les jeux plus grands, les mappers servent à **échanger dynamiquement des banques mémoire** (*bank switching*).

    > 💡 En changeant de “banque”, le jeu peut accéder à des mondes, musiques et graphismes différents **sans recharger la cartouche**.
    """)

    st.markdown("""
    ### 🔌 Exemples de mappers célèbres
    | Mapper | Nom technique | Jeux emblématiques | Fonction |
    |:--:|:--|:--|:--|
    | **MMC1** | Nintendo SxROM | *Zelda*, *Metroid* | Sauvegarde + banques PRG/CHR |
    | **MMC3** | Nintendo TxROM | *Kirby’s Adventure*, *Mega Man 5* | Scroll fin + IRQ (interruption scanline) |
    | **VRC6** | Konami | *Castlevania III (JPN)* | Son amélioré (3 canaux audio supplémentaires) |
    | **UxROM** | Simple mapper | *DuckTales*, *Contra* | Switching basique de PRG |
    """)

    st.info("""
    🧠 **Le mapper est l’intelligence de la cartouche** :
    il fait le lien entre la console et la mémoire,  
    permettant à chaque jeu d’avoir ses propres capacités.
    """)

    st.markdown("""
    ### 🧩 Illustration simplifiée
    ```
    CPU (6502) ─── PRG-ROM ────┐
                    │ Mapper │────→ Bank Switching
    PPU ─────────── CHR-ROM ──┘
    ```
    """)

    st.caption("""
    💡 Chaque jeu NES possède un identifiant de mapper dans son en-tête iNES (byte 6).  
    Les émulateurs l’utilisent pour savoir **comment accéder correctement** à la mémoire.
    """)

    st.success("""
    🎓 **À retenir :**
    - Les cartouches NES contiennent souvent plusieurs puces (ROM, RAM, MMC, batterie).  
    - Les *mappers* ont permis d’étendre les capacités graphiques et sonores.  
    - Sans eux, la plupart des grands jeux NES n’auraient jamais tenu dans 32 Ko !
    """)
    
    
def show_advanced_mappers():
    """Explique les mappers avancés et les extensions audio japonaises."""
    st.header("🧠 Mappers avancés & extensions sonores japonaises")

    st.markdown("""
    Dans la **Famicom japonaise**, les cartouches pouvaient inclure des composants supplémentaires :  
    coprocesseurs, circuits logiques, et même des **synthétiseurs audio**.

    Ces ajouts ont permis de repousser les limites du hardware original,  
    donnant naissance à certains des **jeux les plus impressionnants** techniquement de la NES.
    """)

    st.markdown("""
    ### 🧩 Exemples de mappers avancés

    | Mapper | Nom | Constructeur | Particularités |
    |:--:|:--|:--|:--|
    | **MMC5** | Nintendo MMC5 | Nintendo | Plus de VRAM, IRQ ligne, palettes étendues |
    | **VRC6** | Konami | 3 canaux sonores supplémentaires (2 Pulse + 1 Sawtooth) |
    | **VRC7** | Konami | Synthèse FM (comme une mini carte son) |
    | **FDS** | Disk System | Nintendo | Puce FM intégrée au lecteur de disquettes |
    | **Sunsoft 5B** | Sunsoft | Son PSG supplémentaire, type chiptune |
    """)

    st.image(
        "https://i.ebayimg.com/00/s/MTIwMFgxNjAw/z/R80AAOSwBIVmwUxe/$_57.JPG?set_id=880000500F",
        caption="Carte Famicom avec puce VRC6 — Konami (Castlevania III - Akumajō Densetsu)",
        width=550
    )

    st.markdown("""
    ### 🔊 Extensions audio
    La **Famicom** (au Japon) possédait un **bus audio externe**,  
    permettant aux cartouches d’ajouter des **voies sonores supplémentaires**.

    > 💡 Ces sons ne sont **pas émulés sur NES occidentale**,  
    > ce qui explique pourquoi certaines musiques japonaises sonnent plus riches !
    """)

    # --- Démonstration visuelle des formes d’ondes supplémentaires ---
    t = np.linspace(0, 1, 500)
    pulse = np.sign(np.sin(2 * np.pi * 3 * t))
    saw = 2 * (t * 3 % 1) - 1
    fm = np.sin(2 * np.pi * 3 * t + 0.5 * np.sin(2 * np.pi * 12 * t))

    fig, axs = plt.subplots(3, 1, figsize=(6, 3))
    axs[0].plot(t, pulse, color="#ff6666"); axs[0].set_title("VRC6 — Onde carrée supplémentaire")
    axs[1].plot(t, saw, color="#ffaa33"); axs[1].set_title("VRC6 — Onde en dents de scie")
    axs[2].plot(t, fm, color="#55aaff"); axs[2].set_title("VRC7 / FDS — Synthèse FM")
    for ax in axs:
        ax.set_ylim(-1.2, 1.2)
        ax.set_xticks([]); ax.set_yticks([])
    plt.tight_layout()
    st.pyplot(fig)

    st.caption("""
    💡 Le **VRC6** ajoute deux canaux carrés et un canal “sawtooth”,  
    tandis que le **VRC7** introduit une vraie **synthèse FM**, comme sur les cartes son PC des années 90.
    """)

    st.markdown("""
    ### 🎵 Exemples de jeux utilisant ces extensions :
    | Jeu | Mapper | Extension audio |
    |:--|:--|:--|
    | *Akumajō Densetsu* (Castlevania III JP) | VRC6 | 3 voies sonores supplémentaires |
    | *Bio Miracle Bokutte Upa* | VRC6 | Amélioration sonore |
    | *Lagrange Point* | VRC7 | Synthèse FM |
    | *Famicom Disk System* | FDS | Son FM intégré au lecteur |
    """)

    st.info("""
    🧠 **Détail technique :**
    - Le **VRC6** est l’un des premiers exemples de “coprocesseur audio embarqué”.  
    - Le **VRC7** repose sur un dérivé du **YM2413**, un vrai synthétiseur FM.  
    - Les jeux pouvaient mixer les sons APU et ceux du mapper en temps réel.
    """)

    st.success("""
    🎓 **À retenir :**
    - Certains mappers japonais embarquaient **leurs propres puces audio**.  
    - Cela rendait les musiques plus riches, plus dynamiques, et plus “synthétiques”.  
    - Les émulateurs modernes (comme FCEUX, Mesen) les reproduisent pour retrouver la sonorité d’origine.
    """)

    st.caption("""
    🧩 Ces extensions montrent à quel point les développeurs japonais ont **poussé la NES au-delà de ses limites**,  
    en utilisant chaque cartouche comme une **console améliorée à part entière**.
    """)