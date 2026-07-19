# import 清單與呼叫點

ordinal → 名稱來源：wine-9.0 `.spec`（vendor/wine-src）。呼叫點 = `9a` far call site（seg:off），括號內為所屬函數入口。

## KERNEL

| 函式 | 呼叫點數 | 呼叫點 |
|------|----------|--------|
| KERNEL.#1 | 1 | 11:4bdd (11:4ae0) |
| KERNEL.DOS3Call | 5 | 11:4418 (11:43cc), 11:4708 (11:46f6), 11:472a (11:46f6), 11:485f (11:4807), 11:4891 (11:4873) |
| KERNEL.FatalAppExit | 1 | 11:4bd4 (11:4ae0) |
| KERNEL.GetDOSEnvironment | 1 | 11:4aea (11:4ae0) |
| KERNEL.GetDriveType | 1 | 11:203e (11:2022) |
| KERNEL.GetModuleFileName | 1 | 11:48f8 (11:48d4) |
| KERNEL.GetVersion | 1 | 11:4403 (11:43cc) |
| KERNEL.GlobalAlloc | 22 | 5:64af (5:64a0), 11:215d (11:2154), 11:218d (11:2154), 11:21bd (11:2154), 11:223b (11:2232), 11:226b (11:2232), 11:229a (11:2232), 11:22de (11:2232), 11:230e (11:2232), 11:236e (11:2232), 11:2425 (11:241c), 11:246b (11:2462) … 共 22 |
| KERNEL.GlobalFree | 21 | 5:6549 (5:64a0), 11:21fd (11:21f0), 11:220f (11:21f0), 11:2221 (11:21f0), 11:23b1 (11:23a4), 11:23c3 (11:23a4), 11:23d5 (11:23a4), 11:23e7 (11:23a4), 11:23f9 (11:23a4), 11:240b (11:23a4), 11:245b (11:244e), 11:24a1 (11:2494) … 共 21 |
| KERNEL.GlobalLock | 22 | 5:64c7 (5:64a0), 11:2178 (11:2154), 11:21a8 (11:2154), 11:21d8 (11:2154), 11:2256 (11:2232), 11:2286 (11:2232), 11:22b5 (11:2232), 11:22f9 (11:2232), 11:2329 (11:2232), 11:2389 (11:2232), 11:2440 (11:241c), 11:2486 (11:2462) … 共 22 |
| KERNEL.GlobalReAlloc | 1 | 11:4daf (11:4d7d) |
| KERNEL.GlobalSize | 2 | 11:4dbd (11:4d7d), 11:4f9a (11:4f48) |
| KERNEL.GlobalUnlock | 21 | 5:6543 (5:64a0), 11:21f4 (11:21f0), 11:2206 (11:21f0), 11:2218 (11:21f0), 11:23a8 (11:23a4), 11:23ba (11:23a4), 11:23cc (11:23a4), 11:23de (11:23a4), 11:23f0 (11:23a4), 11:2402 (11:23a4), 11:2452 (11:244e), 11:2498 (11:2494) … 共 21 |
| KERNEL.InitTask | 1 | 11:43cf (11:43cc) |
| KERNEL.LockSegment | 1 | 11:43fe (11:43cc) |
| KERNEL.OpenFile **★** | 1 | 11:205b (11:2022) |
| KERNEL.WaitEvent | 1 | 11:443a (11:43cc) |
| KERNEL._hread **★** | 1 | 3:2c50 (3:2c42) |
| KERNEL._lclose **★** | 3 | 3:2c72 (3:2c6c), 11:2078 (11:2022), 11:2087 (11:2022) |
| KERNEL._lcreat | 1 | 3:2d33 (3:2d2a) |
| KERNEL._llseek **★** | 1 | 3:2c3b (3:2c2e) |
| KERNEL._lopen **★** | 1 | 3:2c26 (3:2c08) |
| KERNEL._lread | 1 | 11:206f (11:2022) |
| KERNEL._lwrite | 1 | 3:2c65 (3:2c58) |

## GDI

