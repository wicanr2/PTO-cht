#!/bin/bash
# 產生 Linux AppImage（骨架：需系統已安裝 Wine，或改用 DOSBox-X）
set -e

GAME_DIR="${1:-assets/patched/PTO2WIN}"
APP_DIR="dist/PTO2-cht.AppDir"
OUT_NAME="PTO2-cht.AppImage"

echo "=== 建立 Linux AppImage ==="
echo "遊戲目錄: $GAME_DIR"

if ! command -v wine >/dev/null 2>&1; then
    echo "錯誤：系統未安裝 wine。請先安裝 wine 或改用 DOSBox-X 方案。"
    exit 1
fi

rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/bin" "$APP_DIR/usr/share/pto2-cht"

# 複製遊戲
cp -r "$GAME_DIR" "$APP_DIR/usr/share/pto2-cht/PTO2WIN"

# AppRun：用系統 wine 啟動
cat > "$APP_DIR/AppRun" <<'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export WINEPREFIX="${WINEPREFIX:-$HOME/.wine_pto2_cht}"
mkdir -p "$WINEPREFIX"
cd "$HERE/usr/share/pto2-cht/PTO2WIN"
exec wine explorer /desktop=pto2,800x600 TEKE2WIN.EXE "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# Desktop file
cat > "$APP_DIR/pto2-cht.desktop" <<'EOF'
[Desktop Entry]
Name=提督之決斷 II 繁體中文
Exec=AppRun
Icon=pto2-cht
Type=Application
Categories=Game;
EOF

# Icon（用遊戲 ICON，暫用空 PNG）
python3 - <<'PY'
from PIL import Image
img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
img.save('dist/PTO2-cht.AppDir/pto2-cht.png')
PY

# 使用說明
cat > "$APP_DIR/使用說明.txt" <<'EOF'
提督之決斷 II 繁體中文化（Linux AppImage）

1. 本包需要系統已安裝 Wine（或相容的 Wine 前綴）。
2. 第一次執行前，請先執行：chmod +x PTO2-cht.AppImage
3. 若出現 FUSE 錯誤，請使用：./PTO2-cht.AppImage --appimage-extract-and-run
4. 已知問題：Wine 對 WinG 支援不完整，可能無法啟動。若遇到問題，請改用 DOSBox-X + 合法 Windows 3.x。
5. 本中文化補丁僅供個人使用，請勿公開散佈。
EOF

# 嘗試用 appimagetool 打包（若存在）
if command -v appimagetool >/dev/null 2>&1; then
    appimagetool "$APP_DIR" "dist/$OUT_NAME"
    echo "完成 -> dist/$OUT_NAME"
else
    echo "appimagetool 未安裝，AppDir 已建立在 $APP_DIR"
    echo "請手動執行：appimagetool $APP_DIR dist/$OUT_NAME"
fi
