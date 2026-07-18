#!/usr/bin/env python3
"""抽出 PTO II 資料表中的英文名稱，輸出譯表 CSV。"""
import os
import re
import csv
import glob
from pathlib import Path

SRC_DIR = Path('assets/origin/PTO-Paci/PTO2WIN')
OUT_DIR = Path('translation/source')

NAME_DATA_FILES = {
    'ARDATA': '將領（日本海軍）',
    'GRDATA': '將領（陸軍／盟軍）',
    'KDATA': '艦船名（簡表）',
    'KSDATA': '艦船名（詳表）',
    'NCTDATA': '地名',
    'PLDATA': '飛機名',
    'SJDATA': '國家領袖',
    'SSDATA': '潛艇名',
    'STDATA': '潛艇型別',
    'TKDATA': '戰車名',
}


def extract():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []
    for fname, ctx in NAME_DATA_FILES.items():
        path = SRC_DIR / fname
        if not path.exists():
            continue
        data = path.read_bytes()
        seen = set()
        rows = []
        for m in re.finditer(rb'[\x20-\x7e]{3,}', data):
            s = m.group().decode('ascii', errors='replace').strip()
            # 過濾明顯不是名稱的雜訊（純控制字 / 過短）
            if len(s) < 3 or s in seen:
                continue
            seen.add(s)
            rows.append({
                'file': fname,
                'id': f'{fname}:{len(rows):04d}',
                'source': s,
                'target': '',
                'note': ctx,
            })
        all_rows.extend(rows)
        print(f'{fname}: {len(rows)} 筆')

    out_csv = OUT_DIR / 'data_names.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['file', 'id', 'source', 'target', 'note'],
                                quoting=csv.QUOTE_ALL, escapechar='\\')
        writer.writeheader()
        writer.writerows(all_rows)
    print(f'寫入 {out_csv}: {len(all_rows)} 筆')


if __name__ == '__main__':
    extract()
