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

### 1. 中文字型（2026-07-19 查證完畢）

**結論：遊戲沒有自訂 bitmap font，文字全部走 GDI TextOut 即時渲染。**

已排除：

- EXE 全部大 data segment（seg51/59/70/106/107/117）bit-image 目視掃描、VGA 8x16 / 8x8 字型簽章掃描：無任何內嵌字型
- NE 資源表只有 ICON/MENU/DIALOG/VERSION，無 FONT/RCDATA 字型
- `DBFILE.TK2`、`WAKU1/2.TK2` 等也非字型

文字管線（seg11 = 繪圖/字型模組）：

- **CreateFont**：seg11:0x66bc（call site 0x66bd；參數 push 於 0x669d–0x66b9）
  - height = -16, width = 8, weight/italic/underline/strikeout = 0
  - **charset = 0x80（SHIFTJIS_CHARSET）**
  - facename = ds:0x7b8e = Shift-JIS「細明朝体」（DGROUP file offset 0xc9f8e）
  - 字型 handle 存至大全域 struct（selector 在 ds:[0x7e00]）+0x0e
- **TextOut**：全 EXE 唯一 call site seg11:0x90f8，count 固定 = 2（一次畫一個雙位元組字）
  - 呼叫者 `seg11:0x9016`：glyph 分派器。先把 16-bit 字碼以 big-endian 存入 2-byte buffer
  - 字碼 0xeb9f–0xebfc / 0xec40–0xec7e / 0xec80–0xec9e → 直接從 seg114 的 32-byte（16x16 1bpp）glyph 表複製（基底 0x894c / 0x8c2c / 0x8c0c；seg114 len=0 是 runtime buffer，推測日版 GAIJI.TK2 載入處，英文版無此檔）
  - 字碼 0x8140（全形空白）→ 跳過
  - 其他 → TextOut 畫進 1bpp 32x16 DIB（BITMAPINFOHEADER 在 struct+0x812：biSize=40, w=32, h=16, planes=1, bpp=1），再 GetDIBits 讀回 → 32-byte mono glyph
  - 注意：seg11:0x9016 在英文版中找不到任何 direct/near/far/export 呼叫者，可能是日版殘留或經函式指標呼叫
- **blit**：`seg11:0x8be8` 把 1bpp glyph 依 fg/bg 色展開成 8bpp；`seg11:0x5195`（AND-blit）/ `seg11:0x51f4` 貼進 WinG DIB
- **文字引擎**：seg11:0x8ca3 起（`enter 0x30`），處理 'C7'/'B1'/'M4'/'R%c' 等 markup，對齊模式 switch 在 seg11:0x80b7 / 0x8e84（jump table 0x80bc / 0x8e89）
- **格式化**：USER.#421 = wvsprintf（對應字串裡的 %s/%d）
- USER 無 DrawText import → 遊戲內所有文字確定都經 TextOut 路徑
- CRT startup（seg11:0x4949–0x4a99）有 SJIS lead-byte（0x81–0x9F, 0xE0–0xFC）判斷，證實日版血統（與 VERSION info「提督の決断II」一致）

GDI import ordinals（已解析）：2=SetBkMode 3=SetMapMode 9=SetTextColor 29=PatBlt 33=TextOut
34=BitBlt 45=SelectObject 52=CreateCompatibleDC 56=CreateFont 68=DeleteDC 69=DeleteObject
80=GetDeviceCaps 92=GetTextFace 93=GetTextMetrics 360=CreatePalette 363=GetPaletteEntries
367=AnimatePalette 375=GetSystemPaletteEntries 441=GetDIBits 442=CreateDIBitmap

**中文化 patch 點（已實作 `tools/patch_big5_font.py`，接入 `tools/build_patch.py`）**：

1. charset：file offset **0x97cad** `68 80 00`（push 0x80）→ `68 88 00`（CHINESEBIG5_CHARSET）✅ 已 patch
2. facename：file offset **0xc9f8e** SJIS「細明朝体」`95 57 8f 80 96 be 92 a9 00` → Big5「新細明體」`b7 73 b2 d3 a9 fa c5 e9 00`（同長度原位覆蓋）✅ 已 patch
3. **lead-byte 檢查：結論是不需要 patch**。已對全部 11 個 code segment 做完整 capstone 掃描：
   - `cmp r8, {0x81,0x9F,0xA0,0xE0,0xFC}` 群集只出現在 CRT startup 的 argv 解析（seg11:0x4949–0x4a99），不影響繪字
   - 無 `test al,0x80` 字串走訪（唯一命中 seg11:0x5936 是 RLE 解壓）、無 `shl ax,8` 字碼合成、無 mbctype 表
   - 換言之繪製路徑沒有 SJIS 範圍閘門，Big5 bytes 不會被拆錯
   - 注意 seg11:0x9016（TextOut DBCS 渲染器）在英文版找不到任何 static 呼叫者，疑為日版殘留或經函式指標呼叫；英文版的逐字渲染鏈（string walker → glyph 取得）未完全定位，但不論走哪條路都不含 byte-range 判斷
