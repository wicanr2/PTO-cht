#!/usr/bin/env python3
"""Scratch debug: combined cave at seg110:0x00 — lazy-call grpseg loader
(seg11:0x2154) when ds:0x8098==0 AND always dump helper args (16 bytes)
to stderr, then run original helper prologue."""
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
if cave_flags == 0xC51:
    struct.pack_into('<H', data, seg_ent(110) + 4, 0x0D50)

cave = bytes([
    0x60,                          # pusha
    0x1E,                          # push ds
    0x80, 0x3E, 0x98, 0x80, 0x00,  # cmp byte [0x8098],0
    0x75, 0x05,                    # jne 0x0e
    0x9A, 0xFF, 0xFF, 0x00, 0x00,  # lcall seg11:0x2154 (site 0x0a)
    0x16,                          # push ss
    0x1F,                          # pop ds
    0x89, 0xE2,                    # mov dx,sp
    0x83, 0xC2, 0x14,              # add dx,0x14
    0xB9, 0x10, 0x00,              # mov cx,0x10
    0xBB, 0x02, 0x00,              # mov bx,2
    0xB4, 0x40,                    # mov ah,0x40
    0xCD, 0x21,                    # int 0x21
    0x1F,                          # pop ds
    0x61,                          # popa
    0xC8, 0x06, 0x00, 0x00,        # enter 6,0
    0x57,                          # push di
    0x56,                          # push si
    0xEA, 0xFF, 0xFF, 0x00, 0x00,  # jmp far seg5:0x5b78 (site 0x28)
])
assert len(cave) == 0x2C
data[cave_file:cave_file + len(cave)] = cave

orig = bytes(data[f5 + 0x5B72:f5 + 0x5B78])
assert orig == bytes.fromhex('c80600005756'), orig.hex()
data[f5 + 0x5B72:f5 + 0x5B78] = bytes([0x9A, 0xFF, 0xFF, 0x00, 0x00, 0x90])

add_reloc(5, 0x5B73, 110, 0x0000)
add_reloc(110, 0x000A, 11, 0x2154)
add_reloc(110, 0x0028, 5, 0x5B78)
open(DST, 'wb').write(data)
print(f'{DST}: combined loader+dump patch applied')
