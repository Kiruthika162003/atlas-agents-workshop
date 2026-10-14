# Agent 2 of 7: the same agent with three Python functions as tools.
# Now it knows where you are and what is really around you.
# Run: adk web learn   then pick agent_2_tools

import math
import os
from typing import Literal

import requests
from dotenv import load_dotenv
from google.adk.agents import Agent

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"))

# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OpenStreetMap's search service. Free, worldwide, no key. It asks for a
# User-Agent and at most one request a second.
NOMINATIM = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "atlas-workshop/1.0", "Accept-Language": "en"}
# The OpenStreetMap community routing server, walking profile.
ROUTER = "https://routing.openstreetmap.de/routed-foot/route/v1/foot/"

# Each kind of spot, and the subtopics inside it. A subtopic is the phrase
# Nominatim searches for and the OpenStreetMap type it should come back with.
KINDS = {
    "food": {"restaurants": ("restaurant", "restaurant"), "cafes": ("cafe", "cafe"), "bakeries": ("bakery", "bakery")},
    "coffee": {"cafes": ("cafe", "cafe")},
    "fun": {"museums": ("museum", "museum"), "attractions": ("attraction", "attraction"),
            "theatres": ("theatre", "theatre"), "cinemas": ("cinema", "cinema")},
    "shopping": {"markets": ("marketplace", "marketplace"), "bookshops": ("book shop", "books"),
                 "malls": ("mall", "mall"), "gift shops": ("gift shop", "gift")},
    "outdoors": {"parks": ("park", "park"), "gardens": ("garden", "garden"),
                 "viewpoints": ("viewpoint", "viewpoint"), "beaches": ("beach", "beach")},
    "schools": {"schools": ("school", "school"), "universities": ("university", "university"),
                "libraries": ("library", "library")},
    "essentials": {"pharmacies": ("pharmacy", "pharmacy"), "cash machines": ("atm", "atm"),
                   "toilets": ("toilet", "toilets"), "stations": ("railway station", "station")},
}
Kind = Literal["food", "coffee", "fun", "shopping", "outdoors", "schools", "essentials"]


def geocode(place: str) -> dict:
    """Turn a place name or address into coordinates.

    Args:
        place: a name and its city, e.g. "Grand Central Market, Los Angeles".
    """
    # Nominatim finds "name, city" but not "name in city".
    hits = _search(q=place.replace(" in ", ", "), limit=1)
    if not hits:
        return {"found": False, "hint": "No match. Ask for the city or a nearby landmark."}
    hit = hits[0]
    return {
        "found": True,
        "name": place.split(",")[0].strip(),
        "address": hit["display_name"],
        "lat": round(float(hit["lat"]), 5),
        "lon": round(float(hit["lon"]), 5),
    }


def nearby_places(
    lat: float, lon: float, kind: Kind, only: str = "", cuisine: str = "", radius_m: int = 600,
) -> dict:
    """List places of one kind around a point, nearest first.

    Args:
        lat: latitude of the person.
        lon: longitude of the person.
        kind: food, coffee, fun, shopping, outdoors, schools, or essentials (pharmacies, cash machines, toilets, stations).
        only: one subtopic of that kind, e.g. "museums" within fun or "bookshops" within shopping. Empty means all of them.
        cuisine: for food only, keep places whose listing mentions it, e.g. "italian". Empty means any.
        radius_m: how far to look, in metres. Widen it when a search comes back with too few.
    """
    radius_m = min(radius_m, 2000)
    subtopics = KINDS[kind]
    if only and only.lower() not in subtopics:
        return {"kind": kind, "count": 0, "places": [], "hint": f"No subtopic '{only}'. Choose from: {', '.join(subtopics)}."}

    found = {}
    for subtopic, (phrase, osm_type) in subtopics.items():
        if only and subtopic != only.lower():
            continue
        hits = _search(q=phrase, viewbox=_box(lat, lon, radius_m), bounded=1, limit=40, extratags=1, addressdetails=1)
        for hit in hits:
            # A toilet or a cash machine rarely has a name, so essentials go by what they are.
            name = hit.get("name") or (subtopic.capitalize() if kind == "essentials" else "")
            if not name or hit["type"] != osm_type:
                continue
            place = {
                "name": name,
                "type": hit["type"],
                "subtopic": subtopic,
                "lat": round(float(hit["lat"]), 5),
                "lon": round(float(hit["lon"]), 5),
                "distance_m": _metres(lat, lon, float(hit["lat"]), float(hit["lon"])),
            }
            # Whatever the map knows beyond the name. Many places have none of these.
            tags = hit.get("extratags") or {}
            street = hit.get("address") or {}
            details = {
                "cuisine": tags.get("cuisine"),
                "address": " ".join(filter(None, [street.get("house_number"), street.get("road")])),
                "website": tags.get("website") or tags.get("contact:website"),
                "phone": tags.get("phone") or tags.get("contact:phone"),
                "opening_hours": tags.get("opening_hours"),
            }
            place.update({key: value for key, value in details.items() if value})
            found[hit["osm_id"]] = place

    places = sorted(found.values(), key=lambda p: p["distance_m"])
    if cuisine:
        places = [p for p in places if cuisine.lower() in p.get("cuisine", "").lower()]
    return {"kind": kind, "subtopics": list(subtopics), "radius_m": radius_m, "count": len(places), "places": places[:15]}


def walking_route(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> dict:
    """The walking route from one point to another: how far, how long, and its shape.

    Args:
        from_lat: latitude of the person.
        from_lon: longitude of the person.
        to_lat: latitude of the place, as nearby_places gave it.
        to_lon: longitude of the place, as nearby_places gave it.
    """
    reply = requests.get(
        f"{ROUTER}{from_lon},{from_lat};{to_lon},{to_lat}",
        params={"overview": "full", "geometries": "polyline"}, headers=HEADERS, timeout=10,
    )
    routes = reply.json().get("routes") if reply.ok else None
    if not routes:
        raise RuntimeError("No walking route found between these two points.")
    best = routes[0]
    return {
        "distance_m": round(best["distance"]),
        "minutes": max(1, round(best["duration"] / 60)),
        "line": best["geometry"],    # the route's shape, packed into a string the map can draw
    }


def _search(**params) -> list:
    """One request to Nominatim. A refusal becomes an error the agent can read."""
    reply = requests.get(NOMINATIM, params={"format": "jsonv2", **params}, headers=HEADERS, timeout=10)
    if not reply.ok:
        raise RuntimeError(f"The map service refused the request (HTTP {reply.status_code}).")
    return reply.json()


def _box(lat: float, lon: float, radius_m: int) -> str:
    """The square around a point, as Nominatim wants it: left,top,right,bottom."""
    dlat = radius_m / 111_320
    dlon = dlat / math.cos(math.radians(lat))
    return f"{lon - dlon},{lat + dlat},{lon + dlon},{lat - dlat}"


def _metres(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    y = math.radians(lat2 - lat1)
    return round(6371000 * math.hypot(x, y))


root_agent = Agent(
    name="agent_2_tools",
    model=os.getenv("ATLAS_MODEL", "gemini-3.8-flash"),
    description="A local guide that looks at the real map.",
    instruction=(
        "You are Atlas, a local guide. People tell you where they are and "
        "what they are after: food, coffee, fun, shopping, outdoors, schools "
        "or essentials.\n"
        "Call geocode to find them, then nearby_places for what they want. "
        "Recommend the three most interesting results with their distance, "
        "in under 80 words. Only name places the tools returned, and say "
        "nothing about them that the tools did not."
    ),
    tools=[geocode, nearby_places, walking_route],
)
