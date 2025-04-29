import streamlit as st
import pydeck as pdk
import pandas as pd
import altair as alt
import numpy as np

st.set_page_config(page_title="Oahu EV Charging Stations", layout="wide")
st.title("Distribution of EV Charging Stations on Oahu")
st.markdown("🟢 *Green* = Charging Stations &nbsp;&nbsp;&nbsp;&nbsp; 🔴 *Red* = Population Centers")
df = pd.read_csv('backend/data/clean_ev_stations.csv')
df_pop = pd.read_csv('backend/data/oahu_zip_population.csv')

df = df.drop(columns=['Charge Fee'])
df = df.dropna(subset=['Latitude', 'Longitude'])

# Match EV stations to nearest population center
df['Zip Code'] = df.apply(
    lambda row: df_pop.loc[
        ((df_pop['Latitude'] - row['Latitude'])**2 + (df_pop['Longitude'] - row['Longitude'])**2).idxmin(),
        'Zip Code'
    ],
    axis=1
)
chargers_by_zip = df.groupby('Zip Code')['Number of Chargers'].sum().reset_index()
chargers_by_zip.columns = ['Zip Code', 'Number of Chargers']  
merged = pd.merge(df_pop, chargers_by_zip, on='Zip Code', how='left')
merged['Number of Chargers'] = merged['Number of Chargers'].fillna(0)  # Fill empty values with 0
merged['Chargers per 1000'] = (merged['Number of Chargers'] / merged['Resident Population']) * 1000
pop_threshold = 3000
filtered = merged[merged['Resident Population'] > pop_threshold]
# Step 1: Sort by lowest chargers per 1000
merged_sorted = filtered.sort_values(by='Chargers per 1000')

# Step 2: Among bottom 10 (or more), choose top 3 by population
bottom_underserved = merged_sorted.head(10)  # can change to 15, 20, etc.
top3_underserved = bottom_underserved.sort_values(by='Resident Population', ascending=False).head(5)


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

st.subheader("Top 5 Most Underserved High-Population Areas")


underserved_display = top3_underserved[[
    'Zip Code', 'Area', 'Resident Population', 'Number of Chargers', 'Chargers per 1000'
]].copy()

underserved_display.columns = ['ZIP', 'Area', 'Population', 'Chargers', 'Chargers per 1000']
underserved_display['Population'] = underserved_display['Population'].astype(int)
underserved_display['Chargers'] = underserved_display['Chargers'].astype(int)
underserved_display['Chargers per 1000'] = underserved_display['Chargers per 1000'].round(2)

underserved_display.index = range(1, len(underserved_display) + 1)  # Force 1-based index
st.table(underserved_display)




# Expandable table to show all
with st.expander("See full station list"):
    st.dataframe(df.drop(columns=["size", "Latitude", "Longitude", "Charger Level"], errors='ignore'))

with st.expander("See full population data"):
    st.dataframe(df_pop.drop(columns=["size", "Latitude", "Longitude"], errors='ignore'))
