import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="Garden Dashboard", layout="wide")

BASE_URL = "https://plants-110c1-default-rtdb.europe-west1.firebasedatabase.app"
plants = [
    {"id": "chamaedorea_elegans", "label": "Chamaedorea", "file": "public/chamaedorea_elegans.jpg"},
    {"id": "epipremnum", "label": "Epipremnum", "file": "public/epipremnum.jpg"},
    {"id": "spathiphyllum", "label": "Spathiphyllum", "file": "public/spathiphyllum.jpg"},
    {"id": "athyrium", "label": "Athyrium", "file": "public/athyrium.jpg"}
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
    except:
        return pd.DataFrame()

st.title("🌿 Smart Garden")

# --- 3. THE TILE GRID (Native Method) ---
cols = st.columns(len(plants))

for i, p in enumerate(plants):
    with cols[i]:
        # Create a bordered container for the "Tile" look
        with st.container(border=True):
            # 1. Show the actual image file
            if os.path.exists(p['file']):
                st.image(p['file'], use_container_width=True)
            else:
                st.error(f"Missing: {p['file']}")
            
            # 2. Get data
            df = fetch_data(p['id'])
            latest_moist = f"{df.iloc[-1]['moisture']}%" if not df.empty else "--%"
            
            # 3. Big Name and Moisture Label
            st.markdown(f"### {p['label']}")
            st.markdown(f"**Moisture:** `{latest_moist}`")
            
            # 4. The Action Button (Click to select)
            # Use width='stretch' for the 2026 button standard
            if st.button(f"View History", key=p['id'], width='stretch'):
                st.session_state.selected_plant = p['id']
                st.rerun()

# --- 4. HISTORICAL GRAPH ---
st.divider()
sel_id = st.session_state.selected_plant
display_name = next((p['label'] for p in plants if p['id'] == sel_id), sel_id)

st.subheader(f"Detailed Analysis: {display_name}")
df_plot = fetch_data(sel_id)

if not df_plot.empty:
    fig = px.line(df_plot, x='timestamp', y='moisture', 
                  markers=True, template="plotly_white")
    
    # 2026 sizing standard
    st.plotly_chart(fig, width='stretch')
else:
    st.info("Select a plant above to see its moisture history.")