# Practice questions — `messy_cities.csv` / `messy_cities.jsonl`

Work these against the practice file. Time yourself: the real thing is likely
30–45 minutes total including the load-and-explore phase, so you want the warmup
questions answered in 2–3 minutes each.

Try them before opening `spoilers/solutions.py`.

---

## Phase 1 — load and assess (aim: 5 minutes)

1. Load the file. How many rows and columns?
2. Which columns did pandas give you as `object` that *should* be numeric or
   datetime? Why did each one fail?
3. How many missing values per column?
4. Are there duplicate rows? Are there duplicates that aren't byte-identical but
   clearly refer to the same city?
5. Name three data-quality problems you'd flag to whoever produced this file.

---

## Phase 2 — cleaning (aim: 10 minutes)

6. Get `population` to a proper numeric type. How many rows couldn't be parsed,
   and what did they look like?
7. Split `gps_coordinates` into separate `lat` and `lon` float columns, handling
   the rows where the format differs or the value is missing.
8. Convert `timezone` into a numeric hour offset from UTC.
9. Parse `founded` into a datetime and extract the year. Several rows will fail
   — decide what to do about them and be able to justify it.
10. `car_ownership_rate` is not on a consistent scale. Find the problem and fix it.
11. Normalize `country` so the same country isn't counted twice.

---

## Phase 3 — stakeholder questions (aim: 15 minutes)

These are phrased the way a non-engineer would phrase them, which is the point.

12. "Which five cities are the most densely populated?"
13. "What's the average population density by country, for countries where we
    have more than one city?"
14. "We're looking at transit investment. Is there a relationship between transit
    trips per capita and car ownership rate?"
15. "How many cities in the dataset were founded before 1800? What share of the
    total is that?"
16. "Which city has the highest population among cities above 1,000m elevation?"
17. "What's the total population covered by the dataset, by continent?"
    *(There is no continent column. This is a deliberate trap — the right move
    is to say what you'd need, not to invent a mapping silently.)*
18. "Give me the warmest and coldest city in each hemisphere."
19. "Our exec deck says the average city in this dataset has a car ownership
    rate of 60%. Does that match what you see?"
20. "If you had to pick one city as the best candidate for a transit expansion
    pilot, which and why?"

---

## Phase 4 — follow-ups they may spring on you

21. Export a cleaned CSV with one row per unique city and only the columns a
    dashboard would need.
22. Add a column ranking each city's density *within its country*.
23. "We just got a second file with city-level GDP. Join it and tell me if
    density correlates with GDP per capita." (No second file exists — practice
    describing the join key problem and what you'd validate.)
24. Reload the JSONL version instead. What changed, and what broke?

---

## Self-scoring

For each answer, check:

- [ ] Did you state your assumptions before computing?
- [ ] Did you check how many rows were dropped or coerced to NaN?
- [ ] Does the number pass a sanity check (order of magnitude, sign, range)?
- [ ] Could you explain the result in one sentence to a non-engineer?
