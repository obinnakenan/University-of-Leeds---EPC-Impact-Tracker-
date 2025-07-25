import streamlit as st
import plotly.express as px
import plotly.graph_objects as go  
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
import base64
import numpy as np
import json
import re

# --- Page Config ---
st.set_page_config(
    page_title="EPC Impact Tracker: Housing, Inequality & Environment",
    layout="wide",
    page_icon="🏡"
)

# --- Function to convert image files to base64 ---
def load_base64_image(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return ""

# --- Load and encode images ---
bg_image = load_base64_image(r"Background image.png")
logo = load_base64_image(r"logo.png")
crest = load_base64_image(r"crest.png")
link_to_paper = "https://www.sciencedirect.com/science/article/pii/S0140988323005406"




# --- Handle intro screen logic ---
query_params = st.query_params

# If button clicked, set session_state and redirect (removes query param)
if query_params.get("show_app") == "1":
    st.session_state["show_app"] = True
    st.query_params.clear()  # Clears the query parameters from the URL
    st.rerun()

# Default: if session_state not set, show intro
if "show_app" not in st.session_state:
    st.session_state["show_app"] = False


# --- INTRO SCREEN ---
if not st.session_state.get("show_app", False):
    st.markdown(f"""
        <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-attachment: scroll;
                height: 100vh;
                margin: 0;
                padding: 0;
            }}

            .transparent-button {{
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 16px;
                color: black;
                cursor: pointer;
                transition: background-color 0.3s ease;
                z-index: 10;
            }}

            .transparent-button:hover {{
                background-color: rgba(255, 255, 255, 0.6);
            }}

            .footer {{
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 10px 0 20px;
                background-color: transparent;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 100;
                width: 100%;
            }}

            .footer .footer-content {{
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 30px;
                text-align: center;
                flex-wrap: wrap;
            }}

            .footer img {{
                height: 30px;
            }}

            .footer .footer-link {{
                font-size: 10px;
                color: black;
                text-decoration: none;
                display: inline-block;
                padding: 4px 8px;
                background-color: transparent;
                cursor: pointer;
                z-index: 1000;
                position: relative;
            }}

            .footer .footer-link:hover {{
                text-decoration: underline;
                background-color: rgba(0, 0, 0, 0.05);
            }}
        </style>

        <div style='
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding-top: 50vh;
            position: relative;
            z-index: 0;
        '>
            <form method="get">
                <input type="hidden" name="show_app" value="1" />
                <button type="submit" class="transparent-button">EXPLORE THE DATA</button>
            </form>
        </div>

        <div class="footer">
            <div class="footer-content">
                <img src="data:image/png;base64,{logo}" alt="Logo">
                <img src="data:image/png;base64,{crest}" alt="Crest">
                <a href="{link_to_paper}" target="_blank" class="footer-link">
                    Regional persistence of the energy efficiency gap <br>
                    (Energy Economics Journal 2023)
                </a>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.stop()

# --- MAIN APP CONTENT ---
if st.session_state.show_app:
    st.markdown("""
        <style>
            .stApp {
                background: none;
            }
            .footer {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)



# --- Banner and Title ---
st.image(r"Banner logo.png",use_container_width=True)
# st.markdown("### EPC Impact Tracker: Housing, Inequality & Environment")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "*Energy Efficiency Gap*", "*Energy Efficiency & Enviromental Impact*", "*Energy Ratings & Property Prices*",
    "*Regional Differences*", "*Modelling*","*Sustainability Insights*"
])



# --- Load and clean data ---
def load_data():
    df = pd.read_csv(r"Merged_yorkshire_humber_EPC.csv")
    # rename of columns
    df.rename(columns={'CURRENT_ENER_EFFICIENCY':'Current Energy Efficiency','POTENTIAL_ENERGY_EFFICIENCY':'Potential Energy Efficiency',
                       'CO2_EMISS_CURR':'Current CO2 Emission',
                       'CO2_EMISS_POTENT':'Potential CO2 Emission'},inplace=True)
    # convet to numerical data type
    df['Current Energy Efficiency'] = pd.to_numeric(df['Current Energy Efficiency'], errors='coerce')
    df['Potential Energy Efficiency'] = pd.to_numeric(df['Potential Energy Efficiency'], errors='coerce')
    df['Current CO2 Emission'] = pd.to_numeric(df['Current CO2 Emission'], errors='coerce')
    df['Potential CO2 Emission'] = pd.to_numeric(df['Potential CO2 Emission'], errors='coerce')
    df['ENV_IMP_CURR'] = pd.to_numeric(df['ENV_IMP_CURR'], errors='coerce')
    df['ENV_IMP_POTENT'] = pd.to_numeric(df['ENV_IMP_POTENT'], errors='coerce')
    df['ENERGY_CONSUM_CURR'] = pd.to_numeric(df['ENERGY_CONSUM_CURR'], errors='coerce')
    df['ENERGY_CONSUM_POTEN'] = pd.to_numeric(df['ENERGY_CONSUM_POTEN'], errors='coerce')
    df['Region name'] = df['Region name'].fillna('Unknown')
    df['Price actual'] = pd.to_numeric(df['Price actual'], errors='coerce')
    # computes the energy gap by subtracting the Potential and Current energy potential
    df['Energy Gap'] = df['Potential Energy Efficiency']  - df['Current Energy Efficiency']
    # computes the CO2 gap by subtracting the Potential and Current CO2 potential
    df['CO2 Gap'] = df['Potential CO2 Emission']  - df['Current CO2 Emission']
    # extract the year from 'Lodgement_date'   
    df['INSPECTION_DATE'] = pd.to_datetime(df['INSPECTION_DATE'],errors='coerce')
    df['Year'] = df['INSPECTION_DATE'].dt.year
    df['Year'] = df['Year'].astype('Int32')
    return df

