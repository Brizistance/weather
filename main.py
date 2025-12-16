"""CLI entry point for personalized weather-friendly month recommendations."""

from __future__ import annotations

import argparse
from typing import Sequence

from decision_engine import WeatherPreferences, rank_months
from location import geocode_location
from weatherdata import get_weather_for_year, to_monthly_profiles


def _parse_range(values: Sequence[float], label: str) -> tuple[float, float]:
    if len(values) != 2:
        raise ValueError(f"{label} must have exactly two values (min max)")
    lower, upper = values
    if lower > upper:
        raise ValueError(f"{label} lower bound must be less than upper bound")
    return float(lower), float(upper)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rank calendar months for a city based on your comfort preferences",
    )
    parser.add_argument("location", help="City to analyze (e.g. 'Lisbon' or 'Austin, TX')")
    parser.add_argument(
        "--year",
        default="2023",
        help="Year of historical data to analyze (default: 2023)",
    )
    parser.add_argument(
        "--temp-range",
        type=float,
        nargs=2,
        metavar=("MIN", "MAX"),
        default=(18.0, 26.0),
        help="Comfortable daily mean temperature range in °C (default: 18 26)",
    )
    parser.add_argument(
        "--dew-range",
        type=float,
        nargs=2,
        metavar=("MIN", "MAX"),
        default=(8.0, 16.0),
        help="Comfortable dew point range in °C (default: 8 16)",
    )
    parser.add_argument(
        "--max-precip-mm",
        type=float,
        default=90.0,
        help="Maximum total monthly precipitation in millimeters (default: 90)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Number of top-ranked months to display (default: 3)",
    )
    parser.add_argument(
        "--weight-temp",
        type=float,
        default=1.0,
        help="Weight for temperature discomfort (default: 1.0)",
    )
    parser.add_argument(
        "--weight-dew",
        type=float,
        default=1.0,
        help="Weight for dew point discomfort (default: 1.0)",
    )
    parser.add_argument(
        "--weight-precip",
        type=float,
        default=0.6,
        help="Weight for precipitation discomfort (default: 0.6)",
    )
    return parser


def main(args: Sequence[str] | None = None) -> int:
    parser = build_parser()
    parsed = parser.parse_args(args=args)

    preferences = WeatherPreferences(
        comfortable_temp_range=_parse_range(parsed.temp_range, "--temp-range"),
        dew_point_range=_parse_range(parsed.dew_range, "--dew-range"),
        max_precipitation_mm=parsed.max_precip_mm,
        temperature_weight=parsed.weight_temp,
        dew_point_weight=parsed.weight_dew,
        precipitation_weight=parsed.weight_precip,
    )

    location = geocode_location(parsed.location)
    if not location:
        parser.error("Location not found. Please try a broader city name.")

    print(f"\nAnalyzing {location.name}, {location.country or ''} using {parsed.year} historical data")
    print(
        "Your comfort profile: temp %s–%s°C, dew point %s–%s°C, max %.0f mm monthly precip"
        % (
            preferences.comfortable_temp_range[0],
            preferences.comfortable_temp_range[1],
            preferences.dew_point_range[0],
            preferences.dew_point_range[1],
            preferences.max_precipitation_mm,
        )
    )

    weather_data = get_weather_for_year(location.latitude, location.longitude, parsed.year)
    profiles = to_monthly_profiles(weather_data)
    if not profiles:
        parser.error("No weather data returned for that location/year.")

    ranked = rank_months(profiles, preferences)
    print("\nTop months (lower score means closer to your preferences):")
    for month_score in ranked[: parsed.top]:
        print(
            f"- {month_score.month_name}: score {month_score.score:.2f}; {month_score.explanation}.",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
