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

另外整合 **grpseg 預載 patch**（2026-07-19 第五/六輪）：遊戲在 Wine 下
開頭狀態機分歧，painter（seg5:0x0000 族）會在 grpseg loader 執行前
以 NULL huge-ptr 崩潰（seg5:0x5b9f）。此 patch 在 huge-ptr helper
（seg5:0x5b72）入口注入 cave：ds:0x8098==0 時先呼叫 grpseg loader
（seg11:0x2154），並把 ds:[0x8096]/[0x8098] 回填呼叫者堆疊上的
index 參數槽。cave 放在 seg110（錯誤字串 data seg 翻成 code seg，
其字串路徑已被上面的檢查 patch nop 掉）。
**目前狀態**：第一層 NULL crash 已修；第二層 crash（無效 selector
0x0497，涉及 grpseg2/readseg 0x76f/0x787）仍待查，見 docs/REVERSE.md。
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

# --- grpseg 預載 cave（seg110:0x0000，0x2f bytes） ---
CAVE_SEG = 110
CAVE_OFF = 0x0000
CAVE = bytes([
    0x60,                                      # 00 pusha
    0x1E,                                      # 01 push ds
    0x80, 0x3E, 0x98, 0x80, 0x00,              # 02 cmp byte [0x8098],0
    0x75, 0x05,                                # 07 jne 0x0e
    0x9A, 0xFF, 0xFF, 0x00, 0x00,              # 09 lcall seg11:0x2154  (reloc site 0x0a)
    0x8B, 0x44, 0x20,                          # 0e mov ax,[sp+0x20]   (stacked index seg)
    0x85, 0xC0,                                # 11 test ax,ax
    0x75, 0x0D,                                # 13 jne 0x22
    0xA1, 0x96, 0x80,                          # 15 mov ax,[0x8096]
    0x89, 0x44, 0x1E,                          # 18 mov [sp+0x1e],ax   (stacked index off)
    0x8B, 0x16, 0x98, 0x80,                    # 1b mov dx,[0x8098]
    0x89, 0x54, 0x20,                          # 1f mov [sp+0x20],dx
    0x1F,                                      # 22 pop ds
    0x61,                                      # 23 popa
    0xC8, 0x06, 0x00, 0x00,                    # 24 enter 6,0
    0x57,                                      # 28 push di
    0x56,                                      # 29 push si
    0xEA, 0xFF, 0xFF, 0x00, 0x00,              # 2a jmp far seg5:0x5b78 (reloc site 0x2b)
])
HELPER_SEG, HELPER_OFF = 5, 0x5B72
HELPER_ORIG = bytes.fromhex('c80600005756')
HELPER_NEW = bytes([0x9A, 0xFF, 0xFF, 0x00, 0x00, 0x90])
# (segnum, reloc site, target seg, target off)
NEW_RELOCS = [
    (5, 0x5B73, 110, 0x0000),   # helper entry lcall -> cave
    (110, 0x000A, 11, 0x2154),  # cave -> grpseg loader
    (110, 0x002B, 5, 0x5B78),   # cave -> back to helper body
]


def seg_ent(data: bytes, segnum: int) -> int:
    ne = struct.unpack_from('<I', data, 0x3C)[0]
    segtab = struct.unpack_from('<H', data, ne + 0x22)[0]
    return ne + segtab + 8 * (segnum - 1)


def seg_info(data: bytes, segnum: int):
    ne = struct.unpack_from('<I', data, 0x3C)[0]
    align = struct.unpack_from('<H', data, ne + 0x32)[0]
    shift = align if align else 0
    off, length, flags, minalloc = struct.unpack_from('<HHHH', data, seg_ent(data, segnum))
    return off << shift, length, flags, minalloc


def seg_file_offset(data: bytes, segnum: int) -> int:
    ne = struct.unpack_from('<I', data, 0x3C)[0]
    if data[ne:ne + 2] != b'NE':
        raise SystemExit('not a Win16 NE executable')
    return seg_info(data, segnum)[0]


def add_reloc(data: bytearray, segnum: int, site: int, t1: int, t2: int) -> None:
    f, ln, fl, _ = seg_info(data, segnum)
    rpos = f + ln
    n = struct.unpack_from('<H', data, rpos)[0]
    data[rpos + 2 + n * 8: rpos + 2 + n * 8 + 8] = struct.pack('<BBHHH', 3, 0, site, t1, t2)
    struct.pack_into('<H', data, rpos, n + 1)


def apply_grpseg_patch(data: bytearray, path: str) -> None:
    f5 = seg_file_offset(data, HELPER_SEG)
    cf, _, cflags, _ = seg_info(data, CAVE_SEG)
    cur = bytes(data[f5 + HELPER_OFF:f5 + HELPER_OFF + 6])
    if cur == HELPER_NEW:
        print(f'  seg{HELPER_SEG}:0x{HELPER_OFF:04x} grpseg preload already patched')
        return
    if cur != HELPER_ORIG:
        raise SystemExit(f'{path}: unexpected bytes at helper entry: {cur.hex()} — refusing')
    if cflags == 0xC51:
        struct.pack_into('<H', data, seg_ent(data, CAVE_SEG) + 4, 0x0D50)
    elif cflags != 0x0D50:
        raise SystemExit(f'{path}: seg{CAVE_SEG} flags {cflags:#x} — refusing')
    data[cf + CAVE_OFF:cf + CAVE_OFF + len(CAVE)] = CAVE
    data[f5 + HELPER_OFF:f5 + HELPER_OFF + 6] = HELPER_NEW
    for sn, site, t1, t2 in NEW_RELOCS:
        add_reloc(data, sn, site, t1, t2)
    print(f'  patched seg{HELPER_SEG}:0x{HELPER_OFF:04x} -> cave seg{CAVE_SEG}:0x{CAVE_OFF:04x} '
          f'(grpseg preload, +{len(NEW_RELOCS)} relocs)')


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
    for off, orig, new, desc in todo:
        data[base + off:base + off + len(new)] = new
        print(f'  patched file 0x{base+off:x} (seg{SEG}:0x{off:04x}) {orig.hex()} -> {new.hex()}  # {desc}')
    apply_grpseg_patch(data, path)
    open(path, 'wb').write(data)
    print(f'{path}: done')


if __name__ == '__main__':
    main()
