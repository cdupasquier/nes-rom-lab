import numpy as np

# === 🎨 Palette maître NES officielle (64 couleurs) ===
# Dérivée du signal NTSC d’origine (source : FCEUX / NESDev)
NES_PALETTE = np.array([
    [124,124,124],[0,0,252],[0,0,188],[68,40,188],
    [148,0,132],[168,0,32],[168,16,0],[136,20,0],
    [80,48,0],[0,120,0],[0,104,0],[0,88,0],
    [0,64,88],[0,0,0],[0,0,0],[0,0,0],

    [188,188,188],[0,120,248],[0,88,248],[104,68,252],
    [216,0,204],[228,0,88],[248,56,0],[228,92,16],
    [172,124,0],[0,184,0],[0,168,0],[0,168,68],
    [0,136,136],[0,0,0],[0,0,0],[0,0,0],

    [248,248,248],[60,188,252],[104,136,252],[152,120,248],
    [248,120,248],[248,88,152],[248,120,88],[252,160,68],
    [248,184,0],[184,248,24],[88,216,84],[88,248,152],
    [0,232,216],[120,120,120],[0,0,0],[0,0,0],

    [252,252,252],[164,228,252],[184,184,248],[216,184,248],
    [248,184,248],[248,164,192],[240,208,176],[252,224,168],
    [248,216,120],[216,248,120],[184,248,184],[184,248,216],
    [0,252,252],[248,216,248],[0,0,0],[0,0,0]
], dtype=np.uint8)


# === 🧩 Palettes de démonstration générales ===
DEMO_PALETTES = {
    "🟩 Herbe / Nature": [0x0F, 0x19, 0x29, 0x39],
    "🏙️ Ville / Métal": [0x0F, 0x11, 0x21, 0x31],
    "🌄 Soleil couchant": [0x0F, 0x06, 0x16, 0x26],
    "🌊 Océan / Glace": [0x0F, 0x02, 0x12, 0x22],
    "🔥 Lave / Enfer": [0x0F, 0x07, 0x17, 0x27],
    "🕹️ Neutre (gris NES)": [0x0F, 0x10, 0x20, 0x30],
}


# === 🎮 Palettes authentiques par jeu NES (approximation documentée) ===
# Chaque ligne correspond à une palette utilisée par le PPU du jeu réel.
GAME_PALETTES = {
    "Super Mario Bros.": {
        "Décor": [0x0F, 0x21, 0x31, 0x30],     # Ciel / sol / briques
        "Mario": [0x0F, 0x16, 0x27, 0x18],     # Rouge / bleu / beige
        "Ennemi": [0x0F, 0x17, 0x27, 0x30],    # Goombas / Koopa
    },
    "The Legend of Zelda": {
        "Décor": [0x0F, 0x16, 0x26, 0x30],
        "Link": [0x0F, 0x19, 0x29, 0x39],
        "Donjon": [0x0F, 0x05, 0x15, 0x25],
    },
    "Metroid": {
        "Décor": [0x0F, 0x07, 0x17, 0x27],
        "Samus": [0x0F, 0x16, 0x26, 0x37],
        "Caverne": [0x0F, 0x06, 0x16, 0x36],
    },
    "Mega Man 2": {
        "Décor": [0x0F, 0x12, 0x22, 0x32],
        "Mega Man": [0x0F, 0x21, 0x31, 0x30],
        "Boss": [0x0F, 0x07, 0x17, 0x27],
    },
    "Castlevania": {
        "Décor": [0x0F, 0x06, 0x16, 0x26],
        "Simon": [0x0F, 0x17, 0x27, 0x37],
        "Ennemi": [0x0F, 0x07, 0x17, 0x27],
    },
    "Duck Hunt": {
        "Ciel": [0x0F, 0x21, 0x30, 0x37],
        "Canard": [0x0F, 0x17, 0x27, 0x30],
        "Chien": [0x0F, 0x06, 0x16, 0x26],
    },
}


# === 🔍 Utilitaire : obtenir la palette selon le SHA1 ou le nom du jeu ===
def get_game_palette(game_name: str, section: str = "Décor"):
    """Retourne une palette NES authentique pour un jeu donné."""
    game = GAME_PALETTES.get(game_name)
    if not game:
        return None
    palette_indices = game.get(section)
    if not palette_indices:
        return None
    return NES_PALETTE[palette_indices]
