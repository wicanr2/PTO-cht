# 提督決斷 II（P.T.O. II）英文加強版中文化計畫

> 狀態：執行中（已完成資產解包、譯表初版、NPK 編解碼、文字注入工具）

## 決策記錄

- 中文版本：**繁體中文（Big5）**
- 中文化深度：**包含所有文字訊息中文化**（需逆向 EXE 繪字管線）
- Linux AppImage 執行環境：**Wine**
- 翻譯稿：**由專案產生初譯，使用者審閱**
- Git repo：`https://github.com/wicanr2/PTO-cht`，commit 作者：`kimi`

## 1. 專案目標

把 `P.T.O. - Pacific Theater of Operations II (1996).zip`（英文 Windows 3.x / Win16 版）進行繁體中文化，並產出可執行成品：

- 圖像按鈕 / UI 靜態文字中文化（NPK 圖檔）
- 遊戲訊息中文化（.TK2 文字檔、資料表人名/艦名/武器名、EXE 內字串）
- Linux AppImage 可執行包
- Windows 可執行包（含必要 DLL / 相容層）

## 2. 現況盤點（已確認）

### 2.1 遊戲主體

| 路徑 | 說明 |
|------|------|
| `PTO-Paci/PTO2WIN/TEKE2WIN.EXE` | 主程式，Win16 NE（MS Windows 3.x） |
| `PTO-Paci/PTO2WIN/*.TK2` | 遊戲資源；分為 NPK 圖檔、純文字檔、二進位資料表 |
| `PTO-Paci/PTO2WIN/*DATA` | 無副檔名資料表：艦船、飛機、將領、地名等名稱 |
| `PTO-Paci/PTO2WIN/PLANE.PAL` | 調色盤 |
| `PTO-Paci/cd/*.bin/*.cue` | CD 映像檔（音軌 + 影片） |
| `PTO-Paci/Apps/` | WinG、VFW、Win32s、QuickTime 安裝檔 |

### 2.2 NPK 圖檔格式

