import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. MODERN PAGE CONFIG & STYLING ---
st.set_page_config(page_title="GardenOS", layout="wide", page_icon="🌿")

# Custom CSS for Modern Glassmorphism Look
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #121212 100%);
        color: #e0e0e0;
    }
    
    /* Card Styling */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        backdrop-filter: blur(10px);
    }
    
    /* Custom Container styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.03) !important;
        transition: transform 0.3s ease;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.07) !important;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 12px !important;
        background: #4caf50 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
    }
    
    .stButton > button:hover {
        background: #66bb6a !important;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.4) !important;
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

if 'selected_plant' not in st.session_state:
    st.session_state.selected_plant = plants[0]['id']

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=30)
def fetch_data(path):
    try:
        r = requests.get(f"{BASE_URL}/{path}.json")
        data = r.json()
        if not data: return pd.DataFrame()
        df = pd.DataFrame(list(data.values()))
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df.sort_values('timestamp')
    except: return pd.DataFrame()

# --- 3. TOP HERO SECTION (Thermostat) ---
st.title("🌿 Garden Control Center")

temp_df = fetch_data("ambient_temperature")
curr_temp = temp_df.iloc[-1]['value'] if not temp_df.empty else None

t_col1, t_col2, t_col3 = st.columns([1, 2, 1])

with t_col2:
    if curr_temp is not None:
        fig_temp = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = curr_temp,
            number = {'suffix': "°C", 'font': {'color': "#ffffff", 'size': 50}},
            gauge = {
                'axis': {'range': [-40, 40], 'tickwidth': 1, 'tickcolor': "#888"},
                'bar': {'color': "#4caf50"},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [-40, 0], 'color': "rgba(33, 150, 243, 0.3)"},
                    {'range': [0, 18], 'color': "rgba(255, 255, 255, 0.1)"},
                    {'range': [18, 28], 'color': "rgba(76, 175, 80, 0.2)"},
                    {'range': [28, 40], 'color': "rgba(244, 67, 54, 0.3)"}
                ]
            }
        ))
        fig_temp.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_temp, width='stretch')
    else:
        st.warning("Awaiting sensor data...")

st.markdown("---")

# --- 4. PLANT GRID ---
st.subheader("Sensor Network")
cols = st.columns(len(plants))

for i, p in enumerate(plants):
    with cols[i]:
        with st.container(border=True):
            if os.path.exists(p['file']):
                st.image(p['file'], use_container_width=True)
            
            df = fetch_data(p['id'])
            moist = df.iloc[-1]['moisture'] if not df.empty else 0
            
            # Dynamic color for moisture
            m_color = "#66bb6a" if moist > 30 else "#ffa726" if moist > 15 else "#ef5350"
            
            st.markdown(f"#### {p['label']}")
            st.markdown(f"**Soil Moisture:** <span style='color:{m_color}; font-size:24px; font-weight:bold;'>{moist}%</span>", unsafe_allow_html=True)
            
            if st.button("Analytics", key=p['id'], width='stretch'):
                st.session_state.selected_plant = p['id']
                st.rerun()

# --- 5. ANALYTICS ---
st.markdown("---")
sel_id = st.session_state.selected_plant
display_name = next((p['label'] for p in plants if p['id'] == sel_id), sel_id)

st.subheader(f"📊 {display_name} History")
df_plot = fetch_data(sel_id)

if not df_plot.empty:
    fig = px.area(df_plot, x='timestamp', y='moisture', 
                  template="plotly_dark",
                  line_shape='spline')
    fig.update_traces(line_color='#4caf50', fillcolor='rgba(76, 175, 80, 0.1)')
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.1)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig, width='stretch')