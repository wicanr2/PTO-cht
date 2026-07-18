#!/usr/bin/env python3
"""把繁體中文譯文注入純文字 .TK2 檔（EVMSG/JOGEN/KAIMSG/SCESETSU/SCESTART/KSNAME/SSNAME）。"""
import csv
import re
from pathlib import Path

SRC_DIR = Path('assets/origin/PTO-Paci/PTO2WIN')
OUT_DIR = Path('patch')
TARGET_CSV = Path('translation/target/text_tk2.csv')

TEXT_FILES = ['EVMSG.TK2', 'JOGEN.TK2', 'KAIMSG.TK2',
              'SCESETSU.TK2', 'SCESTART.TK2', 'KSNAME.TK2', 'SSNAME.TK2']


def split_records(data: bytes, fname: str):
    """把檔案切成 (content, separator) 串列。"""
    if fname in ('KSNAME.TK2', 'SSNAME.TK2'):
        # 單一 \x00 分隔
        parts = data.split(b'\x00')
        records = []
        for i, p in enumerate(parts):
            sep = b'\x00' if i < len(parts) - 1 else b''
            records.append((p, sep))
        return records
    # 4 個以上 \x00 分隔
    records = []
    pos = 0
    while pos < len(data):
        m = re.search(rb'\x00{4,}', data[pos:])
        if not m:
            records.append((data[pos:], b''))
            break
        end = pos + m.start()
        sep_start = end
        sep_end = pos + m.end()
        records.append((data[pos:end], data[sep_start:sep_end]))
        pos = sep_end
    return records


def inject_file(fname: str, rows):
    src_path = SRC_DIR / fname
    data = src_path.read_bytes()
    records = split_records(data, fname)
    # 只處理非空記錄；空記錄照原樣保留
    non_empty_indices = [i for i, (c, _) in enumerate(records) if c.strip()]
    if len(non_empty_indices) != len(rows):
        print(f'[warn] {fname}: 非空記錄 {len(non_empty_indices)} != rows {len(rows)}')
    out = bytearray()
    ok = 0
    row_map = {idx: rows[n] for n, idx in enumerate(non_empty_indices) if n < len(rows)}
    for i, (content, sep) in enumerate(records):
        if i not in row_map:
            out.extend(content)
            out.extend(sep)
            continue
        row = row_map[i]
        target = row['target']
        if not target:
            new_content = content
        else:
            new_content = target.encode('big5', errors='replace')
        if len(new_content) > len(content):
            print(f'  [warn] {row["id"]}: target {len(new_content)} > 原記錄 {len(content)}，將截斷')
            new_content = new_content[:len(content)]
        new_content = new_content + b'\x00' * (len(content) - len(new_content))
        out.extend(new_content)
        out.extend(sep)
        ok += 1
    out_path = OUT_DIR / fname
    OUT_DIR.mkdir(exist_ok=True)
    out_path.write_bytes(out)
    print(f'{fname}: 注入 {ok} 筆 -> {out_path}')


def main():
    rows_by_file = {}
    with open(TARGET_CSV, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            rows_by_file.setdefault(row['file'], []).append(row)
    for fname in TEXT_FILES:
        if fname in rows_by_file:
            inject_file(fname, rows_by_file[fname])


if __name__ == '__main__':
    main()
