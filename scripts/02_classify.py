"""Класифікує відео за типом контенту і рахує медіану переглядів.
Запуск: python3 scripts/02_classify.py lublog"""
import csv, re, sys, statistics as st
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
h = (sys.argv[1] if len(sys.argv) > 1 else "lublog")
RULES = [
 ("Стріми / розіграші", r"техно-(понеділок|вівторок|середа|четвер|п.ятниця)|стрім|стрим|розігру|розыгр"),
 ("Досвід використання", r"\b\d{1,2}\s*(дн|день|дней|днів|тиж|недел|месяц|місяц|год|рік|рок)|(один|одн[ау]|пів|полгода|півроку)\s*(рік|год|року|месяц|місяц|тижд|недел)|^місяць з|^месяц с|півроку|полгода|после года|після року|спустя|через рік|через год|опыт|досвід|вернулся|повернувся|перешел|перейшов|купил|купив"),
 ("Порівняння / вибір", r"\bvs\b|против|сравн|порівн|какой .*(купить|выбрать)|який .*(купити|обрати)|что выбрать|що обрати|выбираем|обираємо|или | або | чи |лучше|краще|замість|вместо|не покупай|не купуй|причин купить|стоит ли|чи варто"),
 ("Топ / добірки", r"\bтоп\b|\btop\b|найкращ|лучшие|лучший смартфон|\d+\s*(гаджет|ігор|игр|смартфон|ноут|аксесуар)"),
 ("Поради / функції", r"как |як |настро|налашт|функци|функці|фишк|фішк|совет|порад|секрет|отключи|вимкн|лайфхак|трюк|пропустил|пропустив|не знал|не знав|что делать|що робити"),
 ("Новини / витоки", r"презентац|новост|новин|event|wwdc|слух|утечк|витік|злил|злила|анонс|показал|показала|чутк|скасов|провал|крах|просит прощения"),
 ("Огляд / розпаковка", r"обзор|огляд|review|распаков|розпаков|первое впечатл|перше враж|unboxing|тест|що вміє|что умеет|наспра|на самом деле"),
]
def cat(t):
    t = t.lower()
    for name, rx in RULES:
        if re.search(rx, t): return name
    # Fallback: у назві є конкретний пристрій -> це неявний огляд
    if re.search(r"iphone|galaxy|xiaomi|redmi|poco|pixel|macbook|ipad|airpods|watch|asus|lenovo|acer|huawei|honor|oneplus|rtx|ноутбук|ноут|zenbook|rog|nothing|sony|realme|motorola|навушник|наушник|планшет|проектор|колонк", t):
        return "Огляд / розпаковка"
    return "Інше"
rows = list(csv.DictReader(open(ROOT/"data"/f"{h}_videos.csv", encoding="utf-8-sig")))
for r in rows:
    r["views"] = int(r["views"]); r["category"] = cat(r["title"])
    r["year"] = int(r["published_at"][:4])
    tl = r["title"].lower()
    caps = len(re.findall(r"\b[A-ZА-ЯІЇЄҐ]{3,}\b", r["title"]))
    r["caps_words"] = caps
    r["curiosity"] = int(bool(re.search(r"\d+\s*%|ігнору|игнор|обман|не знає|не знали|не знаєш|ніхто|никто|шок|правда|секрет|ось чому|вот почему|чому|почему|ці |ця |цей |це |без цих|не купуй|не покупай|\?|!", tl)) or caps >= 2)
    r["brand"] = next((b for b,k in [("Apple",r"iphone|apple|macbook|ipad|airpods|watch ultra|ios"),("Samsung",r"samsung|galaxy"),("Xiaomi",r"xiaomi|redmi|poco"),("Google",r"pixel|google")] if re.search(k,tl)), "Інші")
    r["lang"] = "UA" if re.search(r"[іїєґІЇЄҐ]", r["title"]) else ("RU" if re.search(r"[ыэъёЫЭЪЁ]", r["title"]) else "?")
with open(ROOT/"data"/f"{h}_classified.csv","w",newline="",encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
def report(sub, label):
    print(f"\n=== {label} ({len(sub)} відео) ===")
    g = {}
    for r in sub: g.setdefault(r["category"], []).append(r["views"])
    for k, v in sorted(g.items(), key=lambda kv: -st.median(kv[1])):
        print(f"{k:24} n={len(v):4}  медіана={int(st.median(v)):>8,}")
longs = [r for r in rows if r["is_short"] == "0"]
report(longs, "Довгі відео, усі роки")
other = sum(r["category"]=="Інше" for r in longs)/len(longs)
print(f"\nЧастка «Інше»: {other:.0%}")
ua = [r for r in longs if r["year"] >= 2023]
report(ua, "Довгі відео, UA-період 2023–2026")
print("\nБренд (UA-період):")
g={}
for r in ua: g.setdefault(r["brand"],[]).append(r["views"])
for k,v in sorted(g.items(), key=lambda kv:-st.median(kv[1])): print(f"{k:10} n={len(v):4} медіана={int(st.median(v)):>8,}")
print("\nЗаголовок-інтрига (UA, довгі):")
for c in (1,0):
    v=[r["views"] for r in ua if r["curiosity"]==c]
    print(("інтрига" if c else "звичайний"), len(v), int(st.median(v)))
print("\nМова назв (довгі):")
for L in ("RU","UA","?"):
    v=[r["views"] for r in longs if r["lang"]==L]
    if v: print(L, len(v), int(st.median(v)), "роки", min(r["year"] for r in longs if r["lang"]==L), "-", max(r["year"] for r in longs if r["lang"]==L))
