import streamlit as st
import pandas as pd
import io
import time

# --- 1. CONFIGURATION (CLEAN & PROFESSIONAL) ---
st.set_page_config(
    page_title="KinSakin Refinery",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. MINIMALIST CSS (Just for the Button) ---
st.markdown("""
    <style>
    /* Force a clean look */
    .stApp {
        background-color: #FFFFFF; /* Pure White */
        color: #000000;
    }
    
    /* Professional Header */
    h1, h2, h3 {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        color: #333333 !important;
    }
    
    /* The Action Button (Professional Blue) */
    .stButton>button {
        width: 100%;
        background-color: #0066CC; /* Corporate Blue */
        color: white;
        font-weight: bold;
        border-radius: 5px;
        height: 50px;
        font-size: 18px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #0052A3; /* Darker Blue on Hover */
    }
    
    /* Metric Styling */
    div[data-testid="stMetricValue"] {
        font-size: 26px;
        color: #0066CC;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE (Fixes Caching) ---
if 'data_history' not in st.session_state:
    st.session_state.data_history = []

# --- 4. HEADER ---
st.title("KinSakin Refinery")
st.markdown("**Status:** Ready | **Engine:** V12 Turbo")
st.markdown("---")

# --- 5. SIDEBAR INTAKE ---
st.sidebar.header("📥 Input Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])

# --- 6. MAIN ENGINE ---
if uploaded_file is not None:
    try:
        # A. READ DATA
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.sidebar.success(f"File Loaded: {uploaded_file.name}")
        
        # B. TUNING SHOP (Sidebar)
        st.sidebar.markdown("---")
        st.sidebar.header("⚙️ Cleaning Settings")
        
        # Strategies
        drop_dupes = st.sidebar.checkbox("Remove Duplicates", value=True)
        
        fill_num_strat = st.sidebar.selectbox(
            "Numeric Strategy", 
            ["Fill with Average", "Fill with 0", "Fill with Median", "Drop Rows"]
        )
        
        clean_text = st.sidebar.checkbox("Fix Text Capitalization", value=False)

        # C. DASHBOARD (Raw View)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", df.shape[0])
        c2.metric("Columns", df.shape[1])
        c3.metric("Missing Values", df.isnull().sum().sum())
        c4.metric("Duplicates", df.duplicated().sum())

        with st.expander("🔍 View Raw Data (Click to Expand)", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)

        # D. ACTION AREA
        st.write("")
        st.write("")
        if st.button("🚀 Run Cleaning Process"):
            
            # E. PROCESSING
            with st.spinner("Processing data..."):
                time.sleep(0.5) # UI Feedback
                
                clean_df = df.copy()
                numeric_cols = clean_df.select_dtypes(include=['number']).columns
                text_cols = clean_df.select_dtypes(include=['object']).columns

                # 1. Duplicates
                if drop_dupes:
                    clean_df = clean_df.drop_duplicates()

                # 2. Numeric
                if len(numeric_cols) > 0:
                    for col in numeric_cols:
                        if fill_num_strat == "Fill with Average":
                            clean_df[col] = clean_df[col].fillna(clean_df[col].mean())
                        elif fill_num_strat
