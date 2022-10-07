from turtle import back
import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

st.title("Social Capital Data Interaction.")

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

# altair way to create map chart
# altair supports tooltip on datapoints, but currently doesn't support to zoom in/out a map chart
# reference: https://altair-viz.github.io/altair-tutorial/notebooks/09-Geographic-plots.html
states = alt.topo_feature(data.us_10m.url, feature='states')

background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).project('albersUsa').properties(
    width=500,
    height=300
)

points = alt.Chart(df).mark_circle().encode(
    longitude = 'lng',
    latitude = 'lat',
    size = alt.value(10),
    tooltip = ['zip','lat','lng','ec_zip']
).interactive()

st.write(background+points)