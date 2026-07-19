#!/usr/bin/env python3
"""Win16 NE 完整反組譯地圖產生器（TEKE2WIN.EXE 用，但通用）。

功能：
  - 完整解析 NE header：segment table、entry table、module-ref / imported-names、
    relocation（含 non-additive 修復鏈與 additive 加值）
  - 以 capstone (CS_MODE_16) 對全部 code segment 做線性反組譯
  - 函數邊界偵測：entry table、far/near call 目標、`push bp; mov bp,sp` / `enter` prologue
  - 以 SELECTOR/PTR32 relocation 解析 `9a` far call 目標，產生跨段 call graph
  - import ordinal → 名稱：優先解析 vendor/wine-src 的 .spec 檔，否則用內建小表

用法：
  python3 tools/ne_disasm.py <exe> [--out docs/disasm] [--wine-src vendor/wine-src/wine-9.0]
  python3 tools/ne_disasm.py <exe> --func 11:50c6        # 印出函數反組譯摘錄
  python3 tools/ne_disasm.py <exe> --list-imports        # 只印 import 清單到 stdout

seg:off 與 file offset 換算：file = seg.file_offset + off（segment table offset << shift）。
"""
import argparse
import csv
import os
import re
import struct
import sys
from collections import defaultdict

from capstone import Cs, CS_ARCH_X86, CS_MODE_16

RADDR = {0: 'LOBYTE', 2: 'SELECTOR', 3: 'PTR32', 5: 'OFF16', 11: 'PTR48', 13: 'OFF32'}
RTYPE = {0: 'INTERNAL', 1: 'ORDINAL', 2: 'NAME', 3: 'OSFIXUP'}

# 內建 fallback ordinal 表（僅在找不到 wine .spec 時使用）
FALLBACK_ORDS = {
    'GDI': {2: 'SetBkMode', 3: 'SetMapMode', 9: 'SetTextColor', 29: 'PatBlt',
            33: 'TextOut', 34: 'BitBlt', 45: 'SelectObject', 52: 'CreateCompatibleDC',
            56: 'CreateFont', 68: 'DeleteDC', 69: 'DeleteObject', 80: 'GetDeviceCaps',
            92: 'GetTextFace', 93: 'GetTextMetrics', 360: 'CreatePalette',
            363: 'GetPaletteEntries', 367: 'AnimatePalette',
            375: 'GetSystemPaletteEntries', 441: 'GetDIBits', 442: 'CreateDIBitmap'},
    'WING': {1001: 'WinGCreateDC', 1002: 'WinGRecommendDIBFormat',
             1003: 'WinGCreateBitmap', 1004: 'WinGGetDIBPointer',
             1005: 'WinGGetDIBColorTable', 1006: 'WinGSetDIBColorTable',
             1007: 'WinGCreateHalfTonePalette', 1008: 'WinGCreateHalfToneBrush',
             1009: 'WinGStretchBlt', 1010: 'WinGBitBlt'},
}

# wine-9.0 spec 檔對應（module name -> spec 相對路徑）
SPEC_MAP = {
    'KERNEL': 'dlls/krnl386.exe16/krnl386.exe16.spec',
    'USER': 'dlls/user.exe16/user.exe16.spec',
    'GDI': 'dlls/gdi.exe16/gdi.exe16.spec',
    'MMSYSTEM': 'dlls/mmsystem.dll16/mmsystem.dll16.spec',
    'TOOLHELP': 'dlls/toolhelp.dll16/toolhelp.dll16.spec',
    'WING': 'dlls/wing.dll16/wing.dll16.spec',
}

PROG_ENTRY_HINTS = {'CRT_START': (11, 0x4949)}  # 已知：CRT startup


# ---------------------------------------------------------------- NE parsing

