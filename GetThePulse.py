import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.graph_objects as go
from PIL import Image

payment_category_data = pd.read_csv('C:/Users/Admin/Desktop/notent/aggr_transaction1.csv')
transaction_analysis_data = pd.read_csv('C:/Users/Admin/Desktop/notent/map_transaction1.csv')
user_activity_data = pd.read_csv("C:/Users/Admin/Desktop/notent/map_user1.csv")
top_transaction_data = pd.read_csv('C:/Users/Admin/Desktop/notent/top_transaction1.csv')
top_user_activity_data = pd.read_csv('C:/Users/Admin/Desktop/notent/top_user1.csv')

# Extracting the regions data
payment_category_data_Locations = payment_category_data['state'].unique()
transaction_analysis_data_regions = transaction_analysis_data['big_area'].unique()
user_activity_data_locations = user_activity_data['big_area'].unique()
top_transaction_data_states = top_transaction_data[top_transaction_data['big_area'] != 'India']['big_area'].unique()
top_user_activity_data_states = top_user_activity_data[top_user_activity_data['big_area'] != 'India'][
    'big_area'].unique()

app_mode = st.sidebar.selectbox(
    "**Select the metrics you are interested in, and your insights are just a couple of clicks away**",
    ['Home', 'Payment category Analysis', 'Map Transaction Analysis', 'User Activity',
     'Top Locations based on Transaction data',
     'Top Location based on User activity data']
)

st.session_state.app_mode = app_mode
st.sidebar.markdown(f"**Selected Page:** {app_mode}")

if app_mode == 'Home':
    st.title("Phonepe Pulse data Visualization and Exploration")
    st.markdown(
        "Welcome to PhonePe Pulse Data Visualization. This app provides insightful analysis and visualization of "
        "transaction data from the PhonePe digital payment platform."
    )
    img = Image.open('C:/Users/Admin/Desktop/images/phol.png')
    st.image(img, width=550)
    st.write('\n')
    st.markdown("<h2>How could this app be useful </h2>", unsafe_allow_html=True)
    st.write('\n')
    st.write(
        "The primary objective of this project is to analyze and visualize the five-year transaction data (2018-2022) obtained from PhonePe's GitHub repository.The project starts by cloning the data from the GitHub repository and reading it using the os package.The data is then analyzed and visualized using the plotly and streamlit packages. The data is presented in various graph formats such as aggregated transactions, users, top transactions, and users for state, pincode, and district. The streamlit webpage allows the user to interact with the data and explore the different graphs, allowing for a deeper understanding of the trends and patterns within the data.Overall, this project provides a comprehensive analysis and visualization of PhonePe's transaction data, allowing for insights into the growth and trends of digital payments in India over the past five years.")



# payment category analysis
elif app_mode == 'Payment category Analysis':
    st.markdown("<h2>Payment category Analysis</h2>", unsafe_allow_html=True)
    st.write('\n')
    selected_region = st.selectbox("**Select region**", payment_category_data_Locations)
    st.write('\n')
    selected_year = st.radio("**Select year**", [2018, 2019, 2020, 2021, 2022])
    st.write('\n')
    selected_transaction_category = st.radio("**Select transaction category**",
                                             ['Total_Transaction_Count', 'Total_Transaction_Amount'])
    st.write('\n')

    if st.button("Submit"):
        grouped_data = payment_category_data.groupby('Payment_Category ')[selected_transaction_category].sum()
        filtered_data = payment_category_data[
            (payment_category_data['year'] == selected_year) & (payment_category_data['state'] == selected_region)]
        grouped_data = filtered_data.groupby('Payment_Category ')[selected_transaction_category].sum()
        payment_category = grouped_data.index
        total_transaction = grouped_data.values
        colors = ['blue', 'violet', 'green', 'orange', 'red']
        fig = go.Figure(data=[go.Bar(x=payment_category, y=total_transaction, marker=dict(color=colors))])

        fig.update_layout(
            title=f"Payment Categories in {selected_region} in the year {selected_year} based on the {selected_transaction_category}",
            xaxis_title="Payment Category",
            yaxis_title=f"{selected_transaction_category}"
        )
        st.plotly_chart(fig)



