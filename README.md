# What drives views on a top Ukrainian tech YouTube channel

Analysis of **1,070 videos (2014–2026)** from one of the largest Ukrainian-language tech review channels (437K subscribers), built to answer one question: *which topics, formats and brands predict views?*

**Interactive dashboard:** [Tableau Public](https://public.tableau.com/app/profile/oleksii.riabtsev/viz/YouTubeContentAnalysisLuchkovChannel/WhatdrivesviewsonatopUkrainiantechYouTubechannel1070videos20142026)

## Key findings (long videos, 2023–2026)

| Content format | Median views | Videos |
|---|---|---|
| Long-term use ("30 days with…") | 65,722 | 31 |
| Comparisons & buying guides | 57,753 | 43 |
| Tips & hidden features | 51,354 | 22 |
| News & leaks | 50,384 | 20 |
| Reviews & unboxings | 44,853 | 151 |
| Top lists | 40,630 | 36 |

- Long-term-use videos earn **47% more** than standard reviews, yet reviews are the most common format.
- **Apple** topics lead (median 55.5K) vs Samsung (35.3K).
- The 2023 drop in views matches the channel's switch to Ukrainian, not a change in content quality.
- Viral hits share **curiosity-gap titles** (+29% median), a signal worth A/B testing.

## Method

1. Pull all public videos with the **YouTube Data API v3** (`scripts/01_fetch_youtube.py`).
2. Split Shorts (≤180 s) from long videos.
3. Classify each title into 8 content formats and 5 brands with keyword rules (`scripts/02_classify.py`); unclassified share reduced from 66% to 16% over 3 iterations.
4. Compare **medians** with sample size shown; groups under 10 videos excluded.
5. Validate every Tableau figure against the Python output.

## Run it yourself

```bash
# 1. Get a free YouTube Data API key (Google Cloud Console)
echo "YOUTUBE_API_KEY=your_key_here" > .env

# 2. Fetch any channel by its @handle
python3 scripts/01_fetch_youtube.py lublog

# 3. Classify and print medians
python3 scripts/02_classify.py lublog
```

Python 3.9+, standard library only — no extra packages needed.

## Repository

```
scripts/01_fetch_youtube.py   # YouTube Data API → CSV
scripts/02_classify.py        # format/brand classification + medians
data/lublog_videos.csv        # raw export (public data)
data/lublog_classified.csv    # classified dataset used in Tableau
```

## Author

**Oleksii Riabtsev** — video editor and colorist (5+ years in content production) analysing YouTube channels for creators. Tools: Python, SQL, Tableau, YouTube Data API.
