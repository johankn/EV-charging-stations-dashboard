import streamlit as st
import pandas as pd
import pydeck as pdk

# Load cleaned data
df = pd.read_csv('data/clean_ev_stations.csv')

# Streamlit page setup
st.set_page_config(page_title="Oahu EV Charging Stations", layout="wide")

st.title("🔌 Oahu EV Charging Stations Dashboard")
st.write("Map showing EV charging locations on Oahu, Hawaii.")

# Prepare the DataFrame
map_df = pd.DataFrame({
    'latitude': df['Latitude'],
    'longitude': df['Longitude'],
    'Facility': df['Facility'],
    'Number of Chargers': df['Number of Chargers'],
    'Charger Level': df['Charger Level'],
    'Charge Fee': df['Charge Fee'],
})

# Create a pydeck layer
layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_df,
    get_position='[Longitude, Latitude]',
    get_radius='Number of Chargers * 2000',  # Bigger circles
    get_fill_color='[0, 200, 255, 120]',       # Brighter blue, semi-transparent (RGBA)
    pickable=True,
    opacity=0.5,  # Extra transparency
)

# Set the view of the map
view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.8,
    zoom=10,
    pitch=0,
)

# Show the map
st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={"text": "{Facility}\nChargers: {Number of Chargers}\nFee: {Charge Fee}"}
))

# Expandable table below
with st.expander("See station details"):
    st.dataframe(map_df)
