import csv
import pathlib
from django.contrib.auth import get_user_model

User = get_user_model()

region_field = User._meta.get_field("region")
allowed_regions = [value for value, _ in region_field.choices if value]

print("Allowed region choices:", allowed_regions)

def normalize_region(raw):
    if not raw:
        return ""
    s = str(raw).strip()
    for ch in ("\u2013", "\u2014", "\u2011", "\u2010"):
        s = s.replace(ch, "-")
    s_upper = s.upper()

    best = ""
    for choice in allowed_regions:
        cu = choice.upper()
        if cu in s_upper and len(choice) > len(best):
            best = choice
    return best

files = [
    ("register_live_in.csv", pathlib.Path("imports/register_live_in.csv")),
    ("register_live_out.csv", pathlib.Path("imports/register_live_out.csv")),
]

unknown_rows = []

for label, path in files:
    print(f"\nScanning file: {label}")
    if not path.exists():
        print("  !! Missing:", path)
        continue

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print("  Columns:", reader.fieldnames)

        for row_idx, row in enumerate(reader, start=1):
            raw_region = (row.get("region") or "").strip()
            email = (row.get("email") or "").strip().lower()
            full_name = (row.get("full_name") or "").strip()

            if not email:
                continue  # skip rows with no email

            normalized = normalize_region(raw_region)
            if raw_region and not normalized:
                unknown_rows.append(
                    {
                        "file": label,
                        "row": row_idx,
                        "email": email,
                        "full_name": full_name,
                        "raw_region": raw_region,
                    }
                )

print("\n=== Unknown region rows ===")
for item in unknown_rows:
    print(
        f"{item['file']} | row {item['row']:>4} | {item['email']} | "
        f"{item['full_name']} | raw_region={item['raw_region']!r}"
    )

print("\nTotal unknown region rows:", len(unknown_rows))
