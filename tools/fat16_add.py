#!/usr/bin/env python3
"""在 FAT16 映像根目錄新增一個檔案。

用法: python3 tools/fat16_add.py <img> <host_file> <IMGNAME.EXT>
"""
import struct
import sys

SECTOR = 512


def main():
    img_path, host, name = sys.argv[1], sys.argv[2], sys.argv[3].upper()
    content = open(host, 'rb').read()
    base, ext = (name.split('.') + [''])[:2]
    name83 = base[:8].ljust(8).encode() + ext[:3].ljust(3).encode()

    f = open(img_path, 'r+b')
    f.seek(446 + 8)
    part_start = struct.unpack('<I', f.read(4))[0]
    b = part_start * SECTOR
    f.seek(b)
    bpb = f.read(64)
    spc = bpb[13]
    reserved = struct.unpack_from('<H', bpb, 14)[0]
    nfats = bpb[16]
    root_entries = struct.unpack_from('<H', bpb, 17)[0]
    fat_secs = struct.unpack_from('<H', bpb, 22)[0]
    root_off = (part_start + reserved + nfats * fat_secs) * SECTOR
    data_off = root_off + (root_entries * 32 + SECTOR - 1) // SECTOR * SECTOR
    fat_off = (part_start + reserved) * SECTOR
    fat_size = fat_secs * SECTOR
    f.seek(fat_off)
    fat = bytearray(f.read(fat_size))

    # 找 root dir 空位
    f.seek(root_off)
    root = bytearray(f.read(root_entries * 32))
    slot = None
    for j in range(0, len(root), 32):
        if root[j] in (0x00, 0xE5):
            slot = j
            break
    if slot is None:
        raise RuntimeError('root dir 已滿')

    # 找空叢集
    need = max(1, (len(content) + spc * SECTOR - 1) // (spc * SECTOR))
    free = []
    for c in range(2, len(fat) // 2):
        if struct.unpack_from('<H', fat, c * 2)[0] == 0:
            free.append(c)
            if len(free) == need:
                break
    if len(free) < need:
        raise RuntimeError('空間不足')
    for i, c in enumerate(free):
        nxt = 0xFFFF if i == len(free) - 1 else free[i + 1]
        struct.pack_into('<H', fat, c * 2, nxt)
        off = data_off + (c - 2) * spc * SECTOR
        chunk = content[i * spc * SECTOR:(i + 1) * spc * SECTOR]
        f.seek(off)
        f.write(chunk.ljust(spc * SECTOR, b'\x00'))

    # 寫 FAT 回兩份
    for i in range(nfats):
        f.seek(fat_off + i * fat_size)
        f.write(fat)

    # 寫 dir entry
    e = bytearray(32)
    e[0:11] = name83
    e[11] = 0x20
    struct.pack_into('<H', e, 26, free[0])
    struct.pack_into('<I', e, 28, len(content))
    f.seek(root_off + slot)
    f.write(e)
    f.flush()
    print(f'{name}: {len(content)} bytes, cluster {free[0]}')


if __name__ == '__main__':
    main()
