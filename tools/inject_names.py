#!/usr/bin/env python3
"""把繁體中文譯名注入 PTO II 資料表。"""
import csv
import sys
from pathlib import Path

SRC_DIR = Path('assets/origin/PTO-Paci/PTO2WIN')
OUT_DIR = Path('patch')
TARGET_CSV = Path('translation/target/data_names.csv')


def replace_null_terminated(data: bytearray, pos: int, source: bytes, target: bytes, start_search: int = 0):
    """在 data 中從 start_search 開始找 source，找到後用 target 取代，並用 \\x00 補到原欄位容量。
    回傳 (new_pos, ok, msg)"""
    idx = data.find(source, start_search)
    if idx < 0:
        idx = data.find(source)
        if idx < 0:
            return pos, False, '找不到 source'
    # 計算欄位容量：從 source 結尾開始找第一個非 0 byte
    end = idx + len(source)
    capacity_end = end
    while capacity_end < len(data) and data[capacity_end] == 0:
        capacity_end += 1
    capacity = capacity_end - idx
    if len(target) > capacity:
        # 截斷到 capacity，並確保不切斷 Big5 字元（偶數位元組）
        target = target[:capacity]
        if len(target) % 2:
            target = target[:-1]
        if not target:
            return pos, False, f'target 長度超過欄位容量 {capacity} 且無法截斷'
    # 取代
    padded = target + b'\x00' * (capacity - len(target))
    data[idx:idx+capacity] = padded
    return idx + capacity, True, ''


def main():
    OUT_DIR.mkdir(exist_ok=True)
    rows_by_file = {}
    with open(TARGET_CSV, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            fname = row['file']
            rows_by_file.setdefault(fname, []).append(row)

    for fname, rows in rows_by_file.items():
        src_path = SRC_DIR / fname
        if not src_path.exists():
            print(f'[warn] 找不到 {src_path}')
            continue
        data = bytearray(src_path.read_bytes())
        pos = 0
        ok_count = 0
        for row in rows:
            source = row['source'].encode('ascii', errors='replace')
            target = row['target'].encode('big5', errors='replace') if row['target'] else source
            if target == source:
                continue
            new_pos, ok, msg = replace_null_terminated(data, pos, source, target, pos)
            if ok:
                pos = new_pos
                ok_count += 1
            else:
                print(f'  [warn] {row["id"]} {row["source"]!r}: {msg}')
        out_path = OUT_DIR / fname
        out_path.write_bytes(data)
        print(f'{fname}: 注入 {ok_count}/{len(rows)} 筆 -> {out_path}')


if __name__ == '__main__':
    main()
