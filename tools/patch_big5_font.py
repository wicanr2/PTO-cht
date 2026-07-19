#!/usr/bin/env python3
"""把 TEKE2WIN.EXE 的 GDI 字型從日文（SHIFTJIS / 細明朝体）改成繁中（CHINESEBIG5 / 新細明體）。

背景（詳 docs/REVERSE.md「待解決 > 1. 中文字型」）：
- 遊戲無自訂 bitmap font，文字全部經 GDI TextOut 渲染
- CreateFont 呼叫點 seg11:0x66bc，charset 參數 0x80（SHIFTJIS_CHARSET）
  在 file offset 0x97cae；facename 字串 ds:0x7b8e 在 file offset 0xc9f8e，
  內容為 Shift-JIS「細明朝体」（8 bytes + NUL）
- 本工具把 charset 改成 0x88（CHINESEBIG5_CHARSET），facename 改成
  Big5「新細明體」（同為 8 bytes，原位覆蓋）

另：已對全部 11 個 code segment 做完整反組譯掃描，文字繪製路徑中
不存在 SJIS lead-byte 範圍判斷（0x81–0x9F / 0xE0–0xFC 的 cmp 群只出現在
CRT startup 的 argv 解析 seg11:0x4949–0x4a99，不影響繪字），
因此 Big5 字串不需要再 patch lead-byte 邏輯。

輸入：patch/TEKE2WIN.EXE（不存在則從 assets/origin 複製；絕不修改 origin）
輸出：就地修改 patch/TEKE2WIN.EXE；冪等，已 patch 過會直接報 OK
"""
import shutil
from pathlib import Path

SRC = Path('assets/origin/PTO-Paci/PTO2WIN/TEKE2WIN.EXE')
OUT = Path('patch/TEKE2WIN.EXE')

# (offset, expected_old_bytes, new_bytes, 說明)
PATCHES = [
    (
        0x97CAD,
        b'\x68\x80\x00',          # push 0x80  (CreateFont lfCharSet = SHIFTJIS_CHARSET)
        b'\x68\x88\x00',          # push 0x88  (CHINESEBIG5_CHARSET)
        'CreateFont charset SHIFTJIS(0x80) -> CHINESEBIG5(0x88)',
    ),
    (
        0xC9F8E,
        b'\x95\x57\x8f\x80\x96\xbe\x92\xa9\x00',   # SJIS「細明朝体」+ NUL
        '新細明體'.encode('big5') + b'\x00',        # Big5「新細明體」+ NUL（同長度 8+1）
        'CreateFont facename 細明朝体 -> 新細明體 (Big5)',
    ),
]


def main():
    if not OUT.exists():
        OUT.parent.mkdir(exist_ok=True)
        shutil.copy2(SRC, OUT)
        print(f'{OUT} 不存在，已從 {SRC} 複製')

    data = bytearray(OUT.read_bytes())
    changed = False
    for off, old, new, desc in PATCHES:
        cur = bytes(data[off:off + len(old)])
        if cur == new:
            print(f'OK（已 patch）0x{off:x}: {desc}')
            continue
        if cur != old:
            raise SystemExit(
                f'[error] 0x{off:x} bytes 不符預期：{cur.hex()} != {old.hex()}（{desc}），不寫入')
        data[off:off + len(old)] = new
        changed = True
        print(f'patch 0x{off:x}: {desc}')

    if changed:
        OUT.write_bytes(data)
        print(f'寫入 {OUT}')
    else:
        print('無變更')


if __name__ == '__main__':
    main()
