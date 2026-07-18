#!/bin/bash
# 產生 Windows 可執行包（骨架，尚未完成）
set -e

GAME_DIR="${1:-assets/patched/PTO2WIN}"
OUT_DIR="dist/windows"

echo "此腳本尚未完成。目前建議："
echo "1. 下載 otvdm (WineVDM) 並解壓"
echo "2. 把 $GAME_DIR 複製到 otvdm 目錄旁"
echo "3. 用 otvdmw.exe 啟動 TEKE2WIN.EXE"
echo ""
echo "TODO:"
echo "- 自動下載 otvdm"
echo "- 複製必要 DLL（WinG / VFW / Win32s / QT）"
echo "- 產生 .zip 與 使用說明.txt"
