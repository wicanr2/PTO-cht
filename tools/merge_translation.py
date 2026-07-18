#!/usr/bin/env python3
"""把翻譯好的 chunk 合併成完整譯表。"""
import csv
import glob
from pathlib import Path

OUT = Path('translation/target')
CHUNK_DIR = Path('translation/target/translated')


def merge(pattern: str, out_name: str, exclude_files: set = None):
    rows = []
    for path in sorted(glob.glob(str(CHUNK_DIR / pattern))):
        with open(path, newline='', encoding='utf-8-sig') as f:
            for row in csv.DictReader(f):
                if exclude_files and row.get('file') in exclude_files:
                    continue
                rows.append(row)
    out_path = OUT / out_name
    fieldnames = rows[0].keys()
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames,
                                quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writeheader()
        writer.writerows(rows)
    print(f'寫入 {out_path}: {len(rows)} 筆')


if __name__ == '__main__':
    merge('text_tk2_*.csv', 'text_tk2.csv', exclude_files={'PLANE.TK2', 'TANK.TK2', 'MSG1.TK2'})
    merge('data_names_*.csv', 'data_names.csv')
