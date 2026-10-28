# ============================================
# Berlin Weather Data Pipeline
# Author: Mohammad Shahid
# Description: Fetches real-time hourly
# weather data from Open-Meteo API,
# cleans and analyzes it using Pandas
# ============================================

# ============================================
# STEP 1: IMPORT LIBRARIES
# ============================================

import requests      # fetch data from API
import pandas as pd  # data manipulation
import json          # handle JSON data

print("✅ Step 1 Complete: Libraries imported!")


# ============================================
# STEP 2: BUILD API URL
# ============================================

# Berlin city coordinates
# latitude = 52.52 (north/south position)
# longitude = 13.41 (east/west position)

latitude = 52.52
longitude = 13.41

# Build API URL with 6 weather metrics
url = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    f"&hourly=temperature_2m"
    f",windspeed_10m"
    f",relativehumidity_2m"
    f",apparent_temperature"
    f",precipitation_probability"
    f",weathercode"
    f"&timezone=Europe%2FBerlin"
    f"&forecast_days=7"
)

print("✅ Step 2 Complete: API URL built!")
print(f"URL: {url}")


# ============================================
# STEP 3: FETCH DATA FROM API
# ============================================

print("\n🔄 Fetching data from Open-Meteo API...")

# Send request to weather API
# like opening a webpage but in Python
response = requests.get(url)

# Check if request was successful
# status code 200 = success
# status code 404 = not found
# status code 500 = server error
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("✅ Step 3 Complete: Data fetched successfully!")
else:
    print("❌ Error: Could not fetch data!")
    print("Check your internet connection!")

# Convert response to Python dictionary
# JSON = JavaScript Object Notation
# It is like a nested dictionary in Python
raw_data = response.json()

# See all available keys in response
print(f"\nAvailable Keys: {list(raw_data.keys())}")

# See all available hourly metrics
print(f"\nHourly Metrics: {list(raw_data['hourly'].keys())}")


# ============================================
# STEP 4: CONVERT JSON TO DATAFRAME
# ============================================

print("\n🔄 Converting JSON to DataFrame...")

# Extract hourly data from raw_data
# raw_data['hourly'] contains all 
# weather metrics as dictionary
hourly_data = raw_data['hourly']

# Convert dictionary to Pandas DataFrame
# Each key becomes a column
# Each value list becomes column data
df = pd.DataFrame(hourly_data)

# Rename columns for clarity
# cleaner names for Google Sheets
df.columns = [
    'time',
    'temperature_c',
    'windspeed_kmh',
    'humidity_pct',
    'feels_like_c',
    'rain_chance_pct',
    'weather_code'
]

# Convert time column from text to datetime
# Before: "2026-10-23T00:00" as text
# After: 2026-10-23 00:00:00 as datetime
df['time'] = pd.to_datetime(df['time'])

# See first 5 rows
print("\nFirst 5 Rows:")
print(df.head())

# See shape of DataFrame
# shape = (rows, columns)
print(f"\nDataFrame Shape: {df.shape}")
print(f"Total Hours: {df.shape[0]}")
print(f"Total Columns: {df.shape[1]}")

# See all column names and data types
print("\nColumn Information:")
print(df.dtypes)

print("\n✅ Step 4 Complete: DataFrame created!")


# ============================================
# STEP 5: DATA CLEANING & VALIDATION
# ============================================

print("\n" + "="*50)
print("🔄 Starting Data Cleaning...")
print("="*50)

# ----------------------------------------
# CHECK 1: Missing Values
# ----------------------------------------
print("\n📋 CHECK 1: Missing Values")
missing_values = df.isnull().sum()
print(missing_values)

total_missing = missing_values.sum()
if total_missing == 0:
    print("✅ No missing values found!")
else:
    print(f"⚠️ Found {total_missing} missing values!")
    # Fill missing temperature with average
    df['temperature_c'].fillna(
        df['temperature_c'].mean(), 
        inplace=True
    )
    # Fill missing humidity with average
    df['humidity_pct'].fillna(
        df['humidity_pct'].mean(), 
        inplace=True
    )
    print("✅ Missing values filled with average!")

