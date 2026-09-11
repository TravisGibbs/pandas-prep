# What's hidden in the data

Don't read this until after your first attempt.

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
