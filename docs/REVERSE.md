# 逆向工程紀錄

## 已確認

### 執行檔格式

- `TEKE2WIN.EXE`：Win16 NE（MS Windows 3.x），837,632 bytes
- 117 個 segment，入口點 `b:43cc`
- 使用模組：KERNEL、USER、MMSYSTEM、TOOLHELP、WING
- 資源內含：
  - `APPMENU`：`E&xit`、`&Help`、`&Contents`、`&Search By Keyword`、`&How To Use Help`、`&About Version Information`
  - `APPVERSION` dialog：`P.T.O. II`、`Fixed Sys`、`Pacific Theater of Operations II`、`Version 1.0`、`(C) Copyright KOEI Corporation 1995`、`OK`
  - VERSION info：含 Shift-JIS 字串「提督の決断II」

### 資源檔格式

- `.TK2` 分三類：
  - `NPK016` 圖檔（已可解碼 / 編碼）
  - 純文字檔（EVMSG、JOGEN、KAIMSG、SCESETSU、SCESTART、KSNAME、SSNAME）
  - 二進位資料表（ARDATA、GRDATA、KDATA、KSDATA、NCTDATA、PLDATA、SJDATA、SSDATA、STDATA、TKDATA）
- `MSG1.TK2`、`PLANE.TK2`、`TANK.TK2` 為 XOR `0x96` 加密
  - `MSG1.TK2` 為事件訊息，已解出並翻譯
  - `PLANE.TK2`、`TANK.TK2` 為圖形資料，不應視為文字

### 執行問題

- Wine 內建 `wing` 模組在 `WinGGetDIBPointer16` 會 `page fault`（`setting BITMAPINFO not supported`）
- 原版 `WING.DLL` 已放入 prefix，但 Wine 仍優先使用內建實作
- 遊戲啟動時檢查 256 色顯示，Wine 預設 24-bit 會顯示錯誤

## 待解決

### 1. 中文字型

- 遊戲內文字疑似自訂 bitmap font（非 GDI）
- 尚未定位 `drawString` / `drawGlyph` 與 font data
- 可能方向：
  1. 在 EXE 中尋找 font atlas（16x16 或 8x16 點陣）
  2. 用 `ndisasm` 對 segment 1–11 做反組譯，搜尋對字串的引用
  3. 若 font 為 16x16，可考慮用 Big5 2-byte hook（參考 `retro-directdraw-hires-cjk`）

### 2. WinG 相容

- 需要能正確執行 WinG 的環境：
  - Wine 修正 `WinGGetDIBPointer16`（需 patch Wine）
  - DOSBox-X + 合法 Windows 3.x
  - otvdm（Windows 上執行，Linux 無法直接驗證）

### 3. 包裝

- Windows：`packaging/build_windows.sh` 已產生 `dist/PTO2-cht-windows.zip`（otvdm + 中文化遊戲）
- Linux：`packaging/build_appimage.sh` 產生 AppDir，但需解決 Wine WinG 問題
