# Weather comfort advisor

This project ranks the best months to visit a city based on personal comfort
preferences. It ingests historical weather data, builds monthly profiles, and
scores them against your preferred temperature, humidity (dew point), and
precipitation tolerances.

## How it works
1. **Geocoding** – the city name is resolved via Open-Meteo's geocoding API.
2. **Historical data** – daily means (temperature, dew point, precipitation) for
a chosen year are fetched from Open-Meteo's archive API.
3. **Monthly profiles** – daily observations are aggregated into compact monthly
profiles.
4. **Scoring** – each month is scored with a weighted penalty model that
measures how far it deviates from your comfort ranges. Explanations describe
which factors helped or hurt each score.

## CLI usage
Run the CLI with a city name and optional preference overrides:

```bash
python main.py "Lisbon" \
  --temp-range 18 26 \
  --dew-range 8 16 \
  --max-precip-mm 90 \
  --top 3
```

Key flags:
- `--year`: historical year to analyze (default: 2023)
- `--temp-range`: comfortable mean temperature range in °C (default: 18–26)
- `--dew-range`: comfortable dew point range in °C (default: 8–16)
- `--max-precip-mm`: maximum monthly precipitation in mm before penalties apply
  (default: 90)
- `--weight-temp`, `--weight-dew`, `--weight-precip`: adjust feature weights

The CLI prints the top ranked months along with explanations so you can see
which weather factors matched your preferences.
