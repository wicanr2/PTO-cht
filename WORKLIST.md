# 工作清單（Worklist）

## 已完成

- [x] 專案目錄結構與 `.gitignore`
- [x] 遊戲檔案解壓（`assets/origin/`）
- [x] `PLAN.md`、`README.md`（含遊戲介紹、1995/1996 版本說明、機制）
- [x] NPK016 解碼 / 編碼工具（`tools/npk.py`）
  - 已批次解出 690 張 PNG 到 `assets/images/`
  - `MEIREI.TK2` 解碼 → 編碼 → 解碼 round-trip 驗證通過
- [x] 文字資源萃取工具
  - `tools/extract_text.py`：純文字 TK2 + EXE 字串
  - `tools/extract_data_names.py`：資料表名稱
  - `tools/extract_msg1.py`：MSG1（XOR 0x96）文字
- [x] 初始繁體中文譯表（已上 repo）
  - `translation/source/text_tk2.csv` → `translation/target/text_tk2.csv`
  - `translation/source/data_names.csv` → `translation/target/data_names.csv`
  - `translation/source/msg1_strings.csv` → `translation/target/msg1_translated.csv`
  - `translation/glossary.csv`
- [x] 注入工具與測試
  - `tools/inject_text_tk2.py`：EVMSG/JOGEN/KAIMSG/SCESETSU/SCESTART/KSNAME/SSNAME
  - `tools/inject_names.py`：ARDATA/GRDATA/KDATA/KSDATA/NCTDATA/PLDATA/SJDATA/SSDATA/STDATA/TKDATA
  - `tools/inject_msg1.py`：MSG1（已驗證 Big5 中文可寫回）
  - `tools/inject_exe_strings.py`：APPMENU / APPVERSION 對話框字串
- [x] Git 設定（作者：kimi）、已 push 到 `wicanr2/PTO-cht`

## 進行中

- [ ] 逆向 `TEKE2WIN.EXE` 繪字管線與字體格式
  - 目前發現：APPMENU / APPVERSION 走 Windows 資源，可安全取代
  - 遊戲內文字疑似自訂 bitmap font，尚未定位 `drawString` / `drawGlyph`
- [ ] NPK UI 圖檔中文化（等 image review 結果）

## 待辦

- [ ] 找出 MSG1 雜訊開頭的精確規則，提升譯文對齊品質
- [ ] 產生中文字型 atlas（Big5 子集）與 EXE 2-byte hook（若可行）
- [ ] NPK 圖檔中文標題／按鈕重繪與回填
- [ ] 打包：Linux AppImage（Wine）與 Windows（otvdm）
- [ ] 實機驗證：主選單 → 新遊戲 → 劇本 → 存檔 → 離開
- [ ] 玩家文件：`packaging/README.md`、使用說明

## 已知風險 / 阻塞

- **執行環境**：Wine 對 WinG 支援不完整（`WinGGetDIBPointer16 ... setting BITMAPINFO not supported` → page fault）。原版 `WING.DLL` 已放入 prefix，但 Wine 仍走內建實作。可能需要：
  - 使用 DOSBox-X + 合法 Windows 3.x
  - 或修補 Wine / 改用其他相容層
- **固定長度欄位**：資料表名稱受原檔案長度限制，部分中文譯名需縮短或截斷（已先截斷處理，後續可人工調整）
- **MSG1 對齊**：部分文字開頭黏有二進位雜訊，目前用 regex 抽出後由翻譯 agent 清理，仍須人工複核
