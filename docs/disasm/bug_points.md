# 已知 bug 點反組譯摘錄與解讀

由 `tools/ne_disasm.py --func seg:off` 產生（2026-07-19）。`; ->` / `; imm <-` 註解是
relocation 解析結果（檔案中的立即值是修復鏈佔位值，執行時由 loader 替換）。

## 1. WinG crash：seg5:5b9f（huge-pointer 欄位讀取函式）

函數 `seg5:0x5b72..0x5c4c`（218 bytes，**34 個呼叫點**，見 far_call_graph.csv）。

```
5b78: mov  ax, [bp+0xe]     ; ┐ dx:ax = 32-bit offset（huge 物件內位移）
5b7b: mov  dx, [bp+0x10]    ; ┘
5b7e: add  ax, [bp+0xa]     ; ┐ 加上另一個 32-bit 值（低 16 在 [bp+0xa]，進位入 dx）
5b81: adc  dx, 0            ; ┘
5b84: mov  cx, __AHSHIFT    ; = 3（KERNEL.#113 equate，loader 填常數）
5b87: shl  dx, cl           ; dx = 高位 * 8 = selector 增量（每 64KB = __AHINCR 8）
5b89: add  dx, [bp+0xc]     ; + base selector → 正規化後的 selector
5b8c: mov  bx, ax           ; bx:si = 正規化後 base offset:selector
5b8e: mov  si, dx
5b90: add  ax, 0x0c         ; ┐ 讀 +0x0c 欄位；offset 溢位時 selector += __AHINCR(8)
5b93: sbb  cx, cx           ; │
5b95: and  cx, __AHINCR     ; │（KERNEL.#114 equate）
5b99: add  dx, cx           ; ┘
5b9b: mov  di, ax
5b9d: mov  es, dx
5b9f: mov  al, es:[di]      ; <== CRASH：es = 0（NULL selector）
```

之後以同樣模式讀 +0x0d / +0x0e / +0x0f 共 4 個 byte，`si = b0+b1`、`di = b2+b3`。
**解讀**：這是 Microsoft C huge-model 的「huge 結構體欄位讀取」helper——參數是
huge base 指標（offset@[bp+0xa..]、selector@[bp+0xc]）加 32-bit 索引，回傳某 record
+0x0c..0x0f 的兩個 16-bit 值。crash 是因為呼叫者傳入的 base selector = 0：
與 REVERSE.md 的結論一致（遊戲對 handle 0 做 `_llseek/_hread` 失敗後，沒有檢查就
把 NULL huge pointer 餵進來）。修復方向：在 34 個呼叫點的上游找到該 buffer 的
配置/讀檔路徑（`KERNEL._hread` 唯一呼叫點在 `seg3:0x2c50`，`_llseek` 在
`seg3:0x2c3b`，`OpenFile` 在 `seg11:0x205b`，見 imports.md）。

## 2. NULL memset：seg11:50c6

函數 `seg11:0x5094..0x50cf`（59 bytes，1 個呼叫點）。386 32-bit 寫法：

```
5094: push bp / mov bp,sp / push es / push edi
509a: xor  edi, edi
509d: les  di, [bp+0xa]        ; es:edi = 目的 far 指標
50a0: movsx eax, word [bp+6]   ; ┐ ecx = w*h/4（dword 數）
50a5: movsx ecx, word [bp+8]   ; │
50aa: mul  ecx                 ; │
50b0: shr  ecx, 2              ; ┘
50b4: cmp  word [bp+0xe], 7    ; ┐ 填色：參數==7 → 0x00000000
50ba: mov  eax, 0x10101010     ; ┘ 否則 0x10（8bpp palette index 16）
50c5: cld
50c6: rep stosd es:[edi], eax  ; <== CRASH：es:edi = 0:0
```

