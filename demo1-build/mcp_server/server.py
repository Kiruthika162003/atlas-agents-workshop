"""Atlas places server. Three map tools that any MCP client can call.

Run open, for anyone who can reach it:
    python mcp_server/server.py

Run locked, for the Google accounts you name:
    python mcp_server/server.py --allow you@gmail.com

Serves http://localhost:8001/mcp
"""

import argparse
import math
import os
from typing import Literal

import requests
from google.auth.transport import requests as google_transport
from google.oauth2 import id_token
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver import MCPServer

# Who may call the tools. Empty means the door is open. On Cloud Run the list
# comes from the environment, since there is no command line to type on.
options = argparse.ArgumentParser()
options.add_argument("--allow", default=os.getenv("ATLAS_ALLOWED_EMAILS", ""), help="comma separated Google accounts")
ALLOWED = {email.strip() for email in options.parse_known_args()[0].allow.split(",") if email.strip()}

PORT = int(os.getenv("PORT", 8001))    # Cloud Run chooses the port
URL = os.getenv("ATLAS_MCP_URL", f"http://localhost:{PORT}/mcp")


class GoogleSignIn:
    """Lets a caller in only if Google vouches for them and they are on the list."""

    async def verify_token(self, token: str) -> AccessToken | None:
        try:
            # Checks Google's signature and the expiry. A made-up or old token fails here.
            who = id_token.verify_oauth2_token(token, google_transport.Request())
        except ValueError:
            return None
        if who.get("email") not in ALLOWED:
            return None    # a real Google account, but not one we invited
        return AccessToken(token=token, client_id=who["email"], scopes=[], expires_at=who["exp"])


if ALLOWED:
    # MCP auth is OAuth: this server is the "resource server". It does not
    # hand out tokens itself, it only checks the ones Google issued.
    mcp = MCPServer(
        "atlas-places",
        token_verifier=GoogleSignIn(),
        auth=AuthSettings(issuer_url="https://accounts.google.com", resource_server_url=URL, validate_token_resource=False),
    )
else:
    mcp = MCPServer("atlas-places")

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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


if __name__ == "__main__":
    # On Cloud Run the server has to listen on every address, not just localhost.
    host = "0.0.0.0" if "PORT" in os.environ else "localhost"
    if ALLOWED:
        print("Locked. Only these accounts may call the tools:", ", ".join(sorted(ALLOWED)))
    else:
        print("Open. Anyone who can reach this address may call the tools.")
    mcp.run("streamable-http", host=host, port=PORT)
