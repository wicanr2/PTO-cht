#!/bin/bash
# 產生 Linux AppImage（骨架，尚未完成）
set -e

GAME_DIR="${1:-assets/patched/PTO2WIN}"
OUT_NAME="PTO2-cht.AppImage"

echo "此腳本尚未完成。目前建議："
echo "1. 在 Linux 上用 Wine 跑 $GAME_DIR/TEKE2WIN.EXE（需解決 WinG 問題）"
echo "2. 或使用 DOSBox-X + 合法 Windows 3.x"
echo ""
echo "TODO:"
echo "- 打包 Wine 執行環境（或改用 DOSBox-X）"
echo "- 放入中文化補丁後的遊戲目錄"
echo "- 產生 AppImage"
