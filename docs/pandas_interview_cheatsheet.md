# Pandas cheat sheet — data ingestion & wrangling interview

The goal is muscle memory. No autocomplete, no AI in the room. If you have to
stop and think about `pd.to_numeric(errors="coerce")`, that's 20 seconds you
didn't spend on the actual question.

---

## 0. The one cell you paste at the top of every notebook

```python
import pandas as pd
import numpy as np
import json, ast, re

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
pd.set_option("display.max_rows", 100)
```

Have this saved somewhere you can paste in under five seconds.

---

## 1. Loading — be ready for either format

Their prep page shows a CSV but the starter snippet is `read_json(lines=True)`.
Cover both:

```python
df = pd.read_csv("data.csv")               # CSV
df = pd.read_json("data.jsonl", lines=True)  # JSON Lines (one object per line)
df = pd.read_json("data.json")               # single JSON array
```

If you don't know which you got, look at the file first:

```python
print(open("data.txt").readline())
```

Useful `read_csv` arguments when it fights you:

```python
pd.read_csv(path,
            dtype=str,            # read everything as text, clean it yourself
            na_values=["", "N/A", "NA", "null", "none", "unknown", "-"],
            keep_default_na=True,
            thousands=",",        # parses "16,787,941" as a number
            encoding="utf-8",
            sep=",")
```

`dtype=str` is worth knowing about: it stops pandas silently guessing a column's
type from the first few hundred rows. You then convert deliberately. It costs a
few extra lines but removes a whole class of surprise.

Nested JSON (JSONL often has it):

```python
pd.json_normalize(records)                    # flattens metadata.source -> "metadata.source"
df = pd.json_normalize(df.to_dict("records"))  # flatten after loading
```

---

## 2. First 60 seconds — look before you leap

```python
df.shape
df.head(10)
df.dtypes
df.info()
df.describe(include="all")
df.isna().sum()
df.duplicated().sum()
df["country"].value_counts(dropna=False)
df["country"].unique()
df.nunique()
```

Say what you see out loud. "Population came in as object, not int — something
non-numeric is in there." That narration is a large part of what's being scored.

---

## 3. Type coercion — the core skill

```python
# numbers, bad values -> NaN instead of exception
df["population"] = pd.to_numeric(df["population"], errors="coerce")

# strip separators first if needed
df["population"] = pd.to_numeric(
    df["population"].astype(str).str.replace(",", "", regex=False),
    errors="coerce",
)

# dates
df["founded"] = pd.to_datetime(df["founded"], errors="coerce")
df["founded"] = pd.to_datetime(df["founded"], format="mixed", errors="coerce")
df["founded"] = pd.to_datetime(df["founded"], utc=True, errors="coerce")

df["year"] = df["founded"].dt.year
df["century"] = (df["founded"].dt.year - 1) // 100 + 1
```

Then *check what you lost*:

```python
df["population"].isna().sum()
df.loc[df["population"].isna(), "name"]   # which rows failed to parse?
```

Losing rows silently to `errors="coerce"` is the single most common way to get a
wrong answer that looks confident.

---

## 4. String cleaning

```python
df["name"] = df["name"].str.strip()
df["country_clean"] = df["country"].str.strip().str.lower()
df["country_clean"] = df["country_clean"].replace({
    "u.s.a.": "usa", "united states": "usa", "us": "usa",
})

df["col"].str.replace(r"[^\d.]", "", regex=True)   # keep digits and dots
df["col"].str.contains("york", case=False, na=False)
df["col"].str.extract(r"UTC([+-]\d+)")             # capture group -> new column
df["col"].str.split(",", expand=True)              # -> DataFrame of parts
```

---

## 5. The stringified-list column (they showed you this one)

`gps_coordinates` arrives as the *text* `"[52.52, 13.405]"`. Three ways:

```python
# A. json.loads — strict, needs valid JSON
df["coords"] = df["gps_coordinates"].apply(json.loads)

# B. ast.literal_eval — tolerant of Python-style literals
df["coords"] = df["gps_coordinates"].apply(ast.literal_eval)

# C. safest: handle nulls and malformed values
def parse_coords(v):
    if pd.isna(v):
        return (np.nan, np.nan)
    try:
        lat, lon = ast.literal_eval(v)
    except (ValueError, SyntaxError):
        try:
            lat, lon = [float(x) for x in str(v).split(",")]
        except ValueError:
            return (np.nan, np.nan)
    return (float(lat), float(lon))

df[["lat", "lon"]] = pd.DataFrame(
    df["gps_coordinates"].apply(parse_coords).tolist(), index=df.index
)
```

The `.tolist()` + `pd.DataFrame(..., index=df.index)` pattern for splitting one
column into two is worth memorizing — `index=df.index` is the part people forget,
and without it the assignment misaligns.

---

## 6. UTC offset strings

