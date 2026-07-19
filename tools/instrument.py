#!/usr/bin/env python3
"""Scratch-only: instrument TEKE2WIN.EXE helper seg5:0x5b72 to dump caller
return address + args to stderr (int 21h AH=40, bx=2) when the huge-pointer
segment arg == 0 (the seg5:0x5b9f NULL-deref crash).

Method:
- flip seg110 (error-string data seg, only used by already-nop'd check paths)
  into a code segment (flags 0xc51 -> 0xd50) and put a ~0x33-byte cave at its start
- helper entry seg5:0x5b72 -> lcall seg110:0x0000 (new reloc in seg5)
- cave: pusha/push ds; if [sp+0x24] (ptr seg arg) == 0: write 0x14 stack bytes
  (lcall-ret, caller ret IP/CS, args) to stderr; popa; run original prologue;
  jmp far seg5:0x5b78 (new reloc in seg110)
"""
import struct, sys

SRC = sys.argv[1]
DST = sys.argv[2]

data = bytearray(open(SRC, 'rb').read())
ne = struct.unpack_from('<I', data, 0x3C)[0]
segtab = struct.unpack_from('<H', data, ne + 0x22)[0]
shift = struct.unpack_from('<H', data, ne + 0x32)[0] or 0


def seg_ent(n):
    return ne + segtab + 8 * (n - 1)


def seg_info(n):
    off, ln, fl, ma = struct.unpack_from('<HHHH', data, seg_ent(n))
    return off << shift, ln, fl, ma

# --- 1. flip seg110 to code (flags 0xc51 -> 0xd50) ---
f5_file, f5_len, f5_flags, _ = seg_info(5)
cave_file, cave_len, cave_flags, _ = seg_info(110)
assert cave_flags == 0xC51, hex(cave_flags)
struct.pack_into('<H', data, seg_ent(110) + 4, 0x0D50)

# --- 2. cave code at seg110:0x0000 ---
cave = bytes([
    0x60,                    # pusha
    0x1E,                    # push ds
    0x8B, 0x44, 0x24,        # mov ax,[sp+0x24]  (ptr seg arg)
    0x85, 0xC0,              # test ax,ax
    0x75, 0x1D,              # jnz 0x26
    0x16,                    # push ss
    0x1F,                    # pop ds
    0x89, 0xE2,              # mov dx,sp
    0x83, 0xC2, 0x12,        # add dx,0x12
    0xB9, 0x14, 0x00,        # mov cx,0x14
    0xBB, 0x02, 0x00,        # mov bx,2
    0xB4, 0x40,              # mov ah,0x40
    0xCD, 0x21,              # int 0x21
] + [0x90] * 12 + [          # pad to 0x26
    0x1F,                    # pop ds
    0x61,                    # popa
    0xC8, 0x06, 0x00, 0x00,  # enter 6,0
    0x57,                    # push di
    0x56,                    # push si
    0xEA, 0xFF, 0xFF, 0x00, 0x00,  # jmp far 0x5b78 (off patched by reloc, site=0x2f)
])
assert len(cave) == 0x33
data[cave_file:cave_file + len(cave)] = cave

# --- 3. helper entry: lcall seg110:0x0000 ---
orig = bytes(data[f5_file + 0x5B72:f5_file + 0x5B78])
assert orig == bytes.fromhex('c8060000 5756'.replace(' ', '')), orig.hex()
data[f5_file + 0x5B72:f5_file + 0x5B78] = bytes([0x9A, 0xFF, 0xFF, 0x00, 0x00, 0x90])

# --- 4. append reloc entries ---
def add_reloc(segnum, site, t1, t2):
    f, ln, fl, _ = seg_info(segnum)
    rpos = f + ln
    n = struct.unpack_from('<H', data, rpos)[0]
    entry = struct.pack('<BBHHH', 3, 0, site, t1, t2)  # PTR32, INTERNAL
    data[rpos + 2 + n * 8: rpos + 2 + n * 8 + 8] = entry
    struct.pack_into('<H', data, rpos, n + 1)

add_reloc(5, 0x5B73, 110, 0x0000)      # lcall seg110:0
add_reloc(110, 0x002F, 5, 0x5B78)      # jmp far seg5:0x5b78

open(DST, 'wb').write(data)
print(f'{DST}: instrumented (cave at seg110:0, helper entry lcall)')
