#!/usr/bin/env python3
"""抽出 PTO II 中的文字資源，輸出成譯表 CSV。"""
import os
import re
import csv
import json
import glob
import argparse
from pathlib import Path

SRC_DIR = Path('assets/origin/PTO-Paci/PTO2WIN')
OUT_DIR = Path('translation/source')
XOR_KEY = 0x96

# 已知檔案類型
ASCII_FILES = ['EVMSG.TK2', 'JOGEN.TK2', 'KAIMSG.TK2',
               'SCESETSU.TK2', 'SCESTART.TK2', 'KSNAME.TK2', 'SSNAME.TK2']
XOR_FILES = ['MSG1.TK2', 'PLANE.TK2', 'TANK.TK2']


def split_text(data: bytes, file: str) -> list:
    """把 bytes 切成可翻譯段落。"""
    if file in ('KSNAME.TK2', 'SSNAME.TK2'):
        parts = data.split(b'\x00')
    else:
        # 用連續 4 個以上 \x00 當記錄分隔（去除固定長度記錄的 padding）
        parts = [p for p in re.split(rb'\x00{4,}', data) if p.strip()]
    cleaned = []
    for p in parts:
        # 去掉單獨的 \x00 與前後空白
        text = p.replace(b'\x00', b'').replace(b'\r', b'\n').decode('ascii', errors='replace').strip()
        if text:
            cleaned.append(text)
    return cleaned


def extract_tk2():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for fname in ASCII_FILES + XOR_FILES:
        path = SRC_DIR / fname
        if not path.exists():
            print(f'[warn] missing {path}')
            continue
        data = path.read_bytes()
        if fname in XOR_FILES:
            data = bytes([b ^ XOR_KEY for b in data])
        for i, text in enumerate(split_text(data, fname)):
            rows.append({
                'file': fname,
                'id': f'{fname}:{i:04d}',
                'offset': i,
                'source': text,
                'target': '',
                'note': '',
            })
    out_csv = OUT_DIR / 'text_tk2.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'id', 'offset', 'source', 'target', 'note'],
                                quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writeheader()
        writer.writerows(rows)
    print(f'寫入 {out_csv}: {len(rows)} 筆')
    return rows


def extract_exe():
    path = SRC_DIR / 'TEKE2WIN.EXE'
    data = path.read_bytes()
    # 抓連續可列印 ASCII 與常見空格/分行
    strings = []
    for m in re.finditer(rb'[\x20-\x7e]{4,}', data):
        s = m.group().decode('ascii', errors='replace')
        strings.append((m.start(), s))
    out_csv = OUT_DIR / 'text_exe.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writerow(['offset', 'source', 'target', 'note'])
        for off, s in strings:
            writer.writerow([f'0x{off:06X}', s, '', ''])
    print(f'寫入 {out_csv}: {len(strings)} 筆')
    return strings


def main():
    parser = argparse.ArgumentParser(description='抽出 PTO II 文字資源')
    parser.add_argument('--tk2', action='store_true', default=True, help='抽出 .TK2 文字')
    parser.add_argument('--exe', action='store_true', help='抽出 EXE 字串')
    args = parser.parse_args()

    if args.tk2:
        extract_tk2()
    if args.exe:
        extract_exe()


if __name__ == '__main__':
    main()
