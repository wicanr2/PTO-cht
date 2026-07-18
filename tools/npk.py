#!/usr/bin/env python3
"""NPK016 編解碼工具（光榮早期點陣圖格式）"""
import io
import os
import sys
import glob
import argparse
from PIL import Image


def unpack_npk(src: bytes, line: int, height: int) -> bytes:
    """把 NPK016 壓縮資料解成 color index 串流。"""
    data = io.BytesIO(src)
    dest = bytearray()
    bitflag = 0x0000
    data_len = len(src)
    dest_len = line * height
    while data.tell() < data_len and len(dest) < dest_len:
        if not (bitflag & 0xFF00):
            bitflag = 0xFF00 | data.read(1)[0]
        if bitflag & 1:
            b = data.read(1)[0]
            run_size = (b & 0x1F) + 1
            run_offset = ((b & 0x60) >> 5) + 1
            run_offset = run_offset * line if (b & 0x80) else run_offset * 4
            for _ in range(run_size * 4):
                dest.append(dest[-run_offset])
        else:
            b1 = data.read(1)[0]
            b2 = data.read(1)[0]
            for _ in range(4):
                d = ((b1 & 0x80) >> 4) | ((b1 & 0x08) >> 1) | \
                    ((b2 & 0x80) >> 6) | ((b2 & 0x08) >> 3)
                dest.append(d)
                b1 = (b1 << 1) & 0xFF
                b2 = (b2 << 1) & 0xFF
        bitflag >>= 1
    return bytes(dest)


def pack_npk_literal(idxs: bytes) -> bytes:
    """最簡單的 NPK 編碼：全部用 literal opcode（體積較大但一定正確）。"""
    out = bytearray()
    i = 0
    n = len(idxs)
    while i < n:
        ops = []
        payloads = bytearray()
        for _ in range(8):
            if i >= n:
                break
            ops.append(0)  # literal
            p0, p1, p2, p3 = idxs[i:i+4]
            b1 = ((p0 >> 3) & 1) << 7 | ((p1 >> 3) & 1) << 6 | \
                 ((p2 >> 3) & 1) << 5 | ((p3 >> 3) & 1) << 4 | \
                 ((p0 >> 2) & 1) << 3 | ((p1 >> 2) & 1) << 2 | \
                 ((p2 >> 2) & 1) << 1 | ((p3 >> 2) & 1)
            b2 = ((p0 >> 1) & 1) << 7 | ((p1 >> 1) & 1) << 6 | \
                 ((p2 >> 1) & 1) << 5 | ((p3 >> 1) & 1) << 4 | \
                 ((p0 >> 0) & 1) << 3 | ((p1 >> 0) & 1) << 2 | \
                 ((p2 >> 0) & 1) << 1 | ((p3 >> 0) & 1)
            payloads.append(b1)
            payloads.append(b2)
            i += 4
        bitflag = 0
        for j, op in enumerate(ops):
            if op:
                bitflag |= 1 << j
        out.append(bitflag)
        out.extend(payloads)
    return bytes(out)


def rgb555_to_rgb(x: int) -> tuple:
    r = (x & 0x1f) << 3
    g = ((x >> 5) & 0x1f) << 3
    b = ((x >> 10) & 0x1f) << 3
    return (r, g, b)


def rgb_to_rgb555(c: tuple) -> int:
    r = (c[0] >> 3) & 0x1f
    g = (c[1] >> 3) & 0x1f
    b = (c[2] >> 3) & 0x1f
    return r | (g << 5) | (b << 10)


def parse_npk016_file(path: str):
    """解析可能含多個 NPK016 chunk 的檔案，回傳 [(width, height, palette, indexes)]"""
    with open(path, 'rb') as f:
        data = f.read()
    chunks = []
    start = 0
    while True:
        off = data.find(b'NPK016', start)
        if off < 0:
            break
        if len(data) < off + 48:
            break
        # 解析 header
        screen_w = int.from_bytes(data[off+8:off+10], 'little')
        screen_h = int.from_bytes(data[off+10:off+12], 'little')
        w = int.from_bytes(data[off+12:off+14], 'little')
        h = int.from_bytes(data[off+14:off+16], 'little')
        pal_bytes = data[off+16:off+48]
        palette = [rgb555_to_rgb(int.from_bytes(pal_bytes[i:i+2], 'little')) for i in range(0, 32, 2)]
        next_off = data.find(b'NPK016', off + 1)
        payload = data[off+48:next_off] if next_off > 0 else data[off+48:]
        idxs = unpack_npk(payload, w, h)
        chunks.append({
            'offset': off,
            'screen': (screen_w, screen_h),
            'size': (w, h),
            'palette': palette,
            'indexes': idxs,
            'payload': payload,
        })
        start = off + 1
    return chunks


