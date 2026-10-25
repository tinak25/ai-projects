"""Map of Forest Hill / Nunawading / Blackburn (Melbourne) for wheelchair route planning.

Places are real locations with (latitude, longitude) coordinates taken from Google Maps.
Segment lengths are walking-distance estimates in km. A path can't be shorter than the
straight-line distance between its ends, so build_segments() corrects estimates that are:
- slightly too short (within 10%, i.e. rounding): raised to the straight-line distance, rounded up
- clearly too short: set to the straight-line distance x 1.25 (a typical urban detour factor)
"""
import math

# (latitude, longitude)
LOCATIONS = {
    "Forest Hill Chase": (-37.8355717, 145.1636965),
    "Hungry Jacks": (-37.8339776, 145.1633093),
    "Nunawading Station": (-37.8204299, 145.1751824),
    "Steep Ramp": (-37.83471, 145.17561),
    "Canterbury Hotel": (-37.83532, 145.17196),
    "Mr Robertson Cafe": (-37.8228114, 145.181359),
    "FF Collectibles": (-37.8247951, 145.1800189),
    "Aqualink": (-37.8376418, 145.1757424),
    "Japanese Cafe": (-37.8323082, 145.1870974),
    "Bob Saker": (-37.8423904, 145.1632211),
    "Blackburn Primary School": (-37.8270502, 145.1654828),
    "SGNSS Gurdwara": (-37.8159143, 145.1528508),
    "Narrow Pathway": (-37.81461, 145.15902),
    "Deals Collective": (-37.81117, 145.15718),
    "Cake Decorating": (-37.8106995, 145.1777068),
    "Blackburn Station": (-37.8201591, 145.1499322),
    "Korean Restaurant": (-37.8322486, 145.1486358),
    "Miss Lucy": (-37.8242034, 145.1663208),
    "Woolworths": (-37.8363544, 145.1852152),
    "Ichikuro": (-37.8192132, 145.1526676),
    "Regis Blackburn": (-37.8243645, 145.1593761),
}

# (place A, place B, estimated walking distance in km, terrain)
# terrain: "normal", "steep" (steep ramp) or "narrow" (narrow footpath)
RAW_SEGMENTS = [
    ("Cake Decorating", "Mr Robertson Cafe", 1.4, "normal"),
    ("Narrow Pathway", "SGNSS Gurdwara", 0.55, "narrow"),
    ("Narrow Pathway", "Cake Decorating", 1.7, "narrow"),
    ("Deals Collective", "SGNSS Gurdwara", 0.7, "normal"),
    ("Deals Collective", "Cake Decorating", 1.8, "normal"),
    ("Mr Robertson Cafe", "Miss Lucy", 1.3, "normal"),
    ("Mr Robertson Cafe", "Nunawading Station", 0.3, "normal"),
    ("Miss Lucy", "Korean Restaurant", 1.7, "normal"),
    ("Korean Restaurant", "Regis Blackburn", 1.3, "normal"),
    ("Korean Restaurant", "Forest Hill Chase", 1.4, "normal"),
    ("Korean Restaurant", "Blackburn Station", 1.2, "normal"),
    ("Regis Blackburn", "Nunawading Station", 1.5, "normal"),
    ("Forest Hill Chase", "Bob Saker", 0.8, "normal"),
    ("Hungry Jacks", "Korean Restaurant", 0.3, "normal"),
    ("Hungry Jacks", "Blackburn Primary School", 0.9, "normal"),
    ("Bob Saker", "Aqualink", 0.7, "normal"),
    ("Blackburn Primary School", "SGNSS Gurdwara", 1.3, "normal"),
    ("SGNSS Gurdwara", "Ichikuro", 0.5, "normal"),
    ("SGNSS Gurdwara", "Blackburn Station", 0.4, "normal"),
    ("Ichikuro", "Regis Blackburn", 0.3, "normal"),
    ("Nunawading Station", "Ichikuro", 1.5, "normal"),
    ("Steep Ramp", "Aqualink", 0.32, "steep"),
    ("Steep Ramp", "Nunawading Station", 1.6, "steep"),
    ("Canterbury Hotel", "Aqualink", 0.5, "normal"),
    ("Canterbury Hotel", "Nunawading Station", 1.6, "normal"),
    ("FF Collectibles", "Nunawading Station", 0.3, "normal"),
    ("FF Collectibles", "Japanese Cafe", 1.2, "normal"),
    ("Japanese Cafe", "Woolworths", 0.5, "normal"),
    ("Japanese Cafe", "Aqualink", 1.3, "normal"),
    ("Woolworths", "Aqualink", 1.0, "normal"),
]

DETOUR_FACTOR = 1.25


def haversine_km(a, b):
    """Great-circle distance in km between two (latitude, longitude) points."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def build_segments():
    """Return segments with corrected lengths: (a, b, length_km, terrain, was_corrected)."""
    out = []
    for a, b, est, terrain in RAW_SEGMENTS:
        straight = haversine_km(LOCATIONS[a], LOCATIONS[b])
        if est >= straight:
            out.append((a, b, est, terrain, False))
        elif est >= 0.90 * straight:
            out.append((a, b, math.ceil(straight * 100) / 100, terrain, True))
        else:
            out.append((a, b, math.ceil(straight * DETOUR_FACTOR * 100) / 100, terrain, True))
    return out
