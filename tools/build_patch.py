#!/usr/bin/env python3
"""把原始遊戲檔案 + 翻譯注入產生補丁後的遊戲目錄。"""
import shutil
import subprocess
import sys
from pathlib import Path

SRC_DIR = Path('assets/origin/PTO-Paci/PTO2WIN')
PATCH_DIR = Path('patch')
OUT_DIR = Path('assets/patched/PTO2WIN')

FILES = [
    'EVMSG.TK2', 'JOGEN.TK2', 'KAIMSG.TK2', 'SCESETSU.TK2', 'SCESTART.TK2',
    'KSNAME.TK2', 'SSNAME.TK2', 'MSG1.TK2',
    'ARDATA', 'GRDATA', 'KDATA', 'KSDATA', 'NCTDATA', 'PLDATA',
    'SJDATA', 'SSDATA', 'STDATA', 'TKDATA', 'TEKE2WIN.EXE',
    'MAKE.TK2', 'MEIREI.TK2',
]


def run(cmd):
    print(' '.join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def main():
    # 0. 產生中文化 UI 圖檔
    run([sys.executable, 'tools/render_ui_images.py'])
    # 1. 重新產生 patch/*
    run([sys.executable, 'tools/inject_text_tk2.py'])
    run([sys.executable, 'tools/inject_names.py'])
    run([sys.executable, 'tools/inject_msg1.py'])
    run([sys.executable, 'tools/inject_exe_strings.py'])

    # 2. 複製原始檔案並覆蓋
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    shutil.copytree(SRC_DIR, OUT_DIR)
    for fname in FILES:
        src = PATCH_DIR / fname
        if src.exists():
            shutil.copy2(src, OUT_DIR / fname)
        else:
            print(f'[warn] patch/{fname} 不存在，使用原版')
    print(f'完成 -> {OUT_DIR}')


if __name__ == '__main__':
    main()
