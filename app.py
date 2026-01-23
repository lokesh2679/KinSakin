import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURATION (THE ROYAL THEME) ---
st.set_page_config(
    page_title="KinSakin Refinery",
    
    layout="centered", # 'centered' looks more elegant than 'wide' for this
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (THE "CLASSY" OVERHAUL) ---
st.markdown("""
    <style>
    /* Main Background - Deep "Obsidian" Grey (Not harsh black) */
    .stApp {
        background-color: #121212;
        color: #E0E0E0;
    }
    
    /* Headers - Champagne Gold */
    h1, h2, h3 {
        color: #C5A059 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 300; /* Thinner font looks more expensive */
        letter-spacing: 1px;
    }
    
    /* The "Browse Files" Widget Visibility Fix */
    [data-testid="stFileUploader"] {
        border: 1px dashed #444;
        border-radius: 10px;
        padding: 20px;
    }
    [data-testid="stFileUploader"] section {
        background-color: #1E1E1E; /* Slightly lighter card background */
    }
    /* Force text inside uploader to be visible */
    [data-testid="stFileUploader"] div, 
    [data-testid="stFileUploader"] span, 
    [data-testid="stFileUploader"] small {
        color: #E0E0E0 !important;
    }

    /* Dataframes - Make them blend in */
    div[data-testid="stDataFrame"] {
        border: 1px solid #333;
    }
    
    /* Metrics - Clean and White with Gold Label */
    [data-testid="stMetricLabel"] {
        color: #C5A059 !important;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    
    /* Button Styling - Matte Gold */
    .stButton>button {
        background-color: #C5A059;
        color: #000000;
        border-radius: 4px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #E6C275; /* Lighter gold on hover */
        box-shadow: 0px 4px 15px rgba(197, 160, 89, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. APP HEADER (NO LOGO, JUST TYPE) ---
st.title("KINSAKIN")
st.markdown("<p style='text-align: left; color: #888; margin-top: -20px; font-style: italic;'>The AI Data Refinery</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 4. THE FILE UPLOAD ---
uploaded_file = st.file_uploader("Drop your raw data here (CSV or Excel)", type=['csv', 'xlsx'])

# --- 5. THE REFINERY LOGIC ---
if uploaded_file is not None:
    try:
        # Load Data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # SECTION A: THE SUMMARY (NARRATIVE)
        st.header("Executive Summary")
        
        # Calculate Stats
        row_count = df.shape[0]
        col_count = df.shape[1]
        missing = df.isnull().sum().sum()
        duplicates = df.duplicated().sum()
        
        # Display Narrative Text (The "Classy" way to show data)
        st.markdown(f"""
        <div style="background-color: #1E1E1E; padding: 20px; border-radius: 5px; border-left: 3px solid #C5A059;">
            <p style="font-size: 16px; margin: 0;">
            This dataset contains <strong>{row_count:,}</strong> records across <strong>{col_count}</strong> columns. 
            We detected <strong>{missing}</strong> missing data points (dust) and <strong>{duplicates}</strong> duplicate rows.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick Metrics Row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{row_count:,}")
        c2.metric("Columns", col_count)
        c3.metric("Missing Values", missing)
        c4.metric("Duplicates", duplicates)

        # SECTION B: THE CLEAN DATA (PREVIEW)
        st.markdown("### Cleaned Data Preview")
        st.dataframe(df.head(50), use_container_width=True)

        # SECTION C: AUTOMATED VISUALS
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            st.markdown("### Visual Insights")
            tab1, tab2 = st.tabs(["📈 Trends", "📊 Distribution"])
            
            with tab1:
                target_col = st.selectbox("Select metric to analyze:", numeric_cols)
                st.line_chart(df[target_col], color="#C5A059") # Gold Line Chart
            
            with tab2:
                st.bar_chart(df[target_col], color="#555555") # Grey Bar Chart

    except Exception as e:
        st.error(f"Error reading file: {e}")

else:
    # Empty State (What they see before uploading)
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 50px;'>
        Waiting for raw material...
    </div>
    """, unsafe_allow_html=True)
