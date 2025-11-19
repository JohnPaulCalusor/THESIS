from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

# These are the "full_name" values from the 56 unknown-region CSV rows
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
    # same names appear twice in CSV, but we list them once
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

qs = User.objects.filter(
    Q(region__isnull=True) | Q(region__exact="")
).filter(username__in=NAME_USERNAMES).order_by("id")

print("Total candidate duplicate users (blank region + name-username):", qs.count())
print()

for u in qs:
    print(f"{u.id:4} | username={u.username!r} | email={u.email!r} | region={u.region!r}")
