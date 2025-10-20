# utils/chr.py
import numpy as np

def decode_chr_8x8_tiles(chr_bytes: bytes):
    """Retourne une liste de tiles 8x8 (valeurs 0..3) décodées depuis CHR-ROM"""
    tiles = []
    for off in range(0, len(chr_bytes), 16):
        if off + 16 > len(chr_bytes):
            break
        plane0 = chr_bytes[off:off+8]
        plane1 = chr_bytes[off+8:off+16]
        tile = np.zeros((8, 8), dtype=np.uint8)
        for y in range(8):
            b0 = plane0[y]
            b1 = plane1[y]
            for x in range(8):
                bit = 7 - x
                p0 = (b0 >> bit) & 1
                p1 = (b1 >> bit) & 1
                tile[y, x] = (p1 << 1) | p0
        tiles.append(tile)
    return tiles