class NE:
    def __init__(self, path):
        self.path = path
        self.data = open(path, 'rb').read()
        d = self.data
        ne = struct.unpack_from('<I', d, 0x3c)[0]
        self.ne = ne
        self.entrytab_off = struct.unpack_from('<H', d, ne + 0x04)[0]
        self.cseg = struct.unpack_from('<H', d, ne + 0x1C)[0]
        self.cmod = struct.unpack_from('<H', d, ne + 0x1E)[0]
        self.segtab = struct.unpack_from('<H', d, ne + 0x22)[0]
        self.resrctab = struct.unpack_from('<H', d, ne + 0x24)[0]
        self.resnames = struct.unpack_from('<H', d, ne + 0x26)[0]
        self.modtab = struct.unpack_from('<H', d, ne + 0x28)[0]
        self.imptab = struct.unpack_from('<H', d, ne + 0x2A)[0]
        self.nonres_off = struct.unpack_from('<I', d, ne + 0x2C)[0]
        self.shift = struct.unpack_from('<H', d, ne + 0x32)[0]
        self.flags = struct.unpack_from('<H', d, ne + 0x0C)[0]
        self.start_ip, self.start_seg = struct.unpack_from('<HH', d, ne + 0x14)
        self.segments = []
        for i in range(self.cseg):
            off, length, flags, minalloc = struct.unpack_from('<HHHH', d, ne + self.segtab + 8 * i)
            self.segments.append({
                'num': i + 1,
                'file': off << self.shift,
                'len': length if length else 0x10000,
                'alloc': minalloc if minalloc else 0x10000,
                'flags': flags,
                'is_code': not (flags & 0x0001),
            })
        self.modules = []
        for j in range(self.cmod):
            o = struct.unpack_from('<H', d, ne + self.modtab + 2 * j)[0]
            ln = d[ne + self.imptab + o]
            self.modules.append(d[ne + self.imptab + o + 1: ne + self.imptab + o + 1 + ln]
                                .decode('ascii', 'replace'))
        self.entries = self._parse_entry_table()
        self.relocs = {}      # segnum -> list of reloc dicts (sites 已展開)
        self.site_map = {}    # (segnum, site_off) -> resolved target dict
        self._parse_all_relocs()

    def seg(self, num):
        return self.segments[num - 1]

    def seg_bytes(self, num):
        s = self.seg(num)
        if s['len'] == 0x10000 and s['file'] == 0:  # 無檔案內容的 bss 段
            return b''
        return self.data[s['file']: s['file'] + min(s['len'], len(self.data) - s['file'])]

    def file_off(self, segnum, off):
        return self.seg(segnum)['file'] + off

    def _parse_entry_table(self):
        d = self.data
        pos = self.ne + self.entrytab_off
        entries = []
        while True:
            cnt = d[pos]
            typ = d[pos + 1]
            pos += 2
            if cnt == 0:
                break
            for _ in range(cnt):
                if typ == 0xFF:  # movable
                    fl = d[pos]
                    seg = d[pos + 3]
                    off = struct.unpack_from('<H', d, pos + 4)[0]
                    pos += 6
                    entries.append({'seg': seg, 'off': off, 'flags': fl, 'movable': True})
                elif typ == 0:    # unused bundle
                    pass
                else:             # fixed segment
                    fl = d[pos]
                    off = struct.unpack_from('<H', d, pos + 1)[0]
                    pos += 3
                    entries.append({'seg': typ, 'off': off, 'flags': fl, 'movable': False})
        return entries

    def import_name(self, t2):
        d = self.data
        ln = d[self.ne + self.imptab + t2]
        return d[self.ne + self.imptab + t2 + 1: self.ne + self.imptab + t2 + 1 + ln] \
            .decode('ascii', 'replace')

    def _raw_relocs(self, seg):
        if not (seg['flags'] & 0x0100):
            return []
        pos = seg['file'] + (seg['len'] if seg['len'] != 0x10000 or seg['file'] else 0)
        count = struct.unpack_from('<H', self.data, pos)[0]
        pos += 2
        out = []
        for _ in range(count):
            at, rt, off, t1, t2 = struct.unpack_from('<BBHHH', self.data, pos)
            pos += 8
            out.append({'addr_type': at & 0x7F, 'rtype': rt & 3,
                        'additive': bool(rt & 4), 'offset': off, 't1': t1, 't2': t2})
        return out

    def _walk_chain(self, seg, start):
        """non-additive 修復鏈：low word 存下一個 site。"""
        sites = []
        size = seg['len']
        off = start
        seen = set()
        while off != 0xFFFF and off < size and off not in seen:
            seen.add(off)
            sites.append(off)
            nxt = struct.unpack_from('<H', self.data, seg['file'] + off)[0]
            if nxt == off:
                break
            off = nxt
        return sites

    def resolve_target(self, r):
        """回傳 dict：{'kind': 'internal'|'import'|'self_entry'|'osfixup', ...}"""
        if r['rtype'] == 0:
            if (r['t1'] & 0xFF) == 0xFF:
                e = self.entries[r['t2']] if r['t2'] < len(self.entries) else None
                if e:
                    return {'kind': 'internal', 'seg': e['seg'], 'off': e['off'],
                            'via_entry': r['t2']}
                return {'kind': 'self_entry', 'entry': r['t2']}
            return {'kind': 'internal', 'seg': r['t1'] & 0xFF, 'off': r['t2']}
        if r['rtype'] in (1, 2):
            mod = self.modules[r['t1'] - 1] if 1 <= r['t1'] <= len(self.modules) else f'#{r["t1"]}'
            if r['rtype'] == 1:
                return {'kind': 'import', 'module': mod, 'ordinal': r['t2']}
            return {'kind': 'import', 'module': mod, 'name': self.import_name(r['t2'])}
        return {'kind': 'osfixup', 't1': r['t1'], 't2': r['t2']}

    def _parse_all_relocs(self):
        for seg in self.segments:
            rels = []
            for r in self._raw_relocs(seg):
                tgt = self.resolve_target(r)
                if r['additive']:
                    sites = [r['offset']]
                elif r['addr_type'] in (3, 11):  # PTR32/PTR48：鏈在 low word
                    sites = self._walk_chain(seg, r['offset'])
                else:                            # SELECTOR/OFF16：鏈在 word
                    sites = self._walk_chain(seg, r['offset'])
                r2 = dict(r)
                r2['target'] = tgt
                r2['sites'] = sites
                rels.append(r2)
                for s in sites:
                    addend = 0
                    if r['additive'] and s + 4 <= seg['len']:
                        addend = struct.unpack_from('<I', self.data, seg['file'] + s)[0]
                    st = dict(tgt)
                    st['addr_type'] = r['addr_type']
                    st['addend'] = addend
                    if st.get('kind') == 'internal':
                        st['off'] = (st['off'] + (addend & 0xFFFF)) & 0xFFFF
                    self.site_map[(seg['num'], s)] = st
            self.relocs[seg['num']] = rels


