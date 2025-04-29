import pandas as pd

# Load your existing cleaned data
df = pd.read_csv('data/clean_ev_stations.csv')

# Create new stations as one DataFrame
new_stations = pd.DataFrame([
    {
        'Facility': 'Commercial',
        'Parking Lot': 'Honouliuli Wastewater Treatment Plant',
        'Latitude': 21.33551471222625,
        'Longitude': -158.03749087300034,
        'Number of Chargers': 34,
        'Charger Level': 3,
        'Charge Fee': 'Unknown',
        'Manufacturer': 'J-1772',
    }, 
])

# Concatenate and save
df = pd.concat([df, new_stations], ignore_index=True)
df.to_csv('data/clean_ev_stations.csv', index=False)

print("✅ 6 new stations added successfully!")
