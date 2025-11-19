from django.contrib.auth import get_user_model
from django.db import models, transaction

User = get_user_model()

# Same full-name usernames we used earlier
NAME_USERNAMES = [
    "franklin b. macarayo",
    "nova c. baldo",
    "catherine nicca c. laconsay",
    "rhoda m. malabanan",
    "emily concepcion c. miguel",
    "michael g. millanes",
    "annie g molejon",
    "eugene m. reyes",
    "ednalyn b. alferos",
    "britney gem d. dona",
    "angel l. genato, iv",
    "jacqueline v. iglesias",
    "jesusa c. pasia",
    "marijin p. rueca",
    "mary grace a. desembrana",
    "melody g. agudilla",
    "dexter paul d. dioso",
    "marijoy o. gaduyon",
    "rene iii b. alcala",
    "argielyn a. esmane",
    "marlon j. calceña jr.",
    "michelle g. rodriguez",
    "jose n. magbanua",
    "sheila s. alba",
    "lerry basamot",
    "abe p. cadelina",
    "anna liza apos-ocaya",
    "danilo y. patalinghug",
    "april grace c. cose",
    "reynerio c. abayon, jr.",
    "contessa t. castro",
    "joseph e. padilla",
    "rhodora a. bande",
    "mikaela m. gongora",
    "christina a. gabrillo",
    "rey g. comabig",
    "karen l. molina",
    "minerva b. baclayon",
    "gretta d. guiroy",
    "maria emelee a. bascug",
    "jay a. roslinda",
    "john david o moncada",
    "lory t. alcazar",
    "zulieka cejay b. almonares",
    "pontini albe coloscos",
    "kathryn rose s. bayon",
    "mariejune a. rivera",
    "karlo b. buenavidez",
    "armela g. mendoza",
    "jemaima i. marohom",
    "janice n. sipin",
    "darrel jay r. gato",
    "karla mae f. ramajo",
    "revelyn g. enderes",
]

region_field = User._meta.get_field("region")

# All valid region values from choices, EXCEPT placeholder "Region"
all_region_values = [value for value, _ in region_field.choices if value]
region_choices = [r for r in all_region_values if r.lower() != "region"]

print("Region choices to distribute across:", region_choices)
print("Number of region choices:", len(region_choices))

qs = User.objects.filter(
    models.Q(region__isnull=True) | models.Q(region__exact="")
).filter(username__in=NAME_USERNAMES).order_by("id")

users = list(qs)
print("\nUsers to assign regions to:", len(users))
for u in users:
    print(f"  {u.id} {u.username!r} (current region={u.region!r})")

if not users:
    print("\nNo users to update, exiting.")
else:
    if not region_choices:
        print("\nNo valid region choices found, exiting.")
    else:
        print("\nAssigning regions in round-robin...")
        region_counts = {r: 0 for r in region_choices}

        with transaction.atomic():
            for idx, u in enumerate(users):
                new_region = region_choices[idx % len(region_choices)]
                region_counts[new_region] += 1
                old_region = u.region
                u.region = new_region
                u.save(update_fields=["region"])
                print(f"  [OK] User {u.id} {u.username!r}: {old_region!r} -> {new_region!r}")

        print("\nSummary of assignments:")
        for r, count in region_counts.items():
            if count:
                print(f"  {r}: {count} users")

print("\nDONE.")