# --------------------------------------------------------- ordinal name tables

def parse_spec(path):
    """解析 wine .spec：回傳 ordinal -> name。"""
    ords = {}
    if not os.path.exists(path):
        return ords
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.strip()
        m = re.match(r'^(\d+)\s+(pascal|cdecl|stdcall|varargs|register|interrupt|equate)\b', line)
        if not m:
            continue
        rest = line[m.end():].split('#')[0].split()
        for tok in rest:
            if tok.startswith('-'):
                continue
            name = tok.split('(')[0]
            if name:
                ords[int(m.group(1))] = name
            break
    return ords


def load_ord_tables(wine_src):
    tables = {m: dict(v) for m, v in FALLBACK_ORDS.items()}
    for mod, rel in SPEC_MAP.items():
        p = os.path.join(wine_src, rel) if wine_src else ''
        ords = parse_spec(p)
        if ords:
            tables.setdefault(mod, {}).update(ords)
    return tables


def import_label(tgt, ord_tables):
    mod = tgt.get('module', '?')
    if 'name' in tgt:
        return f'{mod}.{tgt["name"]}'
    o = tgt.get('ordinal')
    nm = ord_tables.get(mod, {}).get(o)
    return f'{mod}.{nm}' if nm else f'{mod}.#{o}'