```python
def utc_offset_hours(tz):
    if pd.isna(tz):
        return np.nan
    m = re.match(r"utc\s*([+-])?\s*(\d{1,2})(?::?(\d{2}))?$", str(tz).strip().lower())
    if not m:
        return np.nan
    sign = -1 if m.group(1) == "-" else 1
    hours = int(m.group(2))
    minutes = int(m.group(3) or 0)
    return sign * (hours + minutes / 60)

df["utc_offset"] = df["timezone"].apply(utc_offset_hours)
```

---

## 7. Duplicates and missing data

```python
df.duplicated().sum()
df[df.duplicated(keep=False)].sort_values("name")     # see all copies
df = df.drop_duplicates()
df = df.drop_duplicates(subset=["name", "country_clean"], keep="first")

df.isna().sum().sort_values(ascending=False)
df.dropna(subset=["population", "area_sq_km"])
df["col"].fillna(df["col"].median())
```

Say your rule out loud before applying it: "I'll dedupe on name + normalized
country and keep the first occurrence — flagging that if the duplicates disagree
on population, first-wins is arbitrary."

---

## 8. Derived columns

```python
df["density"] = df["population"] / df["area_sq_km"]

# guard against divide-by-zero
df["density"] = df["population"] / df["area_sq_km"].replace(0, np.nan)

# chained, readable
df = df.assign(
    density=lambda d: d["population"] / d["area_sq_km"].replace(0, np.nan),
    age_years=lambda d: 2026 - d["founded"].dt.year,
)

# conditional buckets
df["size_class"] = pd.cut(df["population"],
                          bins=[0, 1e6, 5e6, 1e7, np.inf],
                          labels=["small", "mid", "large", "mega"])

df["hemisphere"] = np.where(df["lat"] >= 0, "north", "south")
```

---

## 9. Filter / sort / rank

```python
df.sort_values("density", ascending=False).head(5)
df.nlargest(5, "density")[["name", "country", "density"]]
df.nsmallest(3, "avg_temp_c")

mask = (df["population"] > 1e6) & (df["car_ownership_rate"] < 0.4)
df.loc[mask, ["name", "population"]]

df[df["country_clean"].isin(["usa", "canada"])]
df[df["founded"].dt.year < 1800]
df.query("population > 1e6 and avg_temp_c < 15")
```

`&` and `|` with parentheses around each condition — not `and`/`or`.

---

## 10. Group-by and aggregation

```python
df.groupby("country_clean")["population"].sum().sort_values(ascending=False)

df.groupby("country_clean").agg(
    n_cities=("name", "count"),
    total_pop=("population", "sum"),
    mean_density=("density", "mean"),
    max_elev=("elevation_m", "max"),
).reset_index().sort_values("total_pop", ascending=False)

# top row per group
df.sort_values("population", ascending=False).groupby("country_clean").head(1)

# share of group total
df["pop_share"] = df["population"] / df.groupby("country_clean")["population"].transform("sum")

df.pivot_table(index="country_clean", columns="size_class",
               values="population", aggfunc="sum", fill_value=0)
```

`transform` vs `agg`: `agg` collapses to one row per group, `transform` gives you
a value back for every original row. The share-of-total calculation above only
works because of `transform`.

---

## 11. Relationships

```python
df[["population", "density", "transit_trips_per_capita", "car_ownership_rate"]].corr()
df["transit_trips_per_capita"].corr(df["car_ownership_rate"])
df["transit_trips_per_capita"].corr(df["car_ownership_rate"], method="spearman")
```

If asked "is there a relationship between X and Y", give the number *and* a
caveat: n is small, correlation isn't causation, one outlier may be driving it.
Then check by dropping the outlier and rerunning.

---

## 12. Outliers

```python
df["avg_temp_c"].describe()

q1, q3 = df["density"].quantile([0.25, 0.75])
iqr = q3 - q1
out = df[(df["density"] < q1 - 1.5 * iqr) | (df["density"] > q3 + 1.5 * iqr)]

z = (df["density"] - df["density"].mean()) / df["density"].std()
df[z.abs() > 3]
```

---

## 13. Merging (in case they hand you a second file)

```python
merged = left.merge(right, on="city_id", how="left", validate="one_to_one")
merged = left.merge(right, left_on="name", right_on="city", how="inner")

# always check what happened
print(len(left), len(right), len(merged))
merged = left.merge(right, on="k", how="outer", indicator=True)
merged["_merge"].value_counts()
```

`validate=` and `indicator=True` are how you catch a fan-out join before it
silently inflates your totals.

---

## 14. Output

```python
df.to_csv("out.csv", index=False)   # index=False, always
df.to_dict("records")
print(df.to_string())               # no truncation
```

---

## Things that trip people up under time pressure

- `SettingWithCopyWarning` → you sliced then assigned. Use `.loc[mask, "col"] = x`
  or `.copy()` after the slice.
- `and` / `or` in a boolean mask → use `&` / `|` with parentheses.
- `inplace=True` is not worth the risk; reassign instead.
- Chained `df[df.a > 1]["b"] = 5` silently does nothing. Use `.loc`.
- `df.mean()` skips NaN by default — fine, but know it's happening when you
  report an average.
- Integer columns become floats the moment a NaN appears. That's expected.
- `df.sort_values()` returns a new frame; it doesn't sort in place.
