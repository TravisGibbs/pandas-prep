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
spoilers/                  # answer key + reference solutions — open after you've tried
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Verify it works:

```bash
python spoilers/solutions.py
```

## How to use this

1. Open `docs/practice_questions.md`. Don't look at `spoilers/` yet.
2. Load `data/messy_cities.csv` in a notebook. Spend five minutes only
   inspecting — `.info()`, `.describe()`, `.isna().sum()`, `.value_counts()`.
3. Work the questions in order, timing yourself. Phase 1 in 5 minutes,
   Phase 2 in 10, Phase 3 in 15.
4. Narrate as you go, out loud, as if someone is watching. This is the part
   people skip in practice and get judged on in the room.
5. Then diff your approach against `spoilers/solutions.py`.

Run `python make_practice_data.py` to regenerate the files if you want to edit
the traps and re-run cold.

## Spoilers

The list of intentional data traps and the full reference solutions live in
`spoilers/` — don't open either until after your first attempt.
