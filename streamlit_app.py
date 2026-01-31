import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
import os

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Garden Dashboard", layout="wide")

def get_base64(bin_file):
    base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, bin_file)
    if not os.path.exists(full_path):
        return ""
    with open(full_path, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# CSS for full-tile clickable buttons with background images
st.markdown("""
    <style>
    div.stButton > button {
        width: 100% !important;
        height: 300px !important;
        border: none !important;
        border-radius: 20px !important;
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.9) !important;
        background-size: cover !important;
        background-position: center !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-end !important;
        padding-bottom: 20px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        white-space: pre-wrap !important; /* Vital for the \n line break */
    }
    div.stButton > button:hover {
        transform: translateY(-5px);
        filter: brightness(1.1);
    }
    </style>
    """, unsafe_allow_html=True)

BASE_URL = "https://plants-110c1-default-rtdb.europe-west1.firebasedatabase.app"
plants = [
    {"id": "chamaedorea_elegans", "label": "Chamaedorea", "file": "public/chamaedorea_elegans.jpg"},
    {"id": "epipremnum", "label": "Epipremnum", "file": "public/epipremnum.jpg"},
    {"id": "spathiphyllum", "label": "Spathiphyllum", "file": "public/spathiphyllum.jpg"},
    {"id": "athyrium", "label": "Athyrium", "file": "public/athyrium.jpg"}
]

# Initialize selection state
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

# --- 3. CLICKABLE TILES GRID ---
st.subheader("Tap a plant to view historical data")
cols = st.columns(len(plants))

for i, p in enumerate(plants):
    df = fetch_data(p['id'])
    latest_moist = f"{df.iloc[-1]['moisture']}%" if not df.empty else "--%"
    
    # Inject background image CSS for this specific button
    img_b64 = get_base64(p['file'])
    if img_b64:
        st.markdown(f"""
            <style>
            button[key="{p['id']}"] {{
                background: linear-gradient(0deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.1) 60%), 
                            url(data:image/jpeg;base64,{img_b64}) !important;
                background-size: cover !important;
            }}
            </style>
            """, unsafe_allow_html=True)
    
    with cols[i]:
        # Label combines Name (Big) and Moisture (Underneath)
        label = f"{p['label']}\n{latest_moist}"
        if st.button(label, key=p['id']):
            st.session_state.selected_plant = p['id']
            st.rerun() # Force the app to update the graph immediately

# --- 4. HISTORICAL GRAPH ---
st.divider()
sel_id = st.session_state.selected_plant
display_name = next((p['label'] for p in plants if p['id'] == sel_id), sel_id)

st.subheader(f"Detailed View: {display_name}")

df_plot = fetch_data(sel_id)

if not df_plot.empty:
    fig = px.line(df_plot, x='timestamp', y='moisture', 
                  markers=True, template="plotly_white")
    
    # Modern 2026 sizing
    st.plotly_chart(fig, width='stretch')
else:
    st.warning("No data found for this selection.")