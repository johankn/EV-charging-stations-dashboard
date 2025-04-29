import pandas as pd
import re

df = pd.read_csv('data/Public_Charging_Stations_in_Hawaii.csv')

df = df[df['Island'] == 'Oahu']

def extract_coords(address):
    if pd.isna(address):
        return None, None
    match = re.search(r'\(([-\d.]+),\s*([-\d.]+)\)', address)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    else:
        return None, None

df[['Latitude', 'Longitude']] = df['Address'].apply(lambda x: pd.Series(extract_coords(x)))

df = df.dropna(subset=['Latitude', 'Longitude'])

# Clean up the DataFrame: only keep useful columns
final_df = df[['Facility','Parking Lot', 'Latitude', 'Longitude', 'Number of Chargers', 'Charger Level', 'Charge Fee', 'Manufacturer']]

# Fill missing values for consistency
final_df['Charge Fee'] = final_df['Charge Fee'].fillna('Unknown')

print(final_df.head())

# save to CSV
final_df.to_csv('clean_ev_stations.csv', index=False)
