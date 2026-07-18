# 打包說明

本目錄提供把「提督之決斷 II 繁體中文化補丁」打包成可執行成品的腳本。

## 目標平台

- **Linux**：AppImage（使用 Wine）
- **Windows**：`.zip`（使用 otvdm / WineVDM 相容層）

## 目前狀態

- [x] 遊戲文字與名稱已注入（`tools/build_patch.py`）
- [x] NPK UI 圖檔已重繪（MEIREI_000、MAKE_000、MAKE_001）
- [ ] Linux AppImage 腳本（骨架）
- [ ] Windows 打包腳本（骨架）
- [ ] 實機驗證（Wine 對 WinG 支援不完整，待解決）

## 已知問題

1. **Wine 的 WinG 支援不完整**：原版遊戲使用 WinG 加速繪圖，Wine 內建 `wing` 模組在 `WinGGetDIBPointer16` 會 page fault。即使放入原版 `WING.DLL`，Wine 仍優先使用內建實作。
2. **256 色顯示**：遊戲啟動時檢查顯示驅動是否為 256 色，Wine 預設 24-bit 會顯示錯誤。
3. **CD 音軌**：完整版需要原版 CD（`cd/*.bin/*.cue`）才能播放音樂與過場動畫。

## 建議解法

- **Linux AppImage**：使用 DOSBox-X + 合法 Windows 3.x（玩家自備），或等 Wine WinG 修正。
- **Windows**：使用 [otvdm](https://github.com/otya128/winevdm) 相容層，並附上 `使用說明.txt`。

## 玩家使用說明（預定）

詳細的安裝與啟動說明會寫在各平台包內的 `使用說明.txt`。
