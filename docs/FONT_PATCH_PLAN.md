# 中文字型 Patch 計畫

## 現況

- 遊戲內文字疑似自訂 bitmap font（非 GDI）
- APPMENU / APPVERSION 走 Windows 資源，已可中文化
- MSG1 / EVMSG 等純文字檔已可注入 Big5 中文，但遊戲若無中文字型會顯示亂碼

## 目標

讓遊戲內所有文字（事件、對話、資料表名稱）能顯示繁體中文。

## 可能方案

### 方案 A：2-byte Hook（參考 Pacific General）

1. 逆向 `TEKE2WIN.EXE` 找出 `drawString` / `drawGlyph`
2. 確認字高是否從 font header memory-read
3. 製作 Big5 子集 atlas（16x16 或 24x24）
4. 用 code cave / 新增 PE section 寫入 stub，偵測 lead byte 後跳轉自訂 glyph 查表
5. 保留 ASCII 路徑

**優點**：最徹底，中文清晰  
**缺點**：工程量大，需完整 RE

### 方案 B：替換整個字型檔

1. 找出遊戲字型檔（可能在 EXE 或 .TK2）
2. 把 ASCII glyph 區段替換成中文字型（或追加 Big5 區段）
3. 修改字串編碼為 Big5

**優點**：不用改 EXE 邏輯  
**缺點**：需先找到字型檔格式

### 方案 C：外掛 overlay（不建議）

- 用 Wine / otvdm 外掛 overlay 顯示中文
- 缺點：與遊戲畫面不同步、體驗差

## 下一步

1. 用 `ndisasm` / `capstone` 對 segment 1–11 反組譯，搜尋對字串的引用
2. 找出 font data 位置（嘗試在 EXE 中掃描 16x16 點陣 pattern）
3. 若找到 `drawString`，評估 2-byte hook 可行性
4. 製作 Big5 atlas（用 `build_cjk_font.py` 概念）
