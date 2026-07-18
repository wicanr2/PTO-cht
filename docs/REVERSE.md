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

### 執行問題（2026-07-18 實測更新）

- **256 色已解**：用 `Xvfb :95 -screen 0 1024x768x8` 提供 8-bit 顯示即可通過檢查
- **Wine 16-bit loader 不吃 DllOverrides**：`MODULE_LoadModule16` 無條件優先載入內建 `wing.dll16`；繞道 = `tools/patch_wine_wing.py` 把 EXE import `WING`→`XING` + 提供改名後的原生 `XING.DLL`
- **builtin wing.dll16**：WinG init 全部成功（CreateDC/CreateBitmap/GetDIBPointer 回傳有效 segptr），主視窗可建立（中文化標題正常）；唯一缺口是 WinGGetDIBPointer 不填 BITMAPINFO
- **原生 XING.DLL**：可被載入，但 WinGCreateBitmap 內部需要 display driver DIB engine（WINGDIB.DRV），Wine 沒有 → 回 NULL → 遊戲 NULL memset 當機（seg11:50c6）
- **目前擋路點**：builtin 路線下，遊戲完成 WinG+palette 後對 handle 0 做 `_llseek/_hread(0xfb76)/_lclose`（全失敗），然後在 seg5:5b9f 的 huge-pointer 正規化函式 NULL 解參照。整個 trace 中遊戲**從未發出 file-open 呼叫**，handle 0 來源待查（原版 EXE 同點同樣 crash，與中文化無關）

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
