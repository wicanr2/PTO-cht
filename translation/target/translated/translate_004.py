# -*- coding: utf-8 -*-
"""Translate data_names_004.csv target column into Traditional Chinese."""
import csv
import os

SRC = "translation/target/chunks/data_names_004.csv"
DST = "translation/target/translated/translation/target/chunks/data_names_004.csv"

# 艦船名譯名對照（二戰海戰遊戲語氣）
TRANS = {
    "Shimotsuki": "霜月",
    "Fuyutsuki": "冬月",
    "Take": "竹",
    "Amagi": "天城",
    "Katsuragi": "葛城",
    "Kaiyo": "海鷹",
    "Ume": "梅",
    "Momo": "桃",
    "Kuwa": "桑",
    "Kiri": "桐",
    "Sugi": "杉",
    "Kashi": "樫",
    "Princeton": "普林斯頓",
    "Montrey": "蒙特利",
    "Langley": "蘭利",
    "Cabot": "卡伯特",
    "Bataan": "巴丹",
    "San Jacinto": "聖哈辛托",
    "Mass.": "麻薩諸塞",
    "Alabama": "阿拉巴馬",
    "New Jersey": "紐澤西",
    "Missouri": "密蘇里",
    "Wisconsin": "威斯康辛",
    "Cleveland": "克里夫蘭",
    "Columbia": "哥倫比亞",
    "Montpelier": "蒙彼利埃",
    "Denver": "丹佛",
    "Mobile": "莫比爾",
    "Biloxi": "比洛克西",
    "Smith": "史密斯",
    "Dunlap": "鄧拉普",
    "Mustin": "馬斯廷",
    "Woodworth": "伍德沃斯",
    "Farenholt": "法倫霍爾特",
    "Buchanan": "布坎南",
    "Lansdowne": "蘭斯當",
    "Lardner": "拉德納",
    "McCalla": "麥卡拉",
    "La Vallette": "拉瓦列特",
    "Nicholas": "尼古拉斯",
    "O'Bannon": "奧班農",
    "Waller": "沃勒",
    "Taylor": "泰勒",
    "Stanly": "斯坦利",
    "Conway": "康威",
    "Cony": "科尼",
    "Converse": "康弗斯",
    "Foote": "富特",
    "Spence": "斯彭斯",
    "Thatcher": "柴契爾",
    "Miller": "米勒",
    "Owen": "歐文",
    "T.Sullivans": "蘇利文兄弟",
    "S.Potter": "斯蒂芬·波特",
    "Tingey": "廷吉",
    "Yarnall": "亞納爾",
    "C.Ausburne": "查爾斯·奧斯本",
    "Claxton": "克拉克斯頓",
    "Dyson": "戴森",
    "Hickox": "希科克斯",
    "Hunt": "亨特",
    "L.Hancock": "路易斯·漢考克",
    "Marshall": "馬歇爾",
    "Stockham": "斯托克姆",
    "Leyte": "雷伊泰",
    "Boxer": "拳師",
    "Alaska": "阿拉斯加",
    "Guam": "關島",
    "Tuscaloosa": "塔斯卡盧薩",
    "Augusta": "奧古斯塔",
    "Tirbitz": "提爾皮茨",
    "Shiokaze": "潮風",
}

with open(SRC, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f))

header, data = rows[0], rows[1:]
tidx = header.index("target")
sidx = header.index("source")

translated = kept = 0
for row in data:
    src = row[sidx]
    if src in TRANS:
        row[tidx] = TRANS[src]
        translated += 1
    else:
        # 非名稱雜訊（亂碼片段）：保留原樣
        row[tidx] = src
        kept += 1

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
    w.writerow(header)
    w.writerows(data)

print(f"total={len(data)} translated={translated} noise_kept={kept}")
print(DST)
