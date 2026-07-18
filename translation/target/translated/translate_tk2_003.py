# -*- coding: utf-8 -*-
"""Translate text_tk2_003.csv target column into Traditional Chinese.

內容：KSNAME.TK2 日本艦名（新造艦名冊）、SSNAME.TK2 潛艇名、
MSG1.TK2 山口多聞訣別訊息（後段為二進位雜訊，保留原樣）、
PLANE.TK2 純二進位資料（非文字，保留原樣）。
"""
import csv
import os

SRC = "translation/target/chunks/text_tk2_003.csv"
DST = "translation/target/translated/translation/target/chunks/text_tk2_003.csv"

TRANS = {
    # --- KSNAME.TK2 日本艦名（河川／風／霧／雲／潮／月／波系列） ---
    "Ishikari": "石狩",
    "Uji": "宇治",
    "Touga": "東雅",
    "Kuzuryu": "九頭龍",
    "Kurobe": "黑部",
    "Shimanto": "四萬十",
    "Chikugo": "筑後",
    "Chitose": "千歲",
    "Chikuma": "筑摩",
    "Teshio": "天鹽",
    "Naruse": "成瀨",
    "Niyodo": "仁淀",
    "Hatsuse": "初瀨",
    "Yoneshiro": "米代",
    "Araumi": "荒海",
    "Kiyokaze": "清風",
    "Satokaze": "里風",
    "Shimokaze": "霜風",
    "Murakaze": "村風",
    "Kitakaze": "北風",
    "Kochi": "東風",
    "Nishikaze": "西風",
    "Hae": "南風",
    "Umigiri": "海霧",
    "Yamagiri": "山霧",
    "Aokumo": "青雲",
    "Amagumo": "雨雲",
    "Benikumo": "紅雲",
    "Yukigumo": "雪雲",
    "Okishio": "沖潮",
    "Takashio": "高潮",
    "Nadashio": "灘潮",
    "Hamashio": "濱潮",
    "Yushio": "夕潮",
    "Wakashio": "若潮",
    "Izayoi": "十六夜",
    "Urazuki": "浦月",
    "Mangetsu": "滿月",
    "Minezuki": "峰月",
    "Yamazuki": "山月",
    "Yumizuki": "弓月",
    "Asanami": "朝波",
    "Yunami": "夕波",
    # --- SSNAME.TK2 美軍潛艇（魚類／神話名，加「號」） ---
    "Amberjack": "琥珀魚號",
    "Eel": "鰻魚號",
    "Basilisk": "蛇怪號",
    "Walrus": "海象號",
    "Ulua": "烏魯阿號",
    "Escolar": "油魚號",
    "Garrupa": "石斑魚號",
    "Garlopa": "花石斑號",
    "Greenfish": "青魚號",
    "Goldling": "金鱗號",
    "Sea Panther": "海豹號",
    "Joefish": "喬魚號",
    "Stickleback": "刺魚號",
    "Spinacks": "斯皮納克斯號",
    "Talbot": "塔爾博特號",
    "Diodon": "刺魨號",
    "Tiburon": "鯊魚號",
    "Dogfish": "角鯊號",
    "Dorado": "鯕鰍號",
    "Nerka": "紅鮭號",
    "Needlefish": "針魚號",
    "Halfbeak": "半喙魚號",
    "Whiting": "牙鱈號",
    "Pompano": "鯧鰺號",
    "Unicorn": "獨角獸號",
    # --- SSNAME.TK2 日本潛艇（伊號，沿用 data_names_009 慣例） ---
    "I-80": "伊-80",
    "I-81": "伊-81",
    "I-90": "伊-90",
    "I-91": "伊-91",
    "I-100": "伊-100",
    "I-200": "伊-200",
    "I-201": "伊-201",
    "I-500": "伊-500",
    "I-501": "伊-501",
    "I-600": "伊-600",
    "I-601": "伊-601",
    "I-700": "伊-700",
    "I-701": "伊-701",
    "I-800": "伊-800",
    "I-801": "伊-801",
}

# MSG1.TK2:0000 山口多聞於飛龍號的最後命令；「Hiryu.」之後為二進位雜訊，原樣保留
MSG_PREFIX_EN = (
    "Fleet Commander Tamon Yamaguchi delivered his\n"
    "final order to his crew on the flight deck of\n"
    "the severely damaged Hiryu."
)
MSG_PREFIX_ZH = (
    "艦隊司令山口多聞在身受重創的\n"
    "飛龍號飛行甲板上，向全體乘員\n"
    "下達了最後的命令。"
)

# 輸入檔由 tools/split_translation.py 以 escapechar='\\' 寫出，
# 讀取端必須使用相同 escapechar，雜訊列才能位元一致往返。
with open(SRC, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f, escapechar="\\"))

header, data = rows[0], rows[1:]
tidx = header.index("target")
sidx = header.index("source")

translated = kept = 0
for row in data:
    src = row[sidx]
    if src in TRANS:
        row[tidx] = TRANS[src]
        translated += 1
    elif src.startswith(MSG_PREFIX_EN):
        # 翻譯可辨識文字，保留尾部二進位雜訊
        row[tidx] = MSG_PREFIX_ZH + src[len(MSG_PREFIX_EN):]
        translated += 1
    else:
        # 純雜訊（PLANE.TK2 二進位資料）：保留原樣
        row[tidx] = src
        kept += 1

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
    w.writerow(header)
    w.writerows(data)

print(f"total={len(data)} translated={translated} noise_kept={kept}")
print(DST)
