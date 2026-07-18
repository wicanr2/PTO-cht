#!/usr/bin/env python3
"""把繁體中文譯文注入 MSG1.TK2（XOR 0x96）。"""
import csv
from pathlib import Path

SRC = Path('assets/origin/PTO-Paci/PTO2WIN/MSG1.TK2')
OUT = Path('patch/MSG1.TK2')
CSV = Path('translation/target/msg1_translated.csv')
XOR_KEY = 0x96


def main():
    data = bytearray(SRC.read_bytes())
    dec = bytes([b ^ XOR_KEY for b in data])
    rows = []
    with open(CSV, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            if row['source'] and row['target']:
                rows.append(row)

    for row in rows:
        source = row['source'].encode('ascii', errors='replace')
        target = row['target'].encode('big5', errors='replace')
        offset = int(row['offset'])
        # 從 offset 附近開始找 source
        idx = dec.find(source, offset)
        if idx < 0:
            idx = dec.find(source)
            if idx < 0:
                print(f'  [warn] 找不到 {row["id"]}: {row["source"]!r}')
                continue
        if len(target) > len(source):
            # 截斷到 source 長度，避免破壞後面資料
            target = target[:len(source)]
            if len(target) % 2:
                target = target[:-1]
        # 用空格補到 source 長度（不改變檔案大小）
        padded = target + b' ' * (len(source) - len(target))
        for i, b in enumerate(padded):
            data[idx + i] = b ^ XOR_KEY

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(data)
    print(f'寫入 {OUT}: 注入 {len(rows)} 筆')


if __name__ == '__main__':
    main()