# ------------------------------------------------------------- disassembly

def lcall_anchors(ne, segnum):
    """從 reloc sites 推出每個 `9a` lcall 指令的位址（這些是可信的指令邊界）。"""
    code = ne.seg_bytes(segnum)
    out = set()
    for (sg, site), tgt in ne.site_map.items():
        if sg != segnum:
            continue
        if tgt.get('addr_type') in (3, 11) and site >= 1 and code[site - 1] == 0x9A:
            out.add(site - 1)
        elif tgt.get('addr_type') == 2 and site >= 3 and code[site - 3] == 0x9A:
            out.add(site - 3)
    return out


def disassemble_segment(ne, segnum, anchors=()):
    """anchor-guided linear sweep：先從 0 掃，再從每個 anchor（函數入口、
    lcall site 等可信邊界）重啟，修復 jump table / 內嵌資料造成的 desync。"""
    code = ne.seg_bytes(segnum)
    md = Cs(CS_ARCH_X86, CS_MODE_16)
    md.detail = False
    insns = {}
    starts = [0] + sorted(a for a in anchors if 0 < a < len(code))
    for st in starts:
        if st in insns:
            continue
        for i in md.disasm(code[st:], st):
            a, e = i.address, i.address + i.size
            if a in insns:
                break
            # 刪掉與本指令重疊的舊（desync 殘留）指令；只查 15-byte 窗口（x86 指令最長 15）
            for k in range(max(0, a - 15), e):
                v = insns.get(k)
                if v is not None and k < e and k + v.size > a:
                    del insns[k]
            insns[a] = i
    return [insns[a] for a in sorted(insns)]


def collect_function_entries(ne, seg_insns=None):
    """回傳 {segnum: set(entries)}。來源：entry table、far call 目標、prologue；
    若提供 seg_insns 則再加上 near call (e8) 目標。"""
    entries = defaultdict(set)
    for e in ne.entries:
        if e['flags'] & 0x02:  # exported
            entries[e['seg']].add(e['off'])
    # CS:IP 入口點
    entries[ne.start_seg].add(ne.start_ip)
    for name, (s, o) in PROG_ENTRY_HINTS.items():
        if s <= ne.cseg and ne.seg(s)['is_code']:
            entries[s].add(o)

    # far call 目標：internal reloc sites
    #  - PTR32 import/internal：site = lcall+1
    #  - SELECTOR internal（本 EXE 的主要形式）：site = lcall+3，offset 取自 lcall+1 立即值
    for (segnum, site), tgt in ne.site_map.items():
        if tgt.get('kind') != 'internal':
            continue
        code = ne.seg_bytes(segnum)
        tseg, toff = None, None
        if tgt.get('addr_type') in (3, 11) and site >= 1 and code[site - 1] == 0x9A:
            tseg, toff = tgt['seg'], tgt['off']
        elif tgt.get('addr_type') == 2 and site >= 3 and code[site - 3] == 0x9A:
            tseg = tgt['seg']
            toff = struct.unpack_from('<H', code, site - 2)[0]
        if tseg is not None and 1 <= tseg <= ne.cseg and ne.seg(tseg)['is_code']:
            entries[tseg].add(toff)

    for seg in ne.segments:
        if not seg['is_code']:
            continue
        segnum = seg['num']
        code = ne.seg_bytes(segnum)
        if seg_insns:
            for ins in seg_insns.get(segnum, []):
                if ins.mnemonic == 'call' and ins.bytes and ins.bytes[0] == 0xE8:
                    tgt = (ins.address + ins.size + int.from_bytes(ins.bytes[1:3], 'little', signed=True)) & 0xFFFF
                    entries[segnum].add(tgt)
        # prologue: 55 8b ec (push bp; mov bp,sp) / c8 xx xx 00 (enter imm,0)
        i = 0
        n = len(code)
        while i + 3 <= n:
            if code[i] == 0x55 and code[i + 1] == 0x8B and code[i + 2] == 0xEC:
                entries[segnum].add(i)
                i += 3
            elif code[i] == 0xC8 and i + 4 <= n and code[i + 3] == 0x00:
                entries[segnum].add(i)
                i += 4
            else:
                i += 1
    for s in list(entries):
        if not (1 <= s <= ne.cseg):
            del entries[s]
            continue
        entries[s] = {e for e in entries[s] if 0 <= e < ne.seg(s)['len']}
    return entries


