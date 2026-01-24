import streamlit as st
import pandas as pd
import io
import requests

# --- 1. CONFIGURATION (MUST BE FIRST) ---
API_URL = "http://127.0.0.1:9000"
st.set_page_config(
    page_title="KinSakin Refinery",
    page_icon="💎",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (ROYAL THEME) ---
st.markdown("""
    <style>
    /* Main Background - white */
    .stApp { background-color: #0e1117;
color: #E0E0E0; }
    
    /* Headers - Champagne Gold */
    h1, h2, h3 { color: #C5A059 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 300; }
    
    /* Metrics & Text */
    [data-testid="stMetricLabel"] { color: #C5A059 !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    p, li, label { color: #B0B0B0; }
    
    /* ACTION BUTTONS */
    .stButton>button {
        background-color: #C5A059;
        color: #000000;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 12px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFFFFF;
        box-shadow: 0px 0px 15px #C5A059;
    }

    /* UPLOADER STYLING */
    [data-testid="stFileUploader"] { border: 1px dashed #444; background-color: #161b22; }
    [data-testid="stFileUploader"] div, [data-testid="stFileUploader"] span { color: #E0E0E0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.title("KINSAKIN")
st.markdown("<p style='color: #888; margin-top: -20px; font-style: italic;'>The Sovereign Data Refinery</p>", unsafe_allow_html=True)
st.markdown("---")
with st.sidebar:
    st.header("System Status")
    try:
        # Quick ping to see if server is up
        response = requests.get(f"{API_URL}/docs", timeout=2)
        if response.status_code == 200:
            st.success("🟢 Engine Online (Port 8011)")
            engine_status = True
        else:
            st.error("🔴 Engine Offline")
            engine_status = False
    except:
        st.error("🔴 Engine Offline")
        st.warning("Run: `python server.py`")
        engine_status = False


# --- 4. ENGINE LOGIC ---
try:
    # FILE UPLOAD
    uploaded_file = st.file_uploader("Drop raw data (CSV or Excel)", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        # READ DATA
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # A. AI DIAGNOSTICS
        st.header("1. AI Diagnostics")
        missing_count = df.isnull().sum().sum()
        duplicate_count = df.duplicated().sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Rows", df.shape[0])
        c2.metric("Missing Values", missing_count)
        c3.metric("Duplicates", duplicate_count)

        if missing_count > 0 or duplicate_count > 0:
            st.warning(f"⚠️ **Analysis:** Found {missing_count} missing cells and {duplicate_count} duplicates. \n\n**Recommendation:** Run Auto-Refine.")
        else:
            st.success("✅ **Analysis:** Data is pristine. Ready for export.")

        # B. REFINERY CONTROLS
        st.header("2. Refinery Controls")
        
        col_clean1, col_clean2 = st.columns(2)
        with col_clean1:
            remove_dupes = st.checkbox("Remove Duplicates", value=True)
        with col_clean2:
            fill_mode = st.selectbox("Missing Data Strategy", ["Fill with Zero (0)", "Fill with Average", "Drop Rows", "Do Nothing"])

        st.write("") # Spacer
        
        # C. THE LAUNCH BUTTON
        if st.button("🚀 LAUNCH REFINERY (Clean Data)"):
            
            # --- CLEANING LOGIC ---
            clean_df = df.copy()
            
            # 1. Duplicates
            if remove_dupes:
                clean_df = clean_df.drop_duplicates()
            
            # 2. Missing Data
            if fill_mode == "Fill with Zero (0)":
                clean_df = clean_df.fillna(0)
            elif fill_mode == "Fill with Average":
                # Smart Fill: Average for numbers, "Unknown" for text
                num_cols = clean_df.select_dtypes(include=['number']).columns
                clean_df[num_cols] = clean_df[num_cols].fillna(clean_df[num_cols].mean())
                clean_df = clean_df.fillna("Unknown")
            elif fill_mode == "Drop Rows":
                clean_df = clean_df.dropna()

            st.success("✨ Process Complete. Gold extracted.")

            # D. RESULTS (Visuals + Download)
            st.header("3. Refined Intelligence")
            st.dataframe(clean_df.head(50), use_container_width=True)
            
            # Smart Charting
            numeric_cols = clean_df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                st.bar_chart(clean_df[numeric_cols[0]], color="#C5A059")

            # E. EXPORT
            csv = clean_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Gold (CSV)",
                data=csv,
                file_name="kinsakin_refined.csv",
                mime="text/csv"
            )

    else:
        # EMPTY STATE (Instructions)
        st.info("Waiting for raw material... Upload a CSV or Excel file to begin.")

except Exception as e:
    st.error(f"System Error: {e}")