df = load_data()


with tab1:
    st.write(""" """)

    # View mode
    filter_mode = st.radio(
        "Select Data View Mode:",
        ["Rental", "Sales"],
        horizontal=True
    )

    if filter_mode == "Rental":
        with st.container():
            col_filters, col_main = st.columns([1, 2])

            with col_filters:
                # Three-column layout
                Region_filter, County_area_Filter, Post_town_filter = st.columns(3, gap="medium")

                with Region_filter:
                    st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Region:</div>', unsafe_allow_html=True)
                    select_yorkshire = st.checkbox(
                        "**Yorkshire and The Humber**",
                        value=True,
                        key="yorkshire_chk"
                    )

                if not select_yorkshire:
                    st.error("No data selected. Please tick 'Yorkshire and The Humber' to proceed.")
                    st.stop()

                # Filter Yorkshire data
                yorkshire_df = df[df['Region name'] == 'Yorkshire and The Humber']

                with County_area_Filter:
                    st.markdown('<div style="margin-bottom: 0; font-weight: bold;">County area(s):</div>', unsafe_allow_html=True)
                    county_options = ["All"] + sorted(yorkshire_df['County area name'].dropna().unique())
                    selected_county = st.selectbox(
                        "County Area",
                        options=county_options,
                        key="county_sel",
                        label_visibility="collapsed"
                    )

                with Post_town_filter:
                    st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Post town(s):</div>', unsafe_allow_html=True)

                    if selected_county == "All":
                        towns = sorted(yorkshire_df['Post town name'].dropna().unique())
                    else:
                        towns = sorted(
                            yorkshire_df[yorkshire_df['County area name'] == selected_county]['Post town name'].dropna().unique()
                        )

                    town_options = ["All"] + towns
                    selected_town = st.selectbox(
                        "Post Town",
                        options=town_options,
                        key="town_sel",
                        label_visibility="collapsed"
                    )

                # Filtering based on selection
                filtered_df = yorkshire_df.copy()
                if selected_county != "All":
                    filtered_df = filtered_df[filtered_df['County area name'] == selected_county]
                if selected_town != "All":
                    filtered_df = filtered_df[filtered_df['Post town name'] == selected_town]

                if filtered_df.empty:
                    st.warning("No records matched your filters. Adjust your selections.")
                else:
                    st.success(f"{len(filtered_df)} records matched your filters.")

        with col_main:
            if filtered_df.empty:
                st.info("Adjust filters on the left to see charts.")

    with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    # === 1. Energy Efficiency Distribution ===
                    st.markdown("##### Current vs Potential Energy Efficiency (with Energy Gap Trend)")
                    # Melt the dataframe for histogram
                    eff = filtered_df[['Current Energy Efficiency', 'Potential Energy Efficiency']].melt(
                        var_name="Type", value_name="Efficiency"
                    )

                    # Create histogram figure
                    fig1 = px.histogram(
                        eff, x='Efficiency', color='Type',
                        barmode='overlay', nbins=30,
                        opacity=0.6  # Ensure line is visible
                    )

                    # Energy Gap trend as histogram-style line
                    energy_gap_vals = filtered_df['Energy Gap'].dropna()
                    hist_vals, bin_edges = np.histogram(energy_gap_vals, bins=30)
                    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

                    gap_line = go.Scatter(
                        x=bin_centers,
                        y=hist_vals,
                        mode='lines',
                        name='Energy Gap Trend',
                        line=dict(color='purple', width=2)
                    )

                    # Add the trend line
                    fig1.add_trace(gap_line)

                    # Update layout
                    fig1.update_layout(
                        # title="Current vs Potential Energy Efficiency (with Energy Gap Trend)",
                        hovermode='x',
                        yaxis=dict(title='Count')
                    )


                    # --- Dynamic NLP Summary Based on Filtered Data ---
                    current_avg = filtered_df['Current Energy Efficiency'].mean()
                    potential_avg = filtered_df['Potential Energy Efficiency'].mean()
                    energy_gap_avg = filtered_df['Energy Gap'].mean()
                    gap_range = filtered_df['Energy Gap'].max() - filtered_df['Energy Gap'].min()
                    location_focus = selected_town if selected_town != "All" else selected_county

                    summary_text = f"""

                    The average **Current Energy Efficiency** is **{current_avg:.1f}**, while the **Potential Efficiency** could reach **{potential_avg:.1f}**, 
                    indicating an average **Energy Gap** of **{energy_gap_avg:.1f}**. This suggests that properties in {location_focus} Local Authority District have a moderate opportunity to improve their energy performance.
                    """

                    st.markdown(summary_text)



                    # Display the chart
                    st.plotly_chart(fig1, use_container_width=True)



                with col2:
                    # --- Load GeoJSON file ---
                    with open(r"Local_Authority_Districts_December_2021_UK_BUC_2022_3960795867023731705.geojson") as f:
                        geojson_data = json.load(f)

                    # --- Calculate color scale range ---
                    gap_min = filtered_df['Energy Gap'].min()
                    gap_max = filtered_df['Energy Gap'].max()
                    color_range = [gap_min, gap_max]
                    color_scale = "plasma"

                    # --- Filter rows with valid coordinates and energy gap ---
                    map_df = filtered_df.dropna(subset=['Latitude', 'Longitude', 'Energy Gap'])

                    if not map_df.empty:
                        # --- Compute map center based on available coordinates ---
                        center_lat = map_df['Latitude'].mean()
                        center_lon = map_df['Longitude'].mean()

                        # --- Plot choropleth map ---
                        fig = px.choropleth_mapbox(
                            map_df,
                            geojson=geojson_data,
                            locations='LAD_NM',
                            featureidkey="properties.LAD21NM",  # <- Match to your GeoJSON property
                            color='Energy Gap',
                            color_continuous_scale=color_scale,
                            range_color=color_range,
                            mapbox_style="carto-positron",
                            zoom=6,
                            center={"lat": center_lat, "lon": center_lon},
                            opacity=0.5,
                            hover_name='LAD_NM'
                        )

                       
                        fig.update_layout(title_text=f"Energy Gap by {selected_town} Local Authority District",
                                          margin={"r":0, "t":50, "l":0, "b":0})
                        col2.plotly_chart(fig, use_container_width=True)
                    else:
                        col2.warning("No data to plot for the selected filters.")

                


                with st.container():
                    st.markdown(f"""
                        ##### Trends in Average Energy Gap by Year""")
                    # Get last 5 years
                    available_years = sorted(filtered_df['Year'].dropna().unique())
                    last_five_years = available_years[-15:]

                    # Show checkboxes for each year
                    st.markdown("**Select year(s) to display:**")
                    year_cols = st.columns(len(last_five_years))
                    selected_years = []

                    for i, year in enumerate(last_five_years):
                        if year_cols[i].checkbox(str(year), value=True,key=f"year_checkbox_{year}"):
                            selected_years.append(year)

                    # Plot if any year is selected
                    if selected_years:
                        df_trend = (
                            filtered_df[filtered_df['Year'].isin(selected_years)]
                            .groupby('Year')['Energy Gap']
                            .mean()
                            .reset_index()
                        )

                        fig_trend = px.line(
                            df_trend,
                            x='Year',
                            y='Energy Gap',
                            markers=True,
                            # title="Average Energy Gap by Year",
                            labels={'Energy Gap': 'Average Energy Gap', 'Year': 'Year'}
                        )

                        # Set line color to purple
                        fig_trend.update_traces(line=dict(color='purple'))

                        fig_trend.update_layout(
                            hovermode='x unified',
                            xaxis=dict(dtick=1)
                        )


                    if not df_trend.empty:
                        start_year = df_trend['Year'].min()
                        end_year = df_trend['Year'].max()
                        gap_start = df_trend[df_trend['Year'] == start_year]['Energy Gap'].values[0]
                        gap_end = df_trend[df_trend['Year'] == end_year]['Energy Gap'].values[0]
                        gap_change = gap_end - gap_start

                        trend_direction = "increased" if gap_change > 0 else "decreased" if gap_change < 0 else "remained stable"

                        st.markdown(f"""
                        Over the selected years, the **average energy gap** has **{trend_direction}** from **{gap_start:.1f}** in **{start_year}** to **{gap_end:.1f}** in **{end_year}**.
                        This suggests that energy efficiency has **{"worsened" if gap_change > 0 else "improved" if gap_change < 0 else "not changed significantly"}** over time across the selected region.
                        This trend helps to evaluate the **impact of policy changes**, **renovation efforts**, or **market dynamics** affecting energy performance.
                        """)



                        st.plotly_chart(fig_trend, use_container_width=True)
                    else:
                        st.info("Please select at least one year to view the trend.")





                # === 2. Area-Level Comparison (County or Post Town) ===
                if selected_county == "All":
                    group_level = "County area name"
                else:
                    group_level = "Post town name"

                area_avg = (
                    filtered_df
                    .groupby(group_level)['Current Energy Efficiency']
                    .mean()
                    .reset_index()
                    .dropna()
                )

                fig3 = px.bar(
                    area_avg, 
                    x='Current Energy Efficiency', 
                    y=group_level,
                    orientation='h', 
                    labels={'Current Energy Efficiency': 'Avg Efficiency', group_level: 'Area'},
                    title=f"Average Energy Efficiency by {group_level.replace('_', ' ').title()}"
                )
                st.plotly_chart(fig3, use_container_width=True)


                # === 4. Top 10 Least Efficient ===
                st.markdown("##### Top 10 Least Efficient Properties")
                least10 = filtered_df.nsmallest(10, 'Current Energy Efficiency')
                st.dataframe(
                    least10[[
                        'Address', 'Region name',
                        'Current Energy Efficiency', 'Potential Energy Efficiency'
                    ]]
                )



                # === 5. Energy Gap by Property Type
                st.markdown("##### Avg Energy Gap by Property Type")
                gap_by_type = filtered_df.groupby('PROPERTY_TYPE')['Energy Gap'].mean().reset_index().dropna()
                fig_gap = px.bar(gap_by_type, x='PROPERTY_TYPE', y='Energy Gap')
                # , title="Avg Energy Gap by Property Type")
                st.plotly_chart(fig_gap, use_container_width=True)


                # === 6. Efficiency & CO₂ by Property Type ===
                st.markdown("##### Efficiency and CO₂ by Property Type")
                ptype = (
                    filtered_df
                    .groupby('PROPERTY_TYPE')[['Current Energy Efficiency', 'Current CO2 Emission']]
                    .mean().dropna().reset_index()
                )
                fig_pt = px.bar(
                    ptype.melt(id_vars='PROPERTY_TYPE'),
                    x='PROPERTY_TYPE', y='value', color='variable',
                    barmode='group',
                    labels={"value": "Score / Emission", "variable": "Metric"}
                )
                st.plotly_chart(fig_pt, use_container_width=True)

                best = ptype.nlargest(1, 'Current Energy Efficiency').iloc[0]
                worst = ptype.nsmallest(1, 'Current Energy Efficiency').iloc[0]
                hiCO2 = ptype.nlargest(1, 'Current CO2 Emission').iloc[0]
                loCO2 = ptype.nsmallest(1, 'Current CO2 Emission').iloc[0]
                st.markdown(f"""
                - **Most energy-efficient**: {best['PROPERTY_TYPE']} ({best['Current Energy Efficiency']:.1f})
                - **Least efficient**: {worst['PROPERTY_TYPE']} ({worst['Current Energy Efficiency']:.1f})
                - **Highest CO₂**: {hiCO2['PROPERTY_TYPE']} ({hiCO2['Current CO2 Emission']:.1f} t)
                - **Lowest CO₂**: {loCO2['PROPERTY_TYPE']} ({loCO2['Current CO2 Emission']:.1f} t)
                """)



                # === 7. Efficiency by Age ===

                def classify_construction_age(value):
                    if pd.isna(value) or "NO DATA" in str(value).upper():
                        return "Unknown"
                    
                    value = str(value).replace("England and Wales: ", "").strip().lower()
                    
                    # Handle specific text cases
                    if "before 1900" in value:
                        return "Pre 1950"
                    if re.match(r"\d{4}", value):
                        year = int(value[:4])
                    elif re.match(r"\d{4}-\d{4}", value):
                        year = int(value.split('-')[0])
                    else:
                        return "Unknown"

                    # Assign to band
                    if year < 1950:
                        return "Pre 1950"
                    elif 1950 <= year <= 2011:
                        return "1950 - 2011"
                    elif year >= 2012:
                        return "2012 onwards"
                    else:
                        return "Unknown"

                # Apply to DataFrame
                filtered_df['Construction Band'] = filtered_df['CONSTRUCTION_AGE'].apply(classify_construction_age)



                # Group and visualize
                st.markdown("#### Average Efficiency by Construction Age")
                age_eff = (
                    filtered_df
                    .groupby('Construction Band')['Current Energy Efficiency']
                    .mean()
                    .dropna()
                    .reset_index()
                )

                # Sort categories
                category_order = ["Pre 1950", "1950 - 2011", "2012 onwards", "Unknown"]
                age_eff['Construction Band'] = pd.Categorical(age_eff['Construction Band'], categories=category_order, ordered=True)
                age_eff = age_eff.sort_values('Construction Band')

                # Plot
                fig_age = px.bar(
                    age_eff,
                    x='Current Energy Efficiency',
                    y='Construction Band',
                    orientation='h',
                    labels={"Current Energy Efficiency": "Avg Efficiency", "Construction Band": "Construction Age"}
                )
                st.plotly_chart(fig_age, use_container_width=True)


                # === Download button ===
                st.download_button(
                    label="📥 Download Filtered Data as CSV",
                    data=filtered_df.to_csv(index=False),
                    file_name='filtered_epc_data.csv',
                    mime='text/csv'
                )

            


                