多個 `.TK2` 以 `NPK016` 開頭，屬於光榮早期 NPK 點陣圖格式。初步測試已可用 [tzengyuxio/kaodata](https://github.com/tzengyuxio/kaodata) 的 `unpack_npk` 解出 PNG：

- `MEIREI.TK2`：命令面板（`ORDERS / To: / From:`）
- `LOGO.TK2`：KOEI 商標
- 其他如 `BMAP.TK2`、`PHASE.TK2`、`SHIP.TK2`、`SBT.TK2`、`WAKU1.TK2` 等皆待解包盤點

NPK 檔內含 16 色 RGB555 調色盤與 RLE-like 壓縮點陣，**缺點是尚未有可用的重新封裝工具**，計畫中須實作 `pack_npk`（`unpack_npk` 的逆運算）才能寫回中文化圖檔。

### 2.3 文字資源

| 檔案 | 類型 | 內容 |
|------|------|------|
| `EVMSG.TK2` | 純文字 | 歷史事件敘述 |
| `JOGEN.TK2` | 純文字 | 劇本開場提示 |
| `KAIMSG.TK2` | 純文字 | 會議/預算相關訊息 |
| `SCESETSU.TK2` | 純文字 | 劇本說明 |
| `SCESTART.TK2` | 純文字 | 劇本開頭文字 |
| `MSG1.TK2` | 加密/壓縮 | 可能是選單/UI 訊息，格式待解 |
| `KSNAME.TK2`、`SSNAME.TK2` | 字串表 | 艦船名、潛艇名 |
| `AMDATA`、`ARDATA`、`GRDATA`、`KDATA`、`PLDATA`、`SJDATA`、`STDATA`、`TKDATA` 等 | 二進位資料表 | 將領、艦船、飛機、坦克、武器名稱 |
| `TEKE2WIN.EXE` | 執行檔 | `APPMENU`、`CANCEL`、`ENTER`、`EXECUTE`、`ORDER` 等 UI 字串 |

### 2.4 字體渲染（最大未知數）

`TEKE2WIN.EXE` 為 Win16 NE，使用 WinG 繪圖。初步 `strings` 未發現 `TextOutA`/`CreateFontA` 等 GDI 字串，**極大可能是自訂 bitmap font 繪字**。若屬實，想把訊息中文化就必須：

1. 逆向繪字迴圈（`drawString` / `drawGlyph`）
2. 追加中文字型 atlas（16×16 或 24×24 點陣）
3. 用 2-byte hook 偵測中文 lead byte，跳轉自訂 stub 取 glyph

這條路已在 `retro-directdraw-hires-cjk` skill（Pacific General 案例）實證可行，是**風險最高但也最徹底**的方案。

## 3. 可選技術路線

| 路線 | 做法 | 優點 | 缺點 | 適用情境 |
|------|------|------|------|----------|
| **A. 純資產替換（保守）** | 只改 NPK 圖檔中的靜態英文標籤；純文字 TK2 與資料表維持英文或只做 ASCII 長度內替換 | 風險低、不必碰 EXE | 無法真正顯示中文訊息；資料表無法中文化 | 只想要按鈕圖中文化 |
| **B. 引擎字體 patch（建議）** | 在 A 的基礎上，逆向 EXE 繪字管線，追加 CJK 2-byte hook + 字型 atlas，把所有文字改為中文編碼 | 完整中文化 | 工程量大、需 RE EXE、不一定一次成功 | 目標是「訊息也中文化」 |
| **C. 移植級重製（不建議）** | 把遊戲邏輯重寫成 SDL2 引擎 | 最乾淨、最好維護 | 數月以上、超出本專案範圍 | 僅供參考 |

**建議採用路線 B**，但把 EXE patch 設為可獨立關閉的階段：若 RE 發現不可行，則退回 A 並如實回報。

## 4. 建議工作階段

### Phase 0：工具鍊與環境（1–2 天）

- [ ] 把 `P.T.O. ... .zip` 完整解壓到 `assets/origin/`
- [ ] 建立 Python 工具目錄 `tools/`，包含：
  - `npk_decode.py`：NPK016 → PNG（已驗證概念）
  - `npk_encode.py`：PNG → NPK016（待實作 pack）
  - `tk2_text_extract.py`：抽出純文字 TK2 與資料表字串
  - `exe_strings.py`：抽出 TEKE2WIN.EXE 內可見字串
- [ ] 建立 `translation/` 目錄，存放譯表（CSV/TSV）

### Phase 1：資產解包與盤點（2–3 天）

- [ ] 批次解出所有 `NPK016` 圖檔到 `assets/images/`
- [ ] 標記哪些圖檔含 UI 文字（按鈕、面板、標題），建立對照表
- [ ] 抽出所有純文字 TK2、資料表名稱、EXE 字串，建立第一版譯表
- [ ] 分析 `MSG1.TK2` 加密/壓縮方式（可能是 XOR、LS11 或自定壓縮）

### Phase 2：NPK 重新封裝驗證（2 天）

- [ ] 實作 `pack_npk`，目標：PNG → NPK016 → PNG 與原圖像素級一致
- [ ] 以 `MEIREI.TK2` 為第一個測試案例：把 `ORDERS` 改成中文標籤並寫回
- [ ] 跑遊戲驗證圖檔能被正確載入

### Phase 3：中文字型與 EXE Patch（風險最高，1–2 週）

- [ ] 用反組譯（capstone / objdump / Ghidra）定位 `TEKE2WIN.EXE` 的繪字迴圈
- [ ] 確認字高是否從 font header memory-read；若是，走「路徑 C」最低成本
- [ ] 選定編碼：建議 **Big5**（繁中 lead byte `0x81–0xFE`）或自訂 dense 編碼
- [ ] 製作所需中文字元子集 atlas（16×16/24×24，依螢幕解析度決定）
- [ ] 在 EXE 新增 `.cjk` 區段或使用 code cave，寫入 2-byte hook stub
- [ ] 驗證：中文訊息正確顯示、不閃退、不亂碼

### Phase 4：翻譯與資產回填（與 Phase 3 並行）

- [ ] 完成 NPK UI 圖檔中文化（GIMP / ImageMagick batch）
- [ ] 完成純文字 TK2、資料表名稱、EXE 字串翻譯
- [ ] 所有翻譯經由 `tools/inject_*.py` 寫回遊戲檔案

### Phase 5：打包（2–3 天）

Linux AppImage：

- [ ] 方案選一：
  - **Wine 方案**：bundle 最小 Wine + 遊戲 + 中文化 patch
  - **DOSBox-X + Windows 3.x 方案**：需使用者自行提供合法 Windows 3.x 安裝媒體
- [ ] 撰寫 `packaging/build_appimage.sh`，產生單一 `.AppImage`
- [ ] 附 `使用說明.txt`：FUSE 問題、執行權限

Windows：

- [ ] 使用 [WineVDM / otvdm](https://github.com/otya128/winevdm) 做 Win16 相容層，打包遊戲 + DLL + 啟動器
- [ ] 撰寫 `packaging/build_windows.sh`，產生 `.zip`
- [ ] 附 `使用說明.txt`：SmartScreen、otvdm 說明

### Phase 6：驗證與文件（2 天）

- [ ] 在 Wine / Xvfb 下跑啟動、主選單、進入劇本、存檔截圖
- [ ] 跑 `game_tester` 風格驗證：至少 title → 新遊戲 → 劇本選擇 → 進入遊戲 → 存檔
- [ ] 撰寫 README（玩家向繁中）與 `docs/FORMATS.md`（技術向）

## 5. 風險與待確認事項

| 風險 | 影響 | 對策 |
|------|------|------|
| NPK `pack` 實作不完全 | 圖檔寫回後遊戲讀取失敗 | round-trip 驗證；必要時逐 byte 比對 |
| EXE 繪字邏輯複雜難 patch | 訊息無法中文化 | 設為可關閉階段；退回純圖像中文化 |
| 中文字型 atlas 過大 | Win16 記憶體限制、區段放不下 | 只收錄實際用到的字（子集化），16×16 優先 |
| Win16 在現代 Windows 無法原生執行 | Windows 包跑不起來 | 使用 otvdm；或在 README 說明需 32-bit Windows / Wine |
| CD 音軌/影片依賴 | 打包版可能缺過場 | full 包保留 CD 映像；slim 包需玩家自備原版 CD |
| 版權問題 | 不可公開散佈原版遊戲資料 | 公開 repo 只放 patch 工具與自製資產；完整包僅本機使用 |

## 6. 需要你確認的事項

1. **中文版本**：要繁體中文（Big5）還是簡體中文（GBK）？
2. **訊息中文化深度**：
   - 只做圖像按鈕中文化？
   - 還是要包含所有對話、事件、資料表名稱的完整中文化？（後者需要 EXE patch）
3. **Linux AppImage 執行方式偏好**：
   - 使用 Wine（較大但無需 Windows 授權）
   - 使用 DOSBox-X + Windows 3.x（較小但你需提供合法 Windows 3.x 安裝檔）
4. **你是否已有翻譯稿**，還是要由我們產生初譯後請你審閱？

請回覆以上問題，我會把計畫定案並開始 Phase 0。
