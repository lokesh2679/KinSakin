import streamlit as st
import pandas as pd
import requests
import io
import time

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8011"
st.set_page_config(page_title="KinSakin | Data Cleaning AI", layout="wide", page_icon="✨")

# --- STYLING (The "Empire" Look) ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #d4af37; /* KinSakin Gold */
        text-align: center;
    }
    .stButton>button {
        background-color: #d4af37;
        color: black;
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
    }
    .success-box {
        padding: 15px;
        background-color: #1c2e24;
        border-left: 5px solid #28a745;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("✨ KinSakin")
st.markdown("<h3 style='text-align: center; color: #888;'>The Art of Golden Data Repair</h3>", unsafe_allow_html=True)
st.divider()

# --- SIDEBAR (Status & Stats) ---
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

    st.divider()
    st.markdown("### 🧠 Model Selector")
    # This is your Strategy implemented: Recommended Tag
    model_choice = st.selectbox(
        "Choose AI Engine:",
        ["Gemini 1.5 Flash (Recommended)", "GPT-4o mini (Coming Soon)", "Claude 3 Haiku (Coming Soon)"]
    )
    
    if "Recommended" in model_choice:
        st.info("⚡ Fastest & Most Reliable for general cleaning.")
    else:
        st.warning("🔒 This model is locked in the Prototype version.")

    st.divider()
    st.markdown("---")
    st.caption("v0.9.0 Prototype | Powered by KinSakin Engine")

# --- MAIN LOGIC ---
if not engine_status:
    st.warning("⚠️ The KinSakin Backend is not running. Please start the server terminal.")
    st.stop()

uploaded_file = st.file_uploader("Drop your messy file here (CSV)", type=["csv"])

if uploaded_file:
    # 1. SHOW RAW DATA
    st.subheader("1. Raw Inspection")
    try:
        raw_df = pd.read_csv(uploaded_file)
        st.dataframe(raw_df.head(5), use_container_width=True)
        st.caption(f"Detected {raw_df.shape[0]} rows and {raw_df.shape[1]} columns.")
    except:
        st.error("Could not preview raw file. It's really messy!")
    # ... (keep your existing file upload code) ...

    # ... (keep your existing file upload code) ...

        if uploaded_file is not None:
            # Load Data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # 1. The "Gold" (Clean Data)
                st.subheader("1. The Gold (Clean Data)")
                st.dataframe(df)

                # 2. The "Intel" (AI Summary)
                st.subheader("2. The Intelligence Report")
                
                # Create 3 Columns for KPIs
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Rows", df.shape[0])
                col1.metric("Total Columns", df.shape[1])
                
                # Check for Missing Values (The "Dust")
                missing_values = df.isnull().sum().sum()
                col2.metric("Missing Values (Dust)", missing_values)
                
                # Identify Numeric Columns for Analysis
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                col3.metric("Numeric Fields", len(numeric_cols))

                # 3. The "Vision" (Auto-Visuals)
                if len(numeric_cols) > 0:
                    st.subheader("3. Visual Insights")
                    # Let user pick what to graph
                    target_col = st.selectbox("Select a column to visualize:", numeric_cols)
                    
                    # Create a Line Chart
                    st.line_chart(df[target_col])
                    
                    # Create a Bar Chart
                    st.bar_chart(df[target_col])
                else:
                    st.info("No numeric data detected for visualization.")

            except Exception as e:
                st.error(f"Error processing file: {e}")    
    # 2. THE REPAIR BUTTON
    st.markdown("---")
    if st.button("✨ REPAIR DATA (KinSakin PROCESS)"):
        with st.spinner("Analyzing structure... Detecting entities... Applying Gold Lacquer..."):
            
            uploaded_file.seek(0)
            
            try:
                # SEND TO BACKEND
                files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                response = requests.post(f"{API_URL}/upload", files=files, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result['status'] == 'success':
                        st.balloons()
                        
                        clean_data = result['preview']
                        clean_df = pd.DataFrame(clean_data)
                        
                        # 3. DISPLAY RESULTS
                        st.subheader("2. Golden Result")
                        st.markdown(f'<div class="success-box">✅ Successfully repaired <b>{result["rows"]}</b> rows.</div>', unsafe_allow_html=True)
                        st.markdown("") 
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Cleaned Data Preview:**")
                            st.dataframe(clean_df, use_container_width=True)
                        
                        with col2:
                            st.markdown("**Data Health:**")
                            st.json({
                                "Columns Detected": result.get('detected_columns', list(clean_df.columns)),
                                "Status": "Optimized",
                                "AI Model": "Gemini 1.5 Flash"
                            })
                            
                        # 4. DOWNLOAD
                        csv = clean_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Polished CSV",
                            data=csv,
                            file_name=f"KinSakin_fixed_{uploaded_file.name}",
                            mime="text/csv",
                        )
                        
                    else:
                        st.error(f"Repair Failed: {result.get('reason')}")
                
                elif response.status_code == 429:
                    st.warning("⚠️ Rate Limit Hit. The server is cooling down. Please wait 30s and try again.")
                else:
                    st.error(f"Server Error ({response.status_code})")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")
