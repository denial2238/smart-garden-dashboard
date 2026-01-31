import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. MODERN PAGE CONFIG & STYLING ---
st.set_page_config(page_title="GardenOS", layout="wide", page_icon="🌿")

# Custom CSS for Light Modern Look
st.markdown("""
    <style>
    /* Clean White Background */
    .stApp {
        background-color: #ffffff;
        color: #31333F;
    }
    
    /* Card Styling for Light Theme */
    div[data-testid="stMetric"] {
        background: rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(0, 0, 0, 0.05);
        padding: 15px;
        border-radius: 15px;
    }
    
    /* Custom Container styling (Cards) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px !important;
        border: 1px solid #eeeeee !important;
        background: #ffffff !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02) !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.05) !important;
    }

    /* Button Styling */
    .stButton > button {
        border-radius: 12px !important;
        background: #4caf50 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    .stButton > button:hover {
        background: #45a049 !important;
        color: white !important;
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
            # Changed text color to dark gray for white background
            number = {'suffix': "°C", 'font': {'color': "#31333F", 'size': 50}},
            gauge = {
                'axis': {'range': [-40, 40], 'tickwidth': 1, 'tickcolor': "#31333F"},
                'bar': {'color': "#4caf50"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#eeeeee",
                'steps': [
                    {'range': [-40, 0], 'color': "#e3f2fd"},
                    {'range': [0, 18], 'color': "#f1f8e9"},
                    {'range': [18, 28], 'color': "#c8e6c9"},
                    {'range': [28, 40], 'color': "#fff9c4"}
                ]
            }
        ))
        fig_temp.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_temp, width='stretch')

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
            m_color = "#2e7d32" if moist > 30 else "#ef6c00" if moist > 15 else "#d32f2f"
            
            st.markdown(f"#### {p['label']}")
            st.markdown(f"**Soil Moisture:** <span style='color:{m_color}; font-size:24px; font-weight:bold;'>{moist}%</span>", unsafe_allow_html=True)
            
            if st.button("Analytics", key=p['id'], width='stretch'):
                st.session_state.selected_plant = p['id']
                st.rerun()

# --- 5. ANALYTICS (Fixed Graph) ---
st.markdown("---")
sel_id = st.session_state.selected_plant
display_name = next((p['label'] for p in plants if p['id'] == sel_id), sel_id)

st.subheader(f"📊 {display_name} History")
df_plot = fetch_data(sel_id)

if not df_plot.empty:
    # Switched to plotly_white template
    fig = px.area(df_plot, x='timestamp', y='moisture', 
                  template="plotly_white",
                  line_shape='spline')
    
    fig.update_traces(
        line_color='#4caf50', 
        fillcolor='rgba(76, 175, 80, 0.2)'
    )
    
    fig.update_layout(
        hovermode="x unified",
        yaxis=dict(
            range=[0, 105], 
            gridcolor='#f0f0f0',
            title="Moisture %"
        ),
        xaxis=dict(
            gridcolor='#f0f0f0',
            title="Time"
        ),
        # Ensure the chart area is purely white
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    st.plotly_chart(fig, width='stretch')