| 函式 | 呼叫點數 | 呼叫點 |
|------|----------|--------|
| GDI.AnimatePalette | 1 | 11:9259 (11:91aa) |
| GDI.BitBlt | 1 | 11:8905 (11:8830) |
| GDI.CreateCompatibleDC | 1 | 11:6752 (11:660e) |
| GDI.CreateDIBitmap | 1 | 11:677b (11:660e) |
| GDI.CreateFont **★** | 1 | 11:66bc (11:660e) |
| GDI.CreatePalette | 2 | 11:a3d1 (11:a2be), 11:a41f (11:a3da) |
| GDI.DeleteDC | 3 | 11:6a21 (11:697c), 11:98f1 (11:9840), 11:994d (11:98fe) |
| GDI.DeleteObject | 6 | 11:6265 (11:6210), 11:6a13 (11:697c), 11:6a2f (11:697c), 11:6a4a (11:697c), 11:9942 (11:98fe), 11:a43e (11:a3da) |
| GDI.GetDIBits | 1 | 11:911c (11:9016) |
| GDI.GetDeviceCaps **★** | 3 | 11:151f (11:1500), 11:152c (11:1500), 11:a2ee (11:a2be) |
| GDI.GetPaletteEntries | 2 | 11:61d1 (11:6054), 11:6291 (11:6210) |
| GDI.GetSystemPaletteEntries | 1 | 11:a308 (11:a2be) |
| GDI.GetTextFace | 1 | 11:67e0 (11:660e) |
| GDI.GetTextMetrics | 1 | 11:67cc (11:660e) |
| GDI.PatBlt | 1 | 11:90bc (11:9016) |
| GDI.SelectObject | 7 | 11:6661 (11:660e), 11:678e (11:660e), 11:67b7 (11:660e), 11:69f3 (11:697c), 11:6a05 (11:697c), 11:98dc (11:9840), 11:9939 (11:98fe) |
| GDI.SetBkMode | 1 | 11:90cc (11:9016) |
| GDI.SetMapMode | 2 | 11:67a1 (11:660e), 11:69e1 (11:697c) |
| GDI.SetTextColor | 1 | 11:90df (11:9016) |
| GDI.TextOut **★** | 1 | 11:90f8 (11:9016) |

## USER

