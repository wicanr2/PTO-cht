#!/usr/bin/env python3
"""產生含 MBR 分割表的 FAT16 磁碟映像（不需 root/mtools）。

用法:
  python3 tools/make_fat16_img.py <out.img> <size_mb> <src_dir> [src_dir2 ...]

會把每個 src_dir 的內容（遞迴、8.3 大寫檔名）放進映像根目錄。
"""
import struct
import sys
from pathlib import Path

SECTOR = 512


def to_83(name: str) -> bytes:
    """轉 8.3 大寫檔名（11 bytes）。"""
    name = name.upper()
    if '.' in name:
        base, ext = name.rsplit('.', 1)
    else:
        base, ext = name, ''
    base = base[:8]
    ext = ext[:3]
    return base.ljust(8).encode('ascii') + ext.ljust(3).encode('ascii')


class Fat16Image:
    def __init__(self, total_mb: int):
        # 幾何：16 heads, 63 sectors/track（對齊 MBR end CHS，type 0x06 CHS 定址需要一致）
        self.heads = 16
        self.spt = 63
        cylinders = (total_mb * 1024 * 1024) // (SECTOR * self.heads * self.spt)
        self.cylinders = cylinders
        self.total_sectors = cylinders * self.heads * self.spt
        self.part_start = 63  # CHS 0/1/1
        self.vol_sectors = self.total_sectors - self.part_start
        # 叢集大小：依容量選（FAT16 叢集數需 < 65525）
        self.spc = 4
        while (self.vol_sectors // self.spc) > 65500:
            self.spc *= 2
        # FAT16 BPB 計算
        self.reserved = 1
        self.nfats = 2
        self.root_entries = 512
        self.root_secs = (self.root_entries * 32 + SECTOR - 1) // SECTOR
        # fat 大小（每 entry 2 bytes，涵蓋所有叢集）
        data_secs = self.vol_sectors - self.reserved - self.root_secs
        while True:
            self.fat_secs = max(1, (data_secs // self.spc + 2) * 2 // SECTOR + 1)
            data_secs = self.vol_sectors - self.reserved - self.nfats * self.fat_secs - self.root_secs
            clusters = data_secs // self.spc
            need = (clusters + 2) * 2
            if need <= self.fat_secs * SECTOR:
                break
            self.fat_secs += 1
        self.clusters = data_secs // self.spc
        self.img = bytearray(self.total_sectors * SECTOR)
        self.fat = bytearray(self.fat_secs * SECTOR)
        # FAT[0] = media descriptor
        struct.pack_into('<H', self.fat, 0, 0xFFF8)
        struct.pack_into('<H', self.fat, 2, 0xFFFF)
        self.next_cluster = 2
        self._write_mbr()
        self._write_boot_sector()

    def _write_mbr(self):
        mbr = self.img
        # partition entry 1: boot flag 0, type 0x06 (FAT16 <32MB? 0x06 是 FAT16B)
        e = 446
        mbr[e + 0] = 0x00
        # start CHS = 0/1/1
        mbr[e + 1] = 0x01
        mbr[e + 2] = 0x01
        mbr[e + 3] = 0x00
        mbr[e + 4] = 0x06  # FAT16
        # end CHS = (cylinders-1)/(heads-1)/63
        mbr[e + 5] = self.heads - 1
        last_sec = self.spt | ((self.cylinders - 1) >> 2 & 0xC0)
        mbr[e + 6] = last_sec
        mbr[e + 7] = (self.cylinders - 1) & 0xFF
        struct.pack_into('<I', mbr, e + 8, self.part_start)
        struct.pack_into('<I', mbr, e + 12, self.vol_sectors)
        mbr[510] = 0x55
        mbr[511] = 0xAA

    def _write_boot_sector(self):
        b = self.part_start * SECTOR
        bs = self.img
        bs[b + 0:b + 3] = b'\xeb\x3c\x90'
        bs[b + 3:b + 11] = b'PTO2IMG '
        struct.pack_into('<H', bs, b + 11, SECTOR)          # bytes/sector
        bs[b + 13] = self.spc                                # sectors/cluster
        struct.pack_into('<H', bs, b + 14, self.reserved)    # reserved
        bs[b + 16] = self.nfats
        struct.pack_into('<H', bs, b + 17, self.root_entries)
        big = self.vol_sectors >= 0x10000
        struct.pack_into('<H', bs, b + 19, 0 if big else self.vol_sectors)
        bs[b + 21] = 0xF8                                    # media
        struct.pack_into('<H', bs, b + 22, self.fat_secs)
        struct.pack_into('<H', bs, b + 24, self.spt)
        struct.pack_into('<H', bs, b + 26, self.heads)
        struct.pack_into('<I', bs, b + 28, self.part_start)  # hidden
        struct.pack_into('<I', bs, b + 32, self.vol_sectors if self.vol_sectors >= 0x10000 else 0)
        bs[b + 36] = 0x80                                    # drive number
        bs[b + 38] = 0x29                                    # extended boot sig
        struct.pack_into('<I', bs, b + 39, 0x50544F32)
        bs[b + 43:b + 54] = b'PTO2       '
        bs[b + 54:b + 62] = b'FAT16   '
        bs[b + 510] = 0x55
        bs[b + 511] = 0xAA

    def _data_off(self, cluster: int) -> int:
        sec = self.part_start + self.reserved + self.nfats * self.fat_secs + self.root_secs \
            + (cluster - 2) * self.spc
        return sec * SECTOR

    def _alloc(self, nclusters: int) -> int:
        start = self.next_cluster
        for i in range(nclusters):
            c = start + i
            val = 0xFFFF if i == nclusters - 1 else c + 1
            struct.pack_into('<H', self.fat, c * 2, val)
        self.next_cluster += nclusters
        return start

    def _flush_fat(self):
        base = (self.part_start + self.reserved) * SECTOR
        for i in range(self.nfats):
            off = base + i * self.fat_secs * SECTOR
            self.img[off:off + len(self.fat)] = self.fat

    def _write_dir_sector(self, entries: list, dir_cluster: int | None):
        """entries: list of (name83, attr, cluster, size)。寫入 root 或子目錄。"""
        data = bytearray()
        for name83, attr, cluster, size in entries:
            e = bytearray(32)
            e[0:11] = name83
            e[11] = attr
            struct.pack_into('<H', e, 26, cluster)
            struct.pack_into('<I', e, 28, size)
            data.extend(e)
        if dir_cluster is None:
            # root dir 固定區
            root_off = (self.part_start + self.reserved + self.nfats * self.fat_secs) * SECTOR
            self.img[root_off:root_off + len(data)] = data
        else:
            off = self._data_off(dir_cluster)
            self.img[off:off + len(data)] = data

    def add_tree(self, src: Path, dst_cluster: int | None, dst_entries: list):
        """遞迴把 src 目錄內容加入 dst_entries（並寫入檔案資料）。"""
        for item in sorted(src.iterdir()):
            name83 = to_83(item.name)
            if item.is_dir():
                # 配置一個叢集給子目錄
                sub_entries = []
                dot = bytearray(32)
                dot[0:11] = b'.          '
                dot[11] = 0x10
                dotdot = bytearray(32)
                dotdot[0:11] = b'..         '
                dotdot[11] = 0x10
                struct.pack_into('<H', dotdot, 26, dst_cluster or 0)
                sub_entries_data = [dot, dotdot]
                sub_cluster = self._alloc(1)
                struct.pack_into('<H', dot, 26, sub_cluster)
                sub_list = []
                self.add_tree(item, sub_cluster, sub_list)
                entries_raw = bytearray()
                for e in sub_entries_data:
                    entries_raw.extend(e)
                for name83b, attr, cl, sz in sub_list:
                    e = bytearray(32)
                    e[0:11] = name83b
                    e[11] = attr
                    struct.pack_into('<H', e, 26, cl)
                    struct.pack_into('<I', e, 28, sz)
                    entries_raw.extend(e)
                off = self._data_off(sub_cluster)
                self.img[off:off + len(entries_raw)] = entries_raw
                dst_entries.append((name83, 0x10, sub_cluster, 0))
            else:
                content = item.read_bytes()
                nclusters = max(1, (len(content) + self.spc * SECTOR - 1) // (self.spc * SECTOR))
                cl = self._alloc(nclusters)
                off = self._data_off(cl)
                self.img[off:off + len(content)] = content
                dst_entries.append((name83, 0x20, cl, len(content)))

    def build(self, src_dirs: list):
        root_entries = []
        for d in src_dirs:
            self.add_tree(Path(d), None, root_entries)
        self._write_dir_sector(root_entries, None)
        self._flush_fat()

    def save(self, path: str):
        with open(path, 'wb') as f:
            f.write(self.img)


def main():
    out, size_mb, srcs = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    img = Fat16Image(size_mb)
    print(f'FAT16: {size_mb}MB, spc={img.spc}, clusters={img.clusters}, fat_secs={img.fat_secs}')
    img.build(srcs)
    img.save(out)
    print(f'寫入 {out}')


if __name__ == '__main__':
    main()