RETS = {'ret', 'retf', 'iret'}


def build_functions(ne, seg_insns, entries):
    """函數 = [entry, next_entry)；記大小、結尾指令、call 目標。"""
    funcs = {}  # (seg, off) -> dict
    for segnum, ents in entries.items():
        seg = ne.seg(segnum)
        if not seg['is_code']:
            continue
        ordered = sorted(ents)
        insn_by_addr = {i.address: i for i in (seg_insns.get(segnum) or [])}
        for idx, st in enumerate(ordered):
            end = ordered[idx + 1] if idx + 1 < len(ordered) else seg['len']
            # 找結尾 ret：從 st 線性走，遇到 ret 且下一條位址 >= 下一個 entry 或之後是 padding
            last = None
            for ins in seg_insns.get(segnum, []):
                if st <= ins.address < end:
                    last = ins
                if ins.address >= end:
                    break
            term = ''
            if last is not None:
                term = f'{last.mnemonic} {last.op_str}'.strip()
            # 裁剪尾部 padding（00/cc/90）以估有效大小
            code = ne.seg_bytes(segnum)
            eff = end
            body_end = (last.address + last.size) if last is not None and last.mnemonic in RETS else end
            funcs[(segnum, st)] = {
                'seg': segnum, 'off': st, 'end': end, 'size': end - st,
                'term': term, 'body_end': body_end,
            }
    # 被呼叫次數
    callcount = defaultdict(int)
    callers = defaultdict(set)
    for seg in ne.segments:
        if not seg['is_code']:
            continue
        segnum = seg['num']
        for ins in seg_insns.get(segnum, []):
            tgt = None
            if ins.mnemonic == 'call' and ins.bytes and ins.bytes[0] == 0xE8:
                t = (ins.address + ins.size + int.from_bytes(ins.bytes[1:3], 'little', signed=True)) & 0xFFFF
                tgt = (segnum, t)
            elif ins.bytes and ins.bytes[0] == 0x9A and ins.mnemonic == 'lcall':
                r = resolve_lcall(ne, segnum, ins.address, ne.seg_bytes(segnum))
                if r and r[0] == 'internal':
                    tgt = (r[1], r[2])
            if tgt:
                callcount[tgt] += 1
                callers[tgt].add((segnum, ins.address))
    for key, f in funcs.items():
        f['calls'] = callcount.get(key, 0)
        f['callers'] = sorted(callers.get(key, ()))
    return funcs


def find_func(funcs, segnum, off):
    """找包含 (seg,off) 的函數。"""
    cands = [f for (s, o), f in funcs.items() if s == segnum and o <= off < f['end']]
    return max(cands, key=lambda f: f['off']) if cands else None


