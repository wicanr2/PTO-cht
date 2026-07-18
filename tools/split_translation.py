#!/usr/bin/env python3
"""把大譯表切成小塊，方便分配給 subagent。"""
import csv
import math
import sys
from pathlib import Path

SRC = Path('translation/source')
OUT = Path('translation/target/chunks')


def split(csv_path: Path, chunk_size: int):
    rows = list(csv.DictReader(open(csv_path, newline='', encoding='utf-8-sig')))
    base = csv_path.stem
    n_chunks = math.ceil(len(rows) / chunk_size)
    for i in range(n_chunks):
        chunk = rows[i*chunk_size:(i+1)*chunk_size]
        out_path = OUT / f'{base}_{i:03d}.csv'
        OUT.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys(),
                                    quoting=csv.QUOTE_ALL, escapechar='\\')
            writer.writeheader()
            writer.writerows(chunk)
        print(f'{out_path}: {len(chunk)} 筆')


if __name__ == '__main__':
    split(SRC / 'text_tk2.csv', 100)
    split(SRC / 'data_names.csv', 200)
