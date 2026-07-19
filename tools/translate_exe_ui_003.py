#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate text_exe_ui_003.csv (en -> zh-TW), enforcing byte-length limits."""
import csv, re, sys

SRC = "/home/anr2/cht/tek2_cht/translation/source/chunks_exe/text_exe_ui_003.csv"
DST = "/home/anr2/cht/tek2_cht/translation/target/chunks/text_exe_ui_003.csv"

# source -> (target, note)  only for rows that should be translated
T = {
    "C7Forces %3d(-%2d) ->%3d": ("C7兵力 %3d(-%2d) ->%3d", "Forces=兵力"),
    "C7Tanks  %3d(-%2d) ->%3d": ("C7戰車  %3d(-%2d) ->%3d", "Tanks=戰車"),
    "%s %s Fleet A.F.": ("%s %s 艦隊航空", "A.F.=航空隊；因長度限制縮為「艦隊航空」"),
    "%s %s Base A.F.": ("%s %s 基地航空", "基地航空隊縮為「基地航空」"),
    "C7Planes %3d(-%2d) ->%3d": ("C7飛機 %3d(-%2d) ->%3d", ""),
    "C%d%s Base": ("C%d%s基地", ""),
    "C7Yield  %3d(-%2d) ->%3d": ("C7產量  %3d(-%2d) ->%3d", "Yield=產量"),
    "%s %s Commander": ("%s %s 司令", "Commander=司令(術語表)"),
    "Win this war for us...": ("為我國贏得此戰……", "……為 big5 省略號"),
    "%s Fleet A.F.": ("%s艦隊航空隊", "去空格以容納「航空隊」"),
    "%s A.F.": ("%s航空", "長度僅7 bytes，A.F.縮為「航空」"),
    "%s Base": ("%s基地", ""),
    "HIT ANY KEY": ("請按任意鍵", ""),
    " YES  ": (" 是 ", ""),
    "  NO  ": (" 否 ", ""),
    "Is this OK?": ("可以嗎？", "因長度限制精簡"),
    "B0Force": ("B0軍力", "與選單 FORCE 一致譯軍力"),
    "B0 Oil  Matl": ("B0 油料 資材", "Oil/Matl=油料/資材"),
    "$}Poor    Avg.    Rich": ("$}貧乏    普通    豐富", "$} 為控制碼；資源豐瘠等級"),
    "Poor    Avg.    Rich": ("貧乏    普通    豐富", ""),
    " FLEET  ": (" 艦隊  ", ""),
    "RESOURCE": ("資源", ""),
    " FORCE  ": (" 軍力  ", ""),
    "  NET   ": (" 連線  ", "NET=連線對戰"),
    "  BASE  ": (" 基地  ", ""),
    "  END   ": (" 結束  ", ""),
    "B0 SUB.": ("B0 潛艇", "SUB.=潛艇"),
    "B7 SUB.": ("B7 潛艇", ""),
    "Move": ("移動", ""),
    "Plan": ("計畫", ""),
    "C0Navy Budget%11d": ("C0海軍預算%11d", ""),
    "Naval Materials%7d": ("海軍資材%7d", ""),
    "budget": ("預算", ""),
    "materials": ("資材", ""),
    "There are not enough %s.": ("%s不足。", ""),
    "C0Days required%10d": ("C0所需天數%10d", ""),
    "ENTER": ("確定", ""),
    "CANCEL": ("取消", ""),
    "Please name your ship.": ("請為軍艦命名。", ""),
    "B1%s  %s Class": ("B1%s  %s級", "Class=艦級"),
    "B1Name: %-12s": ("B1名稱: %-12s", ""),
    "warship": ("軍艦", ""),
    "B1%s Class": ("B1%s級", ""),
    "B1Name: %-11s": ("B1名稱: %-11s", ""),
    "submarine": ("潛艇", ""),
    "transport": ("運輸", ""),
    "%2d mo": ("%2d月", "mo=月"),
    "%d mo": ("%d月", ""),
    " DESIGN": (" 設計", ""),
    " BUILD": (" 建造", ""),
    " SCUTTLE": (" 自沉", ""),
    " END": ("結束", "長度僅4 bytes，去掉前導空白"),
    " Design": (" 設計", ""),
    " WARSHIP ": (" 軍艦 ", ""),
    "SUBMARINE": ("潛艇", ""),
    " NEW SHIP": (" 新造艦", ""),
    " Build": (" 建造", ""),
    "WARSHIP ": ("軍艦", ""),
    "AIRCRAFT": ("飛機", "建造類別，譯飛機"),
    "TRANSPORT": ("運輸艦", ""),
    " Scuttle": (" 自沉", ""),
    "What would you like to do?": ("您要執行什麼？", ""),
    "  ENTER  ": ("  確定  ", ""),
    " DONE ": (" 完成 ", ""),
    " INC. ": (" 增加 ", "INC.=增加"),
    "  ENTER   ": ("  確定   ", ""),
    "  CANCEL  ": ("  取消  ", ""),
    "Stern": ("艦尾", ""),
    "Port": ("左舷", "舷側 Port=左舷"),
    "Starboard": ("右舷", ""),
    "Speed": ("速力", ""),
    "Material": ("材質", ""),
    "vs Air": ("對空", ""),
    "Aircraft": ("飛機", "艦艇性能欄，譯飛機"),
    "vs Fleet": ("對艦", ""),
    "Torp.Power": ("魚雷威力", ""),
    "Armor": ("裝甲", ""),
    "B=%s Class": ("B=%s級", ""),
    "B0Capacity": ("B0容量", ""),
    "Rest:%4d/%4d": ("餘:%4d/%4d", "Rest=剩餘，因長度縮為「餘」"),
    "Please design the ship.": ("請設計軍艦。", ""),
    "Please design the submarine.": ("請設計潛艇。", ""),
    "What warship will you design?": ("要設計哪種軍艦？", ""),
    "It has not been completed.": ("尚未完成。", ""),
    "Completed.": ("完成。", ""),
    "Commander": ("司令", ""),
    "Combined": ("聯合", "聯合艦隊"),
    "Pacific": ("太平洋", ""),
    "Victory Conditions": ("勝利條件", ""),
    "Staff": ("幕僚", ""),
    "Operations": ("作戰", ""),
    " What will you do?": (" 將如何行動？", ""),
}

