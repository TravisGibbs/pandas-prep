"""
Reference solutions for practice_questions.md.

Open this only after you've had a go yourself. The point is not that your code
matches mine — it's that you hit the same traps and handled them deliberately.

Run: python3 solutions.py
"""

import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

CURRENT_YEAR = 2026
DATA = Path(__file__).parent / "data"


def rule(label):
    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)


# ----------------------------------------------------------------------
# Phase 1 — load and assess
# ----------------------------------------------------------------------
rule("PHASE 1 — LOAD AND ASSESS")

df = pd.read_csv(DATA / "messy_cities.csv")

print("shape:", df.shape)
print("\ndtypes:\n", df.dtypes)
print("\nmissing per column:\n", df.isna().sum())
print("\nexact duplicate rows:", df.duplicated().sum())

# Near-duplicates: same city, different spelling/whitespace/country label.
near = df.assign(
    _n=df["name"].str.strip().str.lower()
).loc[lambda d: d["_n"].duplicated(keep=False)].sort_values("_n")
print("\nrows sharing a normalized name:\n", near[["name", "country", "population"]])

# Q5 — problems worth flagging:
#   * population mixes raw integers, thousands separators, "1.2M" shorthand,
#     "unknown", and a negative value
#   * country has casing/punctuation variants for the same nation
#   * car_ownership_rate mixes fractions and percentages
#   * founded mixes ISO timestamps, bare years, and US-style dates
#   * one area is 0 (divide-by-zero), one carries a unit suffix
#   * one temperature is clearly Fahrenheit
#   * one coordinate pair is outside valid lat/lon range


# ----------------------------------------------------------------------
# Phase 2 — cleaning
# ----------------------------------------------------------------------
rule("PHASE 2 — CLEANING")

clean = df.copy()

# Q6 — population -------------------------------------------------------
def parse_population(v):
    """Handle '16,787,941', '1.24M', 'unknown', and plain integers."""
    if pd.isna(v):
        return np.nan
    s = str(v).strip().replace(",", "")
    m = re.fullmatch(r"([\d.]+)\s*([KMB])", s, flags=re.IGNORECASE)
    if m:
        mult = {"K": 1e3, "M": 1e6, "B": 1e9}[m.group(2).upper()]
        return float(m.group(1)) * mult
    try:
        return float(s)
    except ValueError:
        return np.nan


clean["population"] = clean["population"].apply(parse_population)

# A negative population is not a real value. Null it rather than let it
# quietly drag down a country total.
n_negative = (clean["population"] < 0).sum()
clean.loc[clean["population"] < 0, "population"] = np.nan
print(f"population: {clean['population'].isna().sum()} unparseable "
      f"(incl. {n_negative} negative values nulled)")
print(df.loc[clean["population"].isna(), ["name", "population"]].to_string(index=False))

# area ------------------------------------------------------------------
clean["area_sq_km"] = pd.to_numeric(
    clean["area_sq_km"].astype(str).str.replace(r"[^\d.]", "", regex=True),
    errors="coerce",
)
# Zero area is not meaningful for a density denominator.
clean.loc[clean["area_sq_km"] <= 0, "area_sq_km"] = np.nan

clean["elevation_m"] = pd.to_numeric(clean["elevation_m"], errors="coerce")
clean["transit_trips_per_capita"] = pd.to_numeric(
    clean["transit_trips_per_capita"], errors="coerce"
)


# Q7 — coordinates ------------------------------------------------------
def parse_coords(v):
    if pd.isna(v):
        return (np.nan, np.nan)
    s = str(v).strip()
    try:
        lat, lon = ast.literal_eval(s)
    except (ValueError, SyntaxError):
        parts = s.split(",")
        if len(parts) != 2:
            return (np.nan, np.nan)
        try:
            lat, lon = float(parts[0]), float(parts[1])
        except ValueError:
            return (np.nan, np.nan)
    lat, lon = float(lat), float(lon)
    # Out-of-range coordinates are corrupt, not merely unusual.
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return (np.nan, np.nan)
    return (lat, lon)


clean[["lat", "lon"]] = pd.DataFrame(
    clean["gps_coordinates"].apply(parse_coords).tolist(), index=clean.index
)
print(f"\ncoordinates: {clean['lat'].isna().sum()} rows without usable lat/lon")


# Q8 — UTC offset -------------------------------------------------------
def utc_offset_hours(tz):
    if pd.isna(tz):
        return np.nan
    m = re.match(r"utc\s*([+-])?\s*(\d{1,2})(?::?(\d{2}))?$", str(tz).strip().lower())
    if not m:
        return np.nan
    sign = -1 if m.group(1) == "-" else 1
    return sign * (int(m.group(2)) + int(m.group(3) or 0) / 60)


clean["utc_offset"] = clean["timezone"].apply(utc_offset_hours)
print(f"utc_offset: {clean['utc_offset'].isna().sum()} unparseable")


