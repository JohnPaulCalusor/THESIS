from django.contrib.auth import get_user_model

User = get_user_model()

# Map emails -> canonical region string (must match choices)
EMAIL_TO_REGION = {
    # CAR
    "fbmacarayo@uc-bcf.edu.ph": "Cordillera Administrative Region",
    "ncbaldo@uc-bcf.edu.ph": "Cordillera Administrative Region",

    # NCR
    "cclaconsay@ust.edu.ph": "National Capital Region",
    "rmmalabanan@rtu.edu.ph": "National Capital Region",
    "michael.millanes@dlsu.edu.ph": "National Capital Region",

    # Ilocos Region
    "osa@lyceum.edu.ph": "Ilocos Region",
    "alferos.ednalyn.b@lyceum.edu.ph": "Ilocos Region",

    # Cagayan Valley
    "ajgenato@nvsu.edu.ph": "Cagayan Valley",

    # Central Luzon
    "susiepasia2000@gmail.com": "Central Luzon",

    # Calabarzon
    "gracedesembrana@gmail.com": "Calabarzon",
    "agudilla.mg@gmail.com": "Calabarzon",

    # Western Visayas
    "dsaunor2015@gmail.com": "Western Visayas",
    "m.gaduyon@usls.edu.ph": "Western Visayas",
    "a.esmane@usls.edu.ph": "Western Visayas",
    "jose.magbanua@antiquespride.edu.ph": "Western Visayas",
    # Strong inference: VMA Global College in Bacolod
    "vma.sas2023@gmail.com": "Western Visayas",

    # Central Visayas
    "abepcadelina@su.edu.ph": "Central Visayas",
    "reynerio.abayon@ctu.edu.ph": "Central Visayas",
    "dannypatalinghug021375@gmail.com": "Central Visayas",

    # Eastern Visayas
    "joseph.padilla@vsu.edu.ph": "Eastern Visayas",
    "rhodora.bande@vsu.edu.ph": "Eastern Visayas",
    "mm.gongora@vsu.edu.ph": "Eastern Visayas",
    "christina.gabrillo@vsu.edu.ph": "Eastern Visayas",
    "kmolina@southernleytestateu.edu.ph": "Eastern Visayas",
    "minervaslsucareercenter@gmail.com": "Eastern Visayas",

    # Zamboanga Peninsula
    "jayroslinda@jrmsu.edu.ph": "Zamboanga Peninsula",

    # Northern Mindanao
    "johndavid.moncada@ustp.edu.ph": "Northern Mindanao",

    # Davao Region
    "lory.alcazar@hcdc.edu.ph": "Davao Region",
    "zuliekacejay.almonares@hcdc.edu.ph": "Davao Region",
    "pontini.coloscos@hcdc.edu.ph": "Davao Region",
    "kbayon@hcdc.edu.ph": "Davao Region",
    "mariejune.rivera@hcdc.edu.ph": "Davao Region",
    "karlo.buenavidez@hcdc.edu.ph": "Davao Region",
    "armela.mendoza@hcdc.edu.ph": "Davao Region",
    "jemaima.marohom@hcdc.edu.ph": "Davao Region",
    "janice.sipin@acn.edu.ph": "Davao Region",

    # Caraga
    "rgenderez@nemsu.edu.ph": "Caraga",
}

# For the one weird "username = location" user
USERNAME_TO_REGION = {
    "sogod southern leyte": "Eastern Visayas",
}

updated = 0
already_ok = 0
missing = []

print("=== Backfilling member regions ===")

for email, region in EMAIL_TO_REGION.items():
    try:
        u = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        missing.append(email)
        print(f"[MISS] No user with email {email!r}")
        continue

    old = (u.region or "").strip()
    if old == region:
        already_ok += 1
        print(f"[SKIP] {u.id} {u.username}: already {region!r}")
        continue

    u.region = region
    u.save(update_fields=["region"])
    updated += 1
    print(f"[OK] {u.id} {u.username}: {old!r} -> {region!r}")

for username, region in USERNAME_TO_REGION.items():
    try:
        u = User.objects.get(username__iexact=username)
    except User.DoesNotExist:
        print(f"[MISS] No user with username {username!r}")
        continue

    old = (u.region or "").strip()
    if old == region:
        print(f"[SKIP] {u.id} {u.username}: already {region!r}")
        continue

    u.region = region
    u.save(update_fields=["region"])
    updated += 1
    print(f"[OK] {u.id} {u.username}: {old!r} -> {region!r}")

print()
print(f"Updated users: {updated}")
print(f"Already correct: {already_ok}")
if missing:
    print("Emails with no matching User row:")
    for e in missing:
        print(" -", e)

print("\nDONE.")
