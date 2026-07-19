#!/usr/bin/env python3
"""跳過 P.T.O. II Win16 開場影片（OPEN.AVI）播放的 patch。

背景：
  seg6:0x232c 是遊戲啟動時的 CD audio / 開場影片初始化函數（被呼叫 1 次）。
  流程：開 cdaudio → 關對話框 → 播 OPEN.AVI（seg11:0x1322），失敗會跳
  「無法開啟影片」錯誤並重試；在無 Video for Windows 或 MCI AVI 出問題的
  環境，後續還會連鎖 GPF 導致無法進主選單。

  seg6:0x2352 的 `jne 0x2372` 原本是「(前一個呼叫成功就) 跳過影片播放」；
  把它改成無條件 jmp（0xEB），遊戲永遠跳過 OPEN.AVI 播放與其錯誤迴圈，
  直接進入收尾（call 6:1872）後返回，logo 之後進主選單。CD audio 開啟
  （BGM）不受影響。

  seg6 檔案偏移 = 0x49c00（見 docs/disasm/segments.md），
  seg6:0x2352 → file offset 0x4BF52，原 bytes = 75 1E。

用法: python3 tools/patch_skip_opening.py <exe>   （冪等，會驗證 bytes）
"""
import sys

PATCHES = [
    # (file offset, orig, patch, 說明)
    # seg6:0x2352 `jne 0x2372` -> `jmp 0x2372`：OPEN.AVI 播放失敗時不再進入
    # 「無法開啟影片」重試迴圈，直接收尾繼續啟動（成功時行為與原本相同，無害）。
    (0x49C00 + 0x2352, bytes([0x75, 0x1E]), bytes([0xEB, 0x1E]),
     'seg6:0x2352 jne->jmp：跳過啟動時的影片錯誤重試迴圈'),
    # 備註：曾嘗試 stub seg3:0x2c94（AVI 播放函數）強制 return 1，會讓遊戲在
    # 開場錯誤對話框後直接退出（流程不一致），已棄用；正解是裝 Video for
    # Windows 並在 WIN.INI [mci extensions] 註冊 avi=AVIVideo，讓 OPEN.AVI
    # 真的播得出來。
]


def main():
    path = sys.argv[1]
    with open(path, 'r+b') as f:
        for off, orig, patch, desc in PATCHES:
            f.seek(off)
            cur = f.read(len(orig))
            if cur == patch:
                print(f'  [{off:#x}] 已套用過：{desc}')
                continue
            if cur != orig:
                raise SystemExit(f'{path}: offset {off:#x} bytes 不符預期: {cur.hex()}（預期 {orig.hex()}）')
            f.seek(off)
            f.write(patch)
            print(f'  [{off:#x}] 已套用：{desc}')
    print(f'{path}: skip-opening patch 完成')


if __name__ == '__main__':
    main()
