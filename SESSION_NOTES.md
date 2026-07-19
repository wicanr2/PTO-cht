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

## 2026-07-19 深夜收尾狀態（明天接續點）

### 今天完成
- EXE 內嵌字串翻譯注入（1349/1782，`inject_exe_ui_strings.py`）
- Big5 GDI 字型 patch（`patch_big5_font.py`）
- 反組譯地圖（`tools/ne_disasm.py` + `docs/disasm/`）
- 繁體中文 Win3.1 ISO 取得並裝進 86Box（`win31cht_hdd.img`，ET4000AX 內建 256 色驅動）
- **86Box 繁中線實測：開場動畫可播、CD 音樂正常、主選單可進、視窗標題中文正常**
- Wine 線結案（256 色 bypass + grpseg 預載第一層修復整合進 `patch_wine_checks.py`；第二層 selector crash 未修，暫停）
- `play.sh` 一鍵啟動（vm_play，DISK BOOT FAILURE 已修：nvr/CMOS 與殘留 process 問題）

### 明天第一件事
**主選單亂碼**：遊戲自繪文字全亂（Big5 被當單 byte 拆），視窗標題正常。假說：seg11:0x9016 日版 DBCS glyph 分派器的 SJIS lead-byte 範圍（0x81-0x9F/0xE0-0xFC）不符 Big5（0xA1-0xFE）。
→ `.venv/bin/python tools/ne_disasm.py assets/patched/PTO2WIN/TEKE2WIN.EXE --func 11:9016` 開始，找 lead-byte 檢查 patch 成 0x81-0xFE。
修好後：映像同步 play_hdd.img → `packaging/build_local_full.sh` → 驗收 → push。

### 環境注意
- 測試 VM 與 play VM 不可同時跑（nvr/CMOS 會互寫 → DISK BOOT FAILURE）
- Xvfb :95/:96/:97/:98 可能還開著，可用可殺
- /tmp/winebuild、/tmp/wineroot、/tmp/teke_wine 是 Wine 線保留環境（重開機會消失，需重建就照 docs/WING_DLL16_BUILD.md）
