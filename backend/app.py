import streamlit as st
import pydeck as pdk
import pandas as pd

# Load your cleaned dataset
df = pd.read_csv('data/clean_ev_stations.csv')

# Drop rows with missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Create a "size" column to determine radius size
# You can make it proportional to number of chargers
df['size'] = df['Number of Chargers'] * 100  # Adjust multiplier to make circles bigger

# Define the ScatterplotLayer
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    id="ev-charging-stations",
    get_position=["Longitude", "Latitude"],
    get_color="[255, 75, 75, 140]",  # Bright red, semi-transparent
    pickable=True,
    auto_highlight=True,
    get_radius="size",  
    radius_min_pixels=1, 
    radius_max_pixels=35,  
)


# Define the view state
view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.8,
    zoom=10,
    pitch=30,
    controller=True,
)

# Build the pydeck chart
chart = pdk.Deck(
    layers=[point_layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v9",
    tooltip={
        "text": "{Facility}\n"
                "Chargers: {Number of Chargers}\n"
                "Fee: {Charge Fee}\n"
                "Level: {Charger Level}\n"
                "Manufacturer: {Manufacturer}"
    },
)

# Streamlit app layout
st.set_page_config(page_title="Oahu EV Charging Stations", layout="wide")
st.title("🔌 Oahu EV Charging Stations Dashboard")
st.write("Circle size = number of chargers.")

# Render the map
event = st.pydeck_chart(chart, on_select="rerun", selection_mode="multi-object")

# Expandable table to show all
with st.expander("See full station list"):
    st.dataframe(df.drop(columns=["size"]))