# ----------------------------------------
# CHECK 2: Duplicate Timestamps
# ----------------------------------------
print("\n📋 CHECK 2: Duplicate Timestamps")
duplicates = df.duplicated(
    subset=['time']
).sum()
print(f"Duplicate Rows: {duplicates}")

if duplicates == 0:
    print("✅ No duplicates found!")
else:
    print(f"⚠️ Found {duplicates} duplicates!")
    df.drop_duplicates(
        subset=['time'], 
        inplace=True
    )
    print("✅ Duplicates removed!")

# ----------------------------------------
# CHECK 3: Invalid Temperature Values
# ----------------------------------------
print("\n📋 CHECK 3: Invalid Temperatures")
# -237.15 is absolute zero in Celsius
# No temperature can be below this
invalid_temp = df[
    df['temperature_c'] < -237.15
].shape[0]
print(f"Invalid Temperatures: {invalid_temp}")

if invalid_temp == 0:
    print("✅ All temperature values are valid!")
else:
    print(f"⚠️ Found {invalid_temp} invalid temperatures!")
    df = df[df['temperature_c'] > -237.15]
    print("✅ Invalid temperatures removed!")

# ----------------------------------------
# CHECK 4: Invalid Humidity Values
# ----------------------------------------
print("\n📋 CHECK 4: Invalid Humidity")
# Humidity must be between 0% and 100%
invalid_humidity = df[
    (df['humidity_pct'] < 0) | 
    (df['humidity_pct'] > 100)
].shape[0]
print(f"Invalid Humidity Values: {invalid_humidity}")

if invalid_humidity == 0:
    print("✅ All humidity values are valid!")
else:
    print(f"⚠️ Found {invalid_humidity} invalid humidity!")
    df = df[
        (df['humidity_pct'] >= 0) & 
        (df['humidity_pct'] <= 100)
    ]
    print("✅ Invalid humidity removed!")

# ----------------------------------------
# CHECK 5: Invalid Rain Chance Values
# ----------------------------------------
print("\n📋 CHECK 5: Invalid Rain Chance")
# Rain chance must be between 0% and 100%
invalid_rain = df[
    (df['rain_chance_pct'] < 0) | 
    (df['rain_chance_pct'] > 100)
].shape[0]
print(f"Invalid Rain Values: {invalid_rain}")

if invalid_rain == 0:
    print("✅ All rain values are valid!")
else:
    print(f"⚠️ Found {invalid_rain} invalid rain values!")
    df = df[
        (df['rain_chance_pct'] >= 0) & 
        (df['rain_chance_pct'] <= 100)
    ]
    print("✅ Invalid rain values removed!")

# ----------------------------------------
# ADD NEW COLUMNS
# ----------------------------------------
print("\n📋 Adding New Columns...")

# Extract date from datetime
df['date'] = df['time'].dt.date

# Extract hour from datetime
df['hour'] = df['time'].dt.hour

# Extract day name (Monday, Tuesday etc)
df['day_name'] = df['time'].dt.day_name()

# Temperature difference
# difference between actual and feels like
df['temp_diff'] = (
    df['temperature_c'] - 
    df['feels_like_c']
).round(2)

# Weather condition from weather code
# Open-Meteo weather codes:
# 0 = Clear sky
# 1,2,3 = Partly cloudy
# 45,48 = Foggy
# 51,53,55 = Drizzle
# 61,63,65 = Rain
# 71,73,75 = Snow
# 95 = Thunderstorm

def get_weather_condition(code):
    if code == 0:
        return 'Clear Sky'
    elif code in [1, 2, 3]:
        return 'Partly Cloudy'
    elif code in [45, 48]:
        return 'Foggy'
    elif code in [51, 53, 55]:
        return 'Drizzle'
    elif code in [61, 63, 65]:
        return 'Rainy'
    elif code in [71, 73, 75]:
        return 'Snowy'
    elif code == 95:
        return 'Thunderstorm'
    else:
        return 'Cloudy'

df['weather_condition'] = df[
    'weather_code'
].apply(get_weather_condition)

print("✅ New columns added!")

# Final DataFrame Info
print("\n📋 Final DataFrame Info:")
print(f"Total Rows: {df.shape[0]}")
print(f"Total Columns: {df.shape[1]}")
print(f"\nAll Columns: {list(df.columns)}")
print("\nFirst 3 Rows:")
print(df.head(3))

