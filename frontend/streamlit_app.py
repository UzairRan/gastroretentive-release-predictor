import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from api_client import get_api_health, get_drug_types, predict_release_rate

# Page configuration
st.set_page_config(
    page_title="Gastroretentive Release Predictor",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colorful styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .sidebar-header {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 0.8rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .button-style {
        background-color: #764ba2;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>Gastroretentive Drug Release Rate Predictor</h1>
    <p>Predict how fast a drug is released from a gastroretentive tablet</p>
</div>
""", unsafe_allow_html=True)

# Check API connection
api_healthy = get_api_health()
if not api_healthy:
    st.sidebar.error("API server is not running. Please start the FastAPI backend first.")

# Sidebar colorful header
st.sidebar.markdown("""
<div class="sidebar-header">
    <h3>Input Parameters</h3>
</div>
""", unsafe_allow_html=True)

# Input fields
drug_type = st.sidebar.selectbox(
    "Drug Type",
    options=get_drug_types(),
    help="Type of drug being formulated"
)

st.sidebar.markdown("---")

dose_mg = st.sidebar.slider(
    "Dose (mg)",
    min_value=50.0,
    max_value=500.0,
    value=200.0,
    step=10.0,
    help="Amount of active pharmaceutical ingredient"
)

st.sidebar.markdown("---")

ph_stomach = st.sidebar.slider(
    "Stomach pH",
    min_value=1.5,
    max_value=5.0,
    value=3.0,
    step=0.1,
    help="Gastric pH level affects drug release"
)

st.sidebar.markdown("---")

desired_release_hr = st.sidebar.slider(
    "Desired Release Duration (hours)",
    min_value=2.0,
    max_value=12.0,
    value=6.0,
    step=0.5,
    help="Target time for complete drug release"
)

st.sidebar.markdown("---")

matrix_density = st.sidebar.slider(
    "Matrix Density (g/cm³)",
    min_value=0.5,
    max_value=1.2,
    value=0.85,
    step=0.01,
    help="Density affects floating ability"
)

st.sidebar.markdown("---")

temperature_c = st.sidebar.slider(
    "Temperature (°C)",
    min_value=36.0,
    max_value=38.5,
    value=37.0,
    step=0.1,
    help="Body temperature (physiological condition)"
)

# Main area columns
col1, col2 = st.columns(2, gap="large")

with col1:
    if st.button("Predict Release Rate", type="primary", use_container_width=True):
        if api_healthy:
            with st.spinner("Calculating release rate..."):
                prediction = predict_release_rate(
                    dose_mg=dose_mg,
                    ph_stomach=ph_stomach,
                    desired_release_hr=desired_release_hr,
                    matrix_density=matrix_density,
                    temperature_c=temperature_c,
                    drug_type=drug_type
                )
                
                if prediction:
                    st.session_state.prediction = prediction
                    st.session_state.dose_mg = dose_mg
                    st.session_state.release_hr = desired_release_hr
        else:
            st.error("Cannot predict: API server is not running")

with col2:
    if "prediction" in st.session_state:
        st.markdown("""
        <div class="prediction-card">
            <h3>Predicted Release Rate</h3>
            <h1>{} mg/hr</h1>
        </div>
        """.format(st.session_state.prediction), unsafe_allow_html=True)
        
        total_release_time = st.session_state.dose_mg / st.session_state.prediction if st.session_state.prediction > 0 else 0
        
        col2a, col2b = st.columns(2)
        with col2a:
            st.markdown("""
            <div class="metric-card">
                <h4>Total Release Time</h4>
                <h2>{:.1f} hours</h2>
            </div>
            """.format(total_release_time), unsafe_allow_html=True)
        
        with col2b:
            st.markdown("""
            <div class="metric-card">
                <h4>Total Dose</h4>
                <h2>{:.0f} mg</h2>
            </div>
            """.format(st.session_state.dose_mg), unsafe_allow_html=True)

# Visualization section
if "prediction" in st.session_state:
    st.markdown("---")
    st.markdown("## Release Profile Visualization")
    
    time_points = list(range(0, int(total_release_time) + 2))
    cumulative_release = [min(st.session_state.prediction * t, st.session_state.dose_mg) for t in time_points]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=cumulative_release,
        mode='lines+markers',
        name='Cumulative Release',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8, color='#764ba2')
    ))
    
    fig.add_hline(
        y=st.session_state.dose_mg,
        line_dash="dash",
        line_color="#f5576c",
        annotation_text="Total Dose",
        annotation_font_size=12
    )
    
    fig.update_layout(
        title=dict(
            text="Drug Release Profile Over Time",
            font=dict(size=18, color="#333"),
            x=0.5
        ),
        xaxis_title="Time (hours)",
        yaxis_title="Cumulative Drug Released (mg)",
        template="plotly_white",
        hovermode="x unified",
        plot_bgcolor="#f8f9fa",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    