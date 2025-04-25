import pandas as pd
import re

# Load the dataset
df = pd.read_csv('data/Public_Charging_Stations_in_Hawaii.csv')

# Drop obviously broken rows
df = df[df['Island'] == 'Oahu']

# Extract latitude and longitude from the Address field
def extract_coords(address):
    """Extract (latitude, longitude) from the address string."""
    if pd.isna(address):
        return None, None
    match = re.search(r'\(([-\d.]+),\s*([-\d.]+)\)', address)
    if match:
        lat = float(match.group(1))
        lon = float(match.group(2))
        return lat, lon
    else:
        return None, None

# Apply extraction
df[['Latitude', 'Longitude']] = df['Address'].apply(lambda x: pd.Series(extract_coords(x)))

# Drop rows where we couldn't extract coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Clean up the DataFrame: only keep useful columns
final_df = df[['Facility', 'Latitude', 'Longitude', 'Number of Chargers', 'Charger Level', 'Charge Fee', 'Manufacturer']]

# Fill missing values for consistency
final_df['Charge Fee'] = final_df['Charge Fee'].fillna('Unknown')

# Preview
print(final_df.head())

# Optionally save to CSV
final_df.to_csv('clean_ev_stations.csv', index=False)
