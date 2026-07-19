#!/bin/bash
# 完整本機包（自用保留，不上傳）：86Box + 繁中 Win3.1 映像 + 中文化遊戲 + 音樂 CD
# 前置：vendor/86box/win31cht_hdd.img 已完成繁中 Win3.1 + 中文化遊戲安裝（agent-20 驗證過）
set -e

OUT="dist-local/PTO2-cht-full"
SRC_ISO="assets/origin/PTO-Paci/cd/Pacific.Theater.of.Operations.2"
HDD="vendor/86box/win31cht_hdd.img"

echo "=== 建立完整本機包 -> $OUT ==="
[ -f "$HDD" ] || { echo "錯誤：$HDD 不存在（86Box 繁中映像尚未完成）"; exit 1; }
[ -f "$SRC_ISO.bin" ] || { echo "錯誤：音樂 CD 映像不存在"; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT"/{86box,hdd,cd,vm}

# 模擬器
cp vendor/86box/86Box-4.2.1.AppImage "$OUT/86box/"
cp -r vendor/86box/roms "$OUT/86box/"

# 硬碟映像（繁中 Win3.1 + 中文化遊戲）
cp "$HDD" "$OUT/hdd/win31cht_hdd.img"

# 音樂 CD
cp "$SRC_ISO.cue" "$SRC_ISO.bin" "$OUT/cd/"

# VM 設定（S3 864 + SB16 + 掛 hdd 與 CD）
cat > "$OUT/vm/86box.cfg" <<EOF
[General]
confirm_exit = 0
vid_resize = 1
vid_renderer = qt_software
emu_build_num = 6130

[Machine]
machine = 4dps
cpu_family = i486dx2
cpu_speed = 66666666
cpu_multi = 2
fpu = builtin
fpu_type = internal
mem_size = 32768
cpu_use_dynarec = 0
fpu_softfloat = 0
time_sync = local

[Video]
gfxcard = s3_86c805_isa

[Input devices]
mouse_type = ps2

[Sound]
sndcard = sb16
mpu401 = 1
fm_driver = nuked

[Storage controllers]
hdc = internal

[Hard disks]
hdd_01_parameters = 63, 16, 520, 0, ide
hdd_01_fn = ../hdd/win31cht_hdd.img
hdd_01_speed = 1997_5400rpm
hdd_01_ide_channel = 0:0

[Floppy and CD-ROM drives]
fdd_01_type = none
cdrom_01_parameters = 1, atapi
cdrom_01_ide_channel = 0:1
cdrom_01_image = ../cd/Pacific.Theater.of.Operations.2.cue
cdrom_01_type = 86BOX_CD-ROM_1.00
EOF

# 啟動腳本
cat > "$OUT/play.sh" <<'EOF'
#!/bin/bash
# 提督的決斷 II 繁體中文版（86Box + 繁體中文 Windows 3.1）
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
cd "$HERE/vm"
exec "$HERE/86box/86Box-4.2.1.AppImage" --vmpath "$HERE/vm" "$@"
EOF
chmod +x "$OUT/play.sh" "$OUT/86box/86Box-4.2.1.AppImage"

# 說明
cat > "$OUT/README.txt" <<'EOF'
提督的決斷 II 繁體中文版（完整本機包）
========================================

內容：
- 86Box 4.2.1（PC 模擬器）+ ROMs
- 繁體中文 Windows 3.1 硬碟映像（含中文化遊戲）
- 音樂 CD 映像（遊戲 BGM 為 CD 音軌，已掛載）

執行：
  ./play.sh

進入 Windows 3.1 後（或自動進入），執行遊戲：
  C:\PTO2WIN\TEKE2WIN.EXE
（或在 DOS 提示字元下輸入：WIN C:\PTO2WIN\TEKE2WIN.EXE）

操作提示：
- 滑鼠擷取/釋放：Ctrl+End 或按滑鼠中鍵
- 全螢幕：Ctrl+Alt+PageDown（視版本而定）
- 關閉 86Box 視窗即結束（已關閉離開確認）

注意：
- 本包僅供個人本機使用，請勿散佈（含原版遊戲與 Windows 3.1）
- 存檔會寫入 hdd/win31cht_hdd.img
EOF

echo "完成 -> $OUT"
du -sh "$OUT"
