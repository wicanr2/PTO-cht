#!/usr/bin/env python3
"""Wine 專用 WinG 繞道補丁（只供 Linux/AppImage 使用，Windows/otvdm 包請勿套用）。

Wine 的 16-bit 模組載入器（MODULE_LoadModule16）會無條件優先載入內建 wing.dll16，
不吃 DllOverrides，導致 WinGGetDIBPointer16 的 fixme 之後 page fault。
這裡把 TEKE2WIN.EXE import table 中的 'WING' 改名為 'XING'，
讓 Wine 找不到 xing.dll16 內建模組而改走原生 NE_LoadModule，
載入我們提供的 XING.DLL（原版 WING.DLL 改名，內部模組名同步改為 XING）。

用法：python3 tools/patch_wine_wing.py <game_dir>
（會在 game_dir 內產生 XING.DLL，並直接修改該處的 TEKE2WIN.EXE；冪等）
"""
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ORIGIN_WING = Path('assets/origin/PTO-Paci/Apps/wing/WING.DL_')


def extract_original_wing() -> bytes:
    """從原版 Apps 目錄解出 WING.DLL 內容。"""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(['7z', 'e', '-y', str(ORIGIN_WING), f'-o{td}'],
                       check=True, capture_output=True)
        outs = list(Path(td).glob('*'))
        if len(outs) != 1:
            raise RuntimeError(f'7z 解出非預期檔案: {outs}')
        return outs[0].read_bytes()


def make_xing_dll() -> bytes:
    data = bytearray(extract_original_wing())
    ne = struct.unpack_from('<I', data, 0x3c)[0]
    restab = struct.unpack_from('<H', data, ne + 0x26)[0]
    name_off = ne + restab
    assert data[name_off] == 4 and data[name_off + 1:name_off + 5] == b'WING', \
        'WING.DLL resident name table 格式不符'
    data[name_off + 1:name_off + 5] = b'XING'
    return bytes(data)


def patch_exe(exe_path: Path) -> str:
    data = exe_path.read_bytes()
    ne = struct.unpack_from('<I', data, 0x3c)[0]
    cmod = struct.unpack_from('<H', data, ne + 0x1E)[0]
    modtab = struct.unpack_from('<H', data, ne + 0x28)[0]
    imptab = struct.unpack_from('<H', data, ne + 0x2A)[0]
    for j in range(cmod):
        o = struct.unpack_from('<H', data, ne + modtab + 2 * j)[0]
        l = data[ne + imptab + o]
        name = bytes(data[ne + imptab + o + 1:ne + imptab + o + 1 + l])
        if name == b'XING':
            return '已經是 XING，略過'
        if name == b'WING':
            patched = bytearray(data)
            patched[ne + imptab + o + 1:ne + imptab + o + 1 + l] = b'XING'
            exe_path.write_bytes(patched)
            return f'EXE import WING -> XING @ {hex(ne + imptab + o + 1)}'
    raise RuntimeError('在 import table 找不到 WING')


def main():
    game_dir = Path(sys.argv[1] if len(sys.argv) > 1 else 'assets/patched/PTO2WIN')
    xing = game_dir / 'XING.DLL'
    if not xing.exists():
        xing.write_bytes(make_xing_dll())
        print(f'產生 {xing}')
    else:
        print(f'{xing} 已存在，沿用')
    print(patch_exe(game_dir / 'TEKE2WIN.EXE'))


if __name__ == '__main__':
    main()
