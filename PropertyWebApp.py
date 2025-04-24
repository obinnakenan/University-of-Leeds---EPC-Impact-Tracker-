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
from streamlit_autorefresh import st_autorefresh

# Remount / keep-alive: refresh every 5 minutes (300 000 ms)
st_autorefresh(interval=300_000, limit=None, key="keep_alive")


# --- Page Config ---
st.set_page_config(
    page_title="EPC Impact Tracker: Housing, Inequality & Environment",
    layout="wide",
    page_icon="🏡"
)

# --- Banner and Title ---
st.image("Uni_Leeds_600_400.jpg", use_container_width=True)
st.markdown("## 🏡 EPC Impact Tracker: Housing, Inequality & Environment")

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "*Energy & enviromental impact*", "*Energy Gap in Housing*", "*Energy Ratings & Property Prices*",
    "*Regional Differences*", "*Modelling*","*Sustainability Insights*"
])



# --- Load and clean data ---
def load_data():
    df = pd.read_csv("merged_England_wales_EPC.csv")
    df['CURRENT_ENER_EFFICIENCY'] = pd.to_numeric(df['CURRENT_ENER_EFFICIENCY'], errors='coerce')
    df['POTENTIAL_ENERGY_EFFICIENCY'] = pd.to_numeric(df['POTENTIAL_ENERGY_EFFICIENCY'], errors='coerce')
    df['CO2_EMISS_CURR'] = pd.to_numeric(df['CO2_EMISS_CURR'], errors='coerce')
    df['CO2_EMISS_POTENT'] = pd.to_numeric(df['CO2_EMISS_POTENT'], errors='coerce')
    df['ENV_IMP_CURR'] = pd.to_numeric(df['ENV_IMP_CURR'], errors='coerce')
    df['ENV_IMP_POTENT'] = pd.to_numeric(df['ENV_IMP_POTENT'], errors='coerce')
    df['ENERGY_CONSUM_CURR'] = pd.to_numeric(df['ENERGY_CONSUM_CURR'], errors='coerce')
    df['ENERGY_CONSUM_POTEN'] = pd.to_numeric(df['ENERGY_CONSUM_POTEN'], errors='coerce')
    df['Region name'] = df['Region name'].fillna('Unknown')
    df['Price actual'] = pd.to_numeric(df['Price actual'], errors='coerce')
    return df

df = load_data()

