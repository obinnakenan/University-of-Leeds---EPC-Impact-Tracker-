import streamlit as st
import plotly.express as px
import plotly.graph_objects as go  
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import base64


# --- Page Config ---
st.set_page_config(
    page_title="EPC Impact Tracker: Housing, Inequality & Environment",
    layout="wide",
    page_icon="🏡"
)



# Set local background image
def set_background_local(png_file):
    with open(png_file, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{data}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .transparent-button button {{
            background-color: green !important;  /* Tiffany Blue */
            border: none;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1.25em;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }}

        .transparent-button button:hover {{
            background-color: #099f9a !important;  /* Slightly darker Tiffany Blue on hover */
            cursor: pointer;
        }}

        .footer-link {{
            position: absolute;
            bottom: -190px;
            right: 400px;
            font-size: 11px;
        }}

        .footer-link a {{
            color: black;
            text-decoration: none;
        }}

        .footer-link a:hover {{
            text-decoration: underline;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- INTRO SCREEN FIRST ---
if 'show_app' not in st.session_state:
    st.session_state.show_app = False

if not st.session_state.show_app:
    set_background_local(r"Background image.png")  # Use uploaded file path

    st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

    # Centered Transparent Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.container():
            st.markdown('<div class="transparent-button">', unsafe_allow_html=True)
            clicked = st.button("EXPLORE THE DATA", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Click logic
    if clicked:
        st.session_state.show_app = True
        st.rerun()
    else:
        st.markdown(
            """
            <div class='footer-link'>
                <a href="https://www.sciencedirect.com/science/article/pii/S0140988323005406" target="_blank">
                Regional persistence of the energy efficiency gap: Evidence from England and Wales<br>
                (Energy Economics Journal 2023)
                </a>
                </a>
                </a>
        </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.stop()



# --- Banner and Title ---
st.image("C:/Users/vbvb850/Downloads/Uni_Leeds_600_400.jpg", use_container_width=True)
st.markdown("### EPC Impact Tracker: Housing, Inequality & Environment")

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
    df['LODGEMENT_DATE'] = pd.to_datetime(df['LODGEMENT_DATE'])
    df['Year'] = df['LODGEMENT_DATE'].dt.year
    return df

df = load_data()


with tab1:
    st.write(""" """)
    with st.container():
        # Overall layout: 1/3 width for filters, 2/3 for charts
        col_filters, col_main = st.columns([1, 2])

        with col_filters:
            # three-column filter layout e.g "Region name", "County area name", and "post town"
            Region_filter, County_area_Filter, Post_town_filter = st.columns(3, gap="medium")

            with Region_filter:
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Region:</div>',unsafe_allow_html=True)
                select_yorkshire = st.checkbox(
                    "**Yorkshire and The Humber**",
                    value=True,
                    key="yorkshire_chk"
                )

            with County_area_Filter:
                # County dropdown
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">County area(s):</div>',unsafe_allow_html=True)
                counties = sorted(df['County area name'].dropna().unique())
                selected_county = st.selectbox(
                    "County Area",
                    options=counties,
                    key="county_sel",
                    label_visibility="collapsed"
                )

            with Post_town_filter:
                # Post Town dropdown (cascading)
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Post town(s):</div>',unsafe_allow_html=True)
                towns = sorted(
                    df.loc[
                        df['County area name'] == selected_county,
                        'Post town name'
                    ].dropna()
                    .unique()
                )
                selected_town = st.selectbox(
                    "Post Town",
                    options=towns,
                    key="town_sel",
                    label_visibility="collapsed"
                )
            
            # displays if no tickbox is selected
            if not select_yorkshire:
                st.error("No data selected. Please tick 'Yorkshire and The Humber' to proceed.")
                st.stop()

            # -- proper filter using exact region string --
            filtered_df = df[
                (df['Region name'] == 'Yorkshire and The Humber') &
                (df['County area name'] == selected_county) &
                (df['Post town name'] == selected_town)
            ]

            if filtered_df.empty:
                st.warning("No records matched your filters. Adjust your selections.")
            else:
                st.success(f"{len(filtered_df)} records matched your filters.")

    with col_main:
            if filtered_df.empty:
                st.info("Adjust filters on the left to see charts.")

    with st.container():
                # === 1. Energy Efficiency Distribution ===
                eff = filtered_df[['Current Energy Efficiency', 'Potential Energy Efficiency']].melt(
                        var_name="Type", value_name="Efficiency"
                    )
                fig1 = px.histogram(
                        eff, x='Efficiency', color='Type',
                        barmode='overlay', nbins=30
                    )
                fig1.update_layout(
                        title="Current vs Potential Energy Efficiency",
                        hovermode='x'
                    )
                st.plotly_chart(fig1, use_container_width=True)

                avg_cur = filtered_df['Current Energy Efficiency'].mean()
                avg_pot = filtered_df['Potential Energy Efficiency'].mean()
                st.markdown(
                        f"**📊 Average current efficiency:** {avg_cur:.1f} | "
                        f"**Potential:** {avg_pot:.1f} "
                        f"(+{avg_pot - avg_cur:.1f} points)"
                    )
                
                col1, col2 = st.columns(2)
                # === 1. Energy Gap Distribution ===
                with col1:
                        if not filtered_df.empty:
                            # --- Calculate color scale range ---
                            gap_min = filtered_df['Energy Gap'].min()
                            gap_max = filtered_df['Energy Gap'].max()
                            color_range = [gap_min, gap_max]
                            color_scale = "plasma"

                            # Clean map data
                            map_df = filtered_df.dropna(subset=['Latitude', 'Longitude', 'Energy Gap'])

                            # --- Histogram ---
                            fig_hist = px.histogram(
                                filtered_df,
                                x='Energy Gap',
                                nbins=30,
                                title=f"Distribution of Energy Gap ",
                                color_discrete_sequence=['purple'],
                                labels={'Energy Gap': 'Energy Gap (points)'}
                            )
                            fig_hist.update_layout(
                                bargap=0.1,
                                xaxis_title="Energy Gap",
                                yaxis_title="Count",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)

                        with col2:
                            # --- Plot 2: Map of Energy Gap ---
                            if not map_df.empty:
                                # --- Map ---
                                    # --- Compute map center based on selected Post Town ---
                                center_lat = map_df['Latitude'].mean()
                                center_lon = map_df['Longitude'].mean()
                                fig_map = px.scatter_mapbox(
                                    map_df,
                                    lat='Latitude',
                                    lon='Longitude',
                                    color='Energy Gap',
                                    size='Energy Gap',
                                    size_max=10,
                                    color_continuous_scale=color_scale,
                                    range_color=color_range,
                                    zoom=10,
                                    center={"lat": center_lat, "lon": center_lon},
                                    mapbox_style="carto-positron",
                                    hover_data=['POSTCODE', 'Energy Gap'],
                                    title=f"Energy Gap in {selected_town}"
                                    )
                                st.plotly_chart(fig_map, use_container_width=True)
                            else:
                                st.warning("No data to plot for the selected filters.")



                with st.container():
                    st.markdown("### 📈 Energy Gap Trend Over Time (Last 5 Years)")

                    # Get last 5 years
                    available_years = sorted(filtered_df['Year'].dropna().unique())
                    last_five_years = available_years[-5:]

                    # Show checkboxes for each year
                    st.markdown("**Select year(s) to display:**")
                    year_cols = st.columns(len(last_five_years))
                    selected_years = []

                    for i, year in enumerate(last_five_years):
                        if year_cols[i].checkbox(str(year), value=True):
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
                            title="Average Energy Gap by Year",
                            labels={'Energy Gap': 'Average Energy Gap', 'Year': 'Year'}
                        )

                        fig_trend.update_layout(
                            hovermode='x unified',
                            xaxis=dict(dtick=1)
                        )

                        st.plotly_chart(fig_trend, use_container_width=True)
                    else:
                        st.info("Please select at least one year to view the trend.")








             # === 2. Regional Comparison ===
                region_avg = (
                    filtered_df
                    .groupby('Region name')['Current Energy Efficiency']
                    .mean()
                    .reset_index()
                )
                fig3 = px.bar(
                    region_avg, x='Current Energy Efficiency', y='Region name',
                    orientation='h', labels={'Current Energy Efficiency': 'Avg Efficiency'}
                )
                st.plotly_chart(fig3, use_container_width=True)

                top_r = region_avg.nlargest(1, 'Current Energy Efficiency').iloc[0]
                bot_r = region_avg.nsmallest(1, 'Current Energy Efficiency').iloc[0]
                st.markdown(
                    f"**📍 Most efficient region:** {top_r['Region name']} "
                    f"({top_r['Current Energy Efficiency']:.1f}) | "
                    f"**Least efficient:** {bot_r['Region name']} "
                    f"({bot_r['Current Energy Efficiency']:.1f})"
                )

                # === 3. Environmental Impact ===
                st.markdown("#### Environmental Impact Rating (Current vs Potential)")
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

                # === 4. Energy Consumption ===
                st.markdown("#### Energy Consumption (kWh/m²)")
                cons = filtered_df[['ENERGY_CONSUM_CURR', 'ENERGY_CONSUM_POTEN']].melt(
                    var_name="Consumption Type", value_name="Energy Consumption"
                )
                fig_cons = px.box(
                    cons, x="Consumption Type", y="Energy Consumption",
                    points="outliers"
                )
                st.plotly_chart(fig_cons, use_container_width=True)
                st.markdown(
                    "Outliers shown; potential scenario generally consumes less energy."
                )

                # === 5. Top 10 Least Efficient ===
                st.markdown("#### 🏚️ Top 10 Least Efficient Properties")
                least10 = filtered_df.nsmallest(10, 'Current Energy Efficiency')
                st.dataframe(
                    least10[[
                        'Address', 'Region name',
                        'Current Energy Efficiency', 'Potential Energy Efficiency'
                    ]]
                )

                # === 6. Efficiency & CO₂ by Property Type ===
                st.markdown("#### 🏠 Efficiency and CO₂ by Property Type")
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
                st.markdown("#### Average Efficiency by Construction Age")
                age_eff = (
                    filtered_df
                    .groupby('CONSTRUCTION_AGE')['Current Energy Efficiency']
                    .mean().dropna().reset_index()
                )
                fig_age = px.bar(
                    age_eff.sort_values('Current Energy Efficiency'),
                    x='Current Energy Efficiency', y='CONSTRUCTION_AGE',
                    orientation='h', labels={"Current Energy Efficiency": "Avg Efficiency"}
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
    with st.container():
        # Overall layout: 1/3 width for filters, 2/3 for charts
        col_filters, col_main = st.columns([1, 2])

        with col_filters:
            # three-column filter layout e.g "Region name", "County area name", and "post town"
            Region_filter, County_area_Filter, Post_town_filter = st.columns(3, gap="medium")

            with Region_filter:
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Region:</div>',unsafe_allow_html=True)
                select_yorkshire = st.checkbox(
                    "**Yorkshire and The Humber**",
                    value=True,
                    key="yorkshire_chk2"
                )

            with County_area_Filter:
                # County dropdown
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">County area(s):</div>',unsafe_allow_html=True)
                counties = sorted(df['County area name'].dropna().unique())
                selected_county = st.selectbox(
                    "County Area",
                    options=counties,
                    key="county_sel2",
                    label_visibility="collapsed"
                )

            with Post_town_filter:
                # Post Town dropdown (cascading)
                st.markdown('<div style="margin-bottom: 0; font-weight: bold;">Post town(s):</div>',unsafe_allow_html=True)
                towns = sorted(
                    df.loc[
                        df['County area name'] == selected_county,
                        'Post town name'
                    ].dropna()
                    .unique()
                )
                selected_town = st.selectbox(
                    "Post Town",
                    options=towns,
                    key="town_sel2",
                    label_visibility="collapsed"
                )
            
            # displays if no tickbox is selected
            if not select_yorkshire:
                st.error("No data selected. Please tick 'Yorkshire and The Humber' to proceed.")
                st.stop()

            # -- proper filter using exact region string --
            filtered_df = df[
                (df['Region name'] == 'Yorkshire and The Humber') &
                (df['County area name'] == selected_county) &
                (df['Post town name'] == selected_town)
            ]

            if filtered_df.empty:
                st.warning("No records matched your filters. Adjust your selections.")
            else:
                st.success(f"{len(filtered_df)} records matched your filters.")

    with col_main:
            if filtered_df.empty:
                st.info("Adjust filters on the left to see charts.")

    with st.container():
                # === 1. CO2 Emission ===
                eff = filtered_df[['Current CO2 Emission', 'Potential CO2 Emission']].melt(
                        var_name="Type", value_name="Emission"
                    )
                fig1 = px.histogram(
                        eff, x='Emission', color='Type',
                        barmode='overlay', nbins=30
                    )
                fig1.update_layout(
                        title="Current vs Potential CO2 Emission",
                        hovermode='x'
                    )
                st.plotly_chart(fig1, use_container_width=True)

                avg_cur = filtered_df['Current CO2 Emission'].mean()
                avg_pot = filtered_df['Potential CO2 Emission'].mean()
                st.markdown(
                        f"**📊 Average co2 emission:** {avg_cur:.1f} | "
                        f"**Potential:** {avg_pot:.1f} "
                        f"(+{avg_pot - avg_cur:.1f} points)"
                    )
                
                col1, col2 = st.columns(2)
                # === 1. C02 Gap Distribution ===
                with col1:
                        if not filtered_df.empty:
                            # --- Calculate color scale range ---
                            gap_min = filtered_df['CO2 Gap'].min()
                            gap_max = filtered_df['CO2 Gap'].max()
                            color_range = [gap_min, gap_max]
                            color_scale = "plasma"

                            # Clean map data
                            map_df = filtered_df.dropna(subset=['Latitude', 'Longitude', 'CO2 Gap'])

                            # --- Histogram ---
                            fig_hist = px.histogram(
                                filtered_df,
                                x='CO2 Gap',
                                nbins=30,
                                title=f"Distribution of CO2 Gap ",
                                color_discrete_sequence=['purple'],
                                labels={'CO2 Gap': 'CO2 Gap (points)'}
                            )
                            fig_hist.update_layout(
                                bargap=0.1,
                                xaxis_title="CO2 Gap",
                                yaxis_title="Count",
                                template="plotly_white"
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)

                        with col2:
                            # --- Plot 2: Map of Energy Gap ---
                            if not map_df.empty:
                                # --- Map ---
                                    # --- Compute map center based on selected Post Town ---
                                center_lat = map_df['Latitude'].mean()
                                center_lon = map_df['Longitude'].mean()
                                fig_map = px.scatter_mapbox(
                                    map_df,
                                    lat='Latitude',
                                    lon='Longitude',
                                    color='CO2 Gap',
                                    size='CO2 Gap',
                                    size_max=10,
                                    color_continuous_scale=color_scale,
                                    range_color=color_range,
                                    zoom=10,
                                    center={"lat": center_lat, "lon": center_lon},
                                    mapbox_style="carto-positron",
                                    hover_data=['POSTCODE', 'CO2 Gap'],
                                    title=f"CO2 Gap in {selected_town}"
                                    )
                                st.plotly_chart(fig_map, use_container_width=True)
                            else:
                                st.warning("No data to plot for the selected filters.")



                with st.container():
                    st.markdown("### 📈 CO2 Gap Trend Over Time (Last 5 Years)")

                    # Get last 5 years
                    available_years = sorted(filtered_df['Year'].dropna().unique())
                    last_five_years = available_years[-5:]

                    # Show checkboxes for each year
                    st.markdown("**Select year(s) to display:**")
                    year_cols = st.columns(len(last_five_years))
                    selected_years = []

                    for i, year in enumerate(last_five_years):
                        if year_cols[i].checkbox(str(year), value=True):
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
                            title="Average CO2 Gap by Year",
                            labels={'CO2 Gap': 'Average CO2 Gap', 'Year': 'Year'}
                        )

                        fig_trend.update_layout(
                            hovermode='x unified',
                            xaxis=dict(dtick=1)
                        )

                        st.plotly_chart(fig_trend, use_container_width=True)
                    else:
                        st.info("Please select at least one year to view the trend.")




















    show_saving = st.checkbox("Show CO2 Saving", value=True)
    co2_current = filtered_df['Current CO2 Emission'].sum()
    co2_potential = filtered_df['Potential CO2 Emission'].sum()
    co2_saving = co2_current - co2_potential

    fig2 = go.Figure()
    fig2.add_bar(x=['Current'], y=[co2_current], name='Current', marker_color='#1f77b4')
    fig2.add_bar(x=['Potential'], y=[co2_potential], name='Potential', marker_color='#2ca02c')
    if show_saving:
        fig2.add_bar(x=['Saving'], y=[co2_saving], name='Saving', marker_color='orange')
        fig2.add_annotation(x=1, y=max(co2_current, co2_potential), text="Projected Saving", showarrow=True, arrowhead=2)
        fig2.update_layout(title="Total CO2 Emissions (Tonnes)", yaxis_title="Tonnes of CO2", barmode='group', hovermode='x')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(f"**🌱 Current CO₂ emissions:** {co2_current:,.0f} tonnes | **Potential:** {co2_potential:,.0f} tonnes. \
                With improvements, emissions could be reduced by **{co2_saving:,.0f} tonnes**, highlighting major environmental benefits.")





    st.markdown("Explore how energy efficiency varies by **price** and **tenure**.")

    tenure_filter = st.multiselect("Select Tenure Types:", df["TENURE"].dropna().unique(), default=df["TENURE"].dropna().unique())
    filtered_df = df[df["TENURE"].isin(tenure_filter)]

    fig1 = px.box(filtered_df, x="TENURE", y="Current Energy Efficiency",
                  title="Energy Efficiency by Tenure Type",
                  labels={"Current Energy Efficiency": "Current Energy Efficiency"},
                  hover_data=["PROPERTY_TYPE", "Amount per week"])
    fig1.update_layout(xaxis_title="Tenure Type", yaxis_title="Energy Efficiency", height=500)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("#### 💡 Energy efficiency vs rent per week")
    fig2 = px.scatter(filtered_df, x="Amount per week", y="Current Energy Efficiency",
                      color="TENURE",
                      title="Energy Efficiency vs Rent per Week",
                      hover_data=["PROPERTY_TYPE", "CONSTRUCTION_AGE", "EPC Rating"])
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)


    st.markdown("Compare average energy efficiency across **construction eras**.")

    age_eff = df.groupby("CONSTRUCTION_AGE")["Current Energy Efficiency"].mean().dropna().sort_values()
    age_eff_df = age_eff.reset_index().rename(columns={"Current Energy Efficiency": "Average Energy Efficiency"})

    fig3 = px.bar(age_eff_df, x="Average Energy Efficiency", y="CONSTRUCTION_AGE",
                  orientation="h", title="Average Energy Efficiency by Construction Age")
    fig3.update_layout(height=600)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("Analyze efficiency by **property type** (detached, flat, terrace, etc.).")

    property_filter = st.multiselect("Select Property Types:", df["PROPERTY_TYPE"].dropna().unique(), default=df["PROPERTY_TYPE"].dropna().unique())
    df_type = df[df["PROPERTY_TYPE"].isin(property_filter)]

    fig4 = px.box(df_type, x="PROPERTY_TYPE", y="Current Energy Efficiency",
                  title="Energy Efficiency by Property Type",
                  hover_data=["TENURE", "Amount", "CONSTRUCTION_AGE"])
    fig4.update_layout(height=500)
    st.plotly_chart(fig4, use_container_width=True)



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





