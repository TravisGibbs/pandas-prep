# Data wrangling interview prep

Practice material for a screen-shared, timed data ingestion and wrangling
exercise: load a raw file, clean it, answer stakeholder questions out loud.

The dataset here is synthetic and deliberately messy. Every column contains at
least one of the failure modes that show up in real ingestion work.

## Layout

```
data/messy_cities.csv      # 43 rows, ~15 embedded data-quality traps
data/messy_cities.jsonl    # same data as JSON Lines, plus nested fields
docs/practice_questions.md # 24 questions across 4 phases — start here
docs/pandas_interview_cheatsheet.md
make_practice_data.py      # regenerate the data
solutions.py               # reference answers — open after you've tried
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Verify it works:

```bash
python solutions.py
```

## How to use this

1. Open `docs/practice_questions.md`. Don't look at `solutions.py` yet.
2. Load `data/messy_cities.csv` in a notebook. Spend five minutes only
   inspecting — `.info()`, `.describe()`, `.isna().sum()`, `.value_counts()`.
3. Work the questions in order, timing yourself. Phase 1 in 5 minutes,
   Phase 2 in 10, Phase 3 in 15.
4. Narrate as you go, out loud, as if someone is watching. This is the part
   people skip in practice and get judged on in the room.
5. Then diff your approach against `solutions.py`.

Run `python make_practice_data.py` to regenerate the files if you want to edit
the traps and re-run cold.

## What's hidden in the data

Spoilers — skip this section until after your first attempt.

<details>
<summary>Reveal</summary>

- `population`: thousands separators, `1.24M` shorthand, `unknown`, a negative
- `country`: `USA` / `U.S.A.` / `United States` / `usa ` for one country
- `area_sq_km`: a zero (divide-by-zero on density), a value with a unit suffix
- `gps_coordinates`: stringified list, one bare `lat,lon`, nulls, one pair
  outside valid range
- `timezone`: `UTC+9`, `UTC-05:00`, `utc+5:30`, blank
- `avg_temp_c`: one value in Fahrenheit
- `car_ownership_rate`: mixes fractions (`0.45`) and percentages (`45.0`)
- `founded`: ISO timestamps, bare years, `MM/DD/YYYY`, a negative (BCE) year,
  and several years before 1677 that overflow `datetime64[ns]`
- one exact duplicate row, one near-duplicate differing by case and whitespace
- JSONL only: nested `metadata` dict and a `tags` array

</details>
