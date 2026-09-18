import streamlit as st
import pandas as pd
import requests

# Set page configuration
st.set_page_config(page_title="Vietnam Weather & Solar Data", layout="wide")

st.title("⛅ Vietnam Weather & Solar Radiation Dashboard")
st.markdown("Collect historical and forecast data from Open-Meteo for any coordinate in Vietnam.")

# --- SIDEBAR: USER INPUTS ---
st.sidebar.header("Configuration")

# Quick-select cities
cities = {
    "Custom Coordinates": {"lat": 14.0583, "lon": 108.2772},
    "Hanoi (North)": {"lat": 21.0285, "lon": 105.8542},
    "Da Nang (Central)": {"lat": 16.0678, "lon": 108.2208},
    "Ho Chi Minh City (South)": {"lat": 10.8231, "lon": 106.6297}
}

selected_city = st.sidebar.selectbox("Select Location", list(cities.keys()))

# Coordinate Inputs
lat = st.sidebar.number_input("Latitude", value=cities[selected_city]["lat"], format="%.4f")
lon = st.sidebar.number_input("Longitude", value=cities[selected_city]["lon"], format="%.4f")

st.sidebar.markdown("---")

# Day Selectors
st.sidebar.subheader("Timeframe")
past_days = st.sidebar.slider("Historical Data (Days)", min_value=0, max_value=90, value=7)
forecast_days = st.sidebar.slider("Forecast Data (Days)", min_value=0, max_value=14, value=3)

# --- DATA FETCHING LOGIC ---
@st.cache_data(show_spinner=False)
def fetch_weather_data(latitude, longitude, past, forecast):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,relative_humidity_2m,shortwave_radiation,direct_radiation,direct_normal_irradiance",
        "timezone": "Asia/Bangkok",
        "past_days": past,
        "forecast_days": forecast
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    hourly = data["hourly"]
    df = pd.DataFrame({
        "Time (ICT)": pd.to_datetime(hourly["time"]),
        "Temperature (°C)": hourly["temperature_2m"],
        "Humidity (%)": hourly["relative_humidity_2m"],
        "GHI Solar Radiation (W/m²)": hourly["shortwave_radiation"],
        "Direct Radiation (W/m²)": hourly["direct_radiation"],
        "DNI Solar Radiation (W/m²)": hourly["direct_normal_irradiance"]
    })
    return df

# --- MAIN INTERFACE ---
if st.sidebar.button("Fetch Data", type="primary", use_container_width=True):
    with st.spinner("Fetching data from Open-Meteo..."):
        try:
            df = fetch_weather_data(lat, lon, past_days, forecast_days)
            
            # --- CHARTS ---
            st.subheader("📈 Solar Radiation (GHI)")
            st.line_chart(df.set_index("Time (ICT)")["GHI Solar Radiation (W/m²)"], color="#f39c12")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🌡️ Temperature (°C)")
                st.line_chart(df.set_index("Time (ICT)")["Temperature (°C)"], color="#e74c3c")
            with col2:
                st.subheader("💧 Humidity (%)")
                st.line_chart(df.set_index("Time (ICT)")["Humidity (%)"], color="#3498db")
            
            # --- DATA TABLE & CSV DOWNLOAD ---
            st.markdown("---")
            st.subheader("📊 Raw Data")
            st.dataframe(df, use_container_width=True)
            
            # Convert dataframe to CSV
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download Data as .CSV",
                data=csv,
                file_name=f"weather_data_{lat}_{lon}.csv",
                mime="text/csv",
                help="CSV is lightweight, opens in Excel, and requires no external software to read."
            )
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")
else:
    st.info("👈 Adjust your settings in the sidebar and click **Fetch Data** to begin.")