FMT = re.compile(r"%[-+0-9.]*[a-zA-Z%]")
CTRL = re.compile(r"^(B[017]|C[07]|D0|\$\})")

rows = []
with open(SRC, encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        rows.append(r)

out, fail = [], 0
for r in rows:
    s = r["source"]
    tgt, note = T.get(s, ("", ""))
    if tgt:
        # byte length check
        if len(tgt.encode("big5")) > len(s.encode("ascii")):
            print("TOO LONG:", repr(s), repr(tgt),
                  len(tgt.encode("big5")), ">", len(s.encode("ascii")))
            fail += 1
        # format spec check (same multiset, same order)
        if FMT.findall(tgt) != FMT.findall(s):
            print("FMT MISMATCH:", repr(s), repr(tgt),
                  FMT.findall(s), FMT.findall(tgt))
            fail += 1
        # control code preserved
        m = CTRL.match(s)
        if m and not tgt.startswith(m.group(1)):
            print("CTRL LOST:", repr(s), repr(tgt))
            fail += 1
    out.append({"offset": r["offset"], "source": s, "target": tgt, "note": note})

if fail:
    sys.exit(f"{fail} problem(s)")

with open(DST, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["offset", "source", "target", "note"],
                       quoting=csv.QUOTE_ALL)
    w.writeheader()
    w.writerows(out)

n = sum(1 for o in out if o["target"])
print(f"OK: wrote {len(out)} rows, {n} translated, {len(out)-n} empty -> {DST}")
