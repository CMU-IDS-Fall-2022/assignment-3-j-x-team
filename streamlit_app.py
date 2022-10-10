import streamlit as st
import pandas as pd
import altair as alt
import urllib.request
# import ssl
from scipy import stats
from vega_datasets import data
import numpy as np
from dataclasses import fields



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

## Add State, County, and City to the df from another csv file.

# ssl._create_default_https_context = ssl._create_unverified_context
url = urllib.request.urlopen('https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv')
city_state_county_df = pd.read_csv(url)

alt.data_transformers.disable_max_rows() #Disabling MaxRowsError to load large dataset

st.title("Social Capital Data Interaction")
@st.cache  # add caching so we load the data only once


def load_data():
    return pd.read_csv("data/social_capital_zip_coords.csv")

df = load_data()

st.write("Let's look at raw data in the Pandas Data Frame.")
# TO DO: display all rows in charts
df = df.head(200) # get the first 1000 rows to data to display charts successfully (if too large the chat fails to display)
st.write(df)
st.write("Total number of zipcodes: "+str(len(df.index)))

# change the webpage's css style to display radio buttons horizontally
# reference: https://discuss.streamlit.io/t/horizontal-radio-buttons/2114/3
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

# create radio buttons for users to select one dimension
dimension = st.radio("Select one dimension of social capital",("Economic Connectedness", "Cohesiveness", "Civic Engagement"))

# use altair to create map chart
# altair supports tooltip on datapoints, but currently doesn't support to zoom in/out a map chart
# reference: https://altair-viz.github.io/altair-tutorial/notebooks/09-Geographic-plots.html
states = alt.topo_feature(data.us_10m.url, feature='states')

# background map
background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).project('albersUsa').properties(
    width=600,
    height=400
)

map_title = dimension + " by Zipcode"
dimension_dic = {
    "Economic Connectedness": "ec_zip",
    "Cohesiveness": "clustering_zip", 
    "Civic Engagement":"volunteering_rate_zip"
    }
map_tooltip_value = dimension_dic[dimension]

st.write(str(dimension)+" is measured by "+str(dimension_dic[dimension])+", the percentage of ..")

# the data points on the map background
# TO DO: update column label names
single_brush = alt.selection_single(on='click',fields=['zip'])
multi_brush = alt.selection_multi(fields=['zip'])
points = alt.Chart(df).mark_circle().encode(
    longitude = 'lng',
    latitude = 'lat',
    size = alt.value(10),
    tooltip = ['zip', map_tooltip_value],
    color=alt.Color(map_tooltip_value, 
                    scale=alt.Scale(
                        domain=[df[map_tooltip_value].min(), df[map_tooltip_value].max()], 
                        range=['red', 'orange','yellow','green','blue'])),
).properties(
    width = 600,
    height = 400,
    title = map_title
).add_selection(single_brush)

# text to show detailed information of one zipcode
# reference: https://altair-viz.github.io/gallery/scatter_linked_table.html
zip_text = alt.Chart(df).mark_text().encode(
    y=alt.Y('row_number:O',axis=None)
).transform_window(
    row_number='row_number()'
).transform_filter(
    single_brush
).transform_window(
    rank='rank(row_number)'
).transform_filter(
    alt.datum.rank<2
)
economic_connectedness = zip_text.encode(text='ec_zip').properties(title='Economic Connectedness')
cohesiveness = zip_text.encode(text='clustering_zip').properties(title='Cohesiveness')
civic_engagement = zip_text.encode(text='volunteering_rate_zip').properties(title='Civic Engagement')

text_area = alt.hconcat(
    economic_connectedness,
    cohesiveness,
    civic_engagement
    )
map_with_text = alt.vconcat(
    background+points,
    text_area
)
st.write(map_with_text)


## Make a table that displays (for the selected zip code):
#   -zip code
#   -num_below_p50 (% of population under 50% income percentile)
#   -ec_zip (economic connectedness score)
#   -clustering_zip (proportion of a person's friends who are friends with each other)
#   -civic_organizations_zip (proportion of people who are members of a civic organization)

individual_df = df[['zip','num_below_p50','ec_zip','clustering_zip','civic_organizations_zip']]
individual_df = individual_df.rename(columns={'num_below_p50':'numer of children under 50% income percentile','ec_zip':'economic connectedness score','clustering_zip':'proportion of a person\'s friends who are friends with each other','civic_organizations_zip':'proportion of people who are members of a civic organization'})
individual_df = individual_df.set_index('zip')

## Add a column for the percentile of the following:
#   ec_zip (economic connectedness), clustering_zip (cohesiveness), and 
#   civic_organizations_zip.

# Drop all rows with NaN values to make processing easier.
individual_df = individual_df.dropna()

ec_zip_percentile_list = []

for i in individual_df['economic connectedness score']:
    percentile = stats.percentileofscore(individual_df['economic connectedness score'], i, kind='strict')
    percentile_val = round(percentile, 2)
    ec_zip_percentile_list.append(percentile_val)

individual_df['ec_zip_percentile'] = ec_zip_percentile_list

clustering_zip_list = []

for i in individual_df['proportion of a person\'s friends who are friends with each other']:
    percentile = stats.percentileofscore(individual_df['proportion of a person\'s friends who are friends with each other'], i, kind='strict')
    percentile_val = round(percentile, 2)
    clustering_zip_list.append(percentile_val)

individual_df['clustering_zip_percentile'] = clustering_zip_list

civic_organizations_list = []

for i in individual_df['proportion of people who are members of a civic organization']:
    percentile = stats.percentileofscore(individual_df['proportion of people who are members of a civic organization'], i, kind='strict')
    percentile_val = round(percentile, 2)
    civic_organizations_list.append(percentile_val)

individual_df['civic_organizations_zip_percentile'] = civic_organizations_list


st.title("Social Capital Metrics of Selected Zip Code")
#   **To Do**
#   Change the iloc to a variable set equal to the index of the zip code selected in the map.

st.table(individual_df.iloc[0:10])

## Make a bar graph that displays the selected zip code's percentile
#   for each of the 3 social capital indicators.
#   On hover, show the raw score for that indicator.
#   TO DO: find a way to connect the map chart with bar graph together. Might using brush instead of an individual data point

source = pd.DataFrame({
    'Social Capital Metric': ['Economic Connectedness', 'Cohesiveness', 'Civic Engagement'],
    'Percentile': [individual_df['ec_zip_percentile'].iloc[0], individual_df['clustering_zip_percentile'].iloc[0], individual_df['civic_organizations_zip_percentile'].iloc[0]],
    'Raw Metric Score': [individual_df['economic connectedness score'].iloc[0], individual_df['proportion of a person\'s friends who are friends with each other'].iloc[0], individual_df['proportion of people who are members of a civic organization'].iloc[0]]
})

source_chart = alt.Chart(source).mark_bar().encode(
    x='Percentile:Q',
    y='Social Capital Metric:N',
    tooltip=['Raw Metric Score:Q']
).properties(
    width=600,
    height=400,
    title='Social Capital Percentiles for Selected Zipcode'
).interactive()

st.altair_chart(source_chart, use_container_width=True)