4. 執行環境系統 codepage 需為 950（Big5）：Windows 上 otvdm 配繁中系統 / locale emulator；Wine 配 zh_TW locale。**實機渲染驗證（otvdm + cp950）仍待做**

### 1b. 256 色 / 640x480 檢查 bypass（2026-07-19 實作，v2 修正）

檢查函式在 **seg11:0x14fe**（同一函式依序檢查 RASTERCAPS RC_PALETTE、
SIZEPALETTE==256、螢幕 >=640x400，失敗才分別顯示 seg110 的
「Please use display driver for 256 colors.」/「640x480」訊息）。
**重要**：此函式除檢查外還負責 RegisterClass/CreateWindow 以及註冊 640x400
WinG surface（函式尾 seg11:0x1611 `lcall seg11:0x6516`，該函式會
`inc word es:[0x204c]` 遞增全域 surface count）。**不可整函式 skip**
（v1 曾改成 `mov ax,1;retf 4` → surface count=0 → 後續 WinGGetDIBPointer(0)
→ crash，見 2 節）。

- patch 工具：`tools/patch_wine_checks.py <EXE>`（冪等，patch 前驗證原始 bytes）
- v2 patch 點（只 nop 失敗分支，保留視窗建立與 surface 註冊）：
  - file 0x92b3e（seg11:0x153e）`74 07` → `90 90`（skip RC_PALETTE error）
  - file 0x92b45（seg11:0x1545）`74 09` → `eb 09`（force SIZEPALETTE ok）
  - file 0x92b64（seg11:0x1564）`0f 8c b4 00` → `90 90 90 90`（skip width<640）
  - file 0x92b6d（seg11:0x156d）`0f 8e ab 00` → `90 90 90 90`（skip height<=400）
- 實測（v2，24-bit Xvfb）：與原版 depth-8 行為完全一致 —— 主視窗 CreateWindowEx
  （標題 "P.T.O. II"）、WinGRecommendDIBFormat/CreateDC/CreateBitmap 全跑，
  最後同點 crash（見下，為另一獨立問題）
- 注意：Wine 的 16-bit loader 不吃 DllOverrides，且 **Wine 9 的 relay/snoop 不再記錄
  16-bit API 呼叫**；16-bit 層追蹤要用 `+int21` / `+wing` / `+win` / `+file` 等 channel

### 2. WinG 相容

- 需要能正確執行 WinG 的環境：
  - Wine 修正 `WinGGetDIBPointer16`（需 patch Wine）
  - DOSBox-X + 合法 Windows 3.x
  - otvdm（Windows 上執行，Linux 無法直接驗證）

#### WinG crash 2026-07-19 攻堅更新（builtin wing 路線）

**迴歸比對結論（三 EXE 同環境實測）**：origin 原版 / assets/patched 最新（字串注入後）
/ v2 check-patched 在 Xvfb depth 8 下行為**完全一致**：CreateWindowEx 建立
「P.T.O. II」視窗（`+win` trace 可見）→ WinGRecommendDIBFormat → WinGCreateDC →
WinGCreateBitmap16(640x-416x8) 成功（hbm=0x49/0x4b）→ WinGGetDIBPointer(hbm, bmi)
→ 同點 crash @ seg5:0x5b9f。**非中文化 patch 迴歸**（舊 session「主視窗建立」說法正確，
先前「未見視窗」是 v1 patch 自傷 + xwininfo 觀察時機問題）。

**crash 鏈（靜態+動態確認）**：

- seg5:0x5b72 = huge-pointer normalize helper，被全 EXE 34 處呼叫；
  crash 時解參照 far ptr **0000:000c**（ES=0, DI=0x0c）→ 某個應被填的 far 指標是 NULL
- surface 管理：count 在全域 struct es:[0x7e00]+0x204c；註冊函式 seg11:0x6516
  （`inc es:[0x204c]`，由 0x14fe 函式尾呼叫）；建立函式 seg11:0x9840（**far call**，叫
  WING.1002/1001/1003 並把 hbm 存入 ds:0x828c table）；取用循環 seg11:0x660e
  （依 count 逐一建立，再 WinGGetDIBPointer(table[0]) 存 bits 至 struct+6/+8）
