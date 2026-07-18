#!/usr/bin/env python3
"""解析 Win16 NE 執行檔的 segment relocation table，還原 far call 目標。

用法：python3 tools/ne_relocs.py <exe> [segnum]
會列出每個 segment 的 relocation entries（含解析後的目標位址）。
"""
import struct
import sys

RADDR = {0: 'LOBYTE', 2: 'SELECTOR', 3: 'PTR32', 5: 'OFF16', 11: 'PTR48', 13: 'OFF32'}
RTYPE = {0: 'INTERNAL', 1: 'ORDINAL', 2: 'NAME', 3: 'OSFIXUP'}


def parse(data: bytes):
    ne = struct.unpack_from('<I', data, 0x3c)[0]
    hdr = {
        'ne': ne,
        'cseg': struct.unpack_from('<H', data, ne + 0x1C)[0],
        'cmod': struct.unpack_from('<H', data, ne + 0x1E)[0],
        'segtab': struct.unpack_from('<H', data, ne + 0x22)[0],
        'modtab': struct.unpack_from('<H', data, ne + 0x28)[0],
        'imptab': struct.unpack_from('<H', data, ne + 0x2A)[0],
        'align': struct.unpack_from('<H', data, ne + 0x32)[0],
    }
    hdr['shift'] = hdr['align'] if hdr['align'] else 0
    return hdr


def segments(data, hdr):
    segs = []
    for i in range(hdr['cseg']):
        off, length, flags, minalloc = struct.unpack_from('<HHHH', data, hdr['ne'] + hdr['segtab'] + 8 * i)
        segs.append({'num': i + 1, 'file': off << hdr['shift'], 'len': length, 'flags': flags})
    return segs


def module_names(data, hdr):
    names = []
    for j in range(hdr['cmod']):
        o = struct.unpack_from('<H', data, hdr['ne'] + hdr['modtab'] + 2 * j)[0]
        l = data[hdr['ne'] + hdr['imptab'] + o]
        names.append(data[hdr['ne'] + hdr['imptab'] + o + 1:hdr['ne'] + hdr['imptab'] + o + 1 + l].decode('ascii', 'replace'))
    return names


def relocs_for_segment(data, hdr, seg):
    """回傳該 segment 的 relocation entries（flags 有 RELOC_DATA 才有）。"""
    if not (seg['flags'] & 0x0100):
        return []
    pos = seg['file'] + (seg['len'] if seg['len'] else 0)
    count = struct.unpack_from('<H', data, pos)[0]
    pos += 2
    out = []
    for i in range(count):
        addr_type, rtype, offset, t1, t2 = struct.unpack_from('<BBHHH', data, pos)
        pos += 8
        out.append({'addr_type': addr_type & 0x7f, 'rtype': rtype & 3,
                    'additive': bool(rtype & 4), 'offset': offset, 't1': t1, 't2': t2})
    return out


def resolve(r, names):
    mod = ''
    if r['rtype'] in (1, 2) and 1 <= r['t1'] <= len(names):
        mod = names[r['t1'] - 1]
    if r['rtype'] == 0:
        if (r['t1'] & 0xff) == 0xff:
            return f'self.entry#{r["t2"]}'
        return f'seg{r["t1"] & 0xff}:0x{r["t2"]:04x}'
    if r['rtype'] == 1:
        return f'{mod}.#{r["t2"]}'
    if r['rtype'] == 2:
        return f'{mod}.[name@{r["t2"]:04x}]'
    return f'osfixup t1={r["t1"]} t2={r["t2"]}'


def walk_chain(data, seg, start):
    """走訪 non-additive 修復鏈，回傳所有 site offsets。"""
    sites = []
    off = start
    size = seg['len'] if seg['len'] else 0x10000
    while off not in (0xffff,) and off < size:
        sites.append(off)
        nxt = struct.unpack_from('<H', data, seg['file'] + off)[0]
        if nxt == off:
            break
        off = nxt
    return sites


def main():
    path = sys.argv[1]
    only_seg = int(sys.argv[2]) if len(sys.argv) > 2 else None
    data = open(path, 'rb').read()
    hdr = parse(data)
    segs = segments(data, hdr)
    names = module_names(data, hdr)
    print(f'{path}: {len(segs)} segments, modules: {names}')
    for seg in segs:
        if only_seg and seg['num'] != only_seg:
            continue
        relocs = relocs_for_segment(data, hdr, seg)
        if not relocs:
            continue
        print(f'== segment {seg["num"]} (file {hex(seg["file"])} len {hex(seg["len"])}): {len(relocs)} relocs')
        for r in relocs:
            at = RADDR.get(r['addr_type'], hex(r['addr_type']))
            tgt = resolve(r, names)
            sites = '' if r['additive'] else f' sites={walk_chain(data, seg, r["offset"])[:20]}'
            print(f'  off=0x{r["offset"]:04x} {at:8s} {tgt}{sites}')


if __name__ == '__main__':
    main()
