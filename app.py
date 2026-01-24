import streamlit as st
import pandas as pd
import io
import time

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KinSakin Refinery",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS STYLING (Clean & Professional) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* Header Styling */
    h1, h2, h3 { color: #333333 !important; font-family: 'Helvetica', sans-serif; }
    
    /* STATUS INDICATORS (Sidebar) */
    div[data-testid="stMetricValue"] { font-size: 20px; }
    
    /* THE LAUNCH BUTTON (Big & Blue) */
    .stButton>button {
        width: 100%;
        background-color: #0066CC;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 15px;
        border-radius: 8px;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #004C99;
        transform: scale(1.02);
    }
    
    /* File Uploader Visibility */
    [data-testid="stFileUploader"] {
        border: 2px dashed #0066CC;
        background-color: #F0F8FF; /* Light Blue Tint */
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (The Cockpit) ---
with st.sidebar:
    st.title("⚙️ SYSTEM STATUS")
    
    # STATUS LIGHTS
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Server", "Online", delta="🟢 Ready")
    col_s2.metric("Engine", "V13 Turbo", delta="⚡ Active")
    
    st.markdown("---")
    
    # SETTINGS (Only appear if needed, but good to keep visible)
    st.header("🔧 Cleaning Protocols")
    drop_dupes = st.checkbox("Remove Duplicates", value=True)
    
    fill_strat = st.selectbox(
        "Empty Number Strategy", 
        ["Fill with Average", "Fill with 0", "Drop Rows", "Do Nothing"]
    )
    
    clean_text = st.checkbox("Standardize Text (Title Case)", value=False)
    
    st.markdown("---")
    st.caption("KinSakin Data Refinery © 2026")

# --- 4. MAIN SCREEN (The Workspace) ---
st.title("KinSakin Data Refinery")
st.markdown("### Upload Raw Data to Begin Purification")

# THE MAIN UPLOADER (Center Stage)
uploaded_file = st.file_uploader("", type=['csv', 'xlsx'], help="Drag and drop your messy CSV or Excel file here.")

# --- 5. ENGINE LOGIC ---
if uploaded_file is not None:
    # A. LOAD DATA
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # B. SHOW RAW STATS
        st.success(f"📂 File Loaded Successfully: {uploaded_file.name}")
        
        # 4-Column Stats
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", df.shape[0])
        c2.metric("Total Columns", df.shape[1])
        c3.metric("Missing Values", df.isnull().sum().sum())
        c4.metric("Duplicates", df.duplicated().sum())

        with st.expander("🔍 Preview Raw Data (Click to Open)", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)

        st.markdown("---")

        # C. THE LAUNCH BUTTON
        # This is the button you were missing. It only appears when a file is loaded.
        if st.button("🚀 LAUNCH REFINERY (Clean Data Now)"):
            
            with st.spinner("Processing... Cleaning Dust... Polishing Data..."):
                time.sleep(1) # Visual feedback
                
                # --- PROCESSING CORE ---
                clean_df = df.copy()
                numeric_cols = clean_df.select_dtypes(include=['number']).columns
                text_cols = clean_df.select_dtypes(include=['object']).columns

                # 1. Duplicates
                if drop_dupes:
                    clean_df = clean_df.drop_duplicates()

                # 2. Numeric Strategy
                if len(numeric_cols) > 0:
                    for col in numeric_cols:
                        if fill_strat == "Fill with Average":
                            clean_df[col] = clean_df[col].fillna(clean_df[col].mean())
                        elif fill_strat == "Fill with 0":
                            clean_df[col] = clean_df[col].fillna(0)
                
                if fill_strat == "Drop Rows":
                    clean_df = clean_df.dropna()

                # 3. Text Strategy
                if len(text_cols) > 0:
                    clean_df[text_cols] = clean_df[text_cols].fillna("Unknown")
                    if clean_text:
                        for col in text_cols:
                            clean_df[col] = clean_df[col].astype(str).str.title().str.strip()

                # --- RESULTS ---
                st.success("✨ Data Purification Complete!")
                
                # Comparison
                col_final1, col_final2 = st.columns(2)
                col_final1.metric("Original Dirt (Missing)", df.isnull().sum().sum())
                col_final2.metric("Final Dirt (Missing)", clean_df.isnull().sum().sum())
                
                st.dataframe(clean_df.head(20), use_container_width=True)
                
                # --- DOWNLOAD ---
                csv = clean_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Clean Data (CSV)",
                    data=csv,
                    file_name=f"Cleaned_{uploaded_file.name}",
                    mime="text/csv"
                )

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    # Empty State Instructions
    st.info("👆 Please upload a file above to activate the Launch Button.")