- **v1 patch 曾造成假像**：整 skip 0x14fe → count=0 → 循環不跑 → GetDIBPointer(0)
  → crash。修正後 count=1、建立成功，但 **crash 依舊在同點**
- `+file` 實測：crash 前遊戲**沒有開啟任何資料檔**（無 TK2 open）；
  `+int21` 僅 GET VERSION/GET/SET VECTOR 0；`+int2f`/`+mci` 無 CD 活動
  → CD 假說排除
- winedbg 無法讀 16-bit stack（"Failed to linearize address"），caller 未能直接定位

**目前最佳假說（已被否決）**：Wine `WinGGetDIBPointer16` 不填呼叫者的 BITMAPINFO
（wine-9.0 源碼 `if (bmpi) FIXME(... setting BITMAPINFO not supported)`），
遊戲接著用該未初始化 buffer 的欄位計算/取得 far 指標 → NULL → seg5:0x5b9f。
佐證：crash 位址固定、緊接 GetDIBPointer 之後、且 helper 讀的是 ptr+0x0c/+0x0d
（恰為 BITMAPINFOHEADER 的 biPlanes/biBitCount 偏移）。
下一步：重編 wine 的 wing.dll16 補 BITMAPINFO 填寫（~15 行），或 EXE patch
讓遊戲略過依賴該 buffer 的路徑；otvdm（WinG 完整）下應不會有此 crash，可比對。

#### 2026-07-19 第三輪：自編 wing.dll16 建成並載入，BITMAPINFO 假說否決

- **wing.dll16 重編成功**（vendor/wine-src/wine-9.0 已含 BITMAPINFO 回填 patch，
  review 無誤）。無 sudo 環境的構建法（詳見本節末）：
  `apt-get download libc6-dev-i386 gcc-13-multilib lib32gcc-13-dev` + dpkg -x 到 /tmp
  + gcc wrapper（-m32 時補 -B/-L/-I）+ 本地編 flex 2.6.4 → configure 精簡版 →
  `make -C tools && make -C dlls/wing.dll16` → 產物 = PE stub（2.5KB）+
  wing.dll16.so（120KB，含實際 16-bit 碼）
- **載入**：`WINEDLLPATH` 對 dll16 無效（ntdll `find_builtin_dll` 搜尋順序是
  系統 dll_dir 優先於 WINEDLLPATH）。解法 = **shadow wine tree**
  （/tmp/wineroot：copy /usr/lib/wine/wine{,64} loader binary，
  `cp -rs` symlink farm /usr/lib/i386-linux-gnu/wine，但 **ntdll.so 必須是實體複本**
  （dladdr realpath 會穿透 symlink 回到系統目錄），
  i386-windows/wing.dll16 與 i386-unix/wing.dll16.so 換成自編版，
  share → /usr/share symlink）。`+module` trace 確認載入
  「fake Wine dll」= 自編版
- **實測結果**：FIXME「setting BITMAPINFO not supported」消失（回填生效），
  但 **crash 依舊在同點 seg5:0x5b9f**（far ptr 0000:000c）→
  BITMAPINFO 不是 NULL 指標來源，假說否決
- **新線索（crash 前最後動作）**：`+global,+resource` trace 顯示
  grpseg 家族大 buffer（56390/58672/59780/61242/60618/56470/59196/59076/57534/58780/
  42063/50548 bytes, flags 0042）**全部 GlobalAlloc 成功**；crash 發生在
  APPMENU 資源載入 + LoadImage(#7fe3) + 三次 GlobalAlloc(2560/8193/32768) 之後，
  即主視窗 menu 初始化完成階段
- seg11:0x2154 起是 packed data segment 載入器：依序處理
  「grpseg / grpseg2 / readseg / pacseg」，失敗訊息為 SJIS
  「ファイルがよめません:」（seg117:0x7a46）；ds:0x8096 = grpseg buffer far ptr
  （GlobalAlloc+GlobalLock 存入），全 EXE 數百處 `push dword [0x8096]` 使用者
- 下一步：取得 crash 當下的 16-bit stack（winedbg 對 16-bit 完全無力：
  breakpoint 不能下、stack 不能讀；考慮 patch helper 0x5b72 把 caller return
  addr 寫入固定位置再觀察，或用 gdb attach 32-bit process 讀 LDT）

### 3. 包裝

- Windows：`packaging/build_windows.sh` 已產生 `dist/PTO2-cht-windows.zip`（otvdm + 中文化遊戲）
- Linux：`packaging/build_appimage.sh` 產生 AppDir，但需解決 Wine WinG 問題
