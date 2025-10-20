# 🧬 NES ROM Lab
> Exploration pédagogique et interactive des ROMs Nintendo NES

[![Streamlit App](https://img.shields.io/badge/🚀%20Open%20on%20Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://nes-rom-lab.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🧠 À propos

**NES ROM Lab** est une application interactive développée avec [Streamlit](https://streamlit.io/) pour explorer le fonctionnement interne des ROMs **Nintendo Entertainment System (NES)**.

L’application permet de :
- Visualiser et décoder les sections **PRG-ROM** (code CPU) et **CHR-ROM** (graphismes).
- Comprendre l’architecture du processeur **6502** et du **PPU** (Picture Processing Unit).
- Observer les tuiles graphiques, les palettes de couleurs et le mécanisme de scrolling.
- Exécuter une **émulation pédagogique** simplifiée, sans exécution réelle de code machine.
- Explorer les principes fondamentaux du format **iNES**.

---

## 🧩 Fonctionnalités

| Section | Description |
|----------|--------------|
| 🎮 Introduction | Présente la console, le concept des octets et le format des ROMs. |
| ⚙️ CPU & Architecture | Analyse du code machine, désassemblage et pas-à-pas du CPU 6502. |
| 🎨 Graphismes (CHR-ROM) | Décodage des tuiles 8x8 et affichage en mosaïque. |
| 🧩 Graphismes (PPU) | Visualisation du PPU, scrolling et palettes NES. |
| 📦 Format iNES | Détails du header, tailles PRG/CHR et vérification SHA1/CRC32. |
| 🧱 Matériel & mémoire | Schémas mémoire, bus, APU et cartouches. |
| 🕹️ Émulation simplifiée | Boucle CPU/PPU simulée image par image. |
| 🧠 Reconstruction Frame NES | Génération d’un frame PPU complet. |
| 🎮 Reconstruction NES | Reconstitution visuelle de scènes graphiques. |

---

## 📂 Structure du projet
nes-rom-lab/
│
├── app.py # Application principale Streamlit
├── requirements.txt # Dépendances Python
├── roms/ # Dossier des ROMs locales (non versionné)
├── utils/ # Modules internes
│ ├── chr.py
│ ├── cpu_manager.py
│ ├── disasm.py
│ ├── edu_helpers.py
│ ├── minimap.py
│ ├── nes_emulator.py
│ ├── nes_palette.py
│ ├── opcodes.py
│ ├── ppu_framebuilder.py
│ ├── ppu_rom_viewer.py
│ ├── ppu_scroll.py
│ └── ppu_viewer.py
└── README.md

---

## 🚀 Déploiement sur Streamlit Cloud

1️⃣ **Cloner le dépôt**
```bash
git clone https://github.com/cdupasquier/nes-rom-lab.git
cd nes-rom-lab
```

2️⃣ **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3️⃣ **Lancer en local**
```bash
streamlit run app.py
```
4️⃣ **Déploiement automatique sur**
```bash
👉 Streamlit Cloud
```
## ⚙️ Configuration automatique

- La **ROM par défaut** — *Super Mario Bros 3 (`SMB3.nes`)* — est automatiquement chargée depuis le dossier **`/roms`** au lancement de l’application.  
- Il est également possible d’**importer d’autres ROMs NES** via la **barre latérale** Streamlit (`.nes` uniquement).  
- Les fichiers doivent suivre le **format standard iNES** (`NES<1A>`), garantissant la compatibilité avec les outils d’analyse et d’émulation internes.

> 💡 Si la ROM par défaut est absente, un message invite simplement à en placer une dans le dossier `/roms`.

---

## 🧩 Technologies utilisées

| Outil | Rôle principal |
|--------|----------------|
| 🐍 **Python 3.11+** | Langage principal du projet |
| 🎈 **Streamlit** | Framework d’interface web interactive |
| 🔢 **NumPy** | Manipulation efficace des données binaires et graphiques |
| 🖼️ **Pillow (PIL)** | Rendu des tuiles CHR et images NES |
| 📊 **Matplotlib** | Visualisation schématique (CPU, mémoire, cycles, etc.) |
| 🔒 **Zlib / Hashlib** | Vérification d’intégrité CRC32 et SHA-1 des ROMs |

---

## 🧑‍💻 Auteur

**👨‍💻 Christophe Dupasquier**  
📍 *Commune de Châtel-St-Denis — Suisse*  
🛡️ *ICT Manager / RSSI*  
💡 Passionné par l’**intelligence artificielle**, la **rétro-ingénierie** et la **pédagogie numérique**.

---

## 📜 Licence

Ce projet est distribué sous licence **MIT**.  
Vous êtes libre de **l’utiliser, le modifier et le redistribuer**, à condition d’en **mentionner la source**.




