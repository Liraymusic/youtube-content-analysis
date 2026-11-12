"""Вивантажує всі відео YouTube-каналу в CSV.
Запуск:  python3 scripts/01_fetch_youtube.py lublog
"""
import csv, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://www.googleapis.com/youtube/v3/"


def load_key():
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("YOUTUBE_API_KEY="):
            key = line.split("=", 1)[1].strip()
            if key and "ВСТАВ" not in key:
                return key
    sys.exit("❌ Ключ не знайдено у .env")


def get(endpoint, **params):
    params["key"] = KEY
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def iso_to_sec(d):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return 0
    dd, h, mi, s = (int(x or 0) for x in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + s


KEY = load_key()
handle = (sys.argv[1] if len(sys.argv) > 1 else "lublog").lstrip("@")

ch = get("channels", part="snippet,contentDetails,statistics", forHandle=handle)
if not ch.get("items"):
    sys.exit(f"❌ Канал @{handle} не знайдено")
ch = ch["items"][0]
print(f"✅ Канал: {ch['snippet']['title']} | підписників: {ch['statistics'].get('subscriberCount')} | відео: {ch['statistics'].get('videoCount')}")
uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]

ids, token = [], None
while True:
    p = {"part": "contentDetails", "playlistId": uploads, "maxResults": 50}
    if token:
        p["pageToken"] = token
    res = get("playlistItems", **p)
    ids += [i["contentDetails"]["videoId"] for i in res["items"]]
    token = res.get("nextPageToken")
    print(f"  зібрано ID: {len(ids)}", end="\r")
    if not token:
        break
print()

rows = []
for i in range(0, len(ids), 50):
    res = get("videos", part="snippet,contentDetails,statistics", id=",".join(ids[i:i + 50]))
    for v in res["items"]:
        sn, st = v["snippet"], v.get("statistics", {})
        sec = iso_to_sec(v["contentDetails"].get("duration"))
        rows.append({
            "video_id": v["id"],
            "title": sn["title"],
            "published_at": sn["publishedAt"],
            "duration_sec": sec,
            "is_short": int(sec <= 180),
            "views": int(st.get("viewCount", 0)),
            "likes": int(st.get("likeCount", 0)),
            "comments": int(st.get("commentCount", 0)),
            "tags": "|".join(sn.get("tags", [])),
            "url": f"https://youtu.be/{v['id']}",
        })

out = ROOT / "data" / f"{handle}_videos.csv"
with out.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)
print(f"✅ Збережено {len(rows)} відео → {out}")
