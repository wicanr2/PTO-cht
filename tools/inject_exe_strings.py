#!/usr/bin/env python3
"""把繁體中文字串注入 TEKE2WIN.EXE（僅限固定長度、可安全取代的字串）。"""
from pathlib import Path

SRC = Path('assets/origin/PTO-Paci/PTO2WIN/TEKE2WIN.EXE')
OUT = Path('patch/TEKE2WIN.EXE')

# (source, target) 皆以 null 結尾；target 長度必須 <= source
MAPPING = [
    # APPMENU
    (b'E&xit\x00', '結束'),
    (b'&Help\x00', '說明'),
    (b'&Contents\x00', '內容'),
    (b'&Search By Keyword\x00', '關鍵字搜尋'),
    (b'&How To Use Help\x00', '使用說明'),
    (b'&About Version Information\x00', '關於版本資訊'),
    # APPVERSION dialog
    (b'P.T.O. II\x00', '提督II'),
    (b'Pacific Theater of Operations II\x00', '提督之決斷 II'),
    (b'Version 1.0\x00', '版本 1.0'),
    (b'(C) Copyright KOEI Corporation 1995\x00', '(C) 光榮 1995'),
]


def main():
    data = bytearray(SRC.read_bytes())
    for source, target_zh in MAPPING:
        target = target_zh.encode('big5') + b'\x00'
        if len(target) > len(source):
            print(f'[warn] {source!r}: target {len(target)} > source {len(source)}，跳過')
            continue
        idx = data.find(source)
        if idx < 0:
            print(f'[warn] 找不到 {source!r}')
            continue
        # 檢查是否唯一
        if data.find(source, idx + 1) >= 0:
            print(f'[warn] {source!r} 出現多次，僅取代第一個')
        padded = target + b'\x00' * (len(source) - len(target))
        data[idx:idx+len(source)] = padded
        print(f'OK {source!r} -> {target_zh}')

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(data)
    print(f'寫入 {OUT}')


if __name__ == '__main__':
    main()
