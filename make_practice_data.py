"""
Generates a deliberately messy 'cities' dataset in CSV and JSONL.

Every row here contains at least one trap of the kind that shows up in a
30-minute data-wrangling interview. Regenerate any time you want a fresh run.
"""

import csv
import json
from pathlib import Path

OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

COLUMNS = [
    "name",
    "country",
    "population",
    "area_sq_km",
    "elevation_m",
    "timezone",
    "gps_coordinates",
    "avg_temp_c",
    "transit_trips_per_capita",
    "car_ownership_rate",
    "founded",
]

# Traps embedded below, by design:
#  - population: thousands separators, "1.2M" shorthand, blanks, "unknown", a negative
#  - country: USA / U.S.A. / United States / "usa " casing + whitespace variants
#  - area_sq_km: a 0 (division-by-zero for density), a null, a string with units
#  - gps_coordinates: "[lat, lon]" strings, bare "lat,lon", nulls, one swapped-looking pair
#  - timezone: UTC+1, UTC-05:00, utc+5:30, blank
#  - avg_temp_c: one obvious Fahrenheit value, one null
#  - car_ownership_rate: mix of fractions (0.65) and percentages (65.0)  <-- the sneaky one
#  - founded: ISO timestamps, bare years, US-style dates, one BCE-ish year
#  - exact duplicate row + near-duplicate differing only by whitespace/case
ROWS = [
    ["Tokyo", "Japan", "13960000", "2194", "40", "UTC+9", "[35.6762, 139.6503]", "16.0", "620", "0.32", "1457-01-01T00:00:00"],
    ["Delhi", "India", "16,787,941", "1484", "216", "UTC+5:30", "[28.7041, 77.1025]", "25.1", "180", "0.19", "1052-01-01T00:00:00"],
    ["New York", "USA", "8336817", "778.2", "10", "UTC-05:00", "[40.7128, -74.006]", "12.9", "230", "0.45", "1624-01-01T00:00:00"],
    ["New York", "United States", "8336817", "778.2", "10", "UTC-5", "[40.7128, -74.006]", "12.9", "230", "45.0", "1624"],
    ["  london ", "United Kingdom", "8982000", "1572", "11", "UTC+0", "[51.5074, -0.1278]", "11.3", "310", "0.36", "0043-01-01T00:00:00"],
    ["London", "united kingdom", "8982000", "1572", "11", "UTC+0", "[51.5074, -0.1278]", "11.3", "310", "0.36", "0043-01-01T00:00:00"],
    ["Paris", "France", "2148000", "105.4", "35", "UTC+1", "[48.8566, 2.3522]", "12.4", "410", "0.33", "0259-01-01T00:00:00"],
    ["Berlin", "Germany", "3645000", "891.7", "34", "UTC+1", "[52.52, 13.405]", "10.4", "380", "0.33", "1237-01-01T00:00:00"],
    ["Madrid", "Spain", "3223000", "604.3", "667", "UTC+1", "[40.4168, -3.7038]", "15.0", "290", "0.47", "0852-01-01T00:00:00"],
    ["Rome", "Italy", "2873000", "1285", "21", "UTC+1", "[41.9028, 12.4964]", "15.7", "260", "0.62", "0753-01-01T00:00:00"],
    ["Cairo", "Egypt", "9540000", "3085", "23", "UTC+2", "[30.0444, 31.2357]", "21.9", "95", "0.12", "0969-01-01T00:00:00"],
    ["Lagos", "Nigeria", "14862000", "1171", "41", "UTC+1", "[6.5244, 3.3792]", "26.8", "60", "0.08", "1730-01-01T00:00:00"],
    ["Sao Paulo", "Brazil", "12330000", "1521", "760", "UTC-3", "[-23.5505, -46.6333]", "19.3", "270", "0.41", "1554-01-25T00:00:00"],
    ["Buenos Aires", "Argentina", "3075000", "203", "25", "UTC-3", "[-34.6037, -58.3816]", "17.9", "240", "0.38", "1536-02-02T00:00:00"],
    ["Mexico City", "Mexico", "9209944", "1485", "2240", "UTC-6", "[19.4326, -99.1332]", "16.7", "205", "0.36", "1325-01-01T00:00:00"],
    ["Toronto", "Canada", "2794356", "630.2", "76", "UTC-5", "[43.6532, -79.3832]", "9.4", "215", "0.54", "1793-01-01T00:00:00"],
    ["Vancouver", "canada", "662248", "115", "70", "UTC-8", "[49.2827, -123.1207]", "11.0", "190", "0.51", "1886-04-06T00:00:00"],
    ["Sydney", "Australia", "5312000", "12368", "58", "UTC+10", "[-33.8688, 151.2093]", "18.3", "150", "0.66", "1788-01-26T00:00:00"],
    ["Melbourne", "Australia", "5078000", "9993", "31", "UTC+10", "[-37.8136, 144.9631]", "15.1", "140", "0.71", "1835-08-30T00:00:00"],
    ["Singapore", "Singapore", "5686000", "728.6", "15", "UTC+8", "[1.3521, 103.8198]", "27.5", "540", "0.11", "1819-01-29T00:00:00"],
    ["Seoul", "South Korea", "9776000", "605.2", "38", "UTC+9", "[37.5665, 126.978]", "12.5", "580", "0.28", "1394-01-01T00:00:00"],
    ["Hong Kong", "China", "7482000", "1104", "6", "UTC+8", "[22.3193, 114.1694]", "23.3", "610", "0.07", "1842-01-01T00:00:00"],
    ["Shanghai", "China", "24870000", "6341", "4", "UTC+8", "[31.2304, 121.4737]", "17.1", "330", "0.21", "1291-01-01T00:00:00"],
    ["Beijing", "china", "21540000", "16411", "43", "UTC+8", "[39.9042, 116.4074]", "12.9", "310", "0.24", "-1045-01-01T00:00:00"],
    ["Mumbai", "India", "1.24M", "603.4", "14", "UTC+5:30", "[19.076, 72.8777]", "27.2", "240", "0.09", "1507-01-01T00:00:00"],
    ["Bangkok", "Thailand", "10539000", "1569", "2", "utc+7", "[13.7563, 100.5018]", "28.1", "130", "0.44", "1782-04-21T00:00:00"],
    ["Jakarta", "Indonesia", "10560000", "661.5", "8", "UTC+7", "13.7563,100.5018", "27.0", "110", "0.31", "1527-06-22T00:00:00"],
    ["Istanbul", "Turkey", "15520000", "5461", "39", "UTC+3", "[41.0082, 28.9784]", "14.4", "280", "0.29", "0660-01-01T00:00:00"],
    ["Moscow", "Russia", "12506000", "2511", "156", "UTC+3", "[55.7558, 37.6173]", "6.3", "470", "0.38", "1147-01-01T00:00:00"],
    ["Stockholm", "Sweden", "975551", "188", "28", "UTC+1", "[59.3293, 18.0686]", "7.4", "360", "0.4", "1252-01-01T00:00:00"],
    ["Oslo", "Norway", "709037", "454", "23", "UTC+1", "", "6.1", "350", "0.42", "1040-01-01T00:00:00"],
    ["Zurich", "Switzerland", "421878", "87.88", "408", "UTC+1", "[47.3769, 8.5417]", "9.3", "560", "0.35", "0015-01-01T00:00:00"],
    ["Reykjavik", "Iceland", "131136", "273", "61", "UTC+0", "[64.1466, -21.9426]", "5.0", "170", "0.68", "0874-01-01T00:00:00"],
    ["Monaco", "Monaco", "38350", "0", "16", "UTC+1", "[43.7384, 7.4246]", "16.4", "220", "0.75", "1215-01-01T00:00:00"],
    ["Nairobi", "Kenya", "4397073", "696", "1795", "UTC+3", "[-1.2921, 36.8219]", "19.0", "85", "0.14", "1899-01-01T00:00:00"],
    ["Lima", "Peru", "9752000", "2672", "154", "UTC-5", "[-12.0464, -77.0428]", "19.2", "160", "0.22", "01/18/1535"],
    ["Santiago", "Chile", "6812000", "641", "570", "UTC-4", "[-33.4489, -70.6693]", "14.6", "195", "0.33", "02/12/1541"],
    ["Phoenix", "U.S.A.", "1608139", "1341 sq km", "331", "UTC-7", "[33.4484, -112.074]", "75.2", "125", "0.82", "1868-01-01T00:00:00"],
    ["Detroit", "usa ", "639111", "", "183", "UTC-5", "[42.3314, -83.0458]", "10.2", "70", "0.79", "1701-07-24T00:00:00"],
    ["Atlantis", "unknown", "unknown", "999", "-2000", "", "[0, 0]", "", "0", "N/A"],
    ["Nowhere", "Testland", "-5000", "12", "", "UTC+0", "[91.0, 200.0]", "", "", "", ],
    ["Dubai", "UAE", "3331000", "4114", "5", "UTC+4", "[25.2048, 55.2708]", "28.0", "90", "0.73", "1833-01-01T00:00:00"],
    # exact duplicate of the Dubai row above
    ["Dubai", "UAE", "3331000", "4114", "5", "UTC+4", "[25.2048, 55.2708]", "28.0", "90", "0.73", "1833-01-01T00:00:00"],
]


def normalize(row):
    """Pad short rows so the CSV writer doesn't choke."""
    return (row + [""] * len(COLUMNS))[: len(COLUMNS)]


def main():
    rows = [normalize(r) for r in ROWS]

    csv_path = OUT / "messy_cities.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(COLUMNS)
        w.writerows(rows)

    # JSONL variant: same data, but blanks become real nulls and a couple of
    # records carry an extra nested field the CSV can't express.
    jsonl_path = OUT / "messy_cities.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            rec = {}
            for col, val in zip(COLUMNS, row):
                rec[col] = None if val == "" else val
            if i % 7 == 0:
                rec["metadata"] = {"source": "gazetteer", "confidence": 0.9}
            if i % 11 == 0:
                rec["tags"] = ["capital", "coastal"]
            f.write(json.dumps(rec) + "\n")

    print(f"wrote {csv_path} ({len(rows)} rows)")
    print(f"wrote {jsonl_path} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