print("\n✅ Step 5 Complete: Data Cleaning Done!")



# ============================================
# STEP 6: STATISTICAL ANALYSIS
# ============================================

print("\n" + "="*50)
print("🔄 Starting Statistical Analysis...")
print("="*50)

# ----------------------------------------
# ANALYSIS 1: Overall Statistics
# ----------------------------------------
print("\n📊 ANALYSIS 1: Overall Statistics")
print(f"📅 Forecast Period: "
    f"{df['date'].min()} to "
    f"{df['date'].max()}")
print(f"🌡️  Average Temperature: "
    f"{df['temperature_c'].mean():.1f}°C")
print(f"🌡️  Highest Temperature: "
    f"{df['temperature_c'].max():.1f}°C")
print(f"🌡️  Lowest Temperature: "
    f"{df['temperature_c'].min():.1f}°C")
print(f"💨 Average Wind Speed: "
    f"{df['windspeed_kmh'].mean():.1f} km/h")
print(f"💧 Average Humidity: "
    f"{df['humidity_pct'].mean():.1f}%")
print(f"🌧️  Average Rain Chance: "
    f"{df['rain_chance_pct'].mean():.1f}%")

# ----------------------------------------
# ANALYSIS 2: Daily Summary
# ----------------------------------------
print("\n📊 ANALYSIS 2: Daily Summary")

daily_summary = df.groupby('date').agg(
    # average temperature per day
    avg_temp = ('temperature_c', 'mean'),
    # maximum temperature per day
    max_temp = ('temperature_c', 'max'),
    # minimum temperature per day
    min_temp = ('temperature_c', 'min'),
    # average humidity per day
    avg_humidity = ('humidity_pct', 'mean'),
    # average wind speed per day
    avg_wind = ('windspeed_kmh', 'mean'),
    # maximum rain chance per day
    max_rain_chance = ('rain_chance_pct', 'max'),
    # most common weather condition
    weather = ('weather_condition', 
            lambda x: x.mode()[0])
).round(1)

print(daily_summary.to_string())

# ----------------------------------------
# ANALYSIS 3: Hottest & Coldest Hours
# ----------------------------------------
print("\n📊 ANALYSIS 3: Hottest & Coldest Hours")

# Find hottest hour
hottest = df.loc[
    df['temperature_c'].idxmax()
]
print(f"\n🔥 Hottest Hour:")
print(f"   Time: {hottest['time']}")
print(f"   Temperature: {hottest['temperature_c']}°C")
print(f"   Feels Like: {hottest['feels_like_c']}°C")
print(f"   Condition: {hottest['weather_condition']}")

# Find coldest hour
coldest = df.loc[
    df['temperature_c'].idxmin()
]
print(f"\n🥶 Coldest Hour:")
print(f"   Time: {coldest['time']}")
print(f"   Temperature: {coldest['temperature_c']}°C")
print(f"   Feels Like: {coldest['feels_like_c']}°C")
print(f"   Condition: {coldest['weather_condition']}")

# ----------------------------------------
# ANALYSIS 4: Windiest Hour
# ----------------------------------------
print("\n📊 ANALYSIS 4: Windiest Hour")

windiest = df.loc[
    df['windspeed_kmh'].idxmax()
]
print(f"\n💨 Windiest Hour:")
print(f"   Time: {windiest['time']}")
print(f"   Wind Speed: {windiest['windspeed_kmh']} km/h")
print(f"   Temperature: {windiest['temperature_c']}°C")
print(f"   Condition: {windiest['weather_condition']}")

# ----------------------------------------
# ANALYSIS 5: Most Humid Hour
# ----------------------------------------
print("\n📊 ANALYSIS 5: Most Humid Hour")

most_humid = df.loc[
    df['humidity_pct'].idxmax()
]
print(f"\n💧 Most Humid Hour:")
print(f"   Time: {most_humid['time']}")
print(f"   Humidity: {most_humid['humidity_pct']}%")
print(f"   Temperature: {most_humid['temperature_c']}°C")
print(f"   Condition: {most_humid['weather_condition']}")

# ----------------------------------------
# ANALYSIS 6: Rain Forecast
# ----------------------------------------
print("\n📊 ANALYSIS 6: Rain Forecast")

