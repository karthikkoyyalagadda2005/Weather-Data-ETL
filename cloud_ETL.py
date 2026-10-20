import os
import json
import sqlite3
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
# Real AI library kosam: pip install google-genai
from google import genai 
load_dotenv()
print(">>> Step 1: Ingesting Live Data from API into Data Lake Staging...")
cities = {
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777}
}

raw_records = []
for city, coords in cities.items():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        raw_records.append({
            "city": city,
            "latitude": coords['lat'],
            "longitude": coords['lon'],
            "weather": data.get("current_weather", {})
        })

os.makedirs("datalake_raw", exist_ok=True)
timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
staging_file = f"datalake_raw/weather_raw_{timestamp_str}.json"
with open(staging_file, "w") as f:
    json.dump(raw_records, f, indent=4)
print(f"Data successfully dumped to raw lake: {staging_file}")

print("\n>>> Step 2: Processing, Cleansing & Dimensional Modeling (ETL)...")
flat_data = []
for item in raw_records:
    w = item["weather"]
    flat_data.append({
        "city_name": item["city"],
        "latitude": item["latitude"],
        "longitude": item["longitude"],
        "temperature": w.get("temperature"),
        "windspeed": w.get("windspeed"),
        "winddirection": w.get("winddirection"),
        "weathercode": w.get("weathercode"),
        "time": w.get("time")
    })

df = pd.DataFrame(flat_data)
df = df.dropna().copy()
df['time'] = pd.to_datetime(df['time'])

# Dim_City
dim_city = df[['city_name', 'latitude', 'longitude']].drop_duplicates().reset_index(drop=True)
dim_city['city_id'] = range(1, len(dim_city) + 1)

# Dim_Date
dim_date = pd.DataFrame({
    'timestamp': df['time'].drop_duplicates(),
    'year': df['time'].dt.year,
    'month': df['time'].dt.month,
    'day': df['time'].dt.day,
    'hour': df['time'].dt.hour
}).reset_index(drop=True)
dim_date['date_id'] = range(101, 101 + len(dim_date))

# Fact_WeatherMetrics
df_merged = df.merge(dim_city, on=['city_name', 'latitude', 'longitude'])
df_merged = df_merged.merge(dim_date, left_on='time', right_on='timestamp')

fact_weather = pd.DataFrame({
    'record_id': range(1001, 1001 + len(df_merged)),
    'city_id': df_merged['city_id'],
    'date_id': df_merged['date_id'],
    'temperature_celsius': df_merged['temperature'],
    'windspeed_kmh': df_merged['windspeed'],
    'weather_condition_code': df_merged['weathercode']
})
print("Star Schema created: Fact_WeatherMetrics, Dim_City, Dim_Date.")

print("\n>>> Step 3: Loading into Analytical Data Warehouse...")
conn = sqlite3.connect("cloud_analytics_dw.db")
dim_city.to_sql("dim_city", conn, if_exists="replace", index=False)
dim_date.to_sql("dim_date", conn, if_exists="replace", index=False)
fact_weather.to_sql("fact_weather", conn, if_exists="replace", index=False)

print("\n>>> Step 4: Running Advanced SQL Queries (Window Functions & CTE)...")
sql_query = """
WITH WeatherMetrics AS (
    SELECT 
        c.city_name,
        f.temperature_celsius,
        f.windspeed_kmh,
        AVG(f.temperature_celsius) OVER() AS global_avg_temp,
        RANK() OVER(ORDER BY f.temperature_celsius DESC) AS temp_rank
    FROM fact_weather f
    JOIN dim_city c ON f.city_id = c.city_id
)
SELECT * FROM WeatherMetrics;
"""
analytics_df = pd.read_sql_query(sql_query, conn)
print(analytics_df.to_string(index=False))

print("\n>>> Step 5: Real GenAI Insight Generation...")
try:
    # os.getenv() dwara .env nundi key theesukuntundi
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    warehouse_data = analytics_df.to_dict(orient="records")
    
    prompt = f"""
    You are an expert Data Analyst. Analyze the following weather data metrics from our data warehouse.
    Provide a concise 3-line executive summary including the city with the most extreme weather.
    Data: {json.dumps(warehouse_data)}
    """
    
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )
    print("\n[Real AI Output]:\n", response.text)

except Exception as e:
    print("\n[AI Error]:", str(e))