# === Tab 2 ===
with tab2:
    st.write(""" """)

        # View mode
    filter_mode2 = st.radio(
            "Select Data View Mode:",
            ["Rental(s)", "Sales"],
            horizontal=True,
            key="radio2"
        )

    if filter_mode2 == "Rental(s)":
        with st.container():
            col_filters, col_main = st.columns([1, 2])

            with col_filters:
                    # Three-column layout
                    Region_filter, County_area_Filter, Post_town_filter = st.columns(3, gap="medium")

                    with Region_filter:
                        st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Region:</div>', unsafe_allow_html=True)
                        select_yorkshire = st.checkbox(
                            "**Yorkshire and The Humber**",
                            value=True,
                            key="yorkshire_chk2"
                        )

                    if not select_yorkshire:
                        st.error("No data selected. Please tick 'Yorkshire and The Humber' to proceed.")
                        st.stop()

                    # Filter Yorkshire data
                    yorkshire_df = df[df['Region name'] == 'Yorkshire and The Humber']

                    with County_area_Filter:
                        st.markdown('<div style="margin-bottom: 0; font-weight: bold;">County area(s):</div>', unsafe_allow_html=True)
                        county_options = ["All"] + sorted(yorkshire_df['County area name'].dropna().unique())
                        selected_county = st.selectbox(
                            "County Area",
                            options=county_options,
                            key="county_sel2",
                            label_visibility="collapsed"
                        )

                    with Post_town_filter:
                        st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Post town(s):</div>', unsafe_allow_html=True)

                        if selected_county == "All":
                            towns = sorted(yorkshire_df['Post town name'].dropna().unique())
                        else:
                            towns = sorted(
                                yorkshire_df[yorkshire_df['County area name'] == selected_county]['Post town name'].dropna().unique()
                            )

                        town_options = ["All"] + towns
                        selected_town = st.selectbox(
                            "Post Town",
                            options=town_options,
                            key="town_sel2",
                            label_visibility="collapsed"
                        )

                    # Filtering based on selection
                    filtered_df = yorkshire_df.copy()
                    if selected_county != "All":
                        filtered_df = filtered_df[filtered_df['County area name'] == selected_county]
                    if selected_town != "All":
                        filtered_df = filtered_df[filtered_df['Post town name'] == selected_town]

                    if filtered_df.empty:
                        st.warning("No records matched your filters. Adjust your selections.")
                    else:
                        st.success(f"{len(filtered_df)} records matched your filters.")

            with col_main:
                if filtered_df.empty:
                    st.info("Adjust filters on the left to see charts.")

            with st.container():
                col1, col2 = st.columns(2)
                
                with col1:
                    # === 1. CO2 Efficiency Distribution ===
                    eff = filtered_df[['Current CO2 Emission', 'Potential CO2 Emission']].melt(
                        var_name="Type", value_name="Emissions"
                    )

                    fig1 = px.histogram(
                        eff, x='Emissions', color='Type',
                        barmode='overlay', nbins=30,
                        opacity=0.6
                    )

                    CO2_gap_vals = filtered_df['CO2 Gap'].dropna()
                    hist_vals, bin_edges = np.histogram(CO2_gap_vals, bins=30)
                    bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

                    gap_line = go.Scatter(
                        x=bin_centers,
                        y=hist_vals,
                        mode='lines',
                        name='CO2 Gap Trend',
                        line=dict(color='purple', width=2)
                    )

                    fig1.add_trace(gap_line)

                    fig1.update_layout(
                        title="Current vs Potential CO2 Emission (with CO2 Gap Trend)",
                        hovermode='x',
                        yaxis=dict(title='Count')
                    )

                    st.plotly_chart(fig1, use_container_width=True)

                with col2:
                    with open(r"Local_Authority_Districts_December_2021_UK_BUC_2022_3960795867023731705.geojson") as f:
                        geojson_data = json.load(f)

                    # Filter and clean original data
                    map_df = filtered_df.dropna(subset=['Latitude', 'Longitude', 'CO2 Gap'])

                    if not map_df.empty:
                        # Get only LADs that are valid in GeoJSON
                        valid_geojson_lads = {feature["properties"]["LAD21NM"] for feature in geojson_data["features"]}
                        visible_map_df = map_df[map_df['LAD_NM'].isin(valid_geojson_lads)]

                        # === Aggregate CO2 Gap per LAD to match what's shown on the map ===
                        agg_map_df = visible_map_df.groupby('LAD_NM', as_index=False)['CO2 Gap'].mean()

                        # Center map on average coordinates of raw property data
                        center_lat = map_df['Latitude'].mean()
                        center_lon = map_df['Longitude'].mean()

                        # Define color scale based on aggregated data
                        gap_min = agg_map_df['CO2 Gap'].min()
                        gap_max = agg_map_df['CO2 Gap'].max()
                        color_range = [gap_min, gap_max]
                        color_scale = "plasma"

                        # === Plot Map ===
                        fig = px.choropleth_mapbox(
                            agg_map_df,
                            geojson=geojson_data,
                            locations='LAD_NM',
                            featureidkey="properties.LAD21NM",
                            color='CO2 Gap',
                            color_continuous_scale=color_scale,
                            range_color=color_range,
                            mapbox_style="carto-positron",
                            zoom=6,
                            center={"lat": center_lat, "lon": center_lon},
                            opacity=0.5,
                            hover_name='LAD_NM'
                        )

                        fig.update_layout(
                            title_text=f"CO₂ Gap by Local Authority District",
                            margin={"r": 0, "t": 50, "l": 0, "b": 0}
                        )
                        col2.plotly_chart(fig, use_container_width=True)

                        # === Determine dynamic location label ===
                        if selected_county == "All":
                            location_label = "Yorkshire and The Humber"
                        elif selected_town == "All":
                            location_label = selected_county
                        else:
                            location_label = selected_town

                        # === NLP Summary using same dataset as the map ===
                        if not agg_map_df.empty:
                            avg_gap = agg_map_df['CO2 Gap'].mean()
                            best_areas = agg_map_df.nsmallest(3, 'CO2 Gap')
                            worst_areas = agg_map_df.nlargest(3, 'CO2 Gap')

                            worst_text = ", ".join([f"{row['LAD_NM']} ({row['CO2 Gap']:.1f})" for _, row in best_areas.iterrows()])
                            best_text = ", ".join([f"{row['LAD_NM']} ({row['CO2 Gap']:.1f})" for _, row in worst_areas.iterrows()])

                            st.markdown(f"""
                            
                            This map illustrates the variation in **CO₂ emissions gap** the difference between current and potential CO₂ output — across **Local Authority Districts** in **{location_label}**.
                            
                            **Average CO₂ gap**: {avg_gap:.1f} units
                            **Top areas with lowest CO₂ gaps** (more efficient): {best_text}
                            **Areas with highest CO₂ gaps** (more potential for improvement): {worst_text}

                            The **CO₂ gap** indicates how much emissions can potentially be reduced through interventions such as improved insulation, modern heating systems, or renewable energy solutions.
                            These insights support more targeted **decarbonization strategies** by helping policymakers prioritize high-impact areas in {location_label}.
                            """)
                        else:
                            st.info("No matching Local Authority Districts in the map for summarization.")
                    else:
                        col2.warning("No data to plot for the selected filters.")



                # co2 gap by year
                with st.container():
                    st.markdown(f"""
                                ##### Trends in Average CO2 Gap by Year""")
                    # Get last 5 years
                    available_years = sorted(filtered_df['Year'].dropna().unique())
                    last_five_years = available_years[-15:]

                    # Show checkboxes for each year
                    st.markdown("**Select year(s) to display:**")
                    year_cols = st.columns(len(last_five_years))
                    selected_years = []

                    for i, year in enumerate(last_five_years):
                            if year_cols[i].checkbox(str(year), value=True,key=f"year2_checkbox_{year}"):
                                    selected_years.append(year)

                    
                    # Plot if any year is selected
                    if selected_years:
                        df_trend = (
                            filtered_df[filtered_df['Year'].isin(selected_years)]
                            .groupby('Year')['CO2 Gap']
                            .mean()
                            .reset_index()
                                    )
                        
                        fig_trend = px.line(
                            df_trend,
                            x='Year',
                            y='CO2 Gap',
                            markers=True,
                            # title="Average Energy Gap by Year",
                            labels={'CO2 Gap': 'Average CO2 Gap', 'Year': 'Year'}
                                    )

                        # Set line color to purple
                        fig_trend.update_traces(line=dict(color='purple'))

                        fig_trend.update_layout(
                            hovermode='x unified',
                            xaxis=dict(dtick=1)
                                    )


                        if not df_trend.empty:
                                start_year = df_trend['Year'].min()
                                end_year = df_trend['Year'].max()
                                gap_start = df_trend[df_trend['Year'] == start_year]['CO2 Gap'].values[0]
                                gap_end = df_trend[df_trend['Year'] == end_year]['CO2 Gap'].values[0]
                                gap_change = gap_end - gap_start

                                trend_direction = "increased" if gap_change > 0 else "decreased" if gap_change < 0 else "remained stable"

                                st.markdown(f"""
                                    Over the selected years, the **average CO2 gap** has **{trend_direction}** from **{gap_start:.1f}** in **{start_year}** to **{gap_end:.1f}** in **{end_year}**.
                                    This suggests that CO2 Emission has **{"worsened" if gap_change > 0 else "improved" if gap_change < 0 else "not changed significantly"}** over time across the selected region.
                                    """)



                        st.plotly_chart(fig_trend, use_container_width=True)
                    else:
                        st.info("Please select at least one year to view the trend.")    


                # === 3. Environmental Impact ===
                st.markdown("##### Environmental Impact Rating (Current vs Potential)")
                imp = filtered_df[['ENV_IMP_CURR', 'ENV_IMP_POTENT']].melt(
                    var_name="Impact Type", value_name="Impact Score"
                )
                fig_imp = px.histogram(
                    imp, x="Impact Score", color="Impact Type",
                    barmode="overlay", nbins=30
                )
                st.plotly_chart(fig_imp, use_container_width=True)
                st.markdown(
                    "Lower potential impact scores indicate opportunity for improvement."
                )      
                

                #=== 4.

                if "WALLS_DESCRIPTION" in filtered_df.columns and "CO2 Gap" in filtered_df.columns:
                    wall_df = filtered_df[["WALLS_DESCRIPTION", "CO2 Gap"]].dropna()

                    if not wall_df.empty:
                        # Aggregate average CO2 Gap by wall type
                        wall_summary = (
                            wall_df.groupby("WALLS_DESCRIPTION")
                            .agg(Avg_CO2_Gap=("CO2 Gap", "mean"), Property_Count=("CO2 Gap", "count"))
                            .reset_index()
                            .rename(columns={"WALLS_DESCRIPTION": "Wall Type"})
                        )

                        # Keep only wall types with a meaningful sample size
                        wall_summary = wall_summary[wall_summary["Property_Count"] >= 10]

                         # Round to 2 decimal places for display
                        wall_summary["Avg_CO2_Gap"] = wall_summary["Avg_CO2_Gap"].round(2)

                        # Sort by average CO2 gap
                        wall_summary = wall_summary.sort_values(by="Avg_CO2_Gap", ascending=False)

                        # Visualize
                        fig = px.bar(
                            wall_summary,
                            x="Avg_CO2_Gap",
                            y="Wall Type",
                            orientation="h",
                            text="Avg_CO2_Gap",
                            labels={"Avg_CO2_Gap": "Average CO₂ Gap", "Wall Type": "Wall Construction Type"},
                            title="Average CO₂ Gap by Wall Type (Top Emitters First)",
                        )

                        fig.update_layout(yaxis=dict(categoryorder="total ascending"))

                        st.plotly_chart(fig, use_container_width=True)

                        
                        # === NLP Summary ===
                        best_walls = wall_summary.head(1)
                        worst_walls = wall_summary.tail(1).sort_values(by="Avg_CO2_Gap")

                        best_text = ", ".join([f"{row['Wall Type']} " for _, row in best_walls.iterrows()])
                        worst_text = ", ".join([f"{row['Wall Type']} " for _, row in worst_walls.iterrows()])

                        st.markdown("""
                        This chart shows the **average CO₂ emissions gap** by wall construction type.
                         **Worst-performing wall types** (most inefficient), """ + worst_text + """ and the **Best-performing wall types** (most efficient), """ + best_text + """

                        Wall types with higher CO₂ gaps suggest a greater opportunity for **carbon savings** through improved insulation, retrofit, or structural upgrades.
                        """)
                    else:
                        st.info("No valid CO₂ gap data for wall descriptions in the current selection.")

                    