# Transaction Analysis
elif app_mode == 'Map Transaction Analysis':
    st.markdown("<h2>Map Transaction Analysis</h2>", unsafe_allow_html=True)
    st.write('\n')
    selected_region = st.selectbox("**Select region**", transaction_analysis_data_regions)
    st.write('\n')
    selected_year = st.radio("**Select year**", [2018, 2019, 2020, 2021, 2022])
    st.write('\n')

    if st.button("Submit"):
        places_lookup = {}
        for i in pd.read_csv("C:/Users/Admin/Desktop/notent/all_locs_lat_lng_5.csv").iloc:
            places_lookup[i["area"]] = (i["lat"], i["lng"])

        gdf_region = gpd.read_file("C:/Users/Admin/Desktop/notent/Indian_States.txt")
        filtered_data = transaction_analysis_data[
            (transaction_analysis_data['big_area'] == selected_region) & (
                        transaction_analysis_data['year'] == selected_year)
            ]
        india_map_data = []
        for _, row in filtered_data.iterrows():
            location_key = row["small_area"] + ", " + row["big_area"]
            if location_key in places_lookup:
                india_map_data.append(
                    [places_lookup[location_key][0], places_lookup[location_key][1], row["small_area"],
                     row["Total_no_transactions"], row["Total_transaction_value"]]
                )
        india_map_pd = pd.DataFrame(
            india_map_data,
            columns=["lat", "lng", "area", "total_transaction", "total_value"]
        )

        gdf_region["geometry"] = (
            gdf_region.to_crs(gdf_region.estimate_utm_crs()).simplify(5000).to_crs(gdf_region.crs))

        fig = px.choropleth_mapbox(
            gdf_region,
            geojson=gdf_region.__geo_interface__,
            color="NAME_1"
        ).update_traces(showlegend=False)

        fig.add_traces(
            px.scatter_mapbox(
                india_map_pd, lat="lat", lon="lng", hover_data=["area", "total_transaction", "total_value"]
            ).data
        )

        fig.update_layout(
            mapbox=dict(
                style="carto-positron",
                zoom=3,
                center=dict(lat=india_map_pd["lat"].mean(), lon=india_map_pd["lng"].mean()),
            )
        )
        st.plotly_chart(fig)


# User Activity
elif app_mode == 'User Activity':
    st.markdown("<h2>User Activity</h2>", unsafe_allow_html=True)
    st.write('\n')
    selected_region = st.selectbox("**Select Location**", user_activity_data_locations)
    st.write('\n')
    selected_year = st.radio("**Select year**", [2018, 2019, 2020, 2021, 2022])
    st.write('\n')
    if st.button("Submit"):
        filtered_data = user_activity_data[
            (user_activity_data['year'] == selected_year) & (user_activity_data['big_area'] == selected_region)]
        yearly_totals = filtered_data.groupby('small_area')[['registeredUsers', 'appOpens']].sum().reset_index()
        data = pd.melt(yearly_totals, id_vars='small_area', var_name='Metric', value_name='Count')
        fig = px.line(data, x='small_area', y='Count', color='Metric',
                      labels={'small_area': 'Small Area', 'Count': 'Count'},
                      title=f" Total Registered Users and App Opens in {selected_region} in the Year {selected_year}")
        fig.update_layout(xaxis_tickangle=-90)
        st.plotly_chart(fig)


# Top Locations based on Transaction data
elif app_mode == 'Top Locations based on Transaction data':
    st.markdown("<h2>Top Locations based on Transaction data</h2>", unsafe_allow_html=True)
    st.write('\n')
    selected_year = st.selectbox("**Select year**", [2018, 2019, 2020, 2021, 2022])
    st.write('\n')
    selected_quarter = st.radio("**Select Quarter**", [1, 2, 3, 4])
    st.write('\n')
    selected_location = st.selectbox("**Select region**", ['India'] + list(top_transaction_data_states))
    st.write('\n')

    if selected_location == 'India':
        selected_location_type = st.radio("**Select Location type**", ['state', 'districts', 'pincodes'])
    else:
        selected_location_type = st.radio("**Select Location type**", ['districts', 'pincodes'])

    st.write('\n')
    if st.button("Submit"):
        filtered_data = top_transaction_data[
            (top_transaction_data['year'] == selected_year) &
            (top_transaction_data['quarter'] == selected_quarter) &
            (top_transaction_data['big_area'] == selected_location) &
            (top_transaction_data['Location type'] == selected_location_type)
            ]
        top_10_locations = filtered_data.head(10)
        location_labels = top_10_locations.apply(lambda x: f'{x["rank"]}. {x["small_area"]}', axis=1)
        location_counts = top_10_locations['Total_transaction_count']

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(location_counts, labels=location_labels, autopct='%1.1f%%')
        ax.set_title(f'Top 10 {selected_location_type.capitalize()} in {selected_location}')
        st.pyplot(fig)


# Top Location based on User activity data
elif app_mode == 'Top Location based on User activity data':
    st.markdown("<h2>Top Locations based on User activity data</h2>", unsafe_allow_html=True)
    st.write('\n')
    selected_year = st.selectbox("**Select year**", [2018, 2019, 2020, 2021, 2022])
    st.write('\n')
    selected_quarter = st.radio("**Select Quarter**", [1, 2, 3, 4])
    st.write('\n')
    selected_location = st.selectbox("**Select region**", ['India'] + list(top_user_activity_data_states))
    st.write('\n')

    if selected_location == 'India':
        selected_location_type = st.radio("**Select Location type**", ['state', 'districts', 'pincodes'])
    else:
        selected_location_type = st.radio("**Select Location type**", ['districts', 'pincodes'])
    st.write('\n')

    if st.button("Submit"):
        filtered_data = top_user_activity_data[
            (top_user_activity_data['year'] == selected_year) &
            (top_user_activity_data['quarter'] == selected_quarter) &
            (top_user_activity_data['big_area'] == selected_location) &
            (top_user_activity_data['Location type'] == selected_location_type)
            ]

        fig = px.pie(
            filtered_data, values='registeredUsers', names='small_area',
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        fig.update_layout(
            title=f"Registered Users Distribution and app opens in {selected_location_type} of {selected_location} in {selected_year} Quarter {selected_quarter}, "
        )

        st.plotly_chart(fig)
