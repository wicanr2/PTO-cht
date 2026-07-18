# -*- coding: utf-8 -*-
"""翻譯 translation/target/chunks/data_names_001.csv 的 target 欄位。"""
import csv
import os

SRC = "translation/target/chunks/data_names_001.csv"
DST = "translation/target/translated/translation/target/chunks/data_names_001.csv"

# source 原文 -> 繁體中文譯名（含雜訊前綴者保留前綴，僅翻譯可辨識部分；
# 純雜訊不列入，保留原樣）
T = {
    # ---- KDATA 艦船名（簡表：艦級名）----
    "Chitose": "千歲",
    "Taiyo": "大鷹",
    "Shinyo": "神鷹",
    "!Kaiyo": "!海鷹",
    "Yamato": "大和",
    "Kongo": "金剛",
    "Fuso": "扶桑",
    "Ise": "伊勢",
    "Nagato": "長門",
    "Furutaka": "古鷹",
    "Aoba": "青葉",
    "Myoko": "妙高",
    "Takao": "高雄",
    "Mogami": "最上",
    "Tone": "利根",
    "Tenryu": "天龍",
    "Kuma": "球磨",
    "Nagara": "長良",
    "Sendai": "川內",
    "Yubari": "夕張",
    "Agano": "阿賀野",
    "Oyodo": "大淀",
    "Minekaze": "峯風",
    "Kamikaze": "神風",
    "Mutsuki": "睦月",
    "Fubuki": "吹雪",
    "Hatsuharu": "初春",
    "Shiratsuyu": "白露",
    "Asashio": "朝潮",
    "Kagero": "陽炎",
    "Yugumo": "夕雲",
    "Shimakaze": "島風",
    "Akizuki": "秋月",
    "Matsu": "松",
    "Lexington": "列星頓",
    "ZYorktown": "Z約克鎮",
    "cWasp": "c胡蜂",
    "TEssex": "T艾塞克斯",
    "cIndependence": "c獨立",
    "-Sungamon": "-桑加蒙",
    '"Casablanca': '"卡薩布蘭卡',
    '"Commencement': '"科曼斯門特灣',
    '"Texas': '"德克薩斯',
    "Oklahoma": "奧克拉荷馬",
    "Pennsylvania": "賓夕法尼亞",
    "New Mexico": "新墨西哥",
    "California": "加利福尼亞",
    "Maryland": "馬里蘭",
    "N.Carolina": "北卡羅來納",
    "South Dakota": "南達科他",
    "Iowa": "愛荷華",
    "Alaska": "阿拉斯加",
    "Pensacola": "彭薩科拉",
    "Northampton": "北安普頓",
    "Indianapolis": "印第安納波利斯",
    "Astoria": "阿斯托里亞",
    "Wichita": "威奇托",
    "Baltimore": "巴爾的摩",
    "Omaha": "奧馬哈",
    "Brooklyn": "布魯克林",
    "Atlanta": "亞特蘭大",
    "Cleveland": "克里夫蘭",
    "Flash Deck": "平甲板",
    "Farragut": "法拉格特",
    "Porter": "波特",
    "Mahan": "馬漢",
    "Craven": "克雷文",
    "Sims": "辛姆斯",
    "Benson": "班森",
    "Livermore": "利弗莫爾",
    "Fletcher": "弗萊徹",
    "A.M.Sumner": "艾倫·薩姆納",
    "Gearing": "基靈",
    "J.C.Butler": "約翰·巴特勒",
    "Illustrious": "光輝",
    "$Hermes": "$競技神",
    "R.Sovereign": "皇家君權",
    "K.George V": "英王喬治五世",
    "Repulse": "反擊",
    "Q.Elizabeth": "伊莉莎白女王",
    "Kent": "肯特",
    "Norfolk": "諾福克",
    "York": "約克",
    "Danae": "達娜厄",
    "Emerald": "翡翠",
    "Perth": "伯斯",
    "Java": "爪哇",
    "De Ruyter": "德魯伊特",
    "Tromp": "特龍普",
    "Scharnhorst": "沙恩霍斯特",
    "Bismarck": "俾斯麥",
    "Prinz Eugen": "歐根親王",
    "Kirov": "基洛夫",
    "Hooh": "鳳凰",
    "ZKii": "Z紀伊",
    "Sanuki": "讚岐",
    "Tokachi": "十勝",
    "Aokumo": "青雲",
    "Hijun": "飛隼",
    "`Suruga": "`駿河",
    "Hitachi": "常陸",
    "Hotaka": "穗高",
    "Kiyokaze": "清風",
    "Unkaku": "雲鶴",
    "cShikishima": "c敷島",
    "Tosa": "土佐",
    "Shirane": "白根",
    "Takashio": "高潮",
    "Shinryu": "神龍",
    "cKawachi": "c河內",
    "Mikawa": "三川",
    "Zaoh": "藏王",
    "Aranami": "荒波",
    "Midway": "中途島",
    "ZMontana": "Z蒙大拿",
    "Kansas": "堪薩斯",
    "Las Vegas": "拉斯維加斯",
    "Turner": "特納",
    "Reprisal": "報復",
    "`N.Hampshire": "`新罕布夏",
    "Illinois": "伊利諾",
    "Seattle": "西雅圖",
    "Stevenson": "史蒂文森",
    "Majesty": "威嚴",
    "cGeorgia": "c喬治亞",
    "Kentucky": "肯塔基",
    "Oregon City": "俄勒岡城",
    "Perry": "培里",
    "Orion": "獵戶座",
    "cWyoming": "c懷俄明",
    "S.Carolina": "南卡羅來納",
    "Sacramento": "沙加緬度",
    "Timmerman": "蒂默曼",
    # ---- KSDATA 艦船名（詳表：個艦名）----
    "Akagi": "赤城",
    "Kaga": "加賀",
    "Soryu": "蒼龍",
    "Hiryu": "飛龍",
    "Shokaku": "翔鶴",
    "Zuikaku": "瑞鶴",
    "Hiyo": "飛鷹",
    "Junyo": "隼鷹",
    "Hosho": "鳳翔",
    "Ryujo": "龍驤",
    "Ryuho": "龍鳳",
    "Zuiho": "瑞鳳",
    "Shoho": "祥鳳",
    "Hiei": "比叡",
    "Haruna": "榛名",
    "Kirishima": "霧島",
    "Yamashiro": "山城",
    "Hyuga": "日向",
    "Mutsu": "陸奧",
    "Musashi": "武藏",
    "Kako": "加古",
    "Kinugasa": "衣笠",
    "Ashigara": "足柄",
    "Haguro": "羽黑",
    "Nachi": "那智",
    "Atago": "愛宕",
    "Maya": "摩耶",
    "Chokai": "鳥海",
    "Mikuma": "三隈",
    "Suzuya": "鈴谷",
    "Kumano": "熊野",
    "Chikuma": "筑摩",
    "Tatsuta": "龍田",
    "Ohi": "大井",
    "Natori": "名取",
    "Abukuma": "阿武隈",
    "Jintsu": "神通",
    "Naka": "那珂",
    "Asakaze": "朝風",
    "Harukaze": "春風",
}


def main():
    with open(SRC, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    out = [rows[0]]
    translated = kept = 0
    for row in rows[1:]:
        row = list(row)
        src = row[2]
        if src in T:
            row[3] = T[src]
            translated += 1
        else:
            # 純雜訊或無法辨識者，保留原樣
            row[3] = src
            kept += 1
        out.append(row)

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
        w.writerows(out)

    print(f"total={len(out) - 1} translated={translated} kept_as_is={kept}")
    print(f"wrote: {DST}")


if __name__ == "__main__":
    main()
