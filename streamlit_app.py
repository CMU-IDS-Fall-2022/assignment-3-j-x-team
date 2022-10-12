import streamlit as st
import pandas as pd
import altair as alt
#import urllib.request
#import ssl
from scipy import stats
from vega_datasets import data
import numpy as np
from dataclasses import fields
from operator import index

## **Data Cleaning**
## Step 1: The LAT and LNG data was added to the dataframe to enable each zip code to be plotted on a map.

# sc_df = pd.read_csv("social_capital_zip.csv")
# sc_df.reset_index(inplace=True)
# sc_df.zip = sc_df.zip.astype(str)

# zip_and_coords = pd.read_table("US Zip Codes from 2013 Government Data")
# zip_and_coords.rename(columns={"ZIP,LAT,LNG": "zip"}, inplace=True)
# zip_and_coords = zip_and_coords['zip'].str.split(',', expand=True)
# zip_and_coords.rename(columns={0: "zip", 1: "lat", 2: "lng"}, inplace=True)

# Merge the two dataframes
# sc_df = pd.merge(sc_df, zip_and_coords, on='zip')
# sc_df.to_csv("social_capital_zip_coords.csv")

# Load the resulting dataframe.
@st.cache  # add caching so we load the data only once
def load_data():
    return pd.read_csv("data/social_capital_zip_coords.csv")

df = load_data()

# Drop unnecessary columns 'County', 'Unnamed: 0', and 'index'.
df = df.drop('county', axis=1)
df = df.drop('Unnamed: 0', axis=1)
df = df.drop('index', axis=1)

# Make the zip code column a string to enable a later merge on the zip code column.
df['zip'] = df['zip'].astype(str)
df = df.dropna()

## Step 2: Import a dataframe that contains the state, city, and county of each zip code.
#ssl._create_default_https_context = ssl._create_unverified_context
#url = urllib.request.urlopen('https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv')
city_state_df = pd.read_csv('https://raw.githubusercontent.com/scpike/us-state-county-zip/master/geo-data.csv')

city_state_df.rename(columns={'zipcode': 'zip'}, inplace=True)


## Step 3: Merge the two dataframes.  City, country, State, state_abbr, and state_fips are added as columns in the df.
df = pd.merge(df, city_state_df, on='zip')
df['Location'] = df['state_abbr']+", "+df['county']+", "+df['city']


## Step 4: Add a column for each percentile of each social capital dimension.
ec_zip_percentile_list = []

for i in df['ec_zip']:
    percentile = stats.percentileofscore(df['ec_zip'], i, kind='strict')
    percentile_val = round(percentile, 2)
    ec_zip_percentile_list.append(percentile_val)

df['Economic Connectedness Percentile'] = ec_zip_percentile_list

clustering_zip_list = []

for i in df['clustering_zip']:
    percentile = stats.percentileofscore(df['clustering_zip'], i, kind='strict')
    percentile_val = round(percentile, 2)
    clustering_zip_list.append(percentile_val)

df['Clustering Percentile'] = clustering_zip_list

volunteering_zip_list = []

for i in df['volunteering_rate_zip']:
    percentile = stats.percentileofscore(df['volunteering_rate_zip'], i, kind='strict')
    percentile_val = round(percentile, 2)
    volunteering_zip_list.append(percentile_val)

df['Volunteering Rate Percentile'] = volunteering_zip_list

## Step 5: 
# Make 3 new columns that describe the meaning of each social capital metric. 
# The value of each column is the same for each row.
# The meaning of each metric will be displayed to the user on hover.
df['zip_meaning'] = 'The zipcode you selected from the mao above'
df['location_meaning'] = "Location of the zipcode, formatted in State, County, City"
df['num_below_p50_meaning'] = "Number of children with below-national-median parental household income."
df['population_2018_meaning'] = 'Population in 2018'
df['ec_zip_meaning'] = "Two times the share of high-SES friends among low-SES individuals, averaged over all low-SES individuals in the ZIP code"
df['clustering_zip_meaning'] = 'The average fraction of an individual\s friend pairs who are also friends with each other'
df['volunteering_zip_meaning'] = 'The percentage of Facebook users who are members of a \'volunteering\' or \'activism\' group'


# Step 6: Remove remaining unnecessary columns from the dataframe.
df = df.drop(columns=['ec_se_zip','nbhd_ec_zip','ec_grp_mem_zip','ec_high_zip','ec_high_se_zip','nbhd_ec_high_zip','ec_grp_mem_high_zip','exposure_grp_mem_zip','exposure_grp_mem_high_zip', 'nbhd_exposure_zip',
       'bias_grp_mem_zip', 'bias_grp_mem_high_zip', 'nbhd_bias_zip', 'nbhd_bias_high_zip',
       'support_ratio_zip', 'state_fips'])

df = df.rename(columns={
    'num_below_p50': 'Number Below Median',
    'pop2018': 'Population in 2018',
    'ec_zip': 'Economic Connectedness',
    'clustering_zip': 'Clustering',
    'volunteering_rate_zip': 'Volunteering Rate',
})

