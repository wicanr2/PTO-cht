# -*- coding: utf-8 -*-
"""Translate target column of translation/target/chunks/data_names_007.csv."""
import csv
import os

SRC = "translation/target/chunks/data_names_007.csv"
DST = "translation/target/translated/translation/target/chunks/data_names_007.csv"

PLACE = {
    "Irkutsk": "伊爾庫茨克",
    "Khabarovsk": "伯力",
    "Vladivostok": "海參崴",
    "Sapporo": "札幌",
    "Tokyo": "東京",
    "Kure": "吳港",
    "Naha": "那霸",
    "Iwo Jima": "硫磺島",
    "Mukden": "奉天",
    "Seoul": "漢城",
    "Taipei": "台北",
    "Peking": "北京",
    "Nanking": "南京",
    "Shanghai": "上海",
    "Wuhan": "武漢",
    "Hong Kong": "香港",
    "Chengtu": "成都",
    "Chungking": "重慶",
    "Kunming": "昆明",
    "Delhi": "德里",
    "Colombo": "可倫坡",
    "Calcutta": "加爾各答",
    "Imphal": "因帕爾",
    "Rangoon": "仰光",
    "Bangkok": "曼谷",
    "Singapore": "新加坡",
    "Saigon": "西貢",
    "Hanoi": "河內",
    "Manila": "馬尼拉",
    "Davao": "達沃",
    "Brunei": "汶萊",
    "Balikpapan": "峇里巴板",
    "Menado": "萬鴉老",
    "Makasar": "望加錫",
    "Palembang": "巨港",
    "Batavia": "巴達維亞",
    "Biak": "比亞克島",
    "Wewak": "韋瓦克",
    "Rabaul": "拉包爾",
    "P.Moresby": "摩斯比港",
    "Port Darwin": "達爾文港",
    "Townsville": "湯斯維爾",
    "Brisbane": "布里斯班",
    "Sydney": "雪梨",
    "Auckland": "奧克蘭",
    "Attu": "阿圖島",
    "D.Harbor": "荷蘭港",
    "Midway": "中途島",
    "Marcus": "馬庫斯島",
    "Wake": "威克島",
    "Saipan": "塞班島",
    "Guam": "關島",
    "Palau": "帛琉",
    "Truk": "特魯克島",
    "Marshall": "馬紹爾群島",
    "Gilbert": "吉爾伯特群島",
    "Guadalcanal": "瓜達爾卡納爾島",
    "E.Santo": "聖埃斯皮里圖島",
    "Fiji": "斐濟",
    "Palmyra": "帕邁拉環礁",
    "Hawaii": "夏威夷",
    "Montreal": "蒙特婁",
    "Seattle": "西雅圖",
    "S.Francisco": "舊金山",
    "Los Angeles": "洛杉磯",
    "Chicago": "芝加哥",
    "New York": "紐約",
    "Washington": "華盛頓",
    "New Orleans": "紐奧良",
    "Panama": "巴拿馬",
}

PLANE = {
    "Mitsubishi A5M": "三菱 A5M 九六式艦戰",
    "A6M2 Zerosen": "A6M2 零式艦上戰鬥機",
    "A6M5 Zerosen": "A6M5 零式艦上戰鬥機",
    "A7M2 Reppu": "A7M2 烈風",
    "J2M3 Raiden": "J2M3 雷電",
    "N1K2-J Shidenkai": "N1K2-J 紫電改",
    "N1K1-J Shinden": "N1K1-J 紫電",
    "Nakajima Kikka": "中島 橘花",
    "Aichi D3A1": "愛知 D3A1 九九式艦爆",
    "D4Y1 Suisei": "D4Y1 彗星",
    "Nakajima B5N2": "中島 B5N2 九七式艦攻",
    "B6N2 Tenzan": "B6N2 天山",
    "B7A2 Ryusei": "B7A2 流星",
    "Mitsubishi G3M2": "三菱 G3M2 九六式陸攻",
    "Mitsubishi G4M": "三菱 G4M 一式陸攻",
    "P1Y1 Ginga": "P1Y1 銀河",
    "Fugaku": "富嶽",
    "Aichi E13A": "愛知 E13A 零式水偵",
    "E16A1 Zuiun": "E16A1 瑞雲",
    "F2A Buffalo": "F2A 水牛",
    "F4F Wildcat": "F4F 野貓",
    "F4U Corsair": "F4U 海盜式",
    "F6F-3 Hellcat": "F6F-3 地獄貓",
    "F8F Bearcat": "F8F 熊貓",
    "SBD Dauntless": "SBD 無畏式",
    "SB2C Helldiver": "SB2C 地獄俯衝者",
    "TBD Devastator": "TBD 蹂躪者",
    "TBF Avenger": "TBF 復仇者",
    "AD Skyraider": "AD 天襲者",
    "OS2U Kingfisher": "OS2U 翠鳥",
    "Fairy Fulmar": "費瑞 管鼻燕",
    "Fairy Swordfish": "費瑞 劍魚",
    "S. Walrus": "超級馬林 海象",
    "Ki-43 Hayabusa": "Ki-43 隼",
    "Ki-44 Shoki": "Ki-44 鍾馗",
    "Ki-61 Hien": "Ki-61 飛燕",
    "Ki-84 Hayate": "Ki-84 疾風",
    "Kawasaki Ki-100": "川崎 Ki-100 五式戰",
    "Mitsubishi Ki-21": "三菱 Ki-21 九七式重爆",
    "Kawasaki Ki-48": "川崎 Ki-48 九九式雙輕爆",
    "Ki-67 Hiryu": "Ki-67 飛龍",
    "Kawasaki Ki-15": "川崎 Ki-15 九七式司偵",
    "Mitsubishi Ki-46": "三菱 Ki-46 百式司偵",
    "P-38 Lightning": "P-38 閃電",
    "P-39 Airacobra": "P-39 空中眼鏡蛇",
    "P-40 Warhawk": "P-40 戰鷹",
    "P-47 Thunderbolt": "P-47 雷霆",
    "P-51 Mustang": "P-51 野馬",
    "P-80 S. Star": "P-80 流星式",
}

TRANSLATIONS = {}
TRANSLATIONS.update(PLACE)
TRANSLATIONS.update(PLANE)

with open(SRC, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.reader(f, quoting=csv.QUOTE_ALL, escapechar="\\"))

header, data = rows[0], rows[1:]
translated = 0
for row in data:
    src = row[2]
    row[3] = TRANSLATIONS.get(src, src)  # noise rows keep original text
    if src in TRANSLATIONS:
        translated += 1

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
    w.writerow(header)
    w.writerows(data)

print(f"total rows: {len(data)}, translated: {translated}, kept-as-is: {len(data) - translated}")
print(f"written: {DST}")