# === Tab 3 ===
with tab3:
    st.write(""" """)
    # --- Set up fallback and initial states ---
    default_color_option = "Efficiency Band"
    use_log_scale = False  # default for Rentals

    filter_mode3 = st.radio(
            "Select Data View Mode:",
            ["Rental(s)", "Sales"],
            horizontal=True,
            key="radio3"
        )
    

    if filter_mode3 == "Rental(s)":
            with st.container():
                col_filters, col_main = st.columns([1, 2])

            with col_filters:
                Region_filter, County_area_Filter, Post_town_filter = st.columns(3, gap="medium")

                with Region_filter:
                    st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Region:</div>', unsafe_allow_html=True)
                    select_yorkshire = st.checkbox(
                    "**Yorkshire and The Humber**",
                    value=True,
                    key="yorkshire_chk3"
                )

            if not select_yorkshire:
                st.error("No data selected. Please tick 'Yorkshire and The Humber' to proceed.")
                st.stop()

            yorkshire_df = df[df['Region name'] == 'Yorkshire and The Humber']

            with County_area_Filter:
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">County area(s):</div>', unsafe_allow_html=True)
                county_options = ["All"] + sorted(yorkshire_df['County area name'].dropna().unique())
                selected_county = st.selectbox(
                    "County Area",
                    options=county_options,
                    key="county_sel3",
                    label_visibility="collapsed"
                )

            with Post_town_filter:
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Post town(s):</div>', unsafe_allow_html=True)
                towns = sorted(
                    yorkshire_df[yorkshire_df['County area name'] == selected_county]['Post town name'].dropna().unique()
                ) if selected_county != "All" else sorted(yorkshire_df['Post town name'].dropna().unique())
                town_options = ["All"] + towns
                selected_town = st.selectbox(
                    "Post Town",
                    options=town_options,
                    key="town_sel3",
                    label_visibility="collapsed"
                )

            # Filtering based on selection
            filtered_df = yorkshire_df.copy()
            if selected_county != "All":
                filtered_df = filtered_df[filtered_df['County area name'] == selected_county]
            if selected_town != "All":
                filtered_df = filtered_df[filtered_df['Post town name'] == selected_town]

            if filtered_df.empty:
                st.warning("No records matched your filters. Adjust your selections.")
                st.stop()
            else:
                st.success(f"{len(filtered_df)} records matched your filters.")

            color_option = default_color_option
            df_filtered = filtered_df.copy()

    else:  # Sales path
        regions = sorted(df['Region name'].dropna().unique())
        selected_region = st.selectbox("Select Region:", ['All'] + regions, key="region_selectbox_tab3")

        price_min, price_max = int(df['Price actual'].min()), int(df['Price actual'].max())
        selected_price = st.slider("Select Price Range (£):", min_value=price_min, max_value=price_max,
                                    value=(price_min, price_max), key="price_slider_tab3")

        color_option = st.selectbox("Choose how to color the scatter plot:",
                                        options=["Efficiency Band", "BUILT_FORM", "PROPERTY_TYPE"],
                                        index=0, key="scatter_color_choice_tab3")

        use_log_scale = st.checkbox("Use log scale for Price", value=False, key="log_scale_tab3")

        df_filtered = df.copy()
        if selected_region != 'All':
            df_filtered = df_filtered[df_filtered['Region name'] == selected_region]

            df_filtered = df_filtered[
                (df_filtered['Price actual'] >= selected_price[0]) &
                (df_filtered['Price actual'] <= selected_price[1])
            ]

            filtered_df = df_filtered.copy()  # Ensure defined for later use

    # --- Common Processing Section ---
    required_columns = ['Price actual', 'Current Energy Efficiency', 'SQM_TOTAL',
                        'Region name', 'PROPERTY_TYPE', 'BUILT_FORM']

    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Dataset is missing required column(s): {', '.join(missing_cols)}")
        st.stop()

    df_filtered = df_filtered[required_columns].dropna(subset=['Price actual', 'Current Energy Efficiency'])

    # Efficiency band function
    def efficiency_band(score):
        if score >= 92: return 'A'
        elif score >= 81: return 'B'
        elif score >= 69: return 'C'
        elif score >= 55: return 'D'
        elif score >= 39: return 'E'
        elif score >= 21: return 'F'
        else: return 'G'

    df_filtered['Efficiency Band'] = df_filtered['Current Energy Efficiency'].apply(efficiency_band)
    df_filtered['Price per SQM'] = df_filtered.apply(
        lambda row: row['Price actual'] / row['SQM_TOTAL']
        if pd.notnull(row['SQM_TOTAL']) and row['SQM_TOTAL'] > 0 else np.nan,
        axis=1
    )

    pre_drop_count = len(df_filtered)
    df_viz = df_filtered.dropna(subset=['Price per SQM'])
    dropped_count = pre_drop_count - len(df_viz)


    # --- Visualization ---
    fig = px.scatter(
        df_viz,
        x='Current Energy Efficiency',
        y='Price actual',
        color=color_option if color_option in df_viz.columns else 'Efficiency Band',
        size='Price per SQM',
        hover_data={
            'Price actual': ':.0f',
            'Current Energy Efficiency': True,
            'Region name': True,
            'PROPERTY_TYPE': True,
            'BUILT_FORM': True,
            'Price per SQM': ':.1f'
        },
        title="Energy Efficiency vs Property Price – Highlighting Price Premium and Affordability",
        labels={
            "Current Energy Efficiency": "Energy Efficiency Score",
            "Price actual": "Price (£)"
        }
    )

    fig.update_traces(marker=dict(opacity=0.7, sizemode='area', line=dict(width=0.5, color='DarkSlateGrey')))
    fig.update_layout(
        legend_title_text=color_option,
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(t=60, b=40, l=10, r=10),
        plot_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgrey',
            title="Price (£)",
            type="log" if filter_mode3 == "Sales" and use_log_scale else "linear"
        )
    )

    st.plotly_chart(fig, use_container_width=True)




    # --- Heatmap: Energy Score vs Price ---
    fig_heatmap = px.density_heatmap(
        filtered_df, 
        x="Current Energy Efficiency", 
        y="Price actual", 
        z="Price actual",
        title=" 🌡️ Heatmap of Property Prices by Energy Efficiency",
        labels={"Current Energy Efficiency": "Energy Efficiency Score", "Price actual": "Price (£)"},
        nbinsx=30, nbinsy=30
    )
    fig_heatmap.update_layout(xaxis_title="Energy Efficiency Score", yaxis_title="Price (£)", coloraxis_colorbar_title="Density")
    st.plotly_chart(fig_heatmap, use_container_width=True)


    st.info("**Tip:** Upgrading a property's EPC rating can significantly boost its resale value and rental appeal — a win-win for both buyers and the environment. 🌍")


