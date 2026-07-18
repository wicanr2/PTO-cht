#!/usr/bin/env python3
"""從 MSG1.TK2（XOR 0x96）抽出 ASCII 文字串。"""
import re
import csv
from pathlib import Path

SRC = Path('assets/origin/PTO-Paci/PTO2WIN/MSG1.TK2')
OUT = Path('translation/source/msg1_strings.csv')
XOR_KEY = 0x96
MIN_LEN = 8


def main():
    data = SRC.read_bytes()
    dec = bytes([b ^ XOR_KEY for b in data])
    rows = []
    for m in re.finditer(rb'[\x20-\x7e]{%d,}' % MIN_LEN, dec):
        s = m.group().decode('ascii', errors='replace')
        rows.append({
            'file': 'MSG1.TK2',
            'id': f'MSG1.TK2:{len(rows):04d}',
            'offset': m.start(),
            'source': s,
            'target': '',
            'note': '',
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'id', 'offset', 'source', 'target', 'note'],
                                quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writeheader()
        writer.writerows(rows)
    print(f'寫入 {OUT}: {len(rows)} 筆')


if __name__ == '__main__':
    main()