# Q9 — founded year -----------------------------------------------------
# Mixed formats, plus years before 1677 that fall outside the datetime64[ns]
# range. Since only the year matters for the questions asked, extract the year
# directly instead of forcing a datetime. Stating that trade-off out loud is
# the thing being tested here.
def parse_founded_year(v):
    if pd.isna(v):
        return np.nan
    s = str(v).strip()
    m = re.match(r"^(-?\d{1,4})-\d{2}-\d{2}", s)     # ISO, incl. negative years
    if m:
        return int(m.group(1))
    m = re.match(r"^\d{1,2}/\d{1,2}/(\d{4})$", s)    # MM/DD/YYYY
    if m:
        return int(m.group(1))
    m = re.fullmatch(r"-?\d{1,4}", s)                # bare year
    if m:
        return int(s)
    return np.nan


clean["founded_year"] = clean["founded"].apply(parse_founded_year)
clean["age_years"] = CURRENT_YEAR - clean["founded_year"]
print(f"founded_year: {clean['founded_year'].isna().sum()} unparseable")


# Q10 — car ownership scale --------------------------------------------
# Values cluster in 0–1, but a couple arrived as percentages. Anything above 1
# on a column documented as a rate is a unit error, not a real outlier.
over_one = clean["car_ownership_rate"].pipe(pd.to_numeric, errors="coerce") > 1
clean["car_ownership_rate"] = pd.to_numeric(clean["car_ownership_rate"], errors="coerce")
print(f"\ncar_ownership_rate: {over_one.sum()} value(s) > 1, rescaling by /100")
clean.loc[over_one, "car_ownership_rate"] = clean.loc[over_one, "car_ownership_rate"] / 100


# temperature -----------------------------------------------------------
clean["avg_temp_c"] = pd.to_numeric(clean["avg_temp_c"], errors="coerce")
# 75.2 "°C" is not a habitable city. Almost certainly Fahrenheit.
suspect_f = clean["avg_temp_c"] > 50
print(f"avg_temp_c: {suspect_f.sum()} value(s) > 50C, treating as Fahrenheit")
clean.loc[suspect_f, "avg_temp_c"] = (clean.loc[suspect_f, "avg_temp_c"] - 32) * 5 / 9


# Q11 — country normalization ------------------------------------------
COUNTRY_ALIASES = {
    "u.s.a.": "United States",
    "usa": "United States",
    "us": "United States",
    "united states": "United States",
    "uae": "United Arab Emirates",
}
_norm = clean["country"].astype(str).str.strip().str.lower()
clean["country_clean"] = _norm.map(COUNTRY_ALIASES).fillna(
    _norm.str.title()
)
clean.loc[_norm.isin(["unknown", "nan", ""]), "country_clean"] = np.nan

clean["name_clean"] = clean["name"].str.strip().str.title()

# Dedupe on the normalized identity.
before = len(clean)
clean = clean.drop_duplicates(subset=["name_clean", "country_clean"], keep="first")
print(f"\ndeduped {before} -> {len(clean)} rows on (name, country)")

# Derived metric.
clean["density"] = clean["population"] / clean["area_sq_km"]


# ----------------------------------------------------------------------
# Phase 3 — stakeholder questions
# ----------------------------------------------------------------------
rule("PHASE 3 — STAKEHOLDER QUESTIONS")

# Q12
print("\nQ12 — five densest cities (people per sq km):")
print(
    clean.nlargest(5, "density")[["name_clean", "country_clean", "population",
                                  "area_sq_km", "density"]]
    .round(0)
    .to_string(index=False)
)

# Q13
print("\nQ13 — mean density by country, countries with >1 city:")
by_country = (
    clean.dropna(subset=["country_clean"])
    .groupby("country_clean")
    .agg(n_cities=("name_clean", "count"),
         mean_density=("density", "mean"),
         total_pop=("population", "sum"))
    .query("n_cities > 1")
    .sort_values("mean_density", ascending=False)
)
print(by_country.round(1).to_string())

# Q14
pair = clean[["transit_trips_per_capita", "car_ownership_rate"]].dropna()
r_pearson = pair["transit_trips_per_capita"].corr(pair["car_ownership_rate"])
r_spearman = pair["transit_trips_per_capita"].corr(
    pair["car_ownership_rate"], method="spearman"
)
print(f"\nQ14 — transit vs car ownership, n={len(pair)}")
print(f"  Pearson  r = {r_pearson:.3f}")
print(f"  Spearman r = {r_spearman:.3f}")
print("  Negative: cities with heavier transit use tend to have lower car")
print("  ownership. Association only — n is small and both are plausibly")
print("  driven by density and city wealth.")

# Q15
founded_known = clean["founded_year"].notna()
pre_1800 = (clean["founded_year"] < 1800) & founded_known
print(f"\nQ15 — founded before 1800: {pre_1800.sum()} of "
      f"{founded_known.sum()} cities with a known founding year "
      f"({pre_1800.sum() / founded_known.sum():.1%})")
