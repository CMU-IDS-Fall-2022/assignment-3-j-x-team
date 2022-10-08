import streamlit as st
import pandas as pd
import altair as alt
from re import U

st.title("Cleaning & Praparing Data")
## Include zip code > lat/lng data code here.
# sc_df = pd.read_csv("social_capital_zip.csv")

# sc_df.reset_index(inplace=True)

# sc_df.zip = sc_df.zip.astype(str)

# zip_and_coords = pd.read_table("US Zip Codes from 2013 Government Data")

# zip_and_coords.rename(columns={"ZIP,LAT,LNG": "zip"}, inplace=True)

# zip_and_coords = zip_and_coords['zip'].str.split(',', expand=True)

# zip_and_coords.rename(columns={0: "zip", 1: "lat", 2: "lng"}, inplace=True)

# Merge the two dataframes

# sc_df = pd.merge(sc_df, zip_and_coords, on='zip')

#sc_df.to_csv("social_capital_zip_coords.csv")

st.title("Social Capital Data Interaction.")
# date: 1007
@st.cache  # add caching so we load the data only once

def load_data():
    return pd.read_csv("data/social_capital_zip_coords.csv")

df = load_data()

st.write("Let's look at raw data in the Pandas Data Frame.")

st.write(df)
st.write(len(df.index))

# streamlit way to create map chart
# allows zoom in/out, but seems not supporting tooltip on data points
geo_data = df[['lat','lng']] # change column name, st.map() only recognize column names of "lat" and "lon"
geo_data = geo_data.rename(columns={'lng':'lon'})
st.map(geo_data)

# altair way to create map chart
# altair supports tooltip on datapoints, but currently doesn't support to zoom in/out a map chart
# reference: https://altair-viz.github.io/altair-tutorial/notebooks/09-Geographic-plots.html

sc_chart = alt.Chart(df).mark_circle().encode(
    longitude='lng:Q',
    latitude='lat:Q',
    size=alt.value(10),
    tooltip='zip'
).project(
    type='albersUsa'
).properties(
    width=600,
    height=400,
    title='Social Capital by Zipcode'
).interactive()

st.altair_chart(sc_chart, use_container_width=True)


# states = alt.topo_feature(data.us_10m.url, feature='states')

# background = alt.Chart(states).mark_geoshape(
#     fill='lightgray',
#     stroke='white'
# ).project('albersUsa').properties(
#     width=1000,
#     height=800
# )

# points = alt.Chart(df).mark_circle().encode(
#     longitude = 'lng',
#     latitude = 'lat',
#     size = alt.value(10),
#     tooltip = ['zip','lat','lng','ec_zip']
# ).interactive()

# st.write(background+points)


## Make a table that displays (for the selected zip code):
#   -zip code
#   -num_below_p50 (% of population under 50% income percentile)
#   -ec_zip (economic connectedness score)
#   -clustering_zip (proportion of a person's friends who are friends with each other)
#   -civic_organizations_zip (proportion of people who are members of a civic organization)

individual_df = df[['zip','num_below_p50','ec_zip','clustering_zip','civic_organizations_zip']]

individual_df = individual_df.rename(columns={'num_below_p50':'numer of children under 50% income percentile','ec_zip':'economic connectedness score','clustering_zip':'proportion of a person\'s friends who are friends with each other','civic_organizations_zip':'proportion of people who are members of a civic organization'})

individual_df = individual_df.set_index('zip')

st.table(individual_df)