def resolve_lcall(ne, segnum, addr, code):
    """解析 `9a` lcall 目標。回傳 ('internal', seg, off) / ('import', tgt_dict) / None。"""
    t = ne.site_map.get((segnum, addr + 1))          # PTR32 import/internal
    if t:
        if t.get('kind') == 'internal':
            return ('internal', t['seg'], t['off'])
        if t.get('kind') == 'import':
            return ('import', t)
    t = ne.site_map.get((segnum, addr + 3))          # SELECTOR：selector word 在 lcall+3
    if t and t.get('kind') == 'internal' and t.get('addr_type') == 2:
        off = struct.unpack_from('<H', code, addr + 1)[0]
        return ('internal', t['seg'], off)
    return None


# ------------------------------------------------------------------ reports

def seg_flags_str(fl):
    bits = []
    if fl & 0x0001: bits.append('DATA')
    else: bits.append('CODE')
    if fl & 0x0010: bits.append('MOVEABLE')
    if fl & 0x0020: bits.append('SHAREABLE')
    if fl & 0x0040: bits.append('PRELOAD')
    if fl & 0x0080: bits.append('EXECONLY')
    if fl & 0x0100: bits.append('RELOCS')
    if fl & 0x1000: bits.append('DISCARDABLE')
    return '|'.join(bits)


KNOWN_USES = {
    11: '繪圖/字型模組 + CRT startup（CreateFont 0x66bc、TextOut 0x90f8、文字引擎 0x8ca3）',
}


