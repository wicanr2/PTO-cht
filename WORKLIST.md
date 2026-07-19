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

- [ ] **86Box 執行驗證（主線）**：`vendor/86box/`
  - 86Box 4.2.1 AppImage + MS-DOS 6.22（`msdos_hdd.img`）+ Windows 3.1
  - 遊戲 CD 映像掛載：`assets/origin/PTO-Paci/cd/Pacific.Theater.of.Operations.2.cue`
  - 已跑起 Windows 3.1 + 遊戲至 KOEI logo；需繼續推進到主選單與遊戲內
  - 中文化檔案用 `tools/fat16_edit.py` / `fat16_add.py` 注入 `msdos_hdd.img` 後在 86Box 內驗證
  - VM 設定：`vendor/86box/vm421/86box.cfg`（注意 `gfxcard = none` 待補顯示卡設定）
- [ ] 逆向 `TEKE2WIN.EXE` 繪字管線與字體格式（背景 subagent 進行中）
  - 目前發現：APPMENU / APPVERSION 走 Windows 資源，可安全取代
  - 遊戲內文字疑似自訂 bitmap font，尚未定位 `drawString` / `drawGlyph`
- [ ] NPK UI 圖檔中文化：**主體完成**（MEIREI_000、MAKE_000/001、END_SF_001、OP4_BC_003 已封回）
  - 僅剩 NWEAPON_000–005（3-4px 微小英文標註，低於可靠重繪下限，暫緩，需先從遊戲字串對照原文）

## 已完成（2026-07-19 追加）

- [x] UI 圖檔中文化封回管線：`tools/patch_ui_tk2.py` + 接入 `tools/build_patch.py`
- [x] 逆向工具：`tools/ne_relocs.py`（NE relocation 解析）、`tools/patch_wine_wing.py`（XING hack）
- [x] FAT16 映像工具：`tools/make_fat16_img.py` / `fat16_edit.py` / `fat16_add.py`
- [x] Wine 執行問題調查（見 SESSION_NOTES「關鍵調查結論」）
- [x] 參考環境：86Box + MS-DOS 6.22 跑起 Windows 3.1 + 遊戲至 KOEI logo
- [x] otvdm 升級 v0.9.0，Windows 包使用說明擴充（commit fd33267）
- [x] `pto2_cd.iso` 製作（vendor/86box，供 86Box 掛載）

## 已完成（2026-07-19 盤點補登）