# Hours with high rain chance (above 50%)
high_rain = df[
    df['rain_chance_pct'] > 50
]
print(f"\n🌧️  Hours With High Rain Chance: "
    f"{len(high_rain)}")

if len(high_rain) > 0:
    print("\nRainy Hours Details:")
    rain_display = high_rain[[
        'time',
        'rain_chance_pct',
        'temperature_c',
        'weather_condition'
    ]].head(5)
    print(rain_display.to_string())
else:
    print("✅ No high rain chance in forecast!")

# ----------------------------------------
# ANALYSIS 7: Weather Condition Summary
# ----------------------------------------
print("\n📊 ANALYSIS 7: Weather Conditions")

condition_summary = df[
    'weather_condition'
].value_counts()
print("\nHours Per Weather Condition:")
for condition, hours in condition_summary.items():
    percentage = (hours/len(df)*100)
    print(f"   {condition}: "
        f"{hours} hours "
        f"({percentage:.1f}%)")

# ----------------------------------------
# ANALYSIS 8: Hourly Temperature Pattern
# ----------------------------------------
print("\n📊 ANALYSIS 8: Hourly Pattern")

hourly_avg = df.groupby('hour').agg(
    avg_temp = ('temperature_c', 'mean'),
    avg_humidity = ('humidity_pct', 'mean')
).round(1)

print("\nAverage Temperature By Hour:")
print(hourly_avg.to_string())

print("\n✅ Step 6 Complete: Analysis Done!")



# ============================================
# STEP 7: BUSINESS INSIGHTS
# ============================================

print("\n" + "="*50)
print("🔄 Generating Business Insights...")
print("="*50)

# ----------------------------------------
# INSIGHT 1: Best Day To Go Outside
# ----------------------------------------
print("\n💡 INSIGHT 1: Best Day To Go Outside")

# Best day = highest temp + lowest rain
# + lowest wind speed
daily_score = df.groupby('date').agg(
    avg_temp = ('temperature_c', 'mean'),
    avg_rain = ('rain_chance_pct', 'mean'),
    avg_wind = ('windspeed_kmh', 'mean')
).round(1)

# Higher temp = better score
# Lower rain = better score
# Lower wind = better score
daily_score['outdoor_score'] = (
    daily_score['avg_temp'] -
    (daily_score['avg_rain'] * 0.3) -
    (daily_score['avg_wind'] * 0.2)
).round(2)

best_day = daily_score[
    'outdoor_score'
].idxmax()

worst_day = daily_score[
    'outdoor_score'
].idxmin()

print(f"\n✅ Best Day To Go Outside: {best_day}")
print(f"   Score: "
    f"{daily_score.loc[best_day, 'outdoor_score']}")
print(f"   Avg Temp: "
    f"{daily_score.loc[best_day, 'avg_temp']}°C")
print(f"   Avg Rain Chance: "
    f"{daily_score.loc[best_day, 'avg_rain']}%")
print(f"   Avg Wind: "
    f"{daily_score.loc[best_day, 'avg_wind']} km/h")

print(f"\n❌ Worst Day To Go Outside: {worst_day}")
print(f"   Score: "
    f"{daily_score.loc[worst_day, 'outdoor_score']}")
print(f"   Avg Temp: "
    f"{daily_score.loc[worst_day, 'avg_temp']}°C")
print(f"   Avg Rain Chance: "
    f"{daily_score.loc[worst_day, 'avg_rain']}%")
print(f"   Avg Wind: "
    f"{daily_score.loc[worst_day, 'avg_wind']} km/h")

# ----------------------------------------
# INSIGHT 2: Health Alerts
# ----------------------------------------
print("\n💡 INSIGHT 2: Health Alerts")

# High humidity alert (above 85%)
high_humidity_hours = df[
    df['humidity_pct'] > 85
]
if len(high_humidity_hours) > 0:
    print(f"\n⚠️  High Humidity Alert!")
    print(f"   {len(high_humidity_hours)} hours "
        f"above 85% humidity")
    print(f"   May cause breathing discomfort!")
else:
    print("\n✅ No high humidity alerts!")

