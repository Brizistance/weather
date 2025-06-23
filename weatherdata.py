import requests
from location import geocode_location
from collections import defaultdict
import calendar

def get_weather_for_year(latitude, longitude, year="2023"):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "daily": ["temperature_2m_mean", "dew_point_2m_mean", "precipitation_sum"],
        "timezone": "auto"
    }

    response = requests.get(url, params=params)
    return response.json()

def analyze_ideal_month(weather_data):
    scores = defaultdict(lambda: {"temp_sum": 0, "dew_sum": 0, "rain_sum": 0, "count": 0})
    dates = weather_data["daily"]["time"]

    for i, date in enumerate(dates):
        month = int(date.split("-")[1])
        scores[month]["temp_sum"] += weather_data["daily"]["temperature_2m_mean"][i]
        scores[month]["dew_sum"] += weather_data["daily"]["dew_point_2m_mean"][i]
        scores[month]["rain_sum"] += weather_data["daily"]["precipitation_sum"][i]
        scores[month]["count"] += 1

    best_month = None
    best_score = float('inf')

    for month, values in scores.items():
        avg_temp = values["temp_sum"] / values["count"]
        avg_dew = values["dew_sum"] / values["count"]
        avg_rain = values["rain_sum"] / values["count"]

        # Score: deviation from ideal temp (21°C), plus dew + rain
        score = abs(avg_temp - 21) + avg_dew + avg_rain

        if score < best_score:
            best_score = score
            best_month = month

    return calendar.month_name[best_month]

if __name__ == "__main__":
    user_input = input("Enter a location: ")
    location = geocode_location(user_input)
    if location:
        weather_data = get_weather_for_year(location["latitude"], location["longitude"])
        ideal_month = analyze_ideal_month(weather_data)
        print(f"Ideal month to visit {location['name']}, {location['country']}: {ideal_month}")
    else:
        print("Location not found.")