# === Tab 4 ===
# with tab4:
#     # Clean up data: drop rows with missing values needed for regression
#     regression_df = df[['Region name', 'Price actual', 'Current Energy Efficiency']].dropna()
#     regression_df = regression_df[regression_df['Price actual'] > 0]

#     # --- Regional Regression Slopes ---
#     region_stats = []

#     for region in regression_df['Region name'].unique():
#         sub_df = regression_df[regression_df['Region name'] == region]
#         if len(sub_df) >= 10:  # Skip regions with insufficient data
#             X = sub_df[['Current Energy Efficiency']]
#             y = sub_df['Price actual']
#             model = LinearRegression().fit(X, y)
#             score = model.score(X, y)
#             slope = model.coef_[0]
#             intercept = model.intercept_
#             region_stats.append({
#                 "Region": region,
#                 "R2": score,
#                 "Slope": slope,
#                 "Intercept": intercept,
#                 "Count": len(sub_df)
#             })

#     region_results_df = pd.DataFrame(region_stats).sort_values(by='R2', ascending=False)

#     # --- Slope and R2 Plot ---
#     fig_regression = px.bar(
#         region_results_df,
#         x='Region', y='Slope',
#         color='R2',
#         hover_data=['R2', 'Count'],
#         title="📈 Impact of Energy Efficiency on Property Price by Region",
#         labels={"Slope": "£ Change per Efficiency Point", "R2": "Model Fit (R²)"}
#     )
#     fig_regression.update_layout(xaxis_tickangle=-45)
#     st.plotly_chart(fig_regression, use_container_width=True)

