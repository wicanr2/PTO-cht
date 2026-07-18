# -*- coding: utf-8 -*-
"""翻譯 translation/target/chunks/data_names_005.csv 的 target 欄位。

- 可辨識的艦船名 → 繁體中文譯名
- 亂碼/雜訊（無法辨識的名稱）→ 保留原文
輸出：UTF-8-sig、csv.QUOTE_ALL、escapechar='\\'
"""
import csv
import os

SRC = "translation/target/chunks/data_names_005.csv"
DST = "translation/target/translated/translation/target/chunks/data_names_005.csv"

# source -> 繁體中文譯名（僅列可辨識的艦船名；其餘保留原文）
TRANS = {
    # 美軍驅逐艦（Fletcher/Sumner 級等）
    "Preston": "普雷斯頓",
    "O'Brien": "歐布萊恩",
    "Laffey": "拉菲",
    "Barton": "巴頓",
    "Laub": "勞勃",
    "Duncan": "鄧肯",
    "Chevalier": "雪佛利亞",
    "Saufley": "索夫利",
    "Strong": "史壯",
    "Bache": "貝奇",
    "Beale": "比爾",
    "Guest": "蓋斯特",
    "Hutchins": "哈欽斯",
    "Pringle": "普林格爾",
    "Phillip": "菲利普",
    "Renshaw": "倫蕭",
    "Ringgold": "林戈德",
    # 日本艦
    "Sakawa": "酒匂",
    "Tascalooga": "塔斯卡盧薩",
    "Harutsuki": "春月",
    "Yoizuki": "宵月",
    "Hanatsuki": "花月",
    "Maki": "槙",
    "Momi": "樅",
    "Kaya": "榧",
    "Nara": "楢",
    "Sakura": "櫻",
    "Yanagi": "柳",
    "Tsubaki": "椿",
    "Hinoki": "檜",
    "Kaede": "楓",
    "Keyaki": "欅",
    "Kashima": "鹿島",
    "Katori": "香取",
    "Kaki": "柿",
    "Hagi": "萩",
    "Kikuzuki": "菊月",
    "Teruzuki": "照月",
    "Natsuzuki": "夏月",
    "Hatsuume": "初梅",
    # 美軍航空母艦／護衛航母
    "Franklin": "富蘭克林",
    "Randolph": "蘭道夫",
    "Hancock": "漢考克",
    "Indepedence": "獨立號",
    "Sangamon": "桑加蒙",
    "Suwanee": "蘇旺尼",
    "Santee": "桑提",
    "Casablanca": "卡薩布蘭卡",
    "Natoma Bay": "納托馬灣",
    "St. Lo": "聖洛",
    "White Plains": "白原",
    "Kalinin Bay": "加里寧灣",
    "Fanshaw Bay": "范肖灣",
    "Kitkun Bay": "基特昆灣",
    "Gambier Bay": "甘比爾灣",
    "Kadashan Bay": "卡達尚灣",
    "Ommaney Bay": "奧曼尼灣",
    "Petrof Bay": "彼得羅夫灣",
    "Lunga Point": "隆加角",
    "Bismarck Sea": "俾斯麥海",
    # 美軍巡洋艦
    "S.Fransisco": "舊金山",
    "Nashville": "納許維爾",
    "Oakland": "奧克蘭",
    "Reno": "雷諾",
    "Birmingham": "伯明罕",
    "Pasadena": "帕薩迪納",
    "Miami": "邁阿密",
    # 美軍驅逐艦／護衛驅逐艦
    "Daly": "戴利",
    "Heermann": "希爾曼",
    "Hoel": "霍埃爾",
    "Brown": "布朗",
    "Haggard": "哈加德",
    "Johnston": "約翰斯頓",
    "Robinson": "羅賓遜",
    "Aulick": "奧利克",
    "Conner": "康納",
    "Newcomb": "紐康",
    "Killen": "基倫",
    "Sigourney": "西格尼",
    "A.W.Grant": "A.W.格蘭特",
    "Caperton": "卡珀頓",
    "Cogswell": "科格斯韋爾",
    "Ingersoll": "英格索爾",
    "Knapp": "納普",
    "Colahan": "科拉漢",
    "Bennion": "班尼恩",
    "H.L.Edwards": "H.L.愛德華茲",
    "R.P. Leary": "R.P.利里",
    "Bryant": "布萊恩特",
    "C.K.Bronson": "C.K.布朗森",
    "Cotton": "科頓",
    "Dorch": "多爾奇",
    "Gatling": "加特林",
    "Healy": "希利",
    "McDermut": "麥克德穆特",
    "McGowan": "麥高恩",
    "Melvin": "梅爾文",
    "Remey": "雷米",
    "Eversole": "埃弗索爾",
    "Shelton": "謝爾頓",
    "S.B.Roberts": "S.B.羅伯茨",
    "L.C.Taylor": "L.C.泰勒",
    "M.R.Newman": "M.R.紐曼",
    "O.Mitchell": "O.米切爾",
    "R.F.Keller": "R.F.凱勒",
    "Welles": "威爾斯",
    "Thorn": "索恩",
    # 日本驅逐艦
    "Sawakaze": "澤風",
    "Yukaze": "夕風",
    "Nokaze": "野風",
    "Namikaze": "波風",
    "Kamikaze": "神風",
}


def main():
    with open(SRC, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))

    header, data = rows[0], rows[1:]
    src_idx = header.index("source")
    tgt_idx = header.index("target")

    translated = 0
    kept = 0
    for row in data:
        source = row[src_idx]
        if source in TRANS:
            row[tgt_idx] = TRANS[source]
            translated += 1
        else:
            # 亂碼/雜訊：保留原樣
            row[tgt_idx] = source
            kept += 1

    os.makedirs(os.path.dirname(DST), exist_ok=True)
    with open(DST, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
        w.writerow(header)
        w.writerows(data)

    print(f"total={len(data)} translated={translated} kept_as_is={kept}")
    print(f"written: {DST}")


if __name__ == "__main__":
    main()
