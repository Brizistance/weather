"""Location utilities for geocoding city names.

This module is intentionally small so that the rest of the application can
focus on weather analysis. The `geocode_location` helper looks up a city using
Open-Meteo's free API and returns a structured dictionary that downstream code
can consume.
"""

from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class GeocodedLocation:
    """Structured representation of a geocoded place."""

    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None


def geocode_location(location_name: str) -> Optional[GeocodedLocation]:
    """Look up a location name using Open-Meteo's geocoding API.

    Args:
        location_name: Free-form string describing a city or place name.

    Returns:
        A :class:`GeocodedLocation` if the API finds a match, otherwise ``None``.
    """

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location_name, "count": 1, "language": "en", "format": "json"}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    result = data["results"][0]
    return GeocodedLocation(
        name=result["name"],
        latitude=result["latitude"],
        longitude=result["longitude"],
        country=result.get("country"),
    )
