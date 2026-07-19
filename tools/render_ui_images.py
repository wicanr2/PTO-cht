#!/usr/bin/env python3
"""把指定 UI 圖檔重繪成繁體中文。"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

IMG_DIR = Path('assets/images')
OUT_DIR = Path('assets/images_zh')

# 字體
FONT_BOLD = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
FONT_REG = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'


def get_font(path, size):
    return ImageFont.truetype(path, size)


def render_meirei_000():
    img = Image.open(IMG_DIR / 'MEIREI_000.png').convert('RGB')
    draw = ImageDraw.Draw(img)
    green = (0, 255, 0)
    black = (0, 0, 0)
    # 覆蓋原文
    draw.rectangle([120, 20, 200, 55], fill=green)   # ORDERS
    draw.rectangle([0, 30, 45, 55], fill=green)    # To:
    draw.rectangle([0, 50, 45, 75], fill=green)    # From:
    # 重繪
    font = get_font(FONT_BOLD, 24)
    text = '命令'
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((160 - w//2, 20), text, font=font, fill=black)
    font2 = get_font(FONT_BOLD, 16)
    draw.text((5, 32), '給：', font=font2, fill=black)
    draw.text((5, 52), '自：', font=font2, fill=black)
    return img


def render_make(name, text, font_size=48):
    img = Image.open(IMG_DIR / name).convert('RGB')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    draw.rectangle([0, 0, w, h], fill=(0, 0, 0))
    font = get_font(FONT_BOLD, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((w - tw)//2, (h - th)//2), text, font=font, fill=(255, 255, 0))
    return img


def render_end_sf_001():
    """THE END → 完（黃字黑底，滿版）。"""
    img = Image.open(IMG_DIR / 'END_SF_001.png').convert('RGB')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    draw.rectangle([0, 0, w, h], fill=(0, 0, 0))
    font = get_font(FONT_BOLD, 72)
    text = '完'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw)//2 - bbox[0], (h - th)//2 - bbox[1]), text, font=font,
              fill=(255, 255, 0))
    return img


def render_op4_bc_003():
    """日文標題「WWIIゲーム 提督の決断II」→ 中文標題（綠字黃綠描邊，黑底）。"""
    img = Image.open(IMG_DIR / 'OP4_BC_003.png').convert('RGB')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    draw.rectangle([0, 0, w, h], fill=(0, 0, 0))
    green = (0, 200, 0)
    outline = (200, 255, 0)
    # 主標題
    font = get_font(FONT_BOLD, 96)
    text = '提督的決斷II'
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw)//2 - bbox[0], h - th - 20 - bbox[1]), text, font=font,
              fill=green, stroke_width=3, stroke_fill=outline)
    # 副標題（右上）
    font2 = get_font(FONT_BOLD, 28)
    sub = '第二次世界大戰'
    bbox2 = draw.textbbox((0, 0), sub, font=font2)
    sw = bbox2[2] - bbox2[0]
    draw.text((w - sw - 16 - bbox2[0], 12 - bbox2[1]), sub, font=font2,
              fill=green, stroke_width=1, stroke_fill=outline)
    return img


def main():
    OUT_DIR.mkdir(exist_ok=True)
    render_meirei_000().save(OUT_DIR / 'MEIREI_000.png')
    render_make('MAKE_000.png', '遊戲結束', font_size=48).save(OUT_DIR / 'MAKE_000.png')
    render_make('MAKE_001.png', '完結', font_size=56).save(OUT_DIR / 'MAKE_001.png')
    render_end_sf_001().save(OUT_DIR / 'END_SF_001.png')
    render_op4_bc_003().save(OUT_DIR / 'OP4_BC_003.png')
    print('完成 ->', OUT_DIR)


if __name__ == '__main__':
    main()