- [x] **翻譯覆蓋率驗證**：`text_tk2` 383/427 列，缺的 44 列全是 PLANE.TK2（38）/TANK.TK2（5）圖形資料誤萃 + MSG1 1 列 → 純文字檔翻譯實質 100%；`data_names` 1832/1832、`msg1` 262/262 全覆蓋
- [x] **UI 全圖盤點**：690 張中逐一目視檢查（MMAP/SHIP/LAND 為地圖與單位圖除外），含英文文字僅 MEIREI_000、MAKE×2、END_SF_001、OP4_BC_003（日文標題）、NWEAPON×6（3-4px 微字，無法可靠重繪，暫緩）；LOGO 為商標/版權保留不譯
- [x] **END_SF_001（THE END→完）、OP4_BC_003（日文標題→「第二次世界大戰 提督的決斷II」）重繪並封回**，`ui_images.csv` 同步更新
- [x] **NPK palette 結論**：所有 TK2 chunk 的 16 色 palette 欄位位元組完全相同 → 該欄位不是真色板（遊戲應用全域 256 色盤/逐場景色盤）。PNG 預覽色偏屬預期，round-trip 編碼安全，**不阻塞改圖**，原「palette 異常」風險解除
- [x] **中文字型逆向定案**：遊戲無自訂字型，全部走 GDI CreateFont+TextOut。`tools/patch_big5_font.py` 完成兩個 byte patch（`0x97cad` charset 0x80→0x88、`0xc9f8e` 細明朝体→新細明體）並接入 `build_patch.py`；全段掃描確認無 SJIS lead-byte 閘門，Big5 不會被拆錯。詳見 `docs/FONT_PATCH_PLAN.md`（方案 G）
- [x] **EXE 內嵌字串翻譯注入**（2026-07-19）：`tools/extract_exe_strings2.py` 萃出 0xC0000–0xCBE00 共 1782 字串，1349 已譯（75.7%，留空為檔名/格式符/class name），`tools/inject_exe_ui_strings.py` 注入並接入 `build_patch.py`；NEW GAME→新遊戲、劇本名與劇情長文全數中文化，0 筆超長失敗
- [x] **Wine wing.dll16 修補備妥**：`vendor/wine-src/wine-9.0/`（9.0 源碼），`WinGGetDIBPointer16` 已補 BITMAPINFO 填寫，待確認 crash 根因後決定是否重編
- [x] **256 色/解析度檢查 bypass**（2026-07-19）：`tools/patch_wine_checks.py` **v2**（只 nop 四個失敗分支：file 0x92b3e/0x92b45/0x92b64/0x92b6d，保留 surface 註冊鏈；v1 整函式 retf 會造成 count=0 假像，已作廢），24-bit Xvfb 實測通過；待接入 `build_patch.py`
- [x] **WinG crash 根因確認**（2026-07-19）：原版/patched 行為一致（非中文化迴歸）；crash @ seg5:0x5b9f 是遊戲讀 `WinGGetDIBPointer16` 未回填的 BITMAPINFO（+0x0c biPlanes）→ NULL+0x0C。Wine builtin wing.dll16 的已知缺陷，遊戲側無分支可跳 → 解法：重編 wing.dll16（源碼與修補已備於 vendor/wine-src）
- [x] **反組譯函數地圖**（2026-07-19）：`tools/ne_disasm.py`（NE 完整解析 + capstone 16-bit + anchor-guided 掃描），產出 `docs/disasm/`：117 segments、3,673 函數、14,363 far call 全解析、import 呼叫點交叉驗證通過、三 bug 點反組譯摘錄。是未來 Win32 重編的基礎資產
- [x] **繁體中文 Win3.1 取得**（2026-07-19）：3.10.0.151 繁體中文版 ISO（22.5MB）+ S3/SB16/WinG/Win32s 驅動，存 `vendor/win31cht/`（來源：使用者提供之 Google Sites 教學頁的 Drive 連結）

## 待辦

- [ ] 找出 MSG1 雜訊開頭的精確規則，提升譯文對齊品質
- [ ] 確認執行環境 codepage 950：86Box 內 Win3.1 需為繁中（或裝新細明體+cp950），否則中文亂碼；otvdm 包需繁中 Windows
- [ ] 打包：
  - Windows `packaging/build_windows.sh` 已可產生 `dist/PTO2-cht-windows.zip`（otvdm + 中文化遊戲 + 使用說明）
  - Linux `packaging/build_appimage.sh` 已產生 AppDir；Wine WinG 問題難解，**主線改為 86Box 方案**（考慮 AppImage 內打包 86Box + DOS/Win3.1 映像）
- [ ] 實機驗證（86Box）：主選單 → 新遊戲 → 劇本 → 存檔 → 離開
- [ ] 玩家文件：`packaging/README.md`、使用說明

## 已知風險 / 阻塞

- **執行環境**：Wine 對 WinG 支援不完整（`WinGGetDIBPointer16 ... setting BITMAPINFO not supported` → page fault），原生 WING.DLL 也需 WINGDIB.DRV 而 Wine 沒有。**Wine 路線已判定死路，主線改用 86Box**（`vendor/86box/`，MS-DOS 6.22 + Windows 3.1，已跑至 KOEI logo）。
- ~~**NPK palette**~~：已查明——16 色 palette 欄位為固定假值，預覽色偏屬正常，round-trip 安全，非風險。
- **固定長度欄位**：資料表名稱受原檔案長度限制，部分中文譯名需縮短或截斷（已先截斷處理，後續可人工調整）
- **MSG1 對齊**：部分文字開頭黏有二進位雜訊，目前用 regex 抽出後由翻譯 agent 清理，仍須人工複核
