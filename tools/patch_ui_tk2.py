#!/usr/bin/env python3
"""把中文化 UI PNG 封回 NPK .TK2（MEIREI / MAKE）。
有中文化版本（assets/images_zh）的 chunk 用中文化圖，其餘沿用原圖。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from npk import parse_npk016_file, encode_file

SRC_DIR = Path('assets/origin/PTO-Paci/PTO2WIN')
IMG_DIR = Path('assets/images')
ZH_DIR = Path('assets/images_zh')
OUT_DIR = Path('patch')

TARGETS = ['MEIREI.TK2', 'MAKE.TK2', 'END_SF.TK2', 'OP4_BC.TK2']


def main():
    OUT_DIR.mkdir(exist_ok=True)
    for fname in TARGETS:
        base = fname.split('.')[0]
        src = SRC_DIR / fname
        chunks = parse_npk016_file(str(src))
        pngs = []
        for i in range(len(chunks)):
            zh = ZH_DIR / f'{base}_{i:03d}.png'
            orig = IMG_DIR / f'{base}_{i:03d}.png'
            pngs.append(str(zh if zh.exists() else orig))
        out = OUT_DIR / fname
        encode_file(pngs, str(src), str(out))


if __name__ == '__main__':
    main()