print(f"  ({(~founded_known).sum()} rows excluded for unparseable dates — "
      f"the denominator matters here.)")

# Q16
high = clean[clean["elevation_m"] > 1000]
print("\nQ16 — largest city above 1000m elevation:")
print(high.nlargest(1, "population")[
    ["name_clean", "country_clean", "elevation_m", "population"]
].to_string(index=False))

# Q17
print("\nQ17 — population by continent:")
print("  There is no continent column in this dataset, and no reliable way to")
print("  derive one from what's here. Options: (a) join a country->continent")
print("  reference table, (b) derive roughly from lat/lon, which misclassifies")
print("  transcontinental countries. I'd want the reference table. What I can")
print("  give you right now is population by country:")
print(clean.dropna(subset=["country_clean"])
      .groupby("country_clean")["population"].sum()
      .sort_values(ascending=False).head(5).to_string())

# Q18
clean["hemisphere"] = np.where(clean["lat"] >= 0, "North", "South")
temps = clean.dropna(subset=["avg_temp_c", "lat"])
print("\nQ18 — temperature extremes by hemisphere:")
for hemi, grp in temps.groupby("hemisphere"):
    warm = grp.loc[grp["avg_temp_c"].idxmax()]
    cold = grp.loc[grp["avg_temp_c"].idxmin()]
    print(f"  {hemi}: warmest {warm['name_clean']} ({warm['avg_temp_c']:.1f}C), "
          f"coldest {cold['name_clean']} ({cold['avg_temp_c']:.1f}C)")

# Q19
mean_car = clean["car_ownership_rate"].mean()
median_car = clean["car_ownership_rate"].median()
print(f"\nQ19 — mean car ownership rate: {mean_car:.1%} "
      f"(median {median_car:.1%}), n={clean['car_ownership_rate'].notna().sum()}")
print("  The deck's 60% doesn't match. Two likely causes: the raw file mixes")
print("  fractions and percentages, so an unconverted average is inflated; and")
print("  this is an unweighted mean across cities, not weighted by population.")
pop_weighted = np.average(
    clean.dropna(subset=["car_ownership_rate", "population"])["car_ownership_rate"],
    weights=clean.dropna(subset=["car_ownership_rate", "population"])["population"],
)
print(f"  Population-weighted rate: {pop_weighted:.1%}")

# Q20
print("\nQ20 — transit pilot candidate (judgement question, defend your criteria):")
cand = clean.dropna(subset=["density", "transit_trips_per_capita", "car_ownership_rate"])
cand = cand.assign(
    score=(
        cand["density"].rank(pct=True)
        + (1 - cand["transit_trips_per_capita"].rank(pct=True))
        + cand["car_ownership_rate"].rank(pct=True)
    )
)
print("  Criteria: high density (demand), low current transit use and high car")
print("  ownership (headroom). Equal-weighted percentile ranks.")
print(cand.nlargest(3, "score")[
    ["name_clean", "country_clean", "density", "transit_trips_per_capita",
     "car_ownership_rate", "score"]
].round(2).to_string(index=False))


# ----------------------------------------------------------------------
# Phase 4 — follow-ups
# ----------------------------------------------------------------------
rule("PHASE 4 — FOLLOW-UPS")

# Q22 — rank within group
clean["density_rank_in_country"] = (
    clean.groupby("country_clean")["density"].rank(ascending=False, method="min")
)
print("\nQ22 — density rank within country (sample):")
print(clean.dropna(subset=["country_clean"])
      .sort_values(["country_clean", "density_rank_in_country"])
      [["country_clean", "name_clean", "density", "density_rank_in_country"]]
      .head(10).round(1).to_string(index=False))

# Q21 — export
cols = ["name_clean", "country_clean", "population", "area_sq_km", "density",
        "lat", "lon", "utc_offset", "avg_temp_c", "transit_trips_per_capita",
        "car_ownership_rate", "founded_year"]
clean[cols].to_csv(Path(__file__).parent / "cities_clean.csv", index=False)
print(f"\nQ21 — wrote cities_clean.csv ({len(clean)} rows, {len(cols)} columns)")

# Q24 — JSONL reload
jl = pd.read_json(DATA / "messy_cities.jsonl", lines=True)
print(f"\nQ24 — JSONL loads to {jl.shape}, vs CSV {df.shape}")
print("  Extra columns present only in JSONL:",
      [c for c in jl.columns if c not in df.columns])
print("  Nested dicts need pd.json_normalize to flatten:")
print(pd.json_normalize(jl.to_dict("records")).columns.tolist()[-4:])
print("  Note JSON nulls arrive as NaN directly, so na_values tricks don't apply,")
print("  and read_json may infer types per-column differently than read_csv.")
