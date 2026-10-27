"""Canonical administrative division registry for India (28 States + 8 Union Territories).
Maintained with official ISO 3166-2:IN codes and stable SEO slugs.
Never derived from unverified free text or LLM inference.
"""

CANONICAL_INDIAN_STATES = [
    {"code": "IN-AP", "name": "Andhra Pradesh", "slug": "andhra-pradesh", "type": "state"},
    {"code": "IN-AR", "name": "Arunachal Pradesh", "slug": "arunachal-pradesh", "type": "state"},
    {"code": "IN-AS", "name": "Assam", "slug": "assam", "type": "state"},
    {"code": "IN-BR", "name": "Bihar", "slug": "bihar", "type": "state"},
    {"code": "IN-CG", "name": "Chhattisgarh", "slug": "chhattisgarh", "type": "state"},
    {"code": "IN-GA", "name": "Goa", "slug": "goa", "type": "state"},
    {"code": "IN-GJ", "name": "Gujarat", "slug": "gujarat", "type": "state"},
    {"code": "IN-HR", "name": "Haryana", "slug": "haryana", "type": "state"},
    {"code": "IN-HP", "name": "Himachal Pradesh", "slug": "himachal-pradesh", "type": "state"},
    {"code": "IN-JH", "name": "Jharkhand", "slug": "jharkhand", "type": "state"},
    {"code": "IN-KA", "name": "Karnataka", "slug": "karnataka", "type": "state"},
    {"code": "IN-KL", "name": "Kerala", "slug": "kerala", "type": "state"},
    {"code": "IN-MP", "name": "Madhya Pradesh", "slug": "madhya-pradesh", "type": "state"},
    {"code": "IN-MH", "name": "Maharashtra", "slug": "maharashtra", "type": "state"},
    {"code": "IN-MN", "name": "Manipur", "slug": "manipur", "type": "state"},
    {"code": "IN-ML", "name": "Meghalaya", "slug": "meghalaya", "type": "state"},
    {"code": "IN-MZ", "name": "Mizoram", "slug": "mizoram", "type": "state"},
    {"code": "IN-NL", "name": "Nagaland", "slug": "nagaland", "type": "state"},
    {"code": "IN-OD", "name": "Odisha", "slug": "odisha", "type": "state"},
    {"code": "IN-PB", "name": "Punjab", "slug": "punjab", "type": "state"},
    {"code": "IN-RJ", "name": "Rajasthan", "slug": "rajasthan", "type": "state"},
    {"code": "IN-SK", "name": "Sikkim", "slug": "sikkim", "type": "state"},
    {"code": "IN-TN", "name": "Tamil Nadu", "slug": "tamil-nadu", "type": "state"},
    {"code": "IN-TG", "name": "Telangana", "slug": "telangana", "type": "state"},
    {"code": "IN-TR", "name": "Tripura", "slug": "tripura", "type": "state"},
    {"code": "IN-UP", "name": "Uttar Pradesh", "slug": "uttar-pradesh", "type": "state"},
    {"code": "IN-UK", "name": "Uttarakhand", "slug": "uttarakhand", "type": "state"},
    {"code": "IN-WB", "name": "West Bengal", "slug": "west-bengal", "type": "state"},
]

CANONICAL_INDIAN_UTS = [
    {"code": "IN-AN", "name": "Andaman and Nicobar Islands", "slug": "andaman-and-nicobar-islands", "type": "union_territory"},
    {"code": "IN-CH", "name": "Chandigarh", "slug": "chandigarh", "type": "union_territory"},
    {"code": "IN-DH", "name": "Dadra and Nagar Haveli and Daman and Diu", "slug": "dadra-and-nagar-haveli-and-daman-and-diu", "type": "union_territory"},
    {"code": "IN-DL", "name": "Delhi", "slug": "delhi", "type": "union_territory"},
    {"code": "IN-JK", "name": "Jammu and Kashmir", "slug": "jammu-and-kashmir", "type": "union_territory"},
    {"code": "IN-LA", "name": "Ladakh", "slug": "ladakh", "type": "union_territory"},
    {"code": "IN-LD", "name": "Lakshadweep", "slug": "lakshadweep", "type": "union_territory"},
    {"code": "IN-PY", "name": "Puducherry", "slug": "puducherry", "type": "union_territory"},
]

ALL_CANONICAL_INDIAN_REGIONS = CANONICAL_INDIAN_STATES + CANONICAL_INDIAN_UTS
