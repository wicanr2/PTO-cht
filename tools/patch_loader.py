#!/usr/bin/env python3
"""Scratch experiment: patch helper seg5:0x5b72 entry to lazily call the
grpseg loader seg11:0x2154 when ds:0x8098 (grpseg ptr seg) is still 0.

cave at seg110:0x60 (inside the nop'd 640x480 error string):
  60: 60              pusha
  61: 80 3e 98 80 00  cmp byte [0x8098],0
  66: 75 05           jne 0x6d
  68: 9a .. ..        lcall seg11:0x2154   (reloc site 0x69)
  6d: 61              popa
  6e: c8 06 00 00     enter 6,0
  72: 57              push di
  73: 56              push si
  74: ea .. ..        jmp far seg5:0x5b78  (reloc site 0x75)
helper entry 0x5b72: 9a .. .. .. .. 90  lcall seg110:0x60 (reloc site 0x5b73)
"""
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

# flip seg110 to code
if cave_flags == 0xC51:
    struct.pack_into('<H', data, seg_ent(110) + 4, 0x0D50)
elif cave_flags != 0x0D50:
    raise SystemExit(f'seg110 flags {cave_flags:#x}')

cave = bytes([0x60, 0x80, 0x3E, 0x98, 0x80, 0x00, 0x75, 0x05,
              0x9A, 0xFF, 0xFF, 0x00, 0x00,
              0x61, 0xC8, 0x06, 0x00, 0x00, 0x57, 0x56,
              0xEA, 0xFF, 0xFF, 0x00, 0x00])
assert len(cave) == 0x19
data[cave_file + 0x60:cave_file + 0x60 + len(cave)] = cave

orig = bytes(data[f5 + 0x5B72:f5 + 0x5B78])
assert orig == bytes.fromhex('c80600005756'), orig.hex()
data[f5 + 0x5B72:f5 + 0x5B78] = bytes([0x9A, 0xFF, 0xFF, 0x00, 0x00, 0x90])

add_reloc(5, 0x5B73, 110, 0x0060)
add_reloc(110, 0x0069, 11, 0x2154)
add_reloc(110, 0x0075, 5, 0x5B78)

open(DST, 'wb').write(data)
print(f'{DST}: lazy grpseg loader patch applied')