## **Build Interaction**
alt.data_transformers.disable_max_rows() #Disabling MaxRowsError to load large dataset

st.title("What are the features of the geographic distribution of social capital metrics?")
st.write("Data source: [Social Capital II: Determinants of Economic Connectedness](https://opportunityinsights.org/paper/social-capital-ii-determinants-of-economic-connectedness/)")

show_raw_data = st.checkbox("Click to show raw data")

if show_raw_data:
    st.write("Total number of zipcodes: "+str(len(df.index)))
    st.write(df[["zip", "Location", "Number Below Median", "Population in 2018", "Economic Connectedness", "Clustering", "Volunteering Rate"]])

# change the webpage's css style to display radio buttons horizontally
# reference: https://discuss.streamlit.io/t/horizontal-radio-buttons/2114/3
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

## Part 1: Map Chart to show each zipcode as one point
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
    "Economic Connectedness": "Economic Connectedness",
    "Cohesiveness": "Clustering", 
    "Civic Engagement":"Volunteering Rate"
}

descp_dict = { "Economic Connectedness": "two times the share of high-SES friends among low-SES individuals, averaged over all low-SES individuals in the ZIP code",
    "Cohesiveness": "the average fraction of an individual\s friend pairs who are also friends with each other", 
    "Civic Engagement": " the percentage of Facebook users who are members of a 'volunteering' or 'activism' group"
}
description = dimension_dic[dimension]

st.write(str(dimension)+" is measured by "+str(dimension_dic[dimension])+", "+str(descp_dict[dimension]))

# the data points on the map background
# TO DO: update column label names
single_brush = alt.selection_single(on='click',fields=['zip'])
multi_brush = alt.selection_multi(fields=['zip'])
points = alt.Chart(df).mark_circle().encode(
    longitude = 'lng',
    latitude = 'lat',
    size = alt.value(10),
    tooltip = ['zip', dimension_dic[dimension]],
    color=alt.Color(dimension_dic[dimension], 
                    scale=alt.Scale(
                        domain=[df[dimension_dic[dimension]].min(), df[dimension_dic[dimension]].max()], 
                        range=['red', 'orange','yellow','green','blue'])),
).properties(
    width = 600,
    height = 400,
    title = map_title
).add_selection(single_brush)


## Part 2: Table that displaying specific info for the selected zip code:
#   -location
#   -num_below_p50 (% of population under 50% income percentile)
#   -ec_zip (economic connectedness score)
#   -clustering_zip (proportion of a person's friends who are friends with each other)
#   -civic_organizations_zip (proportion of people who are members of a civic organization)
st.title("Social Capital Metrics of Selected Zip Code")

# text to show detailed information of one zipcode
# reference: https://altair-viz.github.io/gallery/scatter_linked_table.html
zip_text = alt.Chart(df).mark_text(
    #align='right',
).encode(
    x=alt.X(axis=None),
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
zipcode = zip_text.encode(text='zip', tooltip='zip_meaning').properties(title="Zipcode")
location = zip_text.encode(text='Location', tooltip='location_meaning').properties(title='Location (State, County, City)')
num_below = zip_text.encode(text='Number Below Median', tooltip='num_below_p50_meaning').properties(title='Number Below Median')
population = zip_text.encode(text='Population in 2018', tooltip='population_2018_meaning').properties(title='Population in 2018')

economic_connectedness = zip_text.encode(text='Economic Connectedness', tooltip='ec_zip_meaning').properties(title='Economic Connectedness')
cohesiveness = zip_text.encode(text='Clustering',tooltip='clustering_zip_meaning').properties(title='Cohesiveness')
civic_engagement = zip_text.encode(text='Volunteering Rate', tooltip='volunteering_zip_meaning').properties(title='Civic Engagement')


basic_info = alt.hconcat(
    zipcode,
    location,
    num_below,
    population,
)

# basic_info = alt.HConcatChart(
#     hconcat = [zipcode, location, num_below, population],
#     autosize = 'fit'
# )


social_capital_metric = alt.hconcat(
    economic_connectedness,
    cohesiveness,
    civic_engagement
)

text_area = alt.vconcat(
    basic_info,
    social_capital_metric,
    center = True
)

metrics = ['Economic Connectedness Percentile', 'Clustering Percentile','Volunteering Rate Percentile']

bar = alt.Chart(df).transform_fold(
    fold = metrics
).mark_bar().encode(
    x = alt.X('key:N', 
        title = "Social Capital Metrics", 
        axis=alt.Axis(labelAngle=0),
        sort = metrics),
    y = alt.Y('value:Q',
        title = "Percentile",
        #scale=alt.Scale(domain=[0, 1]),
        ), 
    color = alt.Color('key:N',sort = metrics),
    tooltip ='value:Q',
).properties(
    width=600,
    height=400,
    title='Social Capital Percentiles for Selected Zipcode'
).transform_filter(single_brush)

map_with_text = alt.vconcat(
    background+points,
    text_area,
    bar
)
st.write(map_with_text)