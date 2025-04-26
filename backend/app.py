import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt
import numpy as np

# Streamlit app layout
st.set_page_config(page_title="Oahu EV Charging Stations", layout="wide")
st.title("Distribution of EV Charging Stations on Oahu")
st.write("Green = Charging Stations, Red = Population Centers")

# Load datasets
df = pd.read_csv('data/clean_ev_stations.csv')
df_pop = pd.read_csv('data/oahu_zip_population.csv')

# Drop missing coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

st.markdown(
    """
    <style>
    /* Green pills in sidebar multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #006400 !important;  /* Darker green background */
        color: white !important;               /* White text */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
df_pop = df_pop.dropna(subset=['Latitude', 'Longitude'])

# Sidebar for Facility filter (multiselect)
facility_options = df['Facility'].dropna().unique()
selected_facilities = st.sidebar.multiselect(
    "Select Facility Type(s)", 
    options=facility_options,
    default=[]
)

# Sidebar for Manufacturer filter (multiselect)
manufacturer_options = df['Manufacturer'].dropna().unique()
selected_manufacturers = st.sidebar.multiselect(
    "Select Manufacturer(s)",
    options=manufacturer_options,
    default=[]
)

# Filter based on sidebar selection
if selected_facilities:
    df = df[df['Facility'].isin(selected_facilities)]

if selected_manufacturers:
    df = df[df['Manufacturer'].isin(selected_manufacturers)]


# Create "size" columns
df['size'] = df['Number of Chargers'] * 100
df_pop['size'] = df_pop['Resident Population'] / 50

# Define EV Charging Stations Layer
ev_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    id="ev-charging-stations",
    get_position=["Longitude", "Latitude"],
    get_color="[0, 100, 0, 160]",  
    pickable=True,
    auto_highlight=True,
    get_radius="size",
    radius_min_pixels=2,
    radius_max_pixels=35,
)

# Define Population Centers Layer
pop_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_pop,
    id="population-centers",
    get_position=["Longitude", "Latitude"],
    get_color="[255, 80, 80, 140]",
    pickable=False,
    auto_highlight=True,
    get_radius="size",
    radius_min_pixels=5,
    radius_max_pixels=40,
)

# Define the view
view_state = pdk.ViewState(
    latitude=21.3,
    longitude=-157.8,
    zoom=10,
    pitch=30,
    controller=True,
)

# Build the pydeck map
chart = pdk.Deck(
    layers=[pop_layer, ev_layer],  # Population layer first so chargers show on top
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/light-v9",
    tooltip={
        "html": "<b>Facility:</b> {Facility}<br/>"
                "<b>Parking Lot:</b> {Parking Lot}<br/>"
                "<b>Chargers:</b> {Number of Chargers}<br/>"
                "<b>Fee:</b> {Charge Fee}<br/>"
                "<b>Manufacturer:</b> {Manufacturer}",
        "style": {
            "backgroundColor": "rgba(0, 128, 0, 0.7)",
            "color": "white"
        }
    },
)

# --- Facility Bar Chart ---
facility_counts = df['Facility'].value_counts().reset_index()
facility_counts.columns = ['Facility', 'Count']

bar_chart = alt.Chart(facility_counts).mark_bar().encode(
    x=alt.X('Facility:N', title="Facility"),
    y=alt.Y('Count:Q', title="Number of Stations"),
    color=alt.Color('Facility:N',
        scale=alt.Scale(scheme='greens')
    ),
    tooltip=['Facility', 'Count']
).properties(
    width=500,
    height=400,
    title="Number of Charging Stations by Facility"
)

# --- Layout: Map + Bar Chart ---
col1, col2 = st.columns([3, 2])

with col1:
    st.pydeck_chart(chart, use_container_width=True)

with col2:
    # Create two columns inside col2 for metrics
    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(label="🔋 Charging Stations", value=len(df))

    with metric2:
        st.metric(label="⚡ Individual Chargers", value=int(df['Number of Chargers'].sum()))

    with metric3:
        st.metric(label="📈 Avg Chargers/Station", value=round(df['Number of Chargers'].mean(), 1))
    
    # Then the bar chart below
    st.altair_chart(bar_chart, use_container_width=True)

# Expandable table to show all
with st.expander("See full station list"):
    st.dataframe(df.drop(columns=["size", "Latitude", "Longitude", "Charger Level"], errors='ignore'))

with st.expander("See full population data"):
    st.dataframe(df_pop.drop(columns=["size", "Latitude", "Longitude"], errors='ignore'))
