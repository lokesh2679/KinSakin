import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURATION (ROYAL THEME) ---
st.set_page_config(page_title="KinSakin Refinery", page_icon="💎", layout="centered")

# --- 2. CUSTOM CSS (Dark & Classy) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0e1117; color: #E0E0E0; }
    
    /* Headers - Champagne Gold */
    h1, h2, h3 { color: #C5A059 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 300; }
    
    /* Metrics */
    [data-testid="stMetricLabel"] { color: #C5A059 !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    
    /* PRIMARY ACTION BUTTON (The "Refine" Button) */
    .stButton>button {
        background-color: #C5A059;
        color: #000000;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 15px;
        font-size: 18px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFFFFF;
        box-shadow: 0px 0px 15px #C5A059;
    }

    /* Uploader Visibility */
    [data-testid="stFileUploader"] { border: 1px dashed #444; background-color: #161b22; }
    [data-testid="stFileUploader"] div, [data-testid="stFileUploader"] span { color: #E0E0E0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.title("KINSAKIN")
st.markdown("<p style='color: #888; margin-top: -20px; font-style: italic;'>The Sovereign Data Refinery</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. INPUT SECTION ---
uploaded_file = st.file_uploader("Drop raw data (CSV/Excel)", type=['csv', 'xlsx'])

# --- 5. THE ENGINE ---
if uploaded_file is not None:
    # A. LOAD DATA
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # B. AI DIAGNOSTICS (The "Recommendations")
    st.header("1. AI Diagnostics")
    
    # Calculate Dirt
    missing_count = df.isnull().sum().sum()
    duplicate_count = df.duplicated().sum()
    
    # Show the "Before" Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Rows", df.shape[0])
    c2.metric("Missing Values", missing_count, delta_color="inverse")
    c3.metric("Duplicates", duplicate_count, delta_color="inverse")

    # The AI "Voice" Advice
    if missing_count > 0 or duplicate_count > 0:
        st.warning(f"⚠️ **AI Recommendation:** Detected {missing_count} missing cells and {duplicate_count} duplicates. Recommended Action: Run Auto-Refine.")
    else:
        st.success("✅ **AI Recommendation:** Data appears clean. Ready for export.")

    # C. THE CLEANING STATION (The Missing Buttons)
    st.header("2. Refinery Controls")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        # OPTION 1: REMOVE DUPLICATES
        if st.checkbox("Remove Duplicates"):
            df = df.drop_duplicates()
            st.caption("Duplicates marked for removal.")
            
    with col_b:
        # OPTION 2: FILL MISSING DATA
        fill_strategy = st.selectbox("Handle Missing Data:", ["Do Nothing", "Fill with Zero", "Fill with Average", "Drop Rows"])

    # --- THE BIG BUTTON (ACTION) ---
    st.markdown("###") # Spacer
    if st.button("🚀 LAUNCH REFINERY (Clean Data)"):
        
        # Apply Cleaning Logic
        if fill_strategy == "Fill with Zero":
            df = df.fillna(0)
        elif fill_strategy == "Fill with Average":
            # Only fill numeric columns with average
            numeric_cols = df.select_dtypes(include=['number']).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            # Fill text columns with "Unknown"
            df = df.fillna("Unknown")
        elif fill_strategy == "Drop Rows":
            df = df.dropna()

        # SUCCESS STATE
        st.success("✨ Refinement Complete! Dust removed.")
        
        # D. VISUALS (The "After" View)
        st.header("3. Refined Intelligence")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Quick Graph
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            st.bar_chart(df[numeric_cols[0]], color="#C5A059")

        # E. EXPORT (The Gold Bar)
        st.header("4. Export Gold")
        
        # Convert to CSV for download
        csv_buffer = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Clean Data (CSV)",
            data=csv_buffer,
            file_name="kinsakin_refined_gold.csv",
            mime="text/csv"
        )

else:
    # Empty State
    st.info("Waiting for raw material... Upload a file to activate the AI.")