def write_reports(ne, ord_tables, seg_insns, entries, funcs, outdir):
    os.makedirs(outdir, exist_ok=True)

    # ---- segments.md
    with open(os.path.join(outdir, 'segments.md'), 'w') as f:
        f.write('# TEKE2WIN.EXE segment 清單\n\n')
        f.write(f'- NE header @ 0x{ne.ne:x}，sector shift = {ne.shift}（file offset = seg_offset << {ne.shift}）\n')
        f.write(f'- 入口點 seg{ne.start_seg}:0x{ne.start_ip:04x}，共 {ne.cseg} segments\n')
        code_n = sum(1 for s in ne.segments if s['is_code'])
        f.write(f'- code segments: {code_n}，data segments: {ne.cseg - code_n}\n')
        f.write(f'- import modules: {", ".join(ne.modules)}\n\n')
        f.write('| seg | file off | size | flags | 用途 |\n')
        f.write('|-----|----------|------|-------|------|\n')
        for s in ne.segments:
            use = KNOWN_USES.get(s['num'], '')
            if not use:
                if s['is_code']:
                    n_fn = len([k for k in funcs if k[0] == s['num']])
                    use = f'code，{n_fn} functions'
                else:
                    use = 'data'
                    if s['file'] == 0:
                        use += '（無檔案內容，runtime 配置）'
            f.write(f"| {s['num']} | 0x{s['file']:06x} | 0x{s['len']:05x} | {seg_flags_str(s['flags'])} | {use} |\n")

    # ---- functions_index.md
    with open(os.path.join(outdir, 'functions_index.md'), 'w') as f:
        f.write('# 函數索引\n\n')
        f.write('函數入口來源：entry table exports、CS:IP 入口、far call 目標（經 PTR32 reloc 解析）、'
                'near call (e8) 目標、`push bp; mov bp,sp` / `enter` prologue 掃描。\n\n')
        total = 0
        for seg in ne.segments:
            if not seg['is_code']:
                continue
            fl = [funcs[k] for k in sorted(funcs, key=lambda k: k[1]) if k[0] == seg['num']]
            total += len(fl)
            f.write(f"## seg{seg['num']}（file 0x{seg['file']:06x}，len 0x{seg['len']:x}）：{len(fl)} functions\n\n")
            f.write('| seg:off | size | end insn | 被呼叫 | file off |\n')
            f.write('|---------|------|----------|--------|----------|\n')
            for fn in fl:
                term = fn['term'].replace('|', '\\|')[:40]
                f.write(f"| {fn['seg']}:{fn['off']:04x} | {fn['size']} | {term} | {fn['calls']} | "
                        f"0x{ne.file_off(fn['seg'], fn['off']):06x} |\n")
            f.write('\n')
        f.write(f'\n**總函數數：{total}**\n')

    # ---- far call graph (csv + md)
    far_rows = []
    import_sites = defaultdict(list)  # label -> [(seg, off, caller_func)]
    for seg in ne.segments:
        if not seg['is_code']:
            continue
        segnum = seg['num']
        for ins in seg_insns.get(segnum, []):
            if not (ins.bytes and ins.bytes[0] == 0x9A and ins.mnemonic == 'lcall'):
                continue
            r = resolve_lcall(ne, segnum, ins.address, ne.seg_bytes(segnum))
            caller_fn = find_func(funcs, segnum, ins.address)
            caller = f'{segnum}:{ins.address:04x}'
            if r:
                if r[0] == 'internal':
                    callee = f'{r[1]}:{r[2]:04x}'
                    far_rows.append((caller, callee))
                else:
                    lbl = import_label(r[1], ord_tables)
                    far_rows.append((caller, lbl))
                    cdesc = f"{caller_fn['seg']}:{caller_fn['off']:04x}" if caller_fn else '?'
                    import_sites[lbl].append((segnum, ins.address, cdesc))
            else:
                far_rows.append((caller, 'UNRESOLVED'))
        # call far indirect (ff /3)：記錄但無法靜態解析
    with open(os.path.join(outdir, 'far_call_graph.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['caller', 'callee'])
        for r in sorted(set(far_rows)):
            w.writerow(r)
    with open(os.path.join(outdir, 'far_call_graph.md'), 'w') as f:
        f.write('# far call graph\n\n')
        f.write('`9a` far call 以 PTR32 relocation 鏈解析。完整資料見 `far_call_graph.csv`。\n\n')
        f.write(f'- far call sites（去重後）：{len(set(far_rows))}\n')
        internal = [r for r in set(far_rows) if ':' in r[1]]
        f.write(f'- 跨段/同段 internal far call：{len(internal)}\n')
        f.write(f'- import far call：{len([r for r in set(far_rows) if ":" not in r[1] and r[1] != "UNRESOLVED"])}\n')
        unres = [r for r in set(far_rows) if r[1] == 'UNRESOLVED']
        f.write(f'- 無法解析（無 reloc site）：{len(unres)}'
                '（皆為 jump table / 內嵌資料被線性掃描誤判的假 call，非真實程式碼）\n\n')
        by_callee = defaultdict(list)
        for c, ce in sorted(set(far_rows)):
            by_callee[ce].append(c)
        f.write('| callee | 呼叫點數 | callers |\n|--------|----------|---------|\n')
        for ce, cs in sorted(by_callee.items(), key=lambda kv: -len(kv[1])):
            show = ', '.join(cs[:8]) + (' …' if len(cs) > 8 else '')
            f.write(f'| {ce} | {len(cs)} | {show} |\n')

    # ---- imports.md
    HIGHLIGHT = ('CreateFont', 'TextOut', 'GetDeviceCaps', 'OpenFile', '_llseek',
                 '_hread', '_hwrite', '_lclose', '_lopen', 'WinG')
    with open(os.path.join(outdir, 'imports.md'), 'w') as f:
        f.write('# import 清單與呼叫點\n\n')
        f.write('ordinal → 名稱來源：wine-9.0 `.spec`（vendor/wine-src）。'
                '呼叫點 = `9a` far call site（seg:off），括號內為所屬函數入口。\n\n')
        for mod in ne.modules:
            labels = sorted([l for l in import_sites if l.startswith(mod + '.')])
            if not labels:
                continue
            f.write(f'## {mod}\n\n')
            f.write('| 函式 | 呼叫點數 | 呼叫點 |\n|------|----------|--------|\n')
            for lbl in labels:
                sites = import_sites[lbl]
                star = ' **★**' if any(h in lbl for h in HIGHLIGHT) else ''
                pts = ', '.join(f'{s}:{o:04x} ({cf})' for s, o, cf in sites[:12])
                if len(sites) > 12:
                    pts += f' … 共 {len(sites)}'
                f.write(f'| {lbl}{star} | {len(sites)} | {pts} |\n')
            f.write('\n')

    return len([k for k in funcs])


# ---------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('exe')
    ap.add_argument('--out', default='docs/disasm')
    ap.add_argument('--wine-src', default='vendor/wine-src/wine-9.0')
    ap.add_argument('--func', help='印出 seg:off（hex）所在函數的反組譯摘錄，例如 11:50c6')
    ap.add_argument('--list-imports', action='store_true')
    args = ap.parse_args()

    ne = NE(args.exe)
    ord_tables = load_ord_tables(args.wine_src)

    seg_insns = {}

    def sweep(entries):
        for seg in ne.segments:
            if seg['is_code'] and seg['file']:
                anchors = entries.get(seg['num'], set()) | lcall_anchors(ne, seg['num'])
                seg_insns[seg['num']] = disassemble_segment(ne, seg['num'], anchors)

    # phase 1：不靠反組譯的 entries（entry table、far-call 目標、prologue）
    entries = collect_function_entries(ne)
    sweep(entries)
    # phase 2：加入 near call 目標後重掃，修復第一輪未對齊的區段
    entries = collect_function_entries(ne, seg_insns)
    sweep(entries)
    funcs = build_functions(ne, seg_insns, entries)

    if args.func:
        s, o = args.func.split(':')
        segnum, off = int(s), int(o, 16)
        fn = find_func(funcs, segnum, off)
        if not fn:
            print(f'找不到包含 {args.func} 的函數'); return 1
        print(f"函數 seg{fn['seg']}:0x{fn['off']:04x} .. 0x{fn['end']:04x}"
              f"（size {fn['size']}，被呼叫 {fn['calls']} 次，結尾 {fn['term']!r}）")
        code = ne.seg_bytes(segnum)
        for ins in seg_insns[segnum]:
            if fn['off'] <= ins.address < fn['end']:
                mark = ' <==' if ins.address == off else ''
                note = ''
                if ins.bytes and ins.bytes[0] == 0x9A and ins.mnemonic == 'lcall':
                    r = resolve_lcall(ne, segnum, ins.address, code)
                    if r and r[0] == 'internal':
                        note = f'  ; -> seg{r[1]}:0x{r[2]:04x}'
                    elif r and r[0] == 'import':
                        note = f'  ; -> {import_label(r[1], ord_tables)}'
                else:
                    for k in range(ins.address, ins.address + ins.size):
                        t = ne.site_map.get((segnum, k))
                        if t and t.get('kind') == 'import':
                            note = f'  ; imm <- {import_label(t, ord_tables)}'
                            break
                        if t and t.get('kind') == 'internal' and t.get('addr_type') == 2:
                            note = f"  ; imm <- seg{t['seg']} selector"
                            break
                print(f"  {ins.address:04x}: {ins.bytes.hex():14s} {ins.mnemonic:8s} {ins.op_str}{note}{mark}")
        return 0

    n_funcs = write_reports(ne, ord_tables, seg_insns, entries, funcs, args.out)
    code_n = sum(1 for s in ne.segments if s['is_code'])
    print(f'{args.exe}: {ne.cseg} segments ({code_n} code), functions: {n_funcs}')
    print(f'reports written to {args.out}/')

    if args.list_imports:
        for seg in ne.segments:
            if not seg['is_code']:
                continue
            for (sg, site), tgt in sorted(ne.site_map.items()):
                if sg != seg['num'] or tgt.get('kind') != 'import' or tgt.get('addr_type') not in (3, 11):
                    continue
                print(f'{sg}:{site:04x} {import_label(tgt, ord_tables)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