| 函式 | 呼叫點數 | 呼叫點 |
|------|----------|--------|
| USER.BeginPaint | 1 | 11:9ae3 (11:9a32) |
| USER.CallNextHookEx | 1 | 11:1d10 (11:1cdc) |
| USER.ClientToScreen | 1 | 11:1db3 (11:1d1a) |
| USER.CreateWindow | 1 | 11:15fc (11:1500) |
| USER.DefWindowProc | 1 | 11:9c58 (11:9a32) |
| USER.DestroyWindow | 2 | 11:1656 (11:1632), 11:9c8e (11:9c64) |
| USER.DialogBox | 1 | 11:13e5 (11:1398) |
| USER.DispatchMessage | 1 | 11:94e7 (11:94be) |
| USER.EndDialog | 1 | 11:138c (11:135e) |
| USER.EndPaint | 1 | 11:9b67 (11:9a32) |
| USER.GetClientRect | 2 | 11:1d31 (11:1d1a), 11:9b13 (11:9a32) |
| USER.GetCursorPos | 1 | 11:9504 (11:94ee) |
| USER.GetDC | 6 | 11:1511 (11:1500), 11:65e0 (11:6572), 11:6744 (11:660e), 11:9c06 (11:9a32), 11:a2e3 (11:a2be), 11:a411 (11:a3da) |
| USER.GetSystemMetrics | 10 | 11:9682 (11:967c), 11:968f (11:967c), 11:9698 (11:967c), 11:96a1 (11:967c), 11:96bc (11:96b4), 11:96c5 (11:96b4), 11:96ce (11:96b4), 11:96d8 (11:96b4), 11:9723 (11:96b4), 11:972d (11:96b4) |
| USER.GetTickCount | 2 | 5:6573 (5:6570), 5:65a5 (5:659c) |
| USER.GetWindowRect | 1 | 11:9755 (11:96b4) |
| USER.GetWindowTask | 1 | 11:1f7a (11:1e82) |
| USER.InitApp | 1 | 11:4443 (11:43cc) |
| USER.InvalidateRect | 5 | 11:1e70 (11:1e34), 11:1f5f (11:1e82), 11:6316 (11:6210), 11:9ad3 (11:9a32), 11:9c43 (11:9a32) |
| USER.LoadCursor | 1 | 11:15a6 (11:1500) |
| USER.LoadIcon | 1 | 11:1598 (11:1500) |
| USER.MessageBox | 5 | 6:178f (6:1642), 11:12c8 (11:1126), 11:131b (11:12f4), 11:1349 (11:1322), 11:1f4e (11:1e82) |
| USER.MoveWindow | 1 | 11:97c6 (11:96b4) |
| USER.PeekMessage | 1 | 11:94cf (11:94be) |
| USER.PostMessage | 3 | 11:12dd (11:1126), 11:13c9 (11:1398), 11:1488 (11:142a) |
| USER.PostQuitMessage | 1 | 11:9a9c (11:9a32) |
| USER.RealizePalette | 7 | 11:62f3 (11:6210), 11:6603 (11:6572), 11:680c (11:660e), 11:9292 (11:91aa), 11:9b08 (11:9a32), 11:9c26 (11:9a32), 11:a42f (11:a3da) |
| USER.RegisterClass | 1 | 11:15c8 (11:1500) |
| USER.ReleaseDC | 6 | 11:1537 (11:1500), 11:65a0 (11:6572), 11:69cf (11:697c), 11:9c31 (11:9a32), 11:a3c6 (11:a2be), 11:a446 (11:a3da) |
| USER.ScreenToClient | 1 | 11:9529 (11:94ee) |
| USER.SelectPalette | 8 | 11:62e5 (11:6210), 11:65f5 (11:6572), 11:67fe (11:660e), 11:9279 (11:91aa), 11:9b00 (11:9a32), 11:9c20 (11:9a32), 11:a427 (11:a3da), 11:a438 (11:a3da) |
| USER.SetWindowPos | 1 | 11:1dda (11:1d1a) |
| USER.SetWindowsHookEx | 1 | 11:1f80 (11:1e82) |
| USER.ShowWindow | 1 | 11:693d (11:6818) |
| USER.TranslateMessage | 1 | 11:94dd (11:94be) |
| USER.UnhookWindowsHookEx | 1 | 11:1e48 (11:1e34) |
| USER.UpdateWindow | 3 | 11:1e76 (11:1e34), 11:1f65 (11:1e82), 11:632f (11:6210) |
| USER.WinHelp | 2 | 11:141e (11:1398), 11:145f (11:142a) |
| USER.wvsprintf | 2 | 11:1306 (11:12f4), 11:1334 (11:1322) |

## MMSYSTEM

| 函式 | 呼叫點數 | 呼叫點 |
|------|----------|--------|
| MMSYSTEM.mciSendCommand | 25 | 6:185d (6:1834), 6:188b (6:1872), 6:18c8 (6:189e), 6:1900 (6:18d6), 6:1955 (6:190e), 6:1985 (6:190e), 6:1a00 (6:19d6), 6:1a42 (6:1a18), 6:1a73 (6:1a5c), 6:1b1a (6:1a96), 6:1b66 (6:1a96), 6:1bc5 (6:1b7e) … 共 25 |

## TOOLHELP

| 函式 | 呼叫點數 | 呼叫點 |
|------|----------|--------|
| TOOLHELP.TerminateApp | 1 | 11:9c97 (11:9c64) |
| TOOLHELP.TimerCount | 2 | 11:9471 (11:9460), 11:9497 (11:9460) |

## WING

| 函式 | 呼叫點數 | 呼叫點 |
|------|----------|--------|
| WING.WinGBitBlt **★** | 1 | 11:63c1 (11:633a) |
| WING.WinGCreateBitmap **★** | 1 | 11:98cf (11:9840) |
| WING.WinGCreateDC **★** | 1 | 11:98b8 (11:9840) |
| WING.WinGGetDIBPointer **★** | 2 | 11:65ba (11:6572), 11:6686 (11:660e) |
| WING.WinGRecommendDIBFormat **★** | 1 | 11:984c (11:9840) |
| WING.WinGSetDIBColorTable **★** | 1 | 11:6378 (11:633a) |

