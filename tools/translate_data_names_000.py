# -*- coding: utf-8 -*-
"""Translate translation/target/chunks/data_names_000.csv into Traditional Chinese.

Keeps control-code noise prefixes (e.g. "<<1", "F21", "(!") intact and
translates only the recognizable name suffix. Rows that are pure noise or
initials (e.g. "E.P.", "ZZ(") are left as-is.
"""
import csv
import os

NAMES = {
    # ARDATA - Japanese Navy
    "Yamamoto": "山本五十六",
    "Toyoda": "豐田副武",
    "Koga": "古賀峯一",
    "Takasu": "高須四郎",
    "Kondo": "近藤信竹",
    "Ozawa": "小澤治三郎",
    "Nagumo": "南雲忠一",
    "Tsukahara": "塚原二四三",
    "Inoue": "井上成美",
    "Kurita": "栗田健男",
    "Mikawa": "三川軍一",
    "Ito": "伊藤整一",
    "Kusaka(J)": "草鹿任一",
    "Kusaka(R)": "草鹿龍之介",
    "Hosogaya": "細萱戊子郎",
    "Takagi": "高木武雄",
    "Kakuta": "角田覺治",
    "Ugaki": "宇垣纏",
    "Onishi": "大西瀧治郎",
    "Tanaka": "田中賴三",
    "Nishimura": "西村祥治",
    "Matsunaga": "松永貞市",
    "Shima": "志摩清英",
    "Hara": "原忠一",
    "Abe": "阿部弘毅",
    "Omori": "大森仙太郎",
    "Yamaguchi": "山口多聞",
    "Jyojima": "城島高次",
    "Kimura": "木村昌福",
    "Arima": "有馬正文",
    # ARDATA - Allied Navy
    "Kimmel": "金梅爾",
    "Nimitz": "尼米茲",
    "Halsey": "海爾賽",
    "Fletcher": "佛萊徹",
    "Spruance": "史普魯恩斯",
    "Vandegrift": "范德格里夫特",
    "Kinkaid": "金凱德",
    "Mitscher": "密茲契",
    "Turner": "特納",
    "McCain": "麥凱恩",
    "Smith": "史密斯",
    "Fitch": "費區",
    "Clark": "克拉克",
    "Lee": "李",
    "Callaghan": "卡拉漢",
    "Scott": "史考特",
    "Hoover": "胡佛",
    "Sherman": "雪曼",
    "Wright": "萊特",
    "Oldendorf": "奧登多夫",
    "Montgomery": "蒙哥馬利",
    "Harrill": "哈里爾",
    "Davison": "戴維森",
    "Sprague": "史普拉格",
    "Somerville": "薩默維爾",
    "Mountbatten": "蒙巴頓",
    "Phillips": "菲利普斯",
    "Ghormley": "戈姆利",
    "Doorman": "杜爾曼",
    "Crutchley": "克拉奇利",
    # GRDATA - Japanese Army
    "Hata": "畑俊六",
    "Terauchi": "寺內壽一",
    "Umezu": "梅津美治郎",
    "Okamura": "岡村寧次",
    "Itagaki": "板垣征四郎",
    "Yamashita": "山下奉文",
    "Imamura": "今村均",
    "Ushijima": "牛島滿",
    "Honma": "本間雅晴",
    "Hyakutake": "百武晴吉",
    "Mutaguchi": "牟田口廉也",
    "Iida": "飯田祥二郎",
    "Adachi": "安達二十三",
    "Kuribayashi": "栗林忠道",
    "Miyazaki": "宮崎繁三郎",
    # GRDATA - Allied Army
    "MacArthur": "麥克阿瑟",
    "Eichelberg.": "艾克爾伯格",
    "Swift": "史威夫特",
    "Wainwright": "溫萊特",
    "Krueger": "克魯格",
    "Stilwell": "史迪威",
    "Sutherland": "薩瑟蘭",
    "Kenney": "肯尼",
    "Wedemeyer": "魏德邁",
    "Chennault": "陳納德",
    "Willoughby": "威洛比",
    "Wavell": "韋維爾",
    "Auchinleck": "奧金萊克",
    "Slim": "斯利姆",
    "Percival": "珀西瓦爾",
    # KDATA - ships
    "Akagi": "赤城",
    "Kaga": "加賀",
    "Soryu": "蒼龍",
    "Hiryu": "飛龍",
    "Shokaku": "翔鶴",
    "Hiyo": "飛鷹",
    "Shinano": "信濃",
    "Taiho": "大鳳",
    "Unryu": "雲龍",
    "Hosho": "鳳翔",
    "Ryujo": "龍驤",
    "Ryuho": "龍鳳",
    "Zuiho": "瑞鳳",
}

# Longest keys first so "Tsukahara" wins over "Hara", "Ushijima" over "Shima".
KEYS = sorted(NAMES, key=len, reverse=True)


def translate(source):
    for key in KEYS:
        if source.endswith(key):
            return source[: -len(key)] + NAMES[key]
    return source  # pure noise or initials: keep unchanged


def main():
    src = "translation/target/chunks/data_names_000.csv"
    dst = "translation/target/translated/translation/target/chunks/data_names_000.csv"
    os.makedirs(os.path.dirname(dst), exist_ok=True)

    with open(src, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))

    header, data = rows[0], rows[1:]
    tcol = header.index("target")
    scol = header.index("source")

    for row in data:
        row[tcol] = translate(row[scol])

    with open(dst, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
        w.writerow(header)
        w.writerows(data)

    print(f"wrote {dst}: {len(data)} data rows")


if __name__ == "__main__":
    main()
