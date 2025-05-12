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
st.image(r"Banner logo.png", use_container_width=True)
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
    df['INSPECTION_DATE'] = pd.to_datetime(df['INSPECTION_DATE'], errors='coerce')
    df['Year'] = df['INSPECTION_DATE'].dt.year.astype('Int32')
    return df

df = load_data()


with tab1:
    st.write(""" """)

    # View mode
    filter_mode = st.radio(
        "Select Data View Mode:",
        ["Rental(s)", "Sales"],
        horizontal=True
    )

    if filter_mode == "Rental(s)":
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
                    st.write("Available years in data:", sorted(filtered_df['Year'].dropna().unique()))

                    st.write("Sample raw INSPECTION_DATE values:")
                    st.write(df['INSPECTION_DATE'].head(20))

                    available_years = sorted(filtered_df['Year'].dropna().unique())

                    if len(available_years) == 0:
                        st.warning("⚠️ No valid years available in the current filtered data to display trends.")
                    else:
                        st.markdown("**Select year(s) to display:**")
                        year_cols = st.columns(len(available_years))
                        selected_years = []
                    
                        for i, year in enumerate(available_years):
                            if year_cols[i].checkbox(str(year), value=True):
                                selected_years.append(year)
                    
                        if selected_years:
                            df_trend = (
                                filtered_df[filtered_df['Year'].isin(selected_years)]
                                .groupby('Year')['Energy Gap']
                                .mean()
                                .reset_index()
                            )
                    
                            if not df_trend.empty and len(df_trend['Year'].unique()) > 0:
                                fig_trend = px.line(
                                    df_trend,
                                    x='Year',
                                    y='Energy Gap',
                                    markers=True,
                                    labels={'Energy Gap': 'Average Energy Gap', 'Year': 'Year'}
                                )
                                fig_trend.update_traces(line=dict(color='purple'))
                                fig_trend.update_layout(hovermode='x unified', xaxis=dict(dtick=1))
                                st.plotly_chart(fig_trend, use_container_width=True)
                    
                                if len(df_trend) >= 2:
                                    start_year = df_trend['Year'].min()
                                    end_year = df_trend['Year'].max()
                                    gap_start = df_trend[df_trend['Year'] == start_year]['Energy Gap'].values[0]
                                    gap_end = df_trend[df_trend['Year'] == end_year]['Energy Gap'].values[0]
                                    gap_change = gap_end - gap_start
                                    trend_direction = "increased" if gap_change > 0 else "decreased" if gap_change < 0 else "remained stable"
                    
                                    st.markdown(f"""
                                    Over the selected years, the **average energy gap** has **{trend_direction}** from **{gap_start:.1f}** in **{start_year}** to **{gap_end:.1f}** in **{end_year}**.
                                    This suggests that energy efficiency has **{"worsened" if gap_change > 0 else "improved" if gap_change < 0 else "not changed significantly"}** over time across the selected region.
                                    """)
                                else:
                                    st.info("Only one year selected — trend line needs at least two years for meaningful comparison.")
                            else:
                                st.info("No energy gap data available for the selected years.")
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
                    # === 1. C02 Efficiency Distribution ===
                    # Melt the dataframe for histogram
                    eff = filtered_df[['Current CO2 Emission', 'Potential CO2 Emission']].melt(
                        var_name="Type", value_name="Emissions"
                    )

                    # Create histogram figure
                    fig1 = px.histogram(
                        eff, x='Emissions', color='Type',
                        barmode='overlay', nbins=30,
                        opacity=0.6  # Ensure line is visible
                    )

                    # Energy Gap trend as histogram-style line
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

                    # Add the trend line
                    fig1.add_trace(gap_line)

                    # Update layout
                    fig1.update_layout(
                        title="Current vs Potential CO2 Emission (with CO2 Gap Trend)",
                        hovermode='x',
                        yaxis=dict(title='Count')
                    )

                    # Display the chart
                    st.plotly_chart(fig1, use_container_width=True)


                with col2:
                    # --- Load GeoJSON file ---
                    with open(r"Local_Authority_Districts_December_2021_UK_BUC_2022_3960795867023731705.geojson") as f:
                        geojson_data = json.load(f)

                    # --- Calculate color scale range ---
                    gap_min = filtered_df['CO2 Gap'].min()
                    gap_max = filtered_df['CO2 Gap'].max()
                    color_range = [gap_min, gap_max]
                    color_scale = "plasma"

                    # --- Filter rows with valid coordinates and CO2 gap ---
                    map_df = filtered_df.dropna(subset=['Latitude', 'Longitude', 'CO2 Gap'])

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
                            color='CO2 Gap',
                            color_continuous_scale=color_scale,
                            range_color=color_range,
                            mapbox_style="carto-positron",
                            zoom=6,
                            center={"lat": center_lat, "lon": center_lon},
                            opacity=0.5,
                            hover_name='LAD_NM'
                        )

                       
                        fig.update_layout(title_text=f"CO2 Gap by {selected_town} Local Authority District",
                                          margin={"r":0, "t":50, "l":0, "b":0})
                        col2.plotly_chart(fig, use_container_width=True)

                        # --- NLP Summary that reflects the map output ---
                        # --- NLP Summary ---
                        # Aggregate to get one CO2 Gap per LAD
                        agg_df = map_df.groupby('LAD_NM', as_index=False)['CO2 Gap'].mean()

                        # Get average, min, and max from aggregated data
                        avg_gap = agg_df['CO2 Gap'].mean()
                        best_areas = agg_df.nsmallest(3, 'CO2 Gap')
                        worst_areas = agg_df.nlargest(3, 'CO2 Gap')

                        best_text = ", ".join([f"{row['LAD_NM']} ({row['CO2 Gap']:.1f})" for _, row in best_areas.iterrows()])
                        worst_text = ", ".join([f"{row['LAD_NM']} ({row['CO2 Gap']:.1f})" for _, row in worst_areas.iterrows()])

                        st.markdown(f"""
                        ### 🌍 CO₂ Emission Reduction Potential in {selected_town if selected_town != "All" else selected_county}

                        This map visualizes the geographical variation in **CO₂ emissions gap** — the difference between current and potential CO₂ output — across **Local Authority Districts** in **{selected_town if selected_town != "All" else selected_county}**.

                        - **Average CO₂ gap**: {avg_gap:.1f} units  
                        - ✅ **Best performing areas** (lower CO₂ gap): {best_text}  
                        - 🔍 **Worst performing areas** (higher CO₂ gap): {worst_text}

                        Areas with higher CO₂ gaps represent greater opportunities for **carbon reduction** through energy efficiency upgrades or greener technologies.

                        Lighter-colored regions on the map emit less excess CO₂, while darker regions emit more than their efficient potential.

                        These insights help policymakers and planners focus **decarbonization efforts** in high-impact regions.
                        """)

                    else:
                        col2.warning("No data to plot for the selected filters.")

                
    #             col1, col2 = st.columns(2)
    #             # === 1. C02 Gap Distribution ===
    #             with col1:
    #                     if not filtered_df.empty:
    #                         # --- Calculate color scale range ---
    #                         gap_min = filtered_df['CO2 Gap'].min()
    #                         gap_max = filtered_df['CO2 Gap'].max()
    #                         color_range = [gap_min, gap_max]
    #                         color_scale = "plasma"

    #                         # Clean map data
    #                         map_df = filtered_df.dropna(subset=['Latitude', 'Longitude', 'CO2 Gap'])

    #                         # --- Histogram ---
    #                         fig_hist = px.histogram(
    #                             filtered_df,
    #                             x='CO2 Gap',
    #                             nbins=30,
    #                             title=f"Distribution of CO2 Gap ",
    #                             color_discrete_sequence=['purple'],
    #                             labels={'CO2 Gap': 'CO2 Gap (points)'}
    #                         )
    #                         fig_hist.update_layout(
    #                             bargap=0.1,
    #                             xaxis_title="CO2 Gap",
    #                             yaxis_title="Count",
    #                             template="plotly_white"
    #                         )
    #                         st.plotly_chart(fig_hist, use_container_width=True)

    #                     with col2:
    #                         # --- Plot 2: Map of Energy Gap ---
    #                         if not map_df.empty:
    #                             # --- Map ---
    #                                 # --- Compute map center based on selected Post Town ---
    #                             center_lat = map_df['Latitude'].mean()
    #                             center_lon = map_df['Longitude'].mean()
    #                             fig_map = px.scatter_mapbox(
    #                                 map_df,
    #                                 lat='Latitude',
    #                                 lon='Longitude',
    #                                 color='CO2 Gap',
    #                                 size='CO2 Gap',
    #                                 size_max=10,
    #                                 color_continuous_scale=color_scale,
    #                                 range_color=color_range,
    #                                 zoom=10,
    #                                 center={"lat": center_lat, "lon": center_lon},
    #                                 mapbox_style="carto-positron",
    #                                 hover_data=['POSTCODE', 'CO2 Gap'],
    #                                 title=f"CO2 Gap in {selected_town}"
    #                                 )
    #                             st.plotly_chart(fig_map, use_container_width=True)
    #                         else:
    #                             st.warning("No data to plot for the selected filters.")



    #             with st.container():
    #                 st.markdown("### 📈 CO2 Gap Trend Over Time (Last 5 Years)")

    #                 # Get last 5 years
    #                 available_years = sorted(filtered_df['Year'].dropna().unique())
    #                 last_five_years = available_years[-5:]

    #                 # Show checkboxes for each year
    #                 st.markdown("**Select year(s) to display:**")
    #                 year_cols = st.columns(len(last_five_years))
    #                 selected_years = []

    #                 for i, year in enumerate(last_five_years):
    #                     if year_cols[i].checkbox(str(year), value=True):
    #                         selected_years.append(year)

    #                 # Plot if any year is selected
    #                 if selected_years:
    #                     df_trend = (
    #                         filtered_df[filtered_df['Year'].isin(selected_years)]
    #                         .groupby('Year')['CO2 Gap']
    #                         .mean()
    #                         .reset_index()
    #                     )

    #                     fig_trend = px.line(
    #                         df_trend,
    #                         x='Year',
    #                         y='CO2 Gap',
    #                         markers=True,
    #                         title="Average CO2 Gap by Year",
    #                         labels={'CO2 Gap': 'Average CO2 Gap', 'Year': 'Year'}
    #                     )

    #                     fig_trend.update_layout(
    #                         hovermode='x unified',
    #                         xaxis=dict(dtick=1)
    #                     )

    #                     st.plotly_chart(fig_trend, use_container_width=True)
    #                 else:
    #                     st.info("Please select at least one year to view the trend.")
    #                             # === 4. Energy Consumption ===
    #             st.markdown("#### Energy Consumption (kWh/m²)")
    #             cons = filtered_df[['ENERGY_CONSUM_CURR', 'ENERGY_CONSUM_POTEN']].melt(
    #                 var_name="Consumption Type", value_name="Energy Consumption"
    #             )
    #             fig_cons = px.box(
    #                 cons, x="Consumption Type", y="Energy Consumption",
    #                 points="outliers"
    #             )
    #             st.plotly_chart(fig_cons, use_container_width=True)
    #             st.markdown(
    #                 "Outliers shown; potential scenario generally consumes less energy."
    #             )




















    # show_saving = st.checkbox("Show CO2 Saving", value=True)
    # co2_current = filtered_df['Current CO2 Emission'].sum()
    # co2_potential = filtered_df['Potential CO2 Emission'].sum()
    # co2_saving = co2_current - co2_potential

    # fig2 = go.Figure()
    # fig2.add_bar(x=['Current'], y=[co2_current], name='Current', marker_color='#1f77b4')
    # fig2.add_bar(x=['Potential'], y=[co2_potential], name='Potential', marker_color='#2ca02c')
    # if show_saving:
    #     fig2.add_bar(x=['Saving'], y=[co2_saving], name='Saving', marker_color='orange')
    #     fig2.add_annotation(x=1, y=max(co2_current, co2_potential), text="Projected Saving", showarrow=True, arrowhead=2)
    #     fig2.update_layout(title="Total CO2 Emissions (Tonnes)", yaxis_title="Tonnes of CO2", barmode='group', hovermode='x')
    #     st.plotly_chart(fig2, use_container_width=True)
    #     st.markdown(f"**🌱 Current CO₂ emissions:** {co2_current:,.0f} tonnes | **Potential:** {co2_potential:,.0f} tonnes. \
    #             With improvements, emissions could be reduced by **{co2_saving:,.0f} tonnes**, highlighting major environmental benefits.")





    # st.markdown("Explore how energy efficiency varies by **price** and **tenure**.")

    # tenure_filter = st.multiselect("Select Tenure Types:", df["TENURE"].dropna().unique(), default=df["TENURE"].dropna().unique())
    # filtered_df = df[df["TENURE"].isin(tenure_filter)]

    # fig1 = px.box(filtered_df, x="TENURE", y="Current Energy Efficiency",
    #               title="Energy Efficiency by Tenure Type",
    #               labels={"Current Energy Efficiency": "Current Energy Efficiency"},
    #               hover_data=["PROPERTY_TYPE", "Amount per week"])
    # fig1.update_layout(xaxis_title="Tenure Type", yaxis_title="Energy Efficiency", height=500)
    # st.plotly_chart(fig1, use_container_width=True)

    # st.markdown("#### 💡 Energy efficiency vs rent per week")
    # fig2 = px.scatter(filtered_df, x="Amount per week", y="Current Energy Efficiency",
    #                   color="TENURE",
    #                   title="Energy Efficiency vs Rent per Week",
    #                   hover_data=["PROPERTY_TYPE", "CONSTRUCTION_AGE", "EPC Rating"])
    # fig2.update_layout(height=500)
    # st.plotly_chart(fig2, use_container_width=True)


    # st.markdown("Compare average energy efficiency across **construction eras**.")

    # age_eff = df.groupby("CONSTRUCTION_AGE")["Current Energy Efficiency"].mean().dropna().sort_values()
    # age_eff_df = age_eff.reset_index().rename(columns={"Current Energy Efficiency": "Average Energy Efficiency"})

    # fig3 = px.bar(age_eff_df, x="Average Energy Efficiency", y="CONSTRUCTION_AGE",
    #               orientation="h", title="Average Energy Efficiency by Construction Age")
    # fig3.update_layout(height=600)
    # st.plotly_chart(fig3, use_container_width=True)

    # st.markdown("Analyze efficiency by **property type** (detached, flat, terrace, etc.).")

    # property_filter = st.multiselect("Select Property Types:", df["PROPERTY_TYPE"].dropna().unique(), default=df["PROPERTY_TYPE"].dropna().unique())
    # df_type = df[df["PROPERTY_TYPE"].isin(property_filter)]

    # fig4 = px.box(df_type, x="PROPERTY_TYPE", y="Current Energy Efficiency",
    #               title="Energy Efficiency by Property Type",
    #               hover_data=["TENURE", "Amount", "CONSTRUCTION_AGE"])
    # fig4.update_layout(height=500)
    # st.plotly_chart(fig4, use_container_width=True)



