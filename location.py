import requests

def geocode_location(location_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": location_name, "count": 1, "language": "en", "format": "json"}
    
    response = requests.get(url, params=params)
    data = response.json()

    if "results" not in data or not data["results"]:
        return None  # location not found

    result = data["results"][0]
    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result["country"]
    }

# Prompt user for location input
user_input = input("Enter a location: ")
location = geocode_location(user_input)

if location:
    print(f"\nFound: {location['name']}, {location['country']}")
    print(f"Latitude: {location['latitude']}, Longitude: {location['longitude']}")
else:
    print("Location not found.")