with tab1:
    with st.container():
        # === filter for the region ===
        regions = sorted(df['Region name'].dropna().unique())
        selected_region = st.selectbox(
            "Select Region:", 
            ['All'] + regions, 
            key="region_selectbox"  # <-- Unique key added here
        )

        # Apply filter based on selection
        if selected_region == 'All':
            filtered_df = df
        else:
            filtered_df = df[df['Region name'] == selected_region]



        col1, col2 = st.columns(2)

        # === 1. Energy Efficiency Distribution ===
        with col1:
            plot_type = st.radio("Plot Type", ['Histogram', 'KDE'], horizontal=True)

            efficiency_df = filtered_df[['CURRENT_ENER_EFFICIENCY', 'POTENTIAL_ENERGY_EFFICIENCY']].melt(
                var_name="Type", value_name="Efficiency"
            )

            if plot_type == 'Histogram':
                fig1 = px.histogram(efficiency_df, x='Efficiency', color='Type', barmode='overlay', nbins=30)
            else:
                fig1 = px.density_contour(efficiency_df, x='Efficiency', color='Type')

            fig1.update_layout(title="Current vs Potential Energy Efficiency", hovermode='x')
            st.plotly_chart(fig1, use_container_width=True)

            avg_current = filtered_df['CURRENT_ENER_EFFICIENCY'].mean()
            avg_potential = filtered_df['POTENTIAL_ENERGY_EFFICIENCY'].mean()
            st.markdown(f"**📊 Average current efficiency:** {avg_current:.1f} | **Potential:** {avg_potential:.1f}. \
                This suggests an improvement opportunity of about **{avg_potential - avg_current:.1f} points**.")

        # === 2. CO2 Emissions Chart ===
        with col2:
            show_saving = st.checkbox("Show CO2 Saving", value=True)

            co2_current = filtered_df['CO2_EMISS_CURR'].sum()
            co2_potential = filtered_df['CO2_EMISS_POTENT'].sum()
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

        # === 3. Regional Comparison of EPC ===
        region_avg = filtered_df.groupby('Region name')['CURRENT_ENER_EFFICIENCY'].mean().reset_index()
        fig3 = px.bar(region_avg, x='CURRENT_ENER_EFFICIENCY', y='Region name', orientation='h',
                    labels={'CURRENT_ENER_EFFICIENCY': 'Avg Efficiency'})
        st.plotly_chart(fig3, use_container_width=True)

        top_region = region_avg.sort_values(by='CURRENT_ENER_EFFICIENCY', ascending=False).iloc[0]
        bottom_region = region_avg.sort_values(by='CURRENT_ENER_EFFICIENCY').iloc[0]
        st.markdown(f"**📍 Most efficient region:** {top_region['Region name']} ({top_region['CURRENT_ENER_EFFICIENCY']:.1f}) \
        | **Least efficient:** {bottom_region['Region name']} ({bottom_region['CURRENT_ENER_EFFICIENCY']:.1f})")

        # === 4. Environmental Impact Ratings ===
        st.markdown(" Environmental Impact Rating (Current vs Potential)")
        impact_df = filtered_df[['ENV_IMP_CURR', 'ENV_IMP_POTENT']].melt(var_name="Impact Type", value_name="Impact Score")
        fig_impact = px.histogram(impact_df, x="Impact Score", color="Impact Type", barmode="overlay", nbins=30)
        st.plotly_chart(fig_impact, use_container_width=True)

        st.markdown("This chart shows the shift in environmental impact scores. \
            If the potential scores are skewed to the left (lower values), it indicates a significant environmental improvement opportunity.")

        # === 5. Energy Consumption (kWh/m²) ===
        energy_df = filtered_df[['ENERGY_CONSUM_CURR', 'ENERGY_CONSUM_POTEN']].melt(
            var_name="Consumption Type", value_name="Energy Consumption")
        fig_energy = px.box(energy_df, x="Consumption Type", y="Energy Consumption", points="outliers")
        st.plotly_chart(fig_energy, use_container_width=True)

        st.markdown("Energy consumption typically decreases in the potential scenario. \
            This boxplot reveals the spread and outliers in both current and expected usage, offering a sense of variability.")

        # === 6. Least Efficient Properties ===
        st.markdown("🏚️ Top 10 Least Efficient Properties")
        least_efficient = filtered_df.sort_values(by="CURRENT_ENER_EFFICIENCY").head(10)
        st.dataframe(least_efficient[['Address', 'Region name', 'CURRENT_ENER_EFFICIENCY', 'POTENTIAL_ENERGY_EFFICIENCY']])
        st.markdown("These properties have the lowest energy efficiency ratings. \
            Targeting them could yield high-impact efficiency upgrades.")
        
        
        st.markdown(" 🏠 Efficiency and CO₂ by Property Type")
        # Group by and calculate averages
        property_type_avg = filtered_df.groupby('PROPERTY_TYPE')[['CURRENT_ENER_EFFICIENCY', 'CO2_EMISS_CURR']].mean().dropna().reset_index()

        # Plot
        fig_type = px.bar(
            property_type_avg.melt(id_vars='PROPERTY_TYPE'),
            x='PROPERTY_TYPE', y='value', color='variable', barmode='group',
            labels={"value": "Score / Emission", "variable": "Metric"}
        )
        st.plotly_chart(fig_type, use_container_width=True)

        # --- Dynamic Text Summary ---
        most_efficient = property_type_avg.sort_values('CURRENT_ENER_EFFICIENCY', ascending=False).iloc[0]
        least_efficient = property_type_avg.sort_values('CURRENT_ENER_EFFICIENCY').iloc[0]

        most_co2 = property_type_avg.sort_values('CO2_EMISS_CURR', ascending=False).iloc[0]
        least_co2 = property_type_avg.sort_values('CO2_EMISS_CURR').iloc[0]

        st.markdown(f"""
        - **Most energy-efficient** property type: **{most_efficient['PROPERTY_TYPE']}** with an average score of **{most_efficient['CURRENT_ENER_EFFICIENCY']:.1f}**.
        - **Least efficient**: **{least_efficient['PROPERTY_TYPE']}** at **{least_efficient['CURRENT_ENER_EFFICIENCY']:.1f}**.
        - **Highest CO₂ emissions**: **{most_co2['PROPERTY_TYPE']}** with **{most_co2['CO2_EMISS_CURR']:.1f} tonnes** on average.
        - **Lowest CO₂ emissions**: **{least_co2['PROPERTY_TYPE']}** with **{least_co2['CO2_EMISS_CURR']:.1f} tonnes**.

        This suggests that {most_co2['PROPERTY_TYPE'].lower()} homes could benefit the most from emission reduction efforts,
        while {most_efficient['PROPERTY_TYPE'].lower()} types are already performing well in energy efficiency.
        """)


        # === 8. Efficiency by Age ===
        st.markdown(" Average Efficiency by Construction Age")
        age_efficiency = filtered_df.groupby('CONSTRUCTION_AGE')['CURRENT_ENER_EFFICIENCY'].mean().dropna().reset_index()
        fig_age = px.bar(
            age_efficiency.sort_values('CURRENT_ENER_EFFICIENCY'),
            x='CURRENT_ENER_EFFICIENCY', y='CONSTRUCTION_AGE', orientation='h',
            labels={"CURRENT_ENER_EFFICIENCY": "Avg Efficiency"}
        )
        st.plotly_chart(fig_age, use_container_width=True)

        st.markdown("Older properties generally show lower efficiency ratings. \
            Buildings from more recent construction periods tend to be better insulated and more energy-efficient.")

        # === Download ===
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=filtered_df.to_csv(index=False),
            file_name='filtered_epc_data.csv',
            mime='text/csv'
        )




