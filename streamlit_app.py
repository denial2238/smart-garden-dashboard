import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- 1. CONFIG ---
st.set_page_config(page_title="Plant Care Dashboard", layout="wide", page_icon="🌿")
BASE_URL = "https://plants-110c1-default-rtdb.europe-west1.firebasedatabase.app"
plant_names = ["chamaedorea_elegans", "epipremnum", "spathiphyllum", "athyrium"]

st.title("🌿 My Plant Monitor (Public View)")

# --- 2. DATA FETCHING (Using simple HTTP requests) ---
@st.cache_data(ttl=30)
def fetch_data(plant_name):
    try:
        # Just a simple GET request to the .json endpoint
        response = requests.get(f"{BASE_URL}/{plant_name}.json")
        data = response.json()
        
        if not data:
            return pd.DataFrame()
        
        # Firebase returns a dictionary; convert to list for Pandas
        rows = [val for val in data.values()]
        df = pd.DataFrame(rows)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp')
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# --- 3. LIVE STATUS TILES ---
st.subheader("Live Status")
cols = st.columns(len(plant_names))

for i, name in enumerate(plant_names):
    df = fetch_data(name)
    with cols[i]:
        if not df.empty:
            latest = df.iloc[-1]
            moisture = latest['moisture']
            st.metric(
                label=name.replace("_", " ").title(), 
                value=f"{moisture}%",
                delta="DRY" if moisture < 30 else "OK",
                delta_color="normal" if moisture >= 30 else "inverse"
            )
            st.caption(f"Updated: {latest['timestamp'].strftime('%H:%M')}")
        else:
            st.metric(label=name.title(), value="N/A")

st.divider()

# --- 4. HISTORY GRAPHS ---
st.subheader("Moisture History")
selected_plant = st.selectbox("Select plant", plant_names)
df_plot = fetch_data(selected_plant)

if not df_plot.empty:
    fig = px.line(df_plot, x='timestamp', y='moisture', title=f'Trend: {selected_plant}')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data yet.")