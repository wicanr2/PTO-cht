#!/usr/bin/env python3
"""從 TEKE2WIN.EXE 資料段（0xC0000-0xCBE00，VERSION 資源之前）萃取 UI/訊息字串。

輸出 translation/source/text_exe_ui.csv，欄位：offset,source,note
過濾原則：只丟棄明顯的垃圾（RLE 殘留、純標點、無母音短亂碼），
不確定的一律保留，由翻譯階段決定 target 留空。

冪等：直接讀 assets/origin，不改任何遊戲檔。
"""
import csv
import re
from pathlib import Path

SRC = Path('assets/origin/PTO-Paci/PTO2WIN/TEKE2WIN.EXE')
OUT = Path('translation/source/text_exe_ui.csv')

BEGIN = 0xC0000
END = 0xCBE00  # VERSION 資源（VS_VERSION_INFO）之前，不可觸碰
MIN_LEN = 4

VOWELS = set('aeiouAEIOU')


def extract(data: bytes):
    """掃 NUL 結尾的可列印 ASCII 字串，回傳 (offset, text) 清單。"""
    region = data[BEGIN:END]
    out = []
    i = 0
    while i < len(region):
        if 32 <= region[i] < 127:
            j = i
            while j < len(region) and 32 <= region[j] < 127:
                j += 1
            if j < len(region) and region[j] == 0 and j - i >= MIN_LEN:
                out.append((BEGIN + i, region[i:j].decode('ascii')))
            i = j + 1
        else:
            i += 1
    return out


def is_junk(s: str) -> bool:
    """明顯非人讀字串才回傳 True（保守：不確定就保留）。"""
    stripped = s.strip()
    if not stripped:
        return True  # 純空白
    has_alpha = any(c.isalpha() for c in stripped)
    has_fmt = '%' in stripped
    if not has_alpha and not has_fmt:
        return True  # 純標點/數字/空白，如 '   " '、'  000 '
    # 去掉空白與標點後只剩一種字元（如 '@@@D@'->'@D'? 不適用；'www' -> 'w'）
    core = re.sub(r'[\s\W_]+', '', stripped)
    if core and len(set(core.lower())) == 1:
        return True  # 單一字元重複，如 'wwwwww'
    # 無母音、無空白、無數字、無格式符的短亂碼，如 '@@@D@'、'wwwwwwtwwp'、'D@DDD'
    if (not any(c in VOWELS for c in stripped)
            and ' ' not in stripped and not any(c.isdigit() for c in stripped)
            and not has_fmt):
        return True
    return False


def main():
    data = SRC.read_bytes()
    rows = [(off, s) for off, s in extract(data) if not is_junk(s)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(['offset', 'source', 'note'])
        for off, s in rows:
            w.writerow([f'0x{off:05x}', s, ''])
    print(f'萃取 {len(rows)} 字串 -> {OUT}')


if __name__ == '__main__':
    main()
