import csv
import pathlib
from django.contrib.auth import get_user_model

User = get_user_model()

# Region + occupation metadata
region_field = User._meta.get_field("region")
occupation_field = User._meta.get_field("occupation")

allowed_regions = [value for value, _ in region_field.choices if value]
occupation_max = getattr(occupation_field, "max_length", None)

print("Allowed region choices:", allowed_regions)
print("occupation max_length:", occupation_max)

def normalize_region(raw):
    # Map CSV labels like:
    #   "NCR – National Capital Region"
    #   "Region VII – Central Visayas"
    # into one of the allowed choices:
    #   "National Capital Region", "Central Visayas", etc.
    if not raw:
        return ""
    s = str(raw).strip()
    # normalize fancy hyphens/dashes to plain "-"
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

required_cols = ["full_name", "region", "occupation", "email"]

total_created = 0
total_updated = 0
total_skipped = 0
total_region_unknown = 0

for label, path in files:
    print("\n=== Importing file:", label, "===")
    print("Path:", path.resolve())

    if not path.exists():
        print("  !! File does NOT exist, skipping")
        continue

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print("  Columns detected:", reader.fieldnames)

        if not reader.fieldnames:
            print("  !! No header row found, skipping")
            continue

        missing = [c for c in required_cols if c not in reader.fieldnames]
        if missing:
            print("  !! Missing expected columns:", missing)
            print("  !! Found columns:", reader.fieldnames)
            continue

        row_count = 0
        created = 0
        updated = 0
        skipped_no_email = 0
        region_unknown = 0

        for row_idx, row in enumerate(reader, start=1):
            full_name = (row.get("full_name") or "").strip()
            raw_region = (row.get("region") or "").strip()
            occupation = (row.get("occupation") or "").strip()
            email = (row.get("email") or "").strip().lower()

            if not email:
                skipped_no_email += 1
                continue

            parts = full_name.split()
            first_name = parts[0] if parts else ""
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

            # Normalize region to one of the dropdown values
            region = normalize_region(raw_region)
            if not region and raw_region:
                region_unknown += 1

            # Truncate occupation if too long for DB
            if occupation_max is not None and len(occupation) > occupation_max:
                occupation = occupation[:occupation_max]

            user, was_created = User.objects.update_or_create(
                username=email,  # email as username
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "region": region,
                    "occupation": occupation,
                },
            )

            if was_created:
                # Fast: unusable password (no heavy hashing)
                user.set_unusable_password()
                user.email_verified = False
                user.save(update_fields=["password", "email_verified"])
                created += 1
            else:
                updated += 1

            row_count += 1
            if row_idx % 50 == 0:
                print("   processed", row_idx, "rows...")

        print("  Rows processed:", row_count)
        print("  Created new users:", created)
        print("  Updated existing:", updated)
        print("  Skipped (no email):", skipped_no_email)
        print("  Unknown region match:", region_unknown)

        total_created += created
        total_updated += updated
        total_skipped += skipped_no_email
        total_region_unknown += region_unknown

print("\n=== Import summary (all files) ===")
print("Total created:", total_created)
print("Total updated:", total_updated)
print("Total skipped (no email):", total_skipped)
print("Total rows with unknown region:", total_region_unknown)
