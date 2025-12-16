"""Scoring and recommendation logic for personalized weather preferences."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from weatherdata import MonthlyWeatherProfile


@dataclass
class WeatherPreferences:
    """User-defined comfort envelope with optional weights."""

    comfortable_temp_range: tuple[float, float]
    dew_point_range: tuple[float, float]
    max_precipitation_mm: float
    temperature_weight: float = 1.0
    dew_point_weight: float = 1.0
    precipitation_weight: float = 0.6


@dataclass
class MonthScore:
    """Computed score and rationale for a single month."""

    profile: MonthlyWeatherProfile
    score: float
    explanation: str

    @property
    def month_name(self) -> str:
        return self.profile.month_name


def _range_penalty(value: float, bounds: tuple[float, float]) -> float:
    """Distance from ``value`` to the provided ``bounds`` range."""

    lower, upper = bounds
    if value < lower:
        return lower - value
    if value > upper:
        return value - upper
    return 0.0


def _precipitation_penalty(total_precip_mm: float, threshold: float) -> float:
    """Penalty for precipitation using a soft threshold.

    Values below the threshold yield zero penalty. Above the threshold we scale
    the overage, but keep it relatively gentle to avoid dominating the score.
    """

    if total_precip_mm <= threshold:
        return 0.0
    # dampen the contribution so a few rainy days don't overshadow temperature
    return (total_precip_mm - threshold) / max(threshold, 1.0)


def score_month(profile: MonthlyWeatherProfile, preferences: WeatherPreferences) -> MonthScore:
    """Calculate a weighted discomfort score for a given month."""

    temp_penalty = _range_penalty(profile.average_temperature_c, preferences.comfortable_temp_range)
    dew_penalty = _range_penalty(profile.average_dew_point_c, preferences.dew_point_range)
    precip_penalty = _precipitation_penalty(profile.total_precipitation_mm, preferences.max_precipitation_mm)

    weighted_score = (
        temp_penalty * preferences.temperature_weight
        + dew_penalty * preferences.dew_point_weight
        + precip_penalty * preferences.precipitation_weight
    )

    explanation_parts = []
    if temp_penalty == 0:
        explanation_parts.append(
            f"temperatures stay within your comfort range ({profile.average_temperature_c:.1f}°C)"
        )
    else:
        explanation_parts.append(
            f"temperatures are {temp_penalty:.1f}°C outside your preferred range"
        )

    if dew_penalty == 0:
        explanation_parts.append(
            f"dew point aligns with your humidity tolerance ({profile.average_dew_point_c:.1f}°C)"
        )
    else:
        explanation_parts.append(
            f"dew point drifts {dew_penalty:.1f}°C from your ideal window"
        )

    if precip_penalty == 0:
        explanation_parts.append(
            f"precipitation is below your {preferences.max_precipitation_mm:.0f} mm allowance"
        )
    else:
        explanation_parts.append(
            (
                "precipitation exceeds your allowance by "
                f"{profile.total_precipitation_mm - preferences.max_precipitation_mm:.1f} mm"
            )
        )

    explanation = "; ".join(explanation_parts)
    return MonthScore(profile=profile, score=weighted_score, explanation=explanation)


def rank_months(profiles: List[MonthlyWeatherProfile], preferences: WeatherPreferences) -> List[MonthScore]:
    """Score and order month profiles by lowest discomfort (best first)."""

    scored = [score_month(profile, preferences) for profile in profiles]
    return sorted(scored, key=lambda month_score: month_score.score)
