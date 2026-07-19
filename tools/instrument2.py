#!/usr/bin/env python3
"""Scratch-only v2: additionally instrument painter seg5:0x0000 entry to dump
its caller return address (unconditional, 12 bytes) to stderr."""
import struct, sys

SRC, DST = sys.argv[1], sys.argv[2]
data = bytearray(open(SRC, 'rb').read())
ne = struct.unpack_from('<I', data, 0x3C)[0]
segtab = struct.unpack_from('<H', data, ne + 0x22)[0]
shift = struct.unpack_from('<H', data, ne + 0x32)[0] or 0


def seg_ent(n):
    return ne + segtab + 8 * (n - 1)


def seg_info(n):
    off, ln, fl, ma = struct.unpack_from('<HHHH', data, seg_ent(n))
    return off << shift, ln, fl, ma


def add_reloc(segnum, site, t1, t2):
    f, ln, fl, _ = seg_info(segnum)
    rpos = f + ln
    n = struct.unpack_from('<H', data, rpos)[0]
    data[rpos + 2 + n * 8: rpos + 2 + n * 8 + 8] = struct.pack('<BBHHH', 3, 0, site, t1, t2)
    struct.pack_into('<H', data, rpos, n + 1)


f5, _, _, _ = seg_info(5)
cave_file, _, cave_flags, _ = seg_info(110)
assert cave_flags == 0x0D50  # v1 already applied

# cave2 at seg110:0x40: dump 12 bytes of stack (ret IP/CS of painter's caller + arg)
cave2 = bytes([
    0x60,                    # pusha
    0x1E,                    # push ds
    0x16,                    # push ss
    0x1F,                    # pop ds
    0x89, 0xE2,              # mov dx,sp
    0x83, 0xC2, 0x12,        # add dx,0x12
    0xB9, 0x0C, 0x00,        # mov cx,0x0c
    0xBB, 0x02, 0x00,        # mov bx,2
    0xB4, 0x40,              # mov ah,0x40
    0xCD, 0x21,              # int 0x21
    0x1F,                    # pop ds
    0x61,                    # popa
    0xC8, 0x06, 0x00, 0x00,  # enter 6,0
    0x57,                    # push di
    0x56,                    # push si
    0xEA, 0xFF, 0xFF, 0x00, 0x00,  # jmp far seg5:0x0006 (site=0x60)
])
assert len(cave2) == 0x20
data[cave_file + 0x40:cave_file + 0x40 + len(cave2)] = cave2

# painter entry seg5:0x0000: lcall seg110:0x0040
orig = bytes(data[f5:f5 + 6])
assert orig == bytes.fromhex('c8060000' + '5756'), orig.hex()
data[f5:f5 + 6] = bytes([0x9A, 0x40, 0x00, 0x00, 0x00, 0x90])
add_reloc(5, 0x0001, 110, 0x0040)     # lcall seg110:0x40
add_reloc(110, 0x005C, 5, 0x0006)     # jmp far seg5:0x0006

open(DST, 'wb').write(data)
print(f'{DST}: painter instrumented')
