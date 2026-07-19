#!/usr/bin/env python3
"""Wine 路線 EXE patch：跳過顯示能力檢查（256 色 / 640x480），保留視窗建立與 surface 註冊。

對象：TEKE2WIN.EXE（Win16 NE）。Wine 在現代 24-bit X 下
GetDeviceCaps(SIZEPALETTE)!=256 / 無 RC_PALETTE，遊戲會彈
「Please use display driver for 256 colors.」後退出。

檢查函式在 seg11:0x14fe。**注意**：此函式除檢查外還負責 RegisterClass/
CreateWindow 以及註冊 640x400 WinG surface（seg11:0x1611 call 0x6516，
會遞增全域 surface count es:[0x204c]）。不可整函式 skip（舊版曾改成
mov ax,1;retf 4，會導致 surface count=0 → WinGGetDIBPointer(0) → crash）。

→ 只 nop 掉四個失敗分支：
  seg11:0x153e  je  error        ; 無 RC_PALETTE
  seg11:0x1545  je  ok           ; SIZEPALETTE==256 → 強制 jmp
  seg11:0x1564  jl  error        ; 寬 <640
  seg11:0x156d  jle error        ; 高 <=400

用法：python3 tools/patch_wine_checks.py <TEKE2WIN.EXE 路徑>
冪等：已 patch 則報告並離開；原始 bytes 不符則拒絕修改。
"""
import struct
import sys

SEG = 11
PATCHES = [
    # (seg 內 offset, 原 bytes, 新 bytes, 說明)
    (0x153E, bytes.fromhex('7407'),       bytes.fromhex('9090'),     'skip RC_PALETTE error'),
    (0x1545, bytes.fromhex('7409'),       bytes.fromhex('eb09'),     'force SIZEPALETTE ok'),
    (0x1564, bytes.fromhex('0f8cb400'),   bytes.fromhex('90909090'), 'skip width<640 error'),
    (0x156D, bytes.fromhex('0f8eab00'),   bytes.fromhex('90909090'), 'skip height<=400 error'),
]


def seg_file_offset(data: bytes, segnum: int) -> int:
    ne = struct.unpack_from('<I', data, 0x3C)[0]
    if data[ne:ne + 2] != b'NE':
        raise SystemExit('not a Win16 NE executable')
    segtab = struct.unpack_from('<H', data, ne + 0x22)[0]
    align = struct.unpack_from('<H', data, ne + 0x32)[0]
    shift = align if align else 0
    off, length, flags, minalloc = struct.unpack_from('<HHHH', data, ne + segtab + 8 * (segnum - 1))
    return off << shift


def main() -> None:
    path = sys.argv[1]
    data = bytearray(open(path, 'rb').read())
    base = seg_file_offset(data, SEG)
    todo = []
    for off, orig, new, desc in PATCHES:
        cur = bytes(data[base + off:base + off + len(orig)])
        if cur == new:
            print(f'  seg{SEG}:0x{off:04x} already patched ({desc})')
        elif cur == orig:
            todo.append((off, orig, new, desc))
        else:
            raise SystemExit(f'{path}: unexpected bytes at file 0x{base+off:x}: {cur.hex()} '
                             f'(expected {orig.hex()} or {new.hex()}) — refusing to patch')
    if not todo:
        print(f'{path}: already fully patched')
        return
    for off, orig, new, desc in todo:
        data[base + off:base + off + len(new)] = new
        print(f'  patched file 0x{base+off:x} (seg{SEG}:0x{off:04x}) {orig.hex()} -> {new.hex()}  # {desc}')
    open(path, 'wb').write(data)
    print(f'{path}: {len(todo)} patch(es) applied')


if __name__ == '__main__':
    main()
