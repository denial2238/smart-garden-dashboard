import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Plant Care 2026", layout="wide")

# Function to safely load and encode local images for CSS
def get_base64_image(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

st.markdown("""
    <style>
    /* Card/Tile styling */
    div.stButton > button {
        width: 100%;
        height: 320px;
        border-radius: 20px;
        border: none;
        color: white !important;
        /* Darker text shadow for readability on bright photos */
        text-shadow: 2px 2px 10px rgba(0,0,0,1);
        background-size: cover !important;
        background-position: center !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        transition: transform 0.3s ease;
        padding: 20px !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
    }
    /* Style for the big plant name and moisture label */
    .plant-label { font-size: 28px; font-weight: bold; margin-bottom: 5px; }
    .moisture-label { font-size: 18px; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True) # FIXED: Changed from unsafe_allow_stdio

BASE_URL = "https://plants-110c1-default-rtdb.europe-west1.firebasedatabase.app"
plants = [
    {"id": "chamaedorea_elegans", "name": "Chamaedorea", "file": "public/chamaedorea_elegans.jpg"},
    {"id": "epipremnum", "name": "Epipremnum", "file": "public/epipremnum.jpg"},
    {"id": "spathiphyllum", "name": "Spathiphyllum", "file": "public/spathiphyllum.jpg"},
    {"id": "athyrium", "name": "Athyrium", "file": "public/athyrium.jpg"}
]

if 'selected_plant' not in st.session_state:
    st.session_state.selected_plant = plants[0]['id']

# --- 2. DATA FETCHING ---
@st.cache_data(ttl=30)
def fetch_data(plant_id):
    try:
        r = requests.get(f"{BASE_URL}/{plant_id}.json")
        data = r.json()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(list(data.values()))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp')
    except: return pd.DataFrame()

st.title("🌿 My Smart Garden")

# --- 3. TILES WITH BACKGROUND IMAGES ---
cols = st.columns(len(plants))

for i, p in enumerate(plants):
    df = fetch_data(p['id'])
    val = f"{df.iloc[-1]['moisture']}%" if not df.empty else "--%"
    
    # Inject CSS background for each specific button key
    img_b64 = get_base64_image(p['file'])
    if img_b64:
        st.markdown(f"""
            <style>
            button[key="{p['id']}"] {{
                background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.6)), 
                            url(data:image/jpeg;base64,{img_b64});
            }}
            </style>
            """, unsafe_allow_html=True)
    
    with cols[i]:
        # Label uses newline to separate Name and Moisture
        if st.button(f"{p['name']}\n\n{val}", key=p['id']):
            st.session_state.selected_plant = p['id']

# --- 4. HISTORY CHART ---
st.divider()
sel = st.session_state.selected_plant
st.subheader(f"History: {sel.replace('_', ' ').title()}")

df_plot = fetch_data(sel)
if not df_plot.empty:
    fig = px.line(df_plot, x='timestamp', y='moisture', 
                  template="plotly_dark", markers=True)
    
    # FIXED: Replaced use_container_width=True with width='stretch'
    st.plotly_chart(fig, width='stretch')
else:
    st.info("Waiting for data...")