def indexes_to_image(idxs: bytes, w: int, h: int, palette: list) -> Image.Image:
    img = Image.new('RGB', (w, h), (0, 0, 0))
    for i, idx in enumerate(idxs):
        if i >= w * h:
            break
        y, x = divmod(i, w)
        img.putpixel((x, y), palette[idx])
    return img


def image_to_indexes(img: Image.Image, palette: list) -> bytes:
    """把 PNG/RGB 圖轉回 16 色 index（會做最近似調色盤對應）。"""
    w, h = img.size
    palette_map = {c: i for i, c in enumerate(palette)}
    idxs = bytearray()
    for y in range(h):
        for x in range(w):
            c = img.getpixel((x, y))
            if c not in palette_map:
                # 找最接近色
                c = min(palette, key=lambda p: sum((a-b)**2 for a, b in zip(p, c)))
            idxs.append(palette_map[c])
    return bytes(idxs)


def save_chunks(chunks, out_dir, base):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, c in enumerate(chunks):
        img = indexes_to_image(c['indexes'], c['size'][0], c['size'][1], c['palette'])
        out_path = os.path.join(out_dir, f'{base}_{i:03d}.png')
        img.save(out_path)
        paths.append(out_path)
    return paths


def decode_file(src: str, out_dir: str):
    base = os.path.splitext(os.path.basename(src))[0]
    chunks = parse_npk016_file(src)
    if not chunks:
        print(f'{src}: 沒有 NPK016 chunk')
        return []
    return save_chunks(chunks, out_dir, base)


def encode_file(src_pngs: list, original: str, out: str):
    """用一組 PNG 重建 NPK016 檔案，順序與 chunk 數量需與 original 一致。"""
    chunks = parse_npk016_file(original)
    if len(src_pngs) != len(chunks):
        raise ValueError(f'PNG 數量 {len(src_pngs)} 與原檔 chunk 數 {len(chunks)} 不一致')
    out_data = bytearray()
    for png_path, orig in zip(src_pngs, chunks):
        img = Image.open(png_path).convert('RGB')
        w, h = img.size
        if (w, h) != orig['size']:
            raise ValueError(f'{png_path} 尺寸 {w}x{h} 與原 {orig["size"]} 不一致')
        idxs = image_to_indexes(img, orig['palette'])
        payload = pack_npk_literal(idxs)
        header = bytearray()
        header.extend(b'NPK016')
        header.extend(b'\x04\x00')
        header.extend(orig['screen'][0].to_bytes(2, 'little'))
        header.extend(orig['screen'][1].to_bytes(2, 'little'))
        header.extend(w.to_bytes(2, 'little'))
        header.extend(h.to_bytes(2, 'little'))
        for c in orig['palette']:
            header.extend(rgb_to_rgb555(c).to_bytes(2, 'little'))
        out_data.extend(header)
        out_data.extend(payload)
    with open(out, 'wb') as f:
        f.write(out_data)
    print(f'寫入 {out} ({len(chunks)} chunks)')


def main():
    parser = argparse.ArgumentParser(description='NPK016 編解碼工具')
    sub = parser.add_subparsers(dest='cmd')
    dec = sub.add_parser('decode', help='解出 PNG')
    dec.add_argument('input', help='輸入 .TK2 或目錄')
    dec.add_argument('-o', '--out', default='assets/images', help='輸出目錄')
    enc = sub.add_parser('encode', help='把 PNG 封回 NPK016')
    enc.add_argument('original', help='原始 .TK2')
    enc.add_argument('pngs', nargs='+', help='對應 chunk 的 PNG')
    enc.add_argument('-o', '--out', required=True, help='輸出 .TK2')
    args = parser.parse_args()

    if args.cmd == 'decode':
        if os.path.isdir(args.input):
            files = sorted(glob.glob(os.path.join(args.input, '*.TK2')))
            for f in files:
                decode_file(f, args.out)
        else:
            decode_file(args.input, args.out)
    elif args.cmd == 'encode':
        encode_file(args.pngs, args.original, args.out)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
