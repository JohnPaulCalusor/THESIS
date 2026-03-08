"""
Structured, frontend-focused content source for Regional Chapters.

Keep edits simple:
- add/update officer entries under "officers"
- add/update posts under "posts"
- add/update videos under "videos"
"""

from __future__ import annotations


def _placeholder_region(region_name: str, description: str) -> dict:
    return {
        "region_name": region_name,
        "description": description,
        "officers": [
            {
                "name": "To be announced",
                "position": "Regional President",
                "organization": region_name,
                "image": "/media/papsas_app/images/default_dp.jpeg",
                "show_meta": True,
            },
            {
                "name": "To be announced",
                "position": "Vice President",
                "organization": region_name,
                "image": "/media/papsas_app/images/default_dp.jpeg",
                "show_meta": True,
            },
            {
                "name": "To be announced",
                "position": "Secretary",
                "organization": region_name,
                "image": "/media/papsas_app/images/default_dp.jpeg",
                "show_meta": True,
            }
        ],
        "posts": [
            {
                "title": "Featured Update Coming Soon",
                "body": (
                    "Regional officers, chapter updates, and media content will be "
                    "published here soon. You can manually replace this content any time."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
            {
                "title": "Regional News Item 1",
                "body": (
                    "Additional regional updates can be placed here. Replace this "
                    "placeholder with your first short news item."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
            {
                "title": "Regional News Item 2",
                "body": (
                    "Use this area for another short post, announcement, or event "
                    "highlight with an optional Facebook link."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
        ],
        "videos": [],
    }


REGIONAL_CHAPTERS = {
    "region-i": {
        "region_name": "PAPSAS Region I",
        "description": (
            "Region I chapter initiatives focused on student welfare, leadership "
            "development, and cross-institutional collaboration."
        ),
        "officers": [
            {
                "name": "Prof. Agustina A. Dancel-Matias",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Prof. Emil James P. Tanagon",
                "position": "Vice President for State Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Eugene M. Reyes",
                "position": "Vice President for Private Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Maria Deleilah F. Adriatico",
                "position": "Corporate Secretary",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Prof. Cynthia C. Medrano",
                "position": "Treasurer",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Joemar J. Cabradilla",
                "position": "Auditor",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mr. Aingel C. Palalay",
                "position": "Business Manager",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Cherrylyn S. Ramos",
                "position": "PRO",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ednalyn B. Alferos",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Philip G. Nonales",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Rhegina F. Tubera",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Robert Angel C. Mercurio",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Shalimar L. Navalta",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Neil Tristan N. Baga",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Joe Michael A. Esta",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "PAPSAS Region I Leaders Take Oath",
                "body": (
                    "PAPSAS Region I Executive Officers and Board of Directors held "
                    "their oath-taking ceremony on July 21, 2025 at CHEDRO I."
                ),
                "image": "/media/papsas_app/images/2reg1.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": "2025-07-21",
                "links": [],
            },
            {
                "title": "2025 Midyear Interactive Youth Forum",
                "body": (
                    "The chapter promoted NextGen Leadership for student leaders and "
                    "youth advocates through national collaboration and shared learning."
                ),
                "image": "/media/papsas_app/images/3reg1.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": "2025-09-17",
                "links": [],
            },
            {
                "title": "Region I Board Meeting Milestone",
                "body": (
                    "The first face-to-face regular board meeting strengthened chapter "
                    "governance and strategic direction for SAS programs."
                ),
                "image": "/media/papsas_app/images/5reg1.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": None,
                "links": [],
            },
        ],
        "videos": [
            {
                "title": "PAPSAS National Convention and Training 2023",
                "caption": (
                    "Regional chapter highlight reel and convention media coverage."
                ),
                "src": "https://drive.google.com/file/d/12d-yQ6J8DfdUQWyr5ilSAZqgjr3Ak6Fq/preview",
                "type": "embed",
            }
        ],
    },
    "region-ii": _placeholder_region(
        "PAPSAS Region II",
        "Regional chapter profile and updates for Cagayan Valley.",
    ),
    "region-iii": {
        "region_name": "PAPSAS Region III",
        "description": (
            "Region III chapter updates on conventions, leadership development, and "
            "SAS policy reorientation."
        ),
        "officers": [
            {
                "name": "Dr. Gloria B. Gigante",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Ma. Paz G. Contreras",
                "position": "Vice President for State Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Kathleen S. Angeles",
                "position": "Vice President for Private Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Monica R. Cabanding",
                "position": "Corporate Secretary",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Marissa B. Mendoza",
                "position": "Treasurer",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Jo-ann C. Balagtas",
                "position": "Auditor",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Lovelyn P. Ceralde",
                "position": "Business Manager",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Agnes Raquel B. Mendones",
                "position": "PRO",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Iris Ann G. Castro",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Leilani Capili",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Ms. Leanne Marie Diola-Reyes",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Mr. Christopher Sicat",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Ms. Lorena G. Zapanta",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Tina Presto Dabu",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Irene G. Bustos",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Dr. Gladie Natherine G. Cabanizas",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Mr. Von Gerald Macose",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "Region III Oath-Taking Ceremony",
                "body": (
                    "Newly elected officers and board members formally pledged service "
                    "and commitment to student affairs excellence in Central Luzon."
                ),
                "image": "/media/papsas_app/images/1reg3.png",
                "facebook_url": "https://www.facebook.com/PAPSAS.R3/",
                "date": "2025-06-26",
                "links": [],
            },
            {
                "title": "SAS Reorientation: Legal Bases and Provisions",
                "body": (
                    "Regional reorientation event on legal and policy foundations for "
                    "SAS implementation, with collaborative practitioner participation."
                ),
                "image": "/media/papsas_app/images/3reg3.png",
                "facebook_url": "https://www.facebook.com/PAPSAS.R3/",
                "date": "2025-03-20",
                "links": [
                    {
                        "label": "Registration Link",
                        "url": "https://bit.ly/RegSASReorientation",
                    },
                    {
                        "label": "Program and Guidelines",
                        "url": "https://bit.ly/SASreorientation2025",
                    },
                ],
            },
            {
                "title": "Annual Convention and Student Leader Summit",
                "body": (
                    "Regional convention highlights featuring collaboration between SAS "
                    "practitioners and student leaders."
                ),
                "image": "/media/papsas_app/images/4reg3.png",
                "facebook_url": "https://www.facebook.com/PAPSAS.R3/",
                "date": None,
                "links": [],
            },
        ],
        "videos": [
            {
                "title": "Region III Oath-Taking Ceremony Video",
                "caption": "Official chapter video coverage.",
                "src": "/media/papsas_app/videos/region3_first vid.mp4",
                "type": "local",
            }
        ],
    },
    "region-iv": {
        "region_name": "PAPSAS Region IV",
        "description": (
            "Region IV chapter initiatives on student welfare, legal awareness, "
            "and chapter-wide conference activities."
        ),
        "officers": [
            {
                "name": "Dr. Lucille D. Evangelista",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mr. Ryan N. Alemania",
                "position": "Vice President for State Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mr. Aljon M. Tolentino",
                "position": "Vice President for Private Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mrs. Milette L. De Torres",
                "position": "Corporate Secretary",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Mona Liza U. Avelino",
                "position": "Treasurer",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ana Mae D. Tividad",
                "position": "Auditor",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Billy Jay N. Pedron",
                "position": "Business Manager",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Raizza P. Corpuz",
                "position": "PRO",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Dr. Catherine M. Dungca",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "Russell V. Villarma",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "CHED Region IV Collaborative Conference",
                "body": (
                    "Collaborative conference focused on reviving and strengthening "
                    "student welfare and legal awareness in higher education."
                ),
                "image": "/media/papsas_app/images/1reg4.png",
                "facebook_url": "https://www.facebook.com/papsasregion4",
                "date": "2025-11-28",
                "links": [
                    {"label": "Program Link 1", "url": "https://bit.ly/48VrLE6"},
                    {"label": "Program Link 2", "url": "http://bit.ly/4nSfi8H"},
                ],
            },
            {
                "title": "29th National Conference Photo Highlights",
                "body": (
                    "Regional participation highlights from the national conference and "
                    "training workshop in Puerto Princesa City."
                ),
                "image": "/media/papsas_app/images/2reg4.png",
                "facebook_url": "https://www.facebook.com/papsasregion4",
                "date": "2025-04-10",
                "links": [],
            },
        ],
        "videos": [
            {
                "title": "Interactive Youth Forum Promotion",
                "caption": "Region IV chapter forum promotion and activity clips.",
                "src": "/media/papsas_app/videos/region4_1st vid.mp4",
                "type": "local",
            },
            {
                "title": "PAPSAS Research Conference Feature",
                "caption": "Conference invitation and highlights.",
                "src": "/media/papsas_app/videos/region4_2nd vid.mp4",
                "type": "local",
            },
        ],
    },
    "mimaropa": _placeholder_region(
        "PAPSAS MIMAROPA",
        "Regional chapter profile and updates for MIMAROPA.",
    ),
    "region-v": {
        "region_name": "PAPSAS Region V",
        "description": (
            "Region V chapter updates on student leadership, safety initiatives, and "
            "SAS capability-building activities in Bicol."
        ),
        "officers": [
            {
                "name": "RODOLFO 'SONNY' SB. VIRTUS JR.",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "RHODAVIV V. AVILA",
                "position": "Vice President for Public Higher Education Institutions",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "ADRIAN GIOVANNI C. GERONA",
                "position": "Vice President for Private Higher Education Institutions",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "JAY LEONIL S. CAMO",
                "position": "Secretary",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "DAKILA F. CAPISTRANO",
                "position": "Treasurer",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "GRACE B. ABELLA",
                "position": "Auditor",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "ERWIN B. OCAMPINA",
                "position": "Business Manager",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "DR. NORMAN P. MANLANGIT",
                "position": "PRO",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "ENGR. ANTONIO RICARDO T. AYEN",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "ANGELICA R. CADAG, RGC",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "MARCO B. DISCARGA",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "MARILOU B. EMPIG",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "DAISY SOTO JUDAVAR",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "JOEY A. MANTES",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "DR. BABY BOY BENJAMIN D. NEBRES III",
                "position": "Adviser",
                "group": "Advisers",
                "image": None,
            },
            {
                "name": "DR. MA. PAMELA SORRA-VIÑAS",
                "position": "Adviser",
                "group": "Advisers",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "Student Safety Summit Collaboration",
                "body": (
                    "PAPSAS Region V met city and barangay officials for student safety "
                    "and campus security planning in Naga City."
                ),
                "image": "/media/papsas_app/images/1reg5.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": None,
                "links": [],
            },
            {
                "title": "Bicol Young Leaders Summit",
                "body": (
                    "Regional student leaders gathered for leadership development and "
                    "collaborative training activities."
                ),
                "image": "/media/papsas_app/images/2reg5.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": None,
                "links": [],
            },
        ],
        "videos": [
            {
                "title": "Bicol Young Leaders Summit Highlights",
                "caption": "Region V chapter summit highlights and leadership sessions.",
                "src": "/media/papsas_app/videos/region5_1st vid.mp4",
                "type": "local",
            },
            {
                "title": "PAPSAS Region V In Focus",
                "caption": "Regional chapter initiatives and milestone accomplishments.",
                "src": "/media/papsas_app/videos/region5_2nd vid.mp4",
                "type": "local",
            },
        ],
    },
    "ncr": _placeholder_region(
        "PAPSAS NCR",
        "Regional chapter profile and updates for the National Capital Region.",
    ),
    "car": _placeholder_region(
        "PAPSAS CAR",
        "Regional chapter profile and updates for the Cordillera Administrative Region.",
    ),
    "region-vi": {
        "region_name": "PAPSAS Region VI",
        "description": (
            "Regional chapter profile and updates for Western Visayas."
        ),
        "officers": [
            {
                "name": "MR. SUNNY A. LASALA",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "DR. JOSE N. MAGBANUA",
                "position": "Vice President for Public Higher Education Institutions",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "REV. FR. RAUL N. TICAR, JR. MAEd",
                "position": "Vice President for Private Higher Education Institutions",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "MRS. JEZEL S. APOCERO, MAT",
                "position": "Secretary",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "DR. NEPTHALIE A. APIL",
                "position": "Treasurer",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "DR. MERLITO F. FLAGNE JR.",
                "position": "Auditor",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "DR. JIMMY F. DE JULIAN JR.",
                "position": "Business Manager",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "MS. SITTIE JUMANAH T. PAZAULAN, MAEd",
                "position": "PRO",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "MRS. MICHELLE G. RODRIGUEZ, RGC",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "MRS. JOHANNA FAITH M. CANDIDO, RGC",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "DR. MICHAEL A. BAÑAS",
                "position": "Board of Director",
                "group": "Board of Directors",
                "image": None,
            },
            {
                "name": "DR. BRANDON P. RIVERA",
                "position": "Adviser",
                "group": "Advisers",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "Featured Update Coming Soon",
                "body": (
                    "Regional officers, chapter updates, and media content will be "
                    "published here soon. You can manually replace this content any time."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
            {
                "title": "Regional News Item 1",
                "body": (
                    "Additional regional updates can be placed here. Replace this "
                    "placeholder with your first short news item."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
            {
                "title": "Regional News Item 2",
                "body": (
                    "Use this area for another short post, announcement, or event "
                    "highlight with an optional Facebook link."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
        ],
        "videos": [],
    },
    "region-vii": _placeholder_region(
        "PAPSAS Region VII",
        "Regional chapter profile and updates for Central Visayas.",
    ),
    "region-viii": {
        "region_name": "PAPSAS Region VIII",
        "description": (
            "Region VIII chapter activities on regional conferences, policy engagement, "
            "and student leadership development."
        ),
        "officers": [
            {
                "name": "Mr. Lowe S. Taña",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "3rd PAPSAS VIII Regional Conference Venue Announcement",
                "body": (
                    "Fan's Hotel in Palo, Leyte was announced as the official venue for "
                    "the regional conference activities."
                ),
                "image": "/media/papsas_app/images/1reg8.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": "2025-12-03",
                "links": [],
            },
            {
                "title": "PAPSAS Region VIII at National Conference",
                "body": (
                    "Region VIII officers and members joined the 29th national conference "
                    "to represent Eastern Visayas SAS initiatives."
                ),
                "image": "/media/papsas_app/images/2reg8.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": None,
                "links": [],
            },
        ],
        "videos": [],
    },
    "nir": _placeholder_region(
        "PAPSAS NIR",
        "Regional chapter profile and updates for the Negros Island Region.",
    ),
    "region-ix": _placeholder_region(
        "PAPSAS Region IX",
        "Regional chapter profile and updates for Zamboanga Peninsula.",
    ),
    "region-x": {
        "region_name": "PAPSAS Region X",
        "description": (
            "Regional chapter profile and updates for Northern Mindanao."
        ),
        "officers": [
            {
                "name": "Dr. Lorenzo B. Dinlayan, III",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "Featured Update Coming Soon",
                "body": (
                    "Regional officers, chapter updates, and media content will be "
                    "published here soon. You can manually replace this content any time."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
            {
                "title": "Regional News Item 1",
                "body": (
                    "Additional regional updates can be placed here. Replace this "
                    "placeholder with your first short news item."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
            {
                "title": "Regional News Item 2",
                "body": (
                    "Use this area for another short post, announcement, or event "
                    "highlight with an optional Facebook link."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
        ],
        "videos": [],
    },
    "region-xi": {
        "region_name": "PAPSAS Region XI",
        "description": (
            "Region XI chapter updates on governance, election outcomes, and "
            "professional development in student affairs."
        ),
        "officers": [
            {
                "name": "Ms. Theresa Salaver-Eliab, MS, CSASS",
                "position": "President",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Atty. Marlou Jade L. Eliab",
                "position": "Vice President for State Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mr. Amado S. Ancla, LPT",
                "position": "Vice President for Private Universities and Colleges",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mr. Klein Mamayabay, LPT, PhD",
                "position": "Corporate Secretary",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Anaflor E. Sacopayo, MBA, CSASS",
                "position": "Treasurer",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Wijawati H. Rainu, LPT, MAEM",
                "position": "Auditor",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Sheila T. Caguimbal, LPT, MAED (CAR)",
                "position": "Business Manager",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Mr. Darrel Jay R. Gato, LPT",
                "position": "PRO",
                "group": "Executive Officers",
                "image": None,
            },
            {
                "name": "Ms. Venus R. Bonsubre, LPT",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
            {
                "name": "Mr. Irvin N. Mirabueno, LPT, MAED",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
            {
                "name": "Ms. Estrella A. Soriano, CSASS, CHRA",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
            {
                "name": "Ms. Janice N. Sipin, MS, CSASS",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
            {
                "name": "Ms. Leah M. Cabang, LPT, ED.D",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
            {
                "name": "Mr. Raffy S. Belleza, CSASS, MAEM",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
            {
                "name": "Ms. Bonieve D. Marinez, MPSY, RPSY",
                "position": "Board Member",
                "group": "Board Members",
                "image": None,
            },
        ],
        "posts": [
            {
                "title": "Region XI Elects Board of Trustees and Executive Officers",
                "body": (
                    "PAPSAS Region XI formally elected its officers and trustees for "
                    "AY 2025-2026 during the chapter general assembly and conference."
                ),
                "image": "/media/papsas_app/images/1reg11.png",
                "facebook_url": "https://www.facebook.com/papsasinc",
                "date": "2025-09-26",
                "links": [],
            },
            {
                "title": "More Region XI Chapter Updates Coming Soon",
                "body": (
                    "You can add additional Region XI stories here, including events, "
                    "training highlights, and chapter announcements."
                ),
                "image": None,
                "facebook_url": None,
                "date": None,
                "links": [],
            },
        ],
        "videos": [],
    },
    "region-xii": _placeholder_region(
        "PAPSAS Region XII",
        "Regional chapter profile and updates for SOCCSKSARGEN.",
    ),
    "region-xiii": _placeholder_region(
        "PAPSAS Region XIII",
        "Regional chapter profile and updates for Caraga.",
    ),
    "barmm": _placeholder_region(
        "PAPSAS BARMM - Bangsamoro",
        "Regional chapter profile and updates for BARMM.",
    ),
}

# Shared source-of-truth for public Regional Chapters dropdowns
# (website navbar + dashboard region filter/forms).
#
# This list intentionally mirrors the desired public navigation order/labels.
PUBLIC_REGIONAL_PAGE_CHOICES = (
    ("car", "CAR"),
    ("ncr", "NCR"),
    ("region-i", "Region I"),
    ("region-ii", "Region II"),
    ("region-iii", "Region III"),
    ("region-iv", "Region IV"),
    ("region-v", "Region V"),
    ("region-vi", "Region VI"),
    ("region-vii", "Region VII"),
    ("region-viii", "Region VIII"),
    ("region-ix", "Region IX"),
    ("region-x", "Region X"),
    ("region-xi", "Region XI"),
    ("region-xii", "Region XII"),
    ("region-xiii", "Region XIII"),
    ("barmm", "BARMM"),
)
PUBLIC_REGIONAL_PAGE_SLUGS = tuple(slug for slug, _ in PUBLIC_REGIONAL_PAGE_CHOICES)
PUBLIC_REGIONAL_PAGE_LABELS = dict(PUBLIC_REGIONAL_PAGE_CHOICES)


def get_public_regional_page_choices():
    """Return immutable choices for regions that have public chapter pages."""
    return PUBLIC_REGIONAL_PAGE_CHOICES
