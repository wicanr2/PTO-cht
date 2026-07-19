# 自編 wing.dll16（wine-9.0 + WinGGetDIBPointer16 BITMAPINFO 回填）

來源：vendor/wine-src/wine-9.0（dlls/wing.dll16/wing.c 已含 PTO2-cht patch）

## 構建（無 sudo）
1. `apt-get download libc6-dev-i386 gcc-13-multilib lib32gcc-13-dev lib32gcc-s1`，
   `dpkg -x` 到 /tmp/i386/root；修 /tmp/i386/root/usr/lib32/libc.so 絕對路徑
2. gcc wrapper（僅 -m32 時追加 -B/-L/-I/-idirafter）：/tmp/i386/bin/gcc
3. flex 2.6.4 源碼本地建（只需 m4）：/tmp/flex-install
4. `PATH=/tmp/i386/bin:/tmp/flex-install/bin:$PATH <src>/configure --without-x
   --without-freetype --without-alsa --without-pulse --without-gnutls
   --without-opengl --without-vulkan --without-gstreamer --without-wayland
   --disable-tests ...`（build dir /tmp/winebuild）
5. `make -C tools && make -C dlls/wing.dll16`

## 產物
- `i386-windows/wing.dll16`（PE stub 2.5KB，"fake Wine dll"）
- `i386-unix/wing.dll16.so`（120KB，實際 16-bit 碼）

## 載入（WINEDLLPATH 對 dll16 無效：系統 dll_dir 優先）
shadow tree（/tmp/wineroot）：
- 實體複本 /usr/lib/wine/wine{,64} loader + wineserver*
- `cp -rs /usr/lib/i386-linux-gnu/wine`（symlink farm）
- **i386-unix/ntdll.so 必須換成實體複本**（dladdr realpath 會穿透 symlink）
- i386-unix/wing.dll16.so、i386-windows/wing.dll16 換成本目錄版本
- `ln -s /usr/share /tmp/wineroot/share`
- 執行：`/tmp/wineroot/lib/wine/wine GAME.EXE`

## 實測結論（2026-07-19）
自編 wing 載入成功（+module: "fake Wine dll"），FIXME 消失（BITMAPINFO 有回填），
但 PTO2 的 seg5:0x5b9f crash **依舊** → BITMAPINFO 不是 crash 根因。
