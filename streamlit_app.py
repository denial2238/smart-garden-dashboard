import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Plant Care", layout="wide", page_icon="🌿")

# Custom CSS to make buttons look like "Tiles" with images
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        height: 250px;
        border-radius: 15px;
        border: 1px solid #ddd;
        background-color: white;
        transition: transform 0.2s;
        padding: 0;
        overflow: hidden;
        display: block;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        border-color: #4CAF50;
    }
    .tile-img {
        width: 100%;
        height: 160px;
        object-fit: cover;
    }
    .tile-text {
        padding: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_stdio=True)

BASE_URL = "https://plants-110c1-default-rtdb.europe-west1.firebasedatabase.app"
plants = [
    {"id": "chamaedorea_elegans", "label": "Chamaedorea", "img": "public/chamaedorea_elegans.jpg"},
    {"id": "epipremnum", "label": "Epipremnum", "img": "public/epipremnum.jpg"},
    {"id": "spathiphyllum", "label": "Spathiphyllum", "img": "public/spathiphyllum.jpg"},
    {"id": "athyrium", "label": "Athyrium", "img": "public/athyrium.jpg"}
]

# Initialize session state to track which plant is selected
if 'selected_plant' not in st.session_state:
    st.session_state.selected_plant = plants[0]['id']

# --- 2. DATA FETCHING ---
@st.cache_data(ttl=30)
def fetch_data(plant_id):
    try:
        response = requests.get(f"{BASE_URL}/{plant_id}.json")
        data = response.json()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(list(data.values()))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp')
    except:
        return pd.DataFrame()

st.title("🌿 My Smart Garden")

# --- 3. CLICKABLE TILES GRID ---
st.subheader("Tap a plant to see history")
cols = st.columns(len(plants))

for i, p in enumerate(plants):
    df = fetch_data(p['id'])
    moisture = df.iloc[-1]['moisture'] if not df.empty else "N/A"
    
    with cols[i]:
        # We wrap the image and text inside the button using Markdown label
        tile_html = f'''
            <img src="{p['img']}" class="tile-img">
            <div class="tile-text">
                <b>{p['label']}</b><br>
                <span style="font-size: 20px; color: {'#e74c3c' if moisture != "N/A" and moisture < 30 else '#2ecc71'}">{moisture}%</span>
            </div>
        '''
        if st.button(p['label'], key=p['id'], help=f"Click for {p['label']} details"):
            st.session_state.selected_plant = p['id']

# --- 4. HISTORICAL GRAPH (The "Click Result") ---
st.divider()
selected_id = st.session_state.selected_plant
st.subheader(f"Detailed View: {selected_id.replace('_', ' ').title()}")

df_plot = fetch_data(selected_id)

if not df_plot.empty:
    fig = px.line(df_plot, x='timestamp', y='moisture', 
                  title=f"Moisture Levels for {selected_id}",
                  template="plotly_white")
    
    # UPDATED: Using width='stretch' as per 2026 requirements
    st.plotly_chart(fig, width='stretch')
else:
    st.warning("No historical data found for this plant.")