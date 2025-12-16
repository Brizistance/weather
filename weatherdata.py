"""Weather data retrieval and aggregation helpers.

This module fetches daily observations for a given latitude/longitude pair and
converts them into compact monthly profiles that can be scored against user
preferences.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import calendar

import requests


@dataclass
class MonthlyWeatherProfile:
    """Aggregated weather signal for a calendar month."""

    month: int
    average_temperature_c: float
    average_dew_point_c: float
    total_precipitation_mm: float
    observation_days: int

    @property
    def month_name(self) -> str:
        return calendar.month_name[self.month]


def get_weather_for_year(latitude: float, longitude: float, year: str = "2023") -> Dict:
    """Fetch daily mean weather for a full year from the Open-Meteo archive API."""

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "daily": ["temperature_2m_mean", "dew_point_2m_mean", "precipitation_sum"],
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def to_monthly_profiles(weather_data: Dict) -> List[MonthlyWeatherProfile]:
    """Aggregate daily weather payload into monthly profiles.

    Args:
        weather_data: JSON response from :func:`get_weather_for_year`.

    Returns:
        List of :class:`MonthlyWeatherProfile` sorted by month.
    """

    daily = weather_data.get("daily") or {}
    dates = daily.get("time", [])
    temps = daily.get("temperature_2m_mean", [])
    dew_points = daily.get("dew_point_2m_mean", [])
    precipitation = daily.get("precipitation_sum", [])

    monthly_scores: Dict[int, Dict[str, float]] = {
        m: {"temp_sum": 0.0, "dew_sum": 0.0, "precip_sum": 0.0, "count": 0} for m in range(1, 13)
    }

    for i, date in enumerate(dates):
        month = int(date.split("-")[1])
        monthly_scores[month]["temp_sum"] += temps[i]
        monthly_scores[month]["dew_sum"] += dew_points[i]
        monthly_scores[month]["precip_sum"] += precipitation[i]
        monthly_scores[month]["count"] += 1

    profiles: List[MonthlyWeatherProfile] = []
    for month, values in monthly_scores.items():
        if not values["count"]:
            # Skip months with no data
            continue

        profiles.append(
            MonthlyWeatherProfile(
                month=month,
                average_temperature_c=values["temp_sum"] / values["count"],
                average_dew_point_c=values["dew_sum"] / values["count"],
                total_precipitation_mm=values["precip_sum"],
                observation_days=values["count"],
            )
        )

    profiles.sort(key=lambda profile: profile.month)
    return profiles
