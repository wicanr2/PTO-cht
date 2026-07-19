#!/usr/bin/env python3
"""把 EXE 資料段 UI/訊息字串翻譯注入 TEKE2WIN.EXE。

輸入：translation/target/text_exe_ui.csv（offset,source,target,note）
作用範圍：file offset 0xC0000-0xCBE00（VERSION 資源之前）。

規則：
- target 空白 → 跳過（保留原文）
- target Big5 編碼長度 > 原字串 bytes 數 → 報錯列出，不靜默截斷
- 寫入時以 NUL 補滿原字串長度（含原 NUL 結尾共 len(source)+1 bytes）
- 寫入前驗證該 offset 目前內容是 source 原文或已注入的同一 target（冪等）
- 逐一回讀驗證寫入結果

輸入：patch/TEKE2WIN.EXE（不存在則從 assets/origin 複製；絕不修改 origin）
輸出：就地修改 patch/TEKE2WIN.EXE
"""
import csv
import shutil
from pathlib import Path

SRC = Path('assets/origin/PTO-Paci/PTO2WIN/TEKE2WIN.EXE')
OUT = Path('patch/TEKE2WIN.EXE')
CSV_PATH = Path('translation/target/text_exe_ui.csv')

BEGIN = 0xC0000
END = 0xCBE00


def main():
    if not OUT.exists():
        OUT.parent.mkdir(exist_ok=True)
        shutil.copy2(SRC, OUT)
    data = bytearray(OUT.read_bytes())

    # inject_exe_strings.py 先跑，資源字串（APPMENU/APPVERSION）已是中文，
    # 這些位置接受「該工具的譯文」為合法現狀，略過不覆蓋
    from inject_exe_strings import MAPPING as RES_MAPPING
    res_ok = {}
    for src_b, tgt_zh in RES_MAPPING:
        tgt_b = tgt_zh.encode('big5')
        res_ok[src_b.rstrip(b'\x00')] = tgt_b + b'\x00' * (len(src_b) - len(tgt_b))

    rows = list(csv.DictReader(CSV_PATH.open(encoding='utf-8-sig')))
    errors = []
    injected = skipped = already = 0
    for r in rows:
        target = r['target']
        if not target:
            skipped += 1
            continue
        off = int(r['offset'], 16)
        if not (BEGIN <= off < END):
            errors.append(f'{r["offset"]}: offset 超出範圍')
            continue
        src_bytes = r['source'].encode('ascii')
        tgt_bytes = target.encode('big5')
        if len(tgt_bytes) > len(src_bytes):
            errors.append(f'{r["offset"]}: 超長 {len(tgt_bytes)} > {len(src_bytes)} {target!r}')
            continue
        slot = len(src_bytes) + 1  # 含 NUL 結尾
        current = bytes(data[off:off + slot])
        expected_new = tgt_bytes + b'\x00' * (slot - len(tgt_bytes))
        if current == expected_new:
            already += 1
            continue
        if current != src_bytes + b'\x00':
            if res_ok.get(src_bytes) == current:
                already += 1  # 資源字串工具已注入，保留其譯文
                continue
            # 資源工具的對照可能是本字串的子字串（如 'Pacific Theater of
            # Operations II' 是 'End of ...' 的尾部），此時以本工具的
            # 完整譯文覆蓋
            variant = src_bytes + b'\x00'
            for src_b, tgt_zh in RES_MAPPING:
                tgt_b = tgt_zh.encode('big5')
                variant = variant.replace(
                    src_b, tgt_b + b'\x00' * (len(src_b) - len(tgt_b)))
            if variant == current:
                data[off:off + slot] = expected_new
                if bytes(data[off:off + slot]) != expected_new:
                    errors.append(f'{r["offset"]}: 寫入後驗證失敗')
                    continue
                injected += 1
                continue
            errors.append(f'{r["offset"]}: 現有內容非原文也非已注入譯文 {current!r}')
            continue
        data[off:off + slot] = expected_new
        # 回讀驗證
        if bytes(data[off:off + slot]) != expected_new:
            errors.append(f'{r["offset"]}: 寫入後驗證失敗')
            continue
        injected += 1

    if errors:
        print(f'[error] {len(errors)} 筆失敗：')
        for e in errors:
            print(' ', e)
        raise SystemExit(1)

    OUT.write_bytes(data)
    print(f'注入 {injected} 筆，已注入略過 {already} 筆，留空 {skipped} 筆 -> {OUT}')


if __name__ == '__main__':
    main()