# Strong wind alert (above 30 km/h)
strong_wind_hours = df[
    df['windspeed_kmh'] > 30
]
if len(strong_wind_hours) > 0:
    print(f"\n⚠️  Strong Wind Alert!")
    print(f"   {len(strong_wind_hours)} hours "
        f"above 30 km/h wind speed")
    print(f"   Be careful outdoors!")
else:
    print("✅ No strong wind alerts!")

# Cold temperature alert (below 5°C)
cold_hours = df[
    df['temperature_c'] < 5
]
if len(cold_hours) > 0:
    print(f"\n⚠️  Cold Temperature Alert!")
    print(f"   {len(cold_hours)} hours "
        f"below 5°C")
    print(f"   Wear warm clothes!")
else:
    print("✅ No cold temperature alerts!")

# High rain alert (above 70%)
heavy_rain_hours = df[
    df['rain_chance_pct'] > 70
]
if len(heavy_rain_hours) > 0:
    print(f"\n⚠️  Heavy Rain Alert!")
    print(f"   {len(heavy_rain_hours)} hours "
        f"above 70% rain chance")
    print(f"   Carry umbrella!")
else:
    print("✅ No heavy rain alerts!")

# ----------------------------------------
# INSIGHT 3: Best Hours To Go Outside
# ----------------------------------------
print("\n💡 INSIGHT 3: Best Hours Today")

# Filter only today's data
today = df['date'].min()
today_df = df[df['date'] == today]

# Best hours = temp above average
# and rain chance below 30%
avg_temp_today = (
    today_df['temperature_c'].mean()
)

best_hours = today_df[
    (today_df['temperature_c'] >=
    avg_temp_today) &
    (today_df['rain_chance_pct'] < 30)
]

if len(best_hours) > 0:
    print(f"\n✅ Best Hours To Go Outside Today:")
    for _, row in best_hours.iterrows():
        print(f"   {row['hour']:02d}:00 - "
            f"Temp: {row['temperature_c']}°C - "
            f"Rain: {row['rain_chance_pct']}% - "
            f"{row['weather_condition']}")
else:
    print("\n⚠️  No ideal hours today!")
    print("   Stay indoors if possible!")

# ----------------------------------------
# INSIGHT 4: Weekly Summary Report
# ----------------------------------------
print("\n💡 INSIGHT 4: Weekly Summary Report")
print("\n" + "="*50)
print("   BERLIN WEATHER WEEKLY REPORT")
print("="*50)
print(f"📅 Period: {df['date'].min()} "
    f"to {df['date'].max()}")
print(f"🌡️  Week Avg Temp: "
    f"{df['temperature_c'].mean():.1f}°C")
print(f"🔥 Hottest: "
    f"{df['temperature_c'].max():.1f}°C")
print(f"🥶 Coldest: "
    f"{df['temperature_c'].min():.1f}°C")
print(f"💨 Max Wind: "
    f"{df['windspeed_kmh'].max():.1f} km/h")
print(f"💧 Avg Humidity: "
    f"{df['humidity_pct'].mean():.1f}%")
print(f"🌧️  Max Rain Chance: "
    f"{df['rain_chance_pct'].max():.1f}%")
print(f"🏆 Best Day: {best_day}")
print(f"❌ Worst Day: {worst_day}")
print(f"📊 Total Hours Analyzed: {len(df)}")
print("="*50)

print("\n✅ Step 7 Complete: Insights Generated!")



# ============================================
# STEP 8: EXPORT TO CSV & EXCEL
# ============================================

print("\n" + "="*50)
print("🔄 Exporting Data...")
print("="*50)

# import os to create folders
import os

# ----------------------------------------
# CREATE OUTPUT FOLDER
# ----------------------------------------
# Create output folder if not exists
output_folder = 'output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"\n✅ Created folder: {output_folder}")
else:
    print(f"\n✅ Output folder already exists!")

# ----------------------------------------
# EXPORT 1: Main Weather Data CSV
# ----------------------------------------
print("\n📤 Exporting Main Weather Data...")

# Select important columns for export
export_df = df[[
    'time',
    'date',
    'day_name',
    'hour',
    'temperature_c',
    'feels_like_c',
    'temp_diff',
    'windspeed_kmh',
    'humidity_pct',
    'rain_chance_pct',
    'weather_condition'
]]