# === Tab 3 ===
with tab3:
    col1, col2 = st.columns([1, 5])

    with col1:
        with st.expander("🔍 Filter Options", expanded=True):
            regions = sorted(df['Region name'].dropna().unique())
            selected_region = st.selectbox(
                "Select Region:", 
                ['All'] + regions, 
                key="region_selectbox_tab3"
            )
            
            price_min = int(df['Price actual'].min())
            price_max = int(df['Price actual'].max())

            selected_price = st.slider(
                "Select Price Range (£):",
                min_value=price_min,
                max_value=price_max,
                value=(price_min, price_max),
                key="price_slider_tab3"
            )

            color_option = st.selectbox(
                "Choose how to color the scatter plot:",
                options=["BUILT_FORM", "PROPERTY_TYPE"],
                index=0,
                key="scatter_color_choice_tab3"
            )

    with col2:
        # Apply filters
        filtered_df = df.copy()

        if selected_region != 'All':
            filtered_df = filtered_df[filtered_df['Region name'] == selected_region]
        
        filtered_df = filtered_df[
            (filtered_df['Price actual'] >= selected_price[0]) &
            (filtered_df['Price actual'] <= selected_price[1])
        ]

        # === Scatter Plot (Dynamic Color) ===
        fig_scatter = px.scatter(
            filtered_df, 
            x='Current Energy Efficiency', 
            y='Price actual',
            color=color_option,
            trendline="ols",
            title=f"Price vs Energy Efficiency Score (Colored by {color_option.replace('_', ' ').title()})",
            labels={
                "Current Energy Efficiency": "Energy Efficiency Score", 
                "Price actual": "Price (£)"
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # --- Smart Dynamic Text: Price Premiums by Efficiency ---
        high_efficiency = filtered_df[filtered_df['Current Energy Efficiency'] >= 80]['Price actual'].median()
        low_efficiency = filtered_df[filtered_df['Current Energy Efficiency'] <= 50]['Price actual'].median()

        with st.expander("🧠 Interpretation: Price Premiums by Efficiency"):
            if high_efficiency > low_efficiency:
                price_increase_pct = ((high_efficiency - low_efficiency) / low_efficiency) * 100
                st.markdown(f"""
                Properties with high energy efficiency scores (80 and above) have a **median price of £{high_efficiency:,.0f}**,  
                compared to **£{low_efficiency:,.0f}** for less efficient properties.  
                This reflects a price premium of approximately **{price_increase_pct:.1f}%**, highlighting the market’s growing emphasis on sustainability and lower future energy costs.
                """)
            else:
                st.markdown(f"""
                Surprisingly, properties with **lower** energy efficiency scores (≤50) have a **higher median price** than more efficient homes.  
                This might indicate that **property size, location, or luxury features** currently outweigh energy concerns in price determination.
                """)

        st.divider()

        # === Smart NLP Comparison Based on Selected Color Option ===
        with st.expander(f"🧠 Deeper Insights by {color_option.replace('_', ' ').title()}"):
            # Group by BUILT_FORM or PROPERTY_TYPE dynamically
            group_summary = filtered_df.groupby(color_option).agg(
                avg_efficiency=('Current Energy Efficiency', 'mean'),
                avg_price=('Price actual', 'mean'),
                count=('Price actual', 'count')
            ).reset_index().dropna()

            # Find the best performer (highest avg efficiency)
            if not group_summary.empty:
                best_efficiency = group_summary.sort_values('avg_efficiency', ascending=False).iloc[0]
                best_price = group_summary.sort_values('avg_price', ascending=False).iloc[0]
                worst_efficiency = group_summary.sort_values('avg_efficiency', ascending=True).iloc[0]

                st.markdown(f"""
                - **🏡 Best {color_option.replace('_', ' ').title()} for Energy Efficiency:**  
                  **{best_efficiency[color_option]}** has the highest average energy score of **{best_efficiency['avg_efficiency']:.1f}**.

                - **💸 Most Expensive {color_option.replace('_', ' ').title()}:**  
                  **{best_price[color_option]}** has the highest average price at **£{best_price['avg_price']:,.0f}**.

                - **⚡ Lowest Energy Efficiency:**  
                  **{worst_efficiency[color_option]}** shows the lowest average energy score of **{worst_efficiency['avg_efficiency']:.1f}**, suggesting potential for improvement or retrofit opportunities.

                **Overall**, {color_option.replace('_', ' ').title()} plays an important role in shaping both the **energy performance** and **price premium** of properties.
                """)
            else:
                st.warning("Not enough data to generate detailed insights for the selected filters.")


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
with tab4:
    # Clean up data: drop rows with missing values needed for regression
    regression_df = df[['Region name', 'Price actual', 'Current Energy Efficiency']].dropna()
    regression_df = regression_df[regression_df['Price actual'] > 0]

    # --- Regional Regression Slopes ---
    region_stats = []

    for region in regression_df['Region name'].unique():
        sub_df = regression_df[regression_df['Region name'] == region]
        if len(sub_df) >= 10:  # Skip regions with insufficient data
            X = sub_df[['Current Energy Efficiency']]
            y = sub_df['Price actual']
            model = LinearRegression().fit(X, y)
            score = model.score(X, y)
            slope = model.coef_[0]
            intercept = model.intercept_
            region_stats.append({
                "Region": region,
                "R2": score,
                "Slope": slope,
                "Intercept": intercept,
                "Count": len(sub_df)
            })

    region_results_df = pd.DataFrame(region_stats).sort_values(by='R2', ascending=False)

    # --- Slope and R2 Plot ---
    fig_regression = px.bar(
        region_results_df,
        x='Region', y='Slope',
        color='R2',
        hover_data=['R2', 'Count'],
        title="📈 Impact of Energy Efficiency on Property Price by Region",
        labels={"Slope": "£ Change per Efficiency Point", "R2": "Model Fit (R²)"}
    )
    fig_regression.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_regression, use_container_width=True)

    # --- R² Score Table ---
    st.markdown("### 📊 Regression Summary by Region")
    st.dataframe(region_results_df.style.format({
        "Slope": "£{:.0f}",
        "Intercept": "£{:.0f}",
        "R2": "{:.2f}",
        "Count": "{:.0f}"
    }), use_container_width=True)

    # --- Interpretation ---
    st.markdown("### 🧠 Insights & Interpretation")

    top_region = region_results_df.iloc[0]
    bottom_region = region_results_df.iloc[-1]

    st.markdown(f"""
    - **📍 Highest sensitivity:** In **{top_region['Region']}**, each point increase in energy efficiency corresponds to an increase of **£{top_region['Slope']:,.0f}** in price (R²: {top_region['R2']:.2f}).
    - **🔻 Lowest impact:** In **{bottom_region['Region']}**, the relationship is much weaker, with a slope of only **£{bottom_region['Slope']:,.0f}** (R²: {bottom_region['R2']:.2f}).

    This variation suggests that **regional markets** perceive and value energy efficiency differently — possibly due to **local demand**, **housing stock**, or **policy incentives**.
    """)

    st.info("ℹ️ Note: Regions with low R² values show weak relationships, suggesting other factors may dominate price differences in those areas.")





