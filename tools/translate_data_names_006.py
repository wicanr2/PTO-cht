# -*- coding: utf-8 -*-
"""Translate translation/target/chunks/data_names_006.csv into Traditional Chinese.

KSDATA:0861-0953 (ship names, detail table) and NCTDATA:0000-0106 (place names).
Noise rows (control-code garbage like "!54", '"*V') keep the source verbatim,
mirroring the convention of the other translated chunks.
Read/write use escapechar="\\" symmetrically so raw backslash sequences
round-trip byte-identically.
"""
import csv
import os
import re

SRC = "translation/target/chunks/data_names_006.csv"
DST = "translation/target/translated/translation/target/chunks/data_names_006.csv"

NAMES = {
    # KSDATA - Japanese ships
    "Chuyo": "沖鷹",
    "Enoki": "榎",
    "Kusunoki": "楠",
    "Koba": "樺",
    "Tsuta": "蔦",
    "Nashi": "梨",
    "Shinonome": "東雲",
    "Odake": "雄岳",
    # KSDATA - US carriers / escort carriers
    "Bennington": "班寧頓",
    "Solomons": "所羅門",
    "Marcus Isl.": "馬庫斯島",
    "Savo Island": "薩沃島",
    "Makassar St.": "望加錫海峽",
    "Hollandia": "荷蘭迪亞",
    "Kwajelein": "瓜加林",
    "Bougainville": "布干維爾",
    "Attu": "阿圖",
    "Commencement": "科曼斯門特灣",
    "Block Isl.": "布洛克島",
    "Tulagi": "圖拉吉",
    # KSDATA - US cruisers
    "Pittsburg": "匹茲堡",
    "Flint": "弗林特",
    "Vicksburg": "維克斯堡",
    # KSDATA - US destroyers / escorts
    "Mayrant": "梅蘭特",
    "Trippe": "特里普",
    "Rhind": "林德",
    "Ellyson": "艾利森",
    "Emmons": "埃蒙斯",
    "Hobson": "霍布森",
    "Fullam": "富勒姆",
    "Luce": "盧斯",
    "Bush": "布希",
    "Trathen": "特拉森",
    "Longshaw": "朗肖",
    "Morrison": "莫里森",
    "W.D.Porter": "W.D.波特",
    "Young": "楊",
    "Howorth": "豪沃斯",
    "R.P.Leary": "R.P.利里",
    "Hopewell": "霍普韋爾",
    "Callaghan": "卡拉漢",
    "Colhoun": "科爾洪",
    "Little": "利特爾",
    "A.M.Sumner": "A.M.薩姆納",
    "M.L.Abele": "M.L.艾伯爾",
    "Drexler": "德雷克斯勒",
    "J.C.Owens": "J.C.歐文斯",
    "Gearing": "基靈",
    "F.Knox": "F.諾克斯",
    "Southerland": "薩瑟蘭",
    "R.Brazier": "R.布拉齊爾",
    "Traw": "特勞",
    "M.J.Manuel": "M.J.曼紐爾",
    "Naifeh": "奈費",
    "Jaccard": "賈卡德",
    "Mack": "麥克",
    "Williams": "威廉斯",
    "Straus": "史特勞斯",
    "D.A.Monro": "D.A.門羅",
    "U.M.Moore": "U.M.摩爾",
    "Tweedy": "特威迪",
    "Lewis": "路易斯",
    # KSDATA - US battleship / British ships
    "Arkansas": "阿肯色",
    "Illustrious": "光輝",
    "Victorious": "勝利",
    "K.George V": "英王喬治五世",
    "Duke of York": "約克公爵",
    "Anson": "安森",
    "Howe": "豪",
    # NCTDATA - Soviet Union / Japan
    "Chita": "赤塔",
    "Darasun": "達拉松",
    "Skovorodino": "斯科沃羅季諾",
    "Belogorsk": "別洛戈爾斯克",
    "Dalnercensk": "達利涅列琴斯克",
    "Komsomol'sk": "共青城",
    "Nikolayevsk": "尼古拉耶夫斯克",
    "Kagoshima": "鹿兒島",
    "Osaka": "大阪",
    "Sendai": "仙台",
    "Wakkanai": "稚內",
    "Shikuka": "敷香",
    # NCTDATA - China / Korea
    "Manchouli": "滿洲里",
    "Nomonghan": "諾門罕",
    "Tsitsihar": "齊齊哈爾",
    "Changchun": "長春",
    "Chengteh": "承德",
    "Chongjin": "清津",
    "Pyongyang": "平壤",
    "Pusan": "釜山",
    "Takao": "高雄",
    "Tientsin": "天津",
    "Taiyuan": "太原",
    "Tsining": "濟寧",
    "Suchow": "徐州",
    "Hangchow": "杭州",
    "Fuchow": "福州",
    "Swatow": "汕頭",
    "Changsha": "長沙",
    "Kwangchow": "廣州",
    "Hainan Isl.": "海南島",
    "Nanning": "南寧",
    "Sian": "西安",
    "Hanchwang": "漢莊",
    "Ichang": "宜昌",
    "Tukow": "圖科",
    "Kweiyang": "貴陽",
    "Talai": "塔萊",
    # NCTDATA - India / Southeast Asia
    "Agra": "阿格拉",
    "Benares": "貝拿勒斯",
    "Nagpur": "那格浦爾",
    "Bombay": "孟買",
    "Vizagapatam": "維沙卡帕特南",
    "Hyderabad": "海得拉巴",
    "Madras": "馬德拉斯",
    "Dacca": "達卡",
    "Myitkyina": "密支那",
    "Mandalay": "曼德勒",
    "Pyinmana": "彬馬那",
    "Chiang Mai": "清邁",
    "Chumpong": "春蓬",
    "Kotabaru": "哥打巴魯",
    "K.Lumpur": "吉隆坡",
    "Da Nang": "峴港",
    "Pnompenh": "金邊",
    "Aparri": "阿帕里",
    "Leyte": "雷伊泰",
    "Sandakan": "山打根",
    "Tarakan": "打拉根",
    "Kuching": "古晉",
    "Bandjamasin": "馬辰",
    "Enlekan": "恩雷坎",
    "Surabaya": "泗水",
    "Sorong": "索龍",
    "Madang": "馬當",
    "Lae": "萊城",
    "Buna": "布納",
    # NCTDATA - Australia / Canada
    "Rockhampton": "洛坎普頓",
    "Newcastle": "紐卡斯爾",
    "Canberra": "坎培拉",
    "Melbourne": "墨爾本",
    "Tennant": "坦南特",
    "Dajarra": "達賈拉",
    "Alice Sprg.": "愛麗絲泉",
    "Tarcoola": "塔庫拉",
    "Adelaide": "阿得雷德",
    "Calgary": "卡加利",
    "Regina": "雷吉納",
    "Winnipeg": "溫尼伯",
    "Armstrong": "阿姆斯特朗",
    "Cochrane": "科克倫",
    "Toronto": "多倫多",
    # NCTDATA - United States
    "Portland": "波特蘭",
    "S.Lake City": "鹽湖城",
    "Sacramento": "沙加緬度",
    "Phoenix": "鳳凰城",
    "El Paso": "艾爾帕索",
    "Boston": "波士頓",
    "Cleveland": "克里夫蘭",
    "Norfolk": "諾福克",
    "Charleston": "查爾斯頓",
    "Denver": "丹佛",
    "Kansas City": "堪薩斯城",
    "St. Louis": "聖路易斯",
    "Memphis": "曼菲斯",
    "Dallas": "達拉斯",
    "Houston": "休士頓",
    "Pensacola": "彭薩科拉",
    "Miami": "邁阿密",
}


def translate(source):
    return NAMES.get(source, source)  # noise rows keep source verbatim


def main():
    os.makedirs(os.path.dirname(DST), exist_ok=True)

    with open(SRC, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f, quoting=csv.QUOTE_ALL, escapechar="\\"))

    header, data = rows[0], rows[1:]
    tcol = header.index("target")
    scol = header.index("source")

    untranslated = []
    for row in data:
        row[tcol] = translate(row[scol])
        if row[tcol] == row[scol] and re.match(r"^[A-Za-z]", row[scol]):
            untranslated.append((row[1], row[scol]))

    with open(DST, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
        w.writerow(header)
        w.writerows(data)

    print(f"wrote {DST}: {len(data)} data rows")
    if untranslated:
        print("WARNING name-like rows left as source:")
        for rid, src in untranslated:
            print(f"  {rid}: {src!r}")


if __name__ == "__main__":
    main()
