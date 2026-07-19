#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Translate text_exe_ui_006.csv (EN -> zh-TW) with byte-length & format-spec checks."""
import csv, re, sys

SRC = "/home/anr2/cht/tek2_cht/translation/source/chunks_exe/text_exe_ui_006.csv"
DST = "/home/anr2/cht/tek2_cht/translation/target/chunks/text_exe_ui_006.csv"

# offset -> (target, note)
T = {
 "0xc7a03": ("成功", ""),
 "0xc7a0b": ("失敗", ""),
 "0xc7a48": ("B1 軍官     國籍", "B1 控制碼保留；Officer/Nat. 標題列"),
 "0xc7a74": ("B1 軍官     國籍", "同上"),
 "0xc7a88": ("海軍", ""),
 "0xc7a8d": ("陸軍", ""),
 "0xc7a92": ("提督", "ADMIRAL 放不下『海軍上將』(8>7)，用提督"),
 "0xc7a9a": ("將軍", ""),
 "0xc7ab9": ("U您要執行什麼？", "行首 U 為控制碼保留"),
 "0xc7ad6": ("資料", ""),
 "0xc7adb": ("海軍", ""),
 "0xc7ae0": ("陸軍", ""),
 "0xc7ae5": ("新兵器", ""),
 "0xc7b02": ("1. 佔領敵國首都。", ""),
 "0xc7b21": ("美國", ""),
 "0xc7b2c": ("日本", ""),
 "0xc7b32": ("迫使%s投降。", "%s 保留"),
 "0xc7b4c": ("佔領成功。", ""),
 "0xc7b67": ("未能完成佔領。", ""),
 "0xc7b84": ("敵國目前GNP為%d。", "GNP 保留英文縮寫"),
 "0xc7b9f": ("我方基地目前產量為%d。", ""),
 "0xc7bcc": ("C>H136佔領", "C>H136 視為控制碼保留"),
 "0xc7bd9": ("防衛", ""),
 "0xc7be0": ("破壞", ""),
 "0xc7bf3": ("V勝利條件", "行首 V 控制碼保留"),
 "0xc7c06": ("目前狀態", ""),
 "0xc7c1c": ("作戰目標", ""),
 "0xc7c2c": ("敵方目標", ""),
 "0xc7c3d": ("雙方", ""),
 "0xc7c5c": ("目前不明", ""),
 "0xc7c6f": ("平原", ""),
 "0xc7c76": ("城鎮", ""),
 "0xc7c7b": ("叢林", ""),
 "0xc7c82": ("山地", ""),
 "0xc7cd0": ("%d 隊", "Un=units 縮寫"),
 "0xc7cd6": ("%d 隊", ""),
 "0xc7cdc": ("%d 隊", ""),
 "0xc7ce2": ("%d 隊", ""),
 "0xc7cf8": (" 取消所有委任", "保留一前導空白"),
 "0xc7d74": ("沒有%s。", ""),
 "0xc7d85": ("艦隊", ""),
 "0xc7de1": ("基地空軍", "A.F.=Air Force；『基地航空隊』超長"),
 "0xc7e2f": ("基地空軍", "同上"),
 "0xc7e20": ("無", ""),
 "0xc7e43": ("陸軍師團", "Army Div."),
 "0xc7e69": ("%s艦隊", ""),
 "0xc7e97": ("部隊", ""),
 "0xc7eb8": ("%s艦隊", ""),
 "0xc7ed4": ("步兵", ""),
 "0xc7efc": ("陸軍師團", "army division"),
 "0xc7f78": ("潛艇", ""),
 "0xc7f83": ("海軍航空", "NAVY A.F.；『海軍航空隊』10>9 超長，縮為海軍航空"),
 "0xc7f8d": ("陸軍航空", "ARMY A.F."),
 "0xc7f97": ("陸戰隊", ""),
 "0xc7f9f": ("陸軍師團", "ARMY DIV."),
 "0xc7fa9": ("潛艇", ""),
 "0xc7fc7": ("[艦隊", "[ 為面板括號保留"),
 "0xc7fce": ("單位", ""),
 "0xc7fd3": ("基地", ""),
 "0xc7fd8": ("駐地", "POST 語境不確定，取駐地"),
 "0xc7fdd": ("國家", ""),
 "0xc7fe4": ("外交", ""),
 "0xc7fec": ("目標", ""),
 "0xc8018": ("B1美國   日本", "B1 控制碼保留"),
 "0xc802c": ("日本", ""),
 "0xc8035": ("美國", ""),
 "0xc8041": ("R%c%s海軍預備隊", "R 控制碼保留"),
 "0xc8075": ("日本", ""),
 "0xc807e": ("美國", ""),
 "0xc808a": ("R%c%s陸軍預備隊", "R 控制碼保留"),
 "0xc80bd": ("對空雷達", ""),
 "0xc80cc": ("對海雷達", ""),
 "0xc80db": ("射擊雷達", ""),
 "0xc80e9": ("VT信管", "VT 保留"),
 "0xc80f1": ("密碼機", ""),
 "0xc8101": ("氧氣魚雷", ""),
 "0xc8110": ("燃燒彈", ""),
 "0xc8120": ("火焰放射器", ""),
 "0xc812e": ("艦載火箭", ""),
 "0xc813f": ("導引飛彈", ""),
 "0xc8152": ("B1 新兵器", "B1 控制碼保留"),
 "0xc8161": ("宣戰", ""),
 "0xc816d": ("參戰", ""),
 "0xc8177": ("軍事同盟", "Mil. Pact"),
 "0xc8181": ("援助協定", ""),
 "0xc818a": ("背棄盟約", ""),
 "0xc8196": ("和平條約", ""),
 "0xc81a1": ("談判", ""),
 "0xc81c9": ("]交戰中", "] 為面板括號保留"),
 "0xc81d1": ("同盟", ""),
 "0xc8231": ("貧乏", "資源量 Poor"),
 "0xc8236": ("普通", "Avg."),
 "0xc823b": ("豐富", ""),
 "0xc8274": ("本土", ""),
 "0xc8279": ("首都", "Cap.=Capital"),
 "0xc8283": ("海軍", ""),
 "0xc8288": ("陸軍", ""),
 "0xc82cc": ("%s級", "艦級"),
 "0xc8325": ("高角砲", "high gun"),
 "0xc832e": ("水陸兩用砲", "amphibious gun"),
 "0xc833d": ("雷管", "tube=魚雷發射管，僅 4 bytes 可用"),
 "0xc843f": ("戰車砲", ""),
 "0xc847e": ("級", "『 Class』接於艦名後，如 大和級"),
 "0xc84ec": ("要查詢哪國的情報？", ""),
 "0xc8509": ("日本", ""),
 "0xc850f": ("美國", ""),
 "0xc8516": ("其他", ""),
 "0xc8577": ("%4s艦隊", ""),
 "0xc8581": ("目前不明", ""),
 "0xc8593": ("現役艦艇", "Ship In Service"),
}

FMT = re.compile(r"%[-+0-9.]*[a-zA-Z%]")

def main():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    header, data = rows[0], rows[1:]
    out = [["offset", "source", "target", "note"]]
    errors = []
    for off, src, note in data:
        tgt, tnote = T.get(off, ("", ""))
        if tgt:
            slen = len(src.encode("ascii"))
            tlen = len(tgt.encode("big5"))
            if tlen > slen:
                errors.append(f"{off}: target {tlen}B > source {slen}B")
            sf = FMT.findall(src)
            tf = FMT.findall(tgt)
            if sf != tf:
                errors.append(f"{off}: fmt mismatch {sf} vs {tf}")
            if "&" in src and tgt.count("&") != src.count("&"):
                errors.append(f"{off}: & mismatch")
        out.append([off, src, tgt, tnote])
    if errors:
        print("ERRORS:")
        print("\n".join(errors))
        sys.exit(1)
    import os
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerows(out)
    filled = sum(1 for r in out[1:] if r[2])
    print(f"OK: wrote {DST}")
    print(f"rows={len(out)-1}, translated={filled}, empty={len(out)-1-filled}")

if __name__ == "__main__":
    main()
