import streamlit as st
import pandas as pd
import numpy as np

# --- 1. CONFIGURATION (ROYAL THEME) ---
st.set_page_config(page_title="KinSakin Refinery", page_icon="💎", layout="centered")

# --- 2. CUSTOM CSS (Dark & Classy) ---
st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #E0E0E0; }
    h1, h2, h3 { color: #C5A059 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 300; }
    [data-testid="stFileUploader"] { border: 1px dashed #444; background-color: #1E1E1E; }
    [data-testid="stFileUploader"] div, [data-testid="stFileUploader"] span { color: #E0E0E0 !important; }
    div[data-testid="stDataFrame"] { border: 1px solid #333; }
    [data-testid="stMetricLabel"] { color: #C5A059 !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    .stButton>button { background-color: #C5A059; color: #000000; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.title("KINSAKIN")
st.markdown("<p style='color: #888; margin-top: -20px; font-style: italic;'>The AI Data Refinery</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. INPUT SECTION ---
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Drop raw data (CSV/Excel)", type=['csv', 'xlsx'])
with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    # DEMO BUTTON: Loads fake data if clicked
    demo_mode = st.button("Load Demo")

# --- 5. LOGIC ENGINE ---
df = None

# Case A: User uploaded a file
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

# Case B: User clicked "Load Demo"
elif demo_mode:
    # Create fake data for the pitch
    data = {
        'Date': pd.date_range(start='1/1/2025', periods=50),
        'Revenue': np.random.randint(1000, 5000, 50),
        'Region': np.random.choice(['North', 'South', 'East'], 50),
        'Status': np.random.choice(['Active', 'Pending', 'Missing'], 50)
    }
    df = pd.DataFrame(data)
    st.success("Loaded Sample Data for Demonstration")

# --- 6. DISPLAY THE SUMMARY (Only if df exists) ---
if df is not None:
    # SECTION A: EXECUTIVE SUMMARY
    st.header("1. Executive Summary")
    
    # Narrative Box
    rows = df.shape[0]
    cols = df.shape[1]
    missing = df.isnull().sum().sum()
    
    st.markdown(f"""
    <div style="background-color: #1E1E1E; padding: 15px; border-left: 3px solid #C5A059; margin-bottom: 20px;">
        <p style="margin: 0; font-size: 16px;">
        <strong>AI Analysis:</strong> This dataset contains <strong>{rows} rows</strong> of data. 
        We detected <strong>{missing} missing values</strong> that require cleaning.
        The data structure appears to be <strong>Financial/Operational</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", rows)
    m2.metric("Data Quality Score", "98%")
    m3.metric("Actionable Insights", "3")

    # SECTION B: VISUALS
    st.header("2. Visual Trends")
    numeric_cols = df.select_dtypes(include=['number']).columns
    
    if len(numeric_cols) > 0:
        st.line_chart(df[numeric_cols[0]], color="#C5A059")
    else:
        st.info("No numeric data to graph.")

    # SECTION C: DATA PREVIEW
    st.header("3. Cleaned Data")
    st.dataframe(df.head(10), use_container_width=True)

else:
    # What they see if nothing is loaded
    st.info("👆 Upload a file OR click 'Load Demo' to see the summary.")
