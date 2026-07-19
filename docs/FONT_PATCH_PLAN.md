# 中文字型 Patch 計畫（已定案：GDI 字型 patch）

## 定案結論（2026-07-19）

遊戲**沒有自訂 bitmap font**，所有遊戲內文字經 **GDI `CreateFont` + `TextOut`** 渲染
（反組譯實證，詳 `docs/REVERSE.md`）。因此原方案 A（2-byte hook）與方案 B（換字型檔）
都不適用，改採最直接的 **方案 G：patch CreateFont 參數**。

## 文字管線（seg11 = 繪圖/字型模組）

- `CreateFont` 呼叫點 `seg11:0x66bc`：height=-16, width=8, charset=0x80（SHIFTJIS），
  facename=SJIS「細明朝体」
- `TextOut` 唯一呼叫點 `seg11:0x90f8`（count=2，一次一個雙位元組字），
  渲染進 1bpp 32x16 DIB 後 GetDIBits 讀回當 mono glyph，再經 `seg11:0x8be8`
  （1bpp→8bpp 依 fg/bg 展開）與 blitter（`seg11:0x5195`/`0x51f4`）貼進 WinG DIB
- USER 無 DrawText import → 全部文字確定走 TextOut

## 已施作的 patch（`tools/patch_big5_font.py`，接入 `tools/build_patch.py`）

| file offset | 原值 | 新值 | 說明 |
|---|---|---|---|
| `0x97cad` | `68 80 00` | `68 88 00` | CreateFont lfCharSet：SHIFTJIS(0x80) → CHINESEBIG5(0x88) |
| `0xc9f8e` | SJIS「細明朝体」+NUL（9 bytes） | Big5「新細明體」+NUL（9 bytes） | facename，同長度原位覆蓋 |

工具行為：patch 前驗證目標 bytes 符合預期，不符則報錯不寫入；冪等可重複執行。
目標檔案 `patch/TEKE2WIN.EXE`（不存在則從 origin 複製，不動 origin）。

## Lead-byte 檢查（原方案 A 想 hook 的點）：結論 = 不需要

全 code segment 完整掃描後，文字繪製路徑**不存在 SJIS lead-byte 範圍判斷**：

- `cmp r8, {0x81,0x9F,0xA0,0xE0,0xFC}` 群集只在 CRT startup argv 解析（seg11:0x4949–0x4a99）
- 無 `test al,0x80` 字串走訪、無 `shl ax,8` 字碼合成、無 mbctype 查表
- Big5 lead byte（0x81–0xFE）不會被任何閘門拆錯

## 驗證方式

1. `python3 tools/build_patch.py` 重建（內含本 patch）
2. 檢查 `patch/TEKE2WIN.EXE`：`0x97cad` = `68 88 00`、`0xc9f8e` = `b7 73 b2 d3 a9 fa c5 e9 00`
3. **實機驗證（待做）**：需系統 codepage = 950 的環境
   - Windows：otvdm（`dist/PTO2-cht-windows.zip`）+ 繁中系統或 locale emulator，系統需有新細明體
   - Wine：需解決 WinG 問題（見 REVERSE.md 待解決 2）+ zh_TW locale
   - 進遊戲看事件訊息（MSG1/EVMSG 已注入 Big5 中文）是否正常顯示

## 殘餘風險

- 系統 codepage 非 950 時，Big5 bytes 會被 TextOut 當其他編碼解讀 → 亂碼（環境需求，非 patch 問題）
- 英文版逐字渲染鏈（string walker → glyph 取得）未 100% 定位；若實測發現某路徑仍把
  0xA1–0xFE 當單 byte，再針對該處補 hook
- Wine 下 WinG 不相容問題尚未解，遊戲本身跑不起來時字型 patch 無從驗證
