# 工作階段備忘（供轉移電腦用）

## 專案目標

把 `P.T.O. - Pacific Theater of Operations II (1996).zip`（英文 Windows 3.x / Win16 版）繁體中文化，並打包成 Linux AppImage / Windows 可執行包。

## 已完成

- 專案結構與 `.gitignore`（原版遊戲資料與衍生資產不上 git）
- `PLAN.md`、`README.md`（含遊戲介紹、1995/1996 版本說明、為何中文化這個版本）
- NPK016 解碼/編碼工具（`tools/npk.py`），MEIREI round-trip 驗證通過
- 文字萃取工具：
  - `tools/extract_text.py`（純文字 TK2 + EXE 字串）
  - `tools/extract_data_names.py`（資料表名稱）
  - `tools/extract_msg1.py`（MSG1 XOR 0x96）
- 初始繁體中文譯表（已上 repo）：
  - `translation/source/text_tk2.csv` → `translation/target/text_tk2.csv`
  - `translation/source/data_names.csv` → `translation/target/data_names.csv`
  - `translation/source/msg1_strings.csv` → `translation/target/msg1_translated.csv`
  - `translation/source/ui_images.csv`
  - `translation/glossary.csv`
- 注入工具：
  - `tools/inject_text_tk2.py`
  - `tools/inject_names.py`（超長會截斷）
  - `tools/inject_msg1.py`
  - `tools/inject_exe_strings.py`（APPMENU / APPVERSION）
- UI 圖檔中文化：`tools/render_ui_images.py`（MEIREI_000、MAKE_000、MAKE_001）
- 打包腳本：
  - `packaging/build_windows.sh`（otvdm + 中文化遊戲，可產生 zip）
  - `packaging/build_appimage.sh`（骨架，需 appimagetool + 解決 Wine WinG 問題）
- `tools/build_patch.py`：一鍵產生 `assets/patched/PTO2WIN`

## 目前阻塞

1. **Wine WinG 支援不完整**：`WinGGetDIBPointer16 ... setting BITMAPINFO not supported` → page fault。原版 WING.DLL 放入 prefix 仍走內建。
2. **256 色顯示檢查**：遊戲啟動時檢查顯示驅動，Wine 24-bit 會擋下。
3. **中文字型**：遊戲內文字疑似自訂 bitmap font，尚未定位 `drawString` / `drawGlyph` / font data。需逆向 EXE 才能讓訊息真正顯示中文。

## 下一步建議

1. 在新電腦上先跑 `tools/build_patch.py` 確認能重建 `assets/patched/PTO2WIN`。
2. 用 `packaging/build_windows.sh` 產生 Windows zip，在 Windows 機器上用 otvdm 測試。
3. 繼續逆向 `TEKE2WIN.EXE` 的繪字管線（參考 `docs/FONT_PATCH_PLAN.md` 與 `docs/REVERSE.md`）。
4. 若 Wine WinG 無法解決，考慮 DOSBox-X + 合法 Windows 3.x，或建立 wrapper DLL。

## 重要檔案

- 原版遊戲：`P.T.O. - Pacific Theater of Operations II (1996).zip`
- 工具：`tools/`
- 譯表：`translation/`
- 文件：`docs/`、`PLAN.md`、`README.md`、`WORKLIST.md`、`AGENTS.md`
- 打包：`packaging/`
- 此 session 記憶：`session_backup/`（kimi-code session 資料）

## Git

- Repo：`https://github.com/wicanr2/PTO-cht`
- 分支：`master`
- 最新 commit 已 push
