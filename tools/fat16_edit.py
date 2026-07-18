#!/usr/bin/env python3
"""在 FAT16 映像內直接取代檔案內容（不重建映像）。

用法: python3 tools/fat16_edit.py <img> <path> <new_content_file>
path 形如 WINDOWS/SYSTEM.INI（大小寫不拘、8.3）。
新內容叢集數不可超過原檔案叢集數（變短會更新 dir entry size）。
"""
import struct
import sys

SECTOR = 512


class Fat16:
    def __init__(self, path):
        self.f = open(path, 'r+b')
        self.img = self.f
        self.img.seek(446 + 8)
        self.part_start = struct.unpack('<I', self.img.read(4))[0]
        b = self.part_start * SECTOR
        self.img.seek(b)
        bpb = self.img.read(64)
        self.spc = bpb[13]
        self.reserved = struct.unpack_from('<H', bpb, 14)[0]
        self.nfats = bpb[16]
        self.root_entries = struct.unpack_from('<H', bpb, 17)[0]
        self.fat_secs = struct.unpack_from('<H', bpb, 22)[0]
        self.root_secs = (self.root_entries * 32 + SECTOR - 1) // SECTOR
        self.fat_off = (self.part_start + self.reserved) * SECTOR
        self.root_off = (self.part_start + self.reserved + self.nfats * self.fat_secs) * SECTOR
        self.data_off = self.root_off + self.root_secs * SECTOR
        self.fat = bytearray(self.fat_secs * SECTOR)
        self.img.seek(self.fat_off)
        self.fat[:] = self.img.read(len(self.fat))

    def clus_off(self, c):
        return self.data_off + (c - 2) * self.spc * SECTOR

    def chain(self, start):
        out = []
        c = start
        while 2 <= c < 0xFFF8 and len(out) < 65535:
            out.append(c)
            c = struct.unpack_from('<H', self.fat, c * 2)[0]
        return out

    def read_dir(self, cluster):
        if cluster == 0:
            self.img.seek(self.root_off)
            return self.img.read(self.root_entries * 32), self.root_off
        out = bytearray()
        for c in self.chain(cluster):
            self.img.seek(self.clus_off(c))
            out.extend(self.img.read(self.spc * SECTOR))
        return bytes(out), self.clus_off(cluster)

    def find(self, path):
        parts = path.upper().split('/')
        cluster = 0
        for i, part in enumerate(parts):
            base, ext = (part.split('.') + [''])[:2]
            name83 = base[:8].ljust(8).encode() + ext[:3].ljust(3).encode()
            found_off = None
            cl = None
            if cluster == 0:
                data, off0 = self.read_dir(0)
                for j in range(0, len(data), 32):
                    if data[j:j+11] == name83:
                        found_off = off0 + j
                        cl = struct.unpack_from('<H', data, j + 26)[0]
                        break
            else:
                for c in self.chain(cluster):
                    self.img.seek(self.clus_off(c))
                    data = self.img.read(self.spc * SECTOR)
                    for j in range(0, len(data), 32):
                        if data[j:j+11] == name83:
                            found_off = self.clus_off(c) + j
                            cl = struct.unpack_from('<H', data, j + 26)[0]
                            break
                    if found_off is not None:
                        break
            if found_off is None:
                raise FileNotFoundError(part)
            self.img.seek(found_off)
            e = self.img.read(32)
            size = struct.unpack_from('<I', e, 28)[0]
            if i == len(parts) - 1:
                return cl, size, found_off
            cluster = cl
        raise FileNotFoundError(path)

    def read_file(self, cluster, size):
        out = bytearray()
        for c in self.chain(cluster):
            self.img.seek(self.clus_off(c))
            out.extend(self.img.read(self.spc * SECTOR))
        return bytes(out[:size])

    def write_file(self, cluster, content, dir_off):
        nclus = len(self.chain(cluster))
        cap = nclus * self.spc * SECTOR
        if len(content) > cap:
            raise ValueError(f'新內容 {len(content)} > 原容量 {cap}')
        for i, c in enumerate(self.chain(cluster)):
            chunk = content[i * self.spc * SECTOR:(i + 1) * self.spc * SECTOR]
            if not chunk:
                break
            chunk = chunk.ljust(self.spc * SECTOR, b'\x00')
            self.img.seek(self.clus_off(c))
            self.img.write(chunk)
        self.img.seek(dir_off + 28)
        self.img.write(struct.pack('<I', len(content)))
        self.img.flush()


def main():
    img, path, newf = sys.argv[1], sys.argv[2], sys.argv[3]
    content = open(newf, 'rb').read()
    fs = Fat16(img)
    cl, size, dir_off = fs.find(path)
    old = fs.read_file(cl, size)
    print(f'{path}: {size} bytes -> {len(content)} bytes')
    fs.write_file(cl, content, dir_off)
    print('完成')


if __name__ == '__main__':
    main()