# Export to CSV
# index=False means don't include
# row numbers in CSV
csv_path = os.path.join(
    output_folder,
    'berlin_weather_data.csv'
)
export_df.to_csv(
    csv_path,
    index=False
)
print(f"✅ CSV exported: {csv_path}")
print(f"   Rows: {len(export_df)}")
print(f"   Columns: {len(export_df.columns)}")

# ----------------------------------------
# EXPORT 2: Daily Summary CSV
# ----------------------------------------
print("\n📤 Exporting Daily Summary...")

# Create daily summary DataFrame
daily_export = df.groupby(
    ['date', 'day_name']
).agg(
    avg_temp_c = ('temperature_c', 'mean'),
    max_temp_c = ('temperature_c', 'max'),
    min_temp_c = ('temperature_c', 'min'),
    avg_feels_like_c = ('feels_like_c', 'mean'),
    avg_humidity_pct = ('humidity_pct', 'mean'),
    avg_wind_kmh = ('windspeed_kmh', 'mean'),
    max_wind_kmh = ('windspeed_kmh', 'max'),
    max_rain_chance_pct = ('rain_chance_pct', 'max'),
    avg_rain_chance_pct = ('rain_chance_pct', 'mean'),
    dominant_condition = (
        'weather_condition',
        lambda x: x.mode()[0]
    )
).round(1).reset_index()

# Export daily summary to CSV
daily_csv_path = os.path.join(
    output_folder,
    'berlin_daily_summary.csv'
)
daily_export.to_csv(
    daily_csv_path,
    index=False
)
print(f"✅ Daily Summary CSV exported: "
    f"{daily_csv_path}")
print(f"   Days: {len(daily_export)}")

# ----------------------------------------
# EXPORT 3: Excel File With Multiple Sheets
# ----------------------------------------
print("\n📤 Exporting Excel File...")

excel_path = os.path.join(
    output_folder,
    'berlin_weather_report.xlsx'
)

# ExcelWriter allows multiple sheets
# in one Excel file
with pd.ExcelWriter(
    excel_path,
    engine='openpyxl'
) as writer:

    # Sheet 1: Full hourly data
    export_df.to_excel(
        writer,
        sheet_name='Hourly Data',
        index=False
    )
    print("   ✅ Sheet 1: Hourly Data added!")

    # Sheet 2: Daily summary
    daily_export.to_excel(
        writer,
        sheet_name='Daily Summary',
        index=False
    )
    print("   ✅ Sheet 2: Daily Summary added!")

    # Sheet 3: Weather conditions summary
    condition_summary = df.groupby(
        'weather_condition'
    ).agg(
        total_hours = ('time', 'count'),
        avg_temp = ('temperature_c', 'mean'),
        avg_humidity = ('humidity_pct', 'mean'),
        avg_rain_chance = (
            'rain_chance_pct', 'mean'
        )
    ).round(1).reset_index()

    condition_summary.to_excel(
        writer,
        sheet_name='Conditions Summary',
        index=False
    )
    print("   ✅ Sheet 3: Conditions Summary added!")

    # Sheet 4: Outdoor activity scores
    daily_score_export = daily_score.copy()
    daily_score_export = (
        daily_score_export.reset_index()
    )
    daily_score_export.to_excel(
        writer,
        sheet_name='Outdoor Scores',
        index=False
    )
    print("   ✅ Sheet 4: Outdoor Scores added!")

print(f"\n✅ Excel exported: {excel_path}")
print(f"   Total Sheets: 4")

# ----------------------------------------
# EXPORT SUMMARY
# ----------------------------------------
print("\n" + "="*50)
print("📊 EXPORT SUMMARY")
print("="*50)
print(f"📁 Output Folder: {output_folder}/")
print(f"📄 Files Created:")
print(f"   1. berlin_weather_data.csv")
print(f"      ({len(export_df)} rows, "
    f"{len(export_df.columns)} columns)")
print(f"   2. berlin_daily_summary.csv")
print(f"      ({len(daily_export)} days)")
print(f"   3. berlin_weather_report.xlsx")
print(f"      (4 sheets)")
print("="*50)

print("\n✅ Step 8 Complete: Export Done!")