#     # --- R² Score Table ---
#     st.markdown("### 📊 Regression Summary by Region")
#     st.dataframe(region_results_df.style.format({
#         "Slope": "£{:.0f}",
#         "Intercept": "£{:.0f}",
#         "R2": "{:.2f}",
#         "Count": "{:.0f}"
#     }), use_container_width=True)

#     # --- Interpretation ---
#     st.markdown("### 🧠 Insights & Interpretation")

#     top_region = region_results_df.iloc[0]
#     bottom_region = region_results_df.iloc[-1]

#     st.markdown(f"""
#     - **📍 Highest sensitivity:** In **{top_region['Region']}**, each point increase in energy efficiency corresponds to an increase of **£{top_region['Slope']:,.0f}** in price (R²: {top_region['R2']:.2f}).
#     - **🔻 Lowest impact:** In **{bottom_region['Region']}**, the relationship is much weaker, with a slope of only **£{bottom_region['Slope']:,.0f}** (R²: {bottom_region['R2']:.2f}).

#     This variation suggests that **regional markets** perceive and value energy efficiency differently — possibly due to **local demand**, **housing stock**, or **policy incentives**.
#     """)

#     st.info("ℹ️ Note: Regions with low R² values show weak relationships, suggesting other factors may dominate price differences in those areas.")





