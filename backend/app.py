import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt

# Streamlit app layout
st.set_page_config(page_title="Oahu EV Charging Stations", layout="wide")
st.title("🔌 Oahu EV Charging Stations Dashboard")
st.write("Circle size = number of chargers.")

# Load your cleaned dataset
df = pd.read_csv('data/clean_ev_stations.csv')

# Drop rows with missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])



# Sidebar for Facility filter (multiselect)
facility_options = df['Facility'].dropna().unique()
selected_facilities = st.sidebar.multiselect(
    "Select Facility Type(s)", 
    options=facility_options,
    default=[]  # Default = none selected
)

# Sidebar for Manufacturer filter (multiselect)
manufacturer_options = df['Manufacturer'].dropna().unique()
selected_manufacturers = st.sidebar.multiselect(
    "Select Manufacturer(s)",
    options=manufacturer_options,
    default=[]
)

# Filter based on selection
if selected_facilities:
    df = df[df['Facility'].isin(selected_facilities)]

if selected_manufacturers:
    df = df[df['Manufacturer'].isin(selected_manufacturers)]

# Show how many stations are being displayed
st.write(f"🔋 Showing **{len(df)}** charging station(s).")


# Create a "size" column to determine radius size
# You can make it proportional to number of chargers
df['size'] = df['Number of Chargers'] * 300  # Adjust multiplier to make circles bigger



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
        "Parking Lot: {Parking Lot}\n"
                "Chargers: {Number of Chargers}\n"
                "Fee: {Charge Fee}\n"
                "Level: {Charger Level}\n"
                "Manufacturer: {Manufacturer}",
    },
)

# --- Facility Bar Chart ---
facility_counts = df['Facility'].value_counts().reset_index()
facility_counts.columns = ['Facility', 'Count']

bar_chart = alt.Chart(facility_counts).mark_bar().encode(
    x=alt.X('Facility:N', title="Facility Type"),
    y=alt.Y('Count:Q', title="Number of Stations"),
    color='Facility:N'  # Color bars by facility
).properties(
    width=500,
    height=600,
    title="Number of Charging Stations by Facility Type"
)

# Layout: Map and bar chart side-by-side
col1, col2 = st.columns([3, 2])  # make the map bigger (2/3) and bar chart smaller (1/3)

with col1:
    st.pydeck_chart(chart, use_container_width=True)

with col2:
    st.altair_chart(bar_chart, use_container_width=True)

st.altair_chart(bar_chart, use_container_width=True)
# --- End Facility Bar Chart ---




# Render the map
event = st.pydeck_chart(chart, on_select="rerun", selection_mode="multi-object")

# Expandable table to show all
with st.expander("See full station list"):
    st.dataframe(df.drop(columns=["size"]))