# === Tab 2 ===
with tab2:
    st.markdown("Explore how energy efficiency varies by **price** and **tenure**.")

    tenure_filter = st.multiselect("Select Tenure Types:", df["TENURE"].dropna().unique(), default=df["TENURE"].dropna().unique())
    filtered_df = df[df["TENURE"].isin(tenure_filter)]

    fig1 = px.box(filtered_df, x="TENURE", y="CURRENT_ENER_EFFICIENCY",
                  title="Energy Efficiency by Tenure Type",
                  labels={"CURRENT_ENER_EFFICIENCY": "Current Energy Efficiency"},
                  hover_data=["PROPERTY_TYPE", "Amount per week"])
    fig1.update_layout(xaxis_title="Tenure Type", yaxis_title="Energy Efficiency", height=500)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("#### 💡 Energy efficiency vs rent per week")
    fig2 = px.scatter(filtered_df, x="Amount per week", y="CURRENT_ENER_EFFICIENCY",
                      color="TENURE",
                      title="Energy Efficiency vs Rent per Week",
                      hover_data=["PROPERTY_TYPE", "CONSTRUCTION_AGE", "EPC Rating"])
    fig2.update_layout(height=500)
    st.plotly_chart(fig2, use_container_width=True)


    st.markdown("Compare average energy efficiency across **construction eras**.")

    age_eff = df.groupby("CONSTRUCTION_AGE")["CURRENT_ENER_EFFICIENCY"].mean().dropna().sort_values()
    age_eff_df = age_eff.reset_index().rename(columns={"CURRENT_ENER_EFFICIENCY": "Average Energy Efficiency"})

    fig3 = px.bar(age_eff_df, x="Average Energy Efficiency", y="CONSTRUCTION_AGE",
                  orientation="h", title="Average Energy Efficiency by Construction Age")
    fig3.update_layout(height=600)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("Analyze efficiency by **property type** (detached, flat, terrace, etc.).")

    property_filter = st.multiselect("Select Property Types:", df["PROPERTY_TYPE"].dropna().unique(), default=df["PROPERTY_TYPE"].dropna().unique())
    df_type = df[df["PROPERTY_TYPE"].isin(property_filter)]

    fig4 = px.box(df_type, x="PROPERTY_TYPE", y="CURRENT_ENER_EFFICIENCY",
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
            x='CURRENT_ENER_EFFICIENCY', 
            y='Price actual',
            color=color_option,
            trendline="ols",
            title=f"Price vs Energy Efficiency Score (Colored by {color_option.replace('_', ' ').title()})",
            labels={
                "CURRENT_ENER_EFFICIENCY": "Energy Efficiency Score", 
                "Price actual": "Price (£)"
            }
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # --- Smart Dynamic Text: Price Premiums by Efficiency ---
        high_efficiency = filtered_df[filtered_df['CURRENT_ENER_EFFICIENCY'] >= 80]['Price actual'].median()
        low_efficiency = filtered_df[filtered_df['CURRENT_ENER_EFFICIENCY'] <= 50]['Price actual'].median()

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
                avg_efficiency=('CURRENT_ENER_EFFICIENCY', 'mean'),
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
        x="CURRENT_ENER_EFFICIENCY", 
        y="Price actual", 
        z="Price actual",
        title=" 🌡️ Heatmap of Property Prices by Energy Efficiency",
        labels={"CURRENT_ENER_EFFICIENCY": "Energy Efficiency Score", "Price actual": "Price (£)"},
        nbinsx=30, nbinsy=30
    )
    fig_heatmap.update_layout(xaxis_title="Energy Efficiency Score", yaxis_title="Price (£)", coloraxis_colorbar_title="Density")
    st.plotly_chart(fig_heatmap, use_container_width=True)


    st.info("**Tip:** Upgrading a property's EPC rating can significantly boost its resale value and rental appeal — a win-win for both buyers and the environment. 🌍")


# === Tab 4 ===
with tab4:
    # Clean up data: drop rows with missing values needed for regression
    regression_df = df[['Region name', 'Price actual', 'CURRENT_ENER_EFFICIENCY']].dropna()
    regression_df = regression_df[regression_df['Price actual'] > 0]

    # --- Regional Regression Slopes ---
    region_stats = []

    for region in regression_df['Region name'].unique():
        sub_df = regression_df[regression_df['Region name'] == region]
        if len(sub_df) >= 10:  # Skip regions with insufficient data
            X = sub_df[['CURRENT_ENER_EFFICIENCY']]
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





