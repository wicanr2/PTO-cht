#!/bin/bash
# 產生 Windows 可執行包（otvdm + 中文化遊戲）
set -e

GAME_DIR="${1:-assets/patched/PTO2WIN}"
DIST_DIR="dist/windows"
OTVDM_URL="https://github.com/otya128/winevdm/releases/download/v0.9.0/otvdm-v0.9.0.zip"
OTVDM_DIR="vendor/otvdm"

echo "=== 建立 Windows 可執行包 ==="
echo "遊戲目錄: $GAME_DIR"

# 1. 準備 otvdm
mkdir -p vendor
if [ ! -d "$OTVDM_DIR" ]; then
    echo "下載 otvdm..."
    curl -L -o /tmp/otvdm.zip "$OTVDM_URL"
    rm -rf vendor/otvdm-v0.9.0 vendor/otvdm-v0.8.1
    unzip -q /tmp/otvdm.zip -d vendor/
    mv vendor/otvdm-v0.9.0 "$OTVDM_DIR"
fi

# 2. 準備輸出目錄
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

# 3. 複製 otvdm 主體
cp -r "$OTVDM_DIR"/* "$DIST_DIR/"

# 4. 複製遊戲（中文化補丁）
cp -r "$GAME_DIR" "$DIST_DIR/PTO2WIN"

# 5. 複製必要 DLL（WinG / VFW / Win32s / QT）到遊戲目錄
# 從原版 Apps 目錄解出（若存在）
if [ -d "assets/origin/PTO-Paci/Apps" ]; then
    echo "解出 WinG / VFW / Win32s DLL..."
    mkdir -p "$DIST_DIR/PTO2WIN/system"
    # WinG
    for f in WING.DL_ WING32.DL_ WINGDE.DL_ WINGDIB.DR_ WINGPAL.WN_ SETUPHLP.DL_ DVA.38_; do
        if [ -f "assets/origin/PTO-Paci/Apps/wing/$f" ]; then
            7z e -y "assets/origin/PTO-Paci/Apps/wing/$f" -o"$DIST_DIR/PTO2WIN/system/" >/dev/null
        fi
    done
    # 重新命名 .DL -> .DLL / .DRV / .386 / .WND
    cd "$DIST_DIR/PTO2WIN/system"
    for f in *.DL; do mv "$f" "${f%.*}.DLL"; done
    for f in *.DR; do mv "$f" "${f%.*}.DRV"; done
    for f in *.38; do mv "$f" "${f%.*}.386"; done
    for f in *.WN; do mv "$f" "${f%.*}.WND"; done
    cd - >/dev/null
fi

# 6. 啟動腳本
cat > "$DIST_DIR/play.bat" <<'EOF'
@echo off
cd /d %~dp0
otvdmw.exe PTO2WIN\TEKE2WIN.EXE
EOF

# 7. 使用說明
cat > "$DIST_DIR/使用說明.txt" <<'EOF'
提督之決斷 II 繁體中文化（Windows 版）

【啟動方式】
1. 解壓縮後，執行 play.bat 啟動遊戲。
2. 若出現 SmartScreen 警告，請點「更多資訊」→「仍要執行」。
3. 本包使用 otvdm（WineVDM）執行 Win16 遊戲，無需安裝原版 Windows 3.x。

【關於 CD（重要）】
本遊戲啟動時會檢查原版 CD（MCI cdaudio）。若沒有掛載 CD，會出現：
  - 「Can't open CD-ROM DEVICE.」（找不到 CD 裝置）
  - 「Please insert P.T.O. II's CD-ROM.」（有裝置但讀不到光碟）
要正常遊玩（含開場動畫與 CD 音樂），請掛載原版 CD 映像：
  1. 下載免費的 WinCDEmu（https://wincdemu.sysprogs.org/）
  2. 把原版 CD 映像（Pacific.Theater.of.Operations.2.cue）掛載成虛擬光碟
     （cue/bin 含資料軌與音軌，請務必用支援 cue 的工具，Windows 內建掛載只吃 .iso）
  3. 再執行 play.bat

【沒有 CD 時】
若出現「Please insert P.T.O. II's CD-ROM.」對話框，按「Cancel」可略過，
但開場內容與 CD 音樂會無法播放。建議還是掛載 CD 映像。

【其他】
- otvdm.ini 已隨附預設值，一般情況不需修改。
- 本中文化補丁僅供個人使用，請勿公開散佈。
EOF

# 8. 壓縮
cd dist
zip -qr "PTO2-cht-windows.zip" windows/
cd ..
echo "完成 -> dist/PTO2-cht-windows.zip"
