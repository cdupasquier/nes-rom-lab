🧠 NES ROM Lab — Exploration pédagogique des ROMs Nintendo
🎮 Introduction
NES ROM Lab est une application Streamlit interactive permettant d’explorer, décoder et visualiser les ROMs Nintendo NES de manière pédagogique et interactive.
Elle reconstitue les composants clés de la console — CPU, PPU, mémoire, palettes, et scrolling — tout en offrant des explications détaillées sur le fonctionnement interne d’une ROM.

💡 Ce projet est conçu à des fins éducatives pour comprendre la structure des jeux 8-bit.

🧩 Fonctionnalités principales
🕹️ 1. Analyse de la ROM NES
Chargement automatique de roms/SMB3.nes (Super Mario Bros 3)

Analyse du header iNES (structure standard des ROMs NES)

Calcul d’empreintes SHA1 et CRC32 pour vérifier l’intégrité du fichier

Détection automatique des tailles PRG-ROM et CHR-ROM

⚙️ 2. CPU 6502 — Architecture et désassemblage
Explication détaillée des registres CPU : A, X, Y, P, SP, PC

Simulation d’un désassemblage partiel du code machine PRG-ROM

Avancement pas à pas pour visualiser le cycle d’exécution

Coloration syntaxique des instructions (LDA, STA, JSR, JMP…)

🎨 3. Graphismes (CHR-ROM)
Visualisation de toutes les tuiles 8×8 contenues dans la CHR-ROM

Décodage des plans de bits haut/bas (bitplane)

Explication du mapping couleur (4 niveaux → 4 teintes NES)

Démonstration interactive du décodage d’une tuile

Prise en charge des ROMs CHR-RAM (jeux dynamiques comme Metroid ou Kirby)

🧩 4. PPU — Picture Processing Unit
Simulation du scrolling NES (déplacement de la caméra sur une grande carte de tuiles)

Visualisation de la fenêtre visible 256×240 px

Sélection interactive de palettes NES réelles ou démo

Explications pédagogiques sur le fonctionnement du PPU et des Name Tables

🧱 5. Mémoire & matériel
Carte mémoire interactive des composants NES

Explication du bus mémoire, de la VRAM, du PPU, et de l’APU

Présentation des mappers et extensions de cartouche

Vue synthétique du cycle de frame NES

🕹️ 6. Émulation simplifiée
Simulation de la boucle CPU ↔ PPU

Affichage dynamique d’images à partir de la CHR-ROM

Animation image par image (frames) pour montrer le rendu progressif

🧠 7. Reconstruction graphique complète
Génération d’une frame NES réaliste à partir des tuiles CHR

Thèmes de scène : Mario, Zelda, Metroid

Sélection de palettes colorées NES

Reconstitution pédagogique du rendu à l’écran

📦 8. Fichier iNES — Structure interne
Décomposition du header binaire (16 octets)

Explication champ par champ (PRG, CHR, Mapper, Flags, etc.)

Vérification automatique du format

Messages de diagnostic :

✅ ROM valide

⚠️ ROM hackée / modifiée

❌ ROM corrompue ou format non conforme

ℹ️ 9. À propos
Auteurs : Christophe Dupasquier

Projet open-source à vocation éducative

Compatible Windows / macOS / Linux / Raspberry Pi

Développé avec ❤️ en Python 3.12 et Streamlit

🗂️ Structure du projet
python
Copier le code
nes-rom-lab/
│
├── app.py                      # Application principale Streamlit
├── requirements.txt            # Dépendances Python
│
├── roms/                       # Dossier contenant les ROMs locales (.nes)
│   └── SMB3.nes
│
├── utils/                      # Modules pédagogiques
│   ├── edu_helpers.py          # Textes explicatifs et illustrations
│   ├── cpu_manager.py          # Désassemblage 6502 simplifié
│   ├── disasm.py               # Logique de désassemblage
│   ├── minimap.py              # Carte mémoire et diagrammes
│   ├── nes_emulator.py         # Simulation CPU ↔ PPU
│   ├── ppu_viewer.py           # Mosaïque CHR
│   ├── ppu_scroll.py           # Scrolling NES
│   ├── ppu_framebuilder.py     # Rendu NES animé (fond + sprites)
│   ├── ppu_rom_viewer.py       # Reconstruction d’écran complet
│   ├── nes_palette.py          # Palettes de couleurs NES
│   ├── opcodes.py              # Liste d’instructions CPU 6502
│   └── chr.py                  # Gestion des tuiles CHR-ROM
│
└── README.md                   # Ce fichier
⚙️ Installation
1️⃣ Cloner le dépôt
bash
Copier le code
git clone https://github.com/<ton_user>/nes-rom-lab.git
cd nes-rom-lab
2️⃣ Installer les dépendances
bash
Copier le code
pip install -r requirements.txt
3️⃣ Lancer l’application
bash
Copier le code
streamlit run app.py
💡 Si SMB3.nes est présent dans /roms, il sera chargé automatiquement au démarrage.

🧱 Environnement de développement recommandé
Python 3.12+

Streamlit 1.36+

VS Code ou PyCharm

Testé sur Windows 11, macOS Sonoma, et Raspberry Pi OS 2025

🎨 Technologies utilisées
Composant	Rôle
🧠 Streamlit	Interface pédagogique et visuelle
🧮 NumPy	Calculs binaires et manipulation mémoire
🖼️ Pillow	Rendu des images NES
📊 Matplotlib	Graphiques explicatifs
🧩 Bitstring / Construct	Parsing du format iNES
🎨 Colorama / Pygments	Coloration et interface terminale

🔒 Avertissement
Ce projet est fourni à des fins éducatives uniquement.
Il ne contient ni jeu complet, ni code propriétaire Nintendo.
Les ROMs officielles doivent être obtenues légalement.

🧩 Licence
Ce projet est distribué sous licence MIT — libre d’utilisation, de modification et de diffusion,
tant que la mention d’origine est conservée.