**解讀**：DIB 清除函式。呼叫者（唯一，見 functions_index callers）把
`WinGCreateBitmap`（seg11:0x98cf）/`WinGGetDIBPointer`（seg11:0x65ba、0x6686）
回傳的指標未檢查直接傳入；原生 XING.DLL 下 CreateBitmap 回 NULL → es:edi=0:0 →
page fault。patch 點可選 `50c5`/`50c6` 前加 `es:edi` 非零檢查，或修上游呼叫者。

## 3. 256 色檢查：seg11:0x1500

函數 `seg11:0x1500..0x1632`（WinMain 前段初始化，含 RegisterClass/CreateWindow）。

```
150f: push 0
1511: lcall USER.GetDC              ; hdc = GetDC(NULL)
151c: push di / push 0x26           ; 0x26 = 38 = RASTERCAPS
151f: lcall GDI.GetDeviceCaps
1524: and  ax, 0x100                ; RC_PALETTE
1527: mov  si, ax
1529: push di / push 0x68           ; 0x68 = 104 = SIZEPALETTE
152c: lcall GDI.GetDeviceCaps
1531: mov  [bp-2], ax
1534: push 0 / push di
1537: lcall USER.ReleaseDC
153c: or   si, si                   ; RC_PALETTE 有嗎？
153e: je   0x1547                   ; 無 → 錯誤
1540: cmp  word [bp-2], 0x100       ; SIZEPALETTE == 256？
1545: je   0x1550                   ; 是 → 繼續（0x1550 檢查解析度 ≥ 640x400…）
1547: push 0x161d                   ; 錯誤訊息字串（seg110 selector）
154a: push 0x28                     ; MB_OK|MB_ICONINFORMATION
154d: jmp  0x1622                   ; → MessageBox 後離開
1550: ...  cmp [bp-6], 0x280 (640) / cmp [bp-8], 0x190 (400) 解析度檢查
```

**解讀**：檢查條件 = `RC_PALETTE` 旗標 + `SIZEPALETTE==256`。Wine 24-bit 桌面兩者
都不滿足 → 跳錯誤訊息。目前已用 `Xvfb :95 -screen 0 1024x768x8` 繞過；若要 binary
patch，把 `1540: cmp word [bp-2],0x100` 改成恆等比較，或把 `1545: je` 改成 `jmp`
（file offset = 0x91600 + 0x1540 = 0x92b40 起，換算見 segments.md 與
`ne_disasm.py` 的 `file_off`）。

---

## 工具與資料檔

- `tools/ne_disasm.py`：解析 + 反組譯 + 報告產生（重跑約 16 秒）
  - `python3 tools/ne_disasm.py <exe>` → 產生本目錄四份報告
  - `--func 11:50c6` → 印出所在函數的附註解反組譯
  - `--list-imports` → 全部 import fixup site 清單
- `segments.md`：117 segments 清單（file offset 已套用 NE sector shift）
- `functions_index.md`：11 個 code segment、**3,672 個函數**入口索引
- `far_call_graph.csv` / `.md`：14,363 個 `9a` far call site，14,087 個 internal、
  274 個 import，**全部解析成功**；2 個 UNRESOLVED（4:516c、11:5b96）經查是
  jump table / data table 內嵌資料被線性掃描誤判的假 call，非真實程式碼
- `imports.md`：KERNEL/USER/GDI/MMSYSTEM/TOOLHELP/WING import 與呼叫點
  （★ = CreateFont/TextOut/GetDeviceCaps/OpenFile/_llseek/_hread/WinG* 等重點）

### 技術備註（NE 格式層面）

- 本 EXE 的 far call **沒有** internal PTR32 reloc；同段/跨段 call 的 selector 由
  **SELECTOR reloc**（修復鏈掛在 `9a` 指令 +3 的 segment word）修復，offset 是
  立即值。import call 才用 PTR32 reloc（site = `9a`+1）。
- `KERNEL.#113/#114` 是 `equate` import（`__AHSHIFT`=3、`__AHINCR`=8），loader
  直接填常數——seg5:5b9f 函數裡看似位址的立即值（0x5bb1 等）其實是修復鏈 link。
- seg:off → file offset：`seg.file_offset + off`（segment table offset 已 << shift，shift=9）。
