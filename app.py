import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="KinSakin Refinery", layout="wide")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3 { color: #333333 !important; font-family: 'Helvetica', sans-serif; }
    .stButton>button {
        width: 100%;
        background-color: #0066CC;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #004C99; transform: scale(1.02); }
    div[data-testid="stSidebar"] .stButton>button { background-color: #28a745; }
    [data-testid="stFileUploader"] { border: 2px dashed #0066CC; background-color: #F0F8FF; padding: 20px; }
    .stChatMessage { background-color: #F7F7F7; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE SETUP ---
if "clean_df" not in st.session_state:
    st.session_state.clean_df = None
if "last_file_id" not in st.session_state:
    st.session_state.last_file_id = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ SYSTEM STATUS")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Server", "Online", delta="🟢 Ready")
    col_s2.metric("Engine", "V19 Auto-Flush", delta="⚡ Secure")
    
    st.markdown("---")
    
    # API Key
    st.header("🔑 AI Access")
    user_key_input = st.text_input("Enter Google Gemini Key", type="password")
    if st.button("🔌 Connect Key"):
        if user_key_input:
            st.session_state.api_key = user_key_input
            st.success("✅ Key Connected!")
            time.sleep(1)
            st.rerun()

    # Model Selector
    st.header("🧠 AI Model")
    model_choice = st.selectbox("Select Intelligence:", 
                                ["Gemini 1.5 Flash (⭐ Best)", "Gemini 2.0 Flash Exp (⚡ Fast)", "Gemini 1.5 Pro (🎓 Smart)"])
    
    # Cleaning Protocols
    st.header("🔧 Cleaning Protocols")
    drop_dupes = st.checkbox("Remove Duplicates", value=True)
    fill_strat = st.selectbox("Empty Number Strategy", ["Fill with Average", "Fill with 0", "Drop Rows"])
    
    # Manual Reset
    if st.button("🔄 Reset All"):
        st.session_state.clean_df = None
        st.session_state.last_file_id = None
        st.session_state.messages = []
        st.rerun()

# --- 5. OPTIMIZED DATA LOADER ---
@st.cache_data(ttl=3600)
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file, engine='openpyxl')

# --- 6. MAIN WORKSPACE ---
st.title("KinSakin Data Refinery")
uploaded_file = st.file_uploader("Upload Raw Data (CSV/Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # --- AUTO-FLUSH LOGIC (The Fix) ---
    # Detect if this is a NEW file. If yes, clear old memory.
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_file_id != file_id:
        st.session_state.clean_df = None  # WIPE OLD DATA
        st.session_state.last_file_id = file_id # Update ID
        st.toast("New file detected. Workspace cleared.", icon="🧹")

    try:
        df = load_data(uploaded_file)
        
        # Raw Stats
        st.info(f"📂 File: {uploaded_file.name} | Total Rows: {df.shape[0]}")
        
        # --- SECTION A: CLEANING ---
        st.markdown("### 2. Action Zone")
        
        # Only show the button if we haven't cleaned this specific file yet
        if st.session_state.clean_df is None:
            if st.button("🚀 LAUNCH REFINERY (Clean Data Now)"):
                with st.spinner("Refining... Please wait..."):
                    temp_df = df.copy()
                    
                    # Cleaning Steps
                    if drop_dupes: temp_df = temp_df.drop_duplicates()
                    num_cols = temp_df.select_dtypes(include=['number']).columns
                    if fill_strat == "Fill with Average":
                        temp_df[num_cols] = temp_df[num_cols].fillna(temp_df[num_cols].mean())
                    elif fill_strat == "Fill with 0":
                        temp_df = temp_df.fillna(0)
                    
                    # Save Result
                    st.session_state.clean_df = temp_df
                    st.rerun() # Refresh to show results immediately
        
        # --- RESULTS DISPLAY ---
        if st.session_state.clean_df is not None:
            clean_df = st.session_state.clean_df
            
            # Metrics
            c1, c2 = st.columns(2)
            c1.metric("Original Rows", df.shape[0])
            c2.metric("Cleaned Rows", clean_df.shape[0])
            
            # Preview (Limited)
            st.warning(f"⚠️ PREVIEW ONLY: Showing first 100 rows. The download below contains all {clean_df.shape[0]} rows.")
            st.dataframe(clean_df.head(100), use_container_width=True)
            
            # DEBUG CHECK FOR YOU
            st.write(f"✅ **Ready to Download:** Packaging {clean_df.shape[0]} rows into CSV...")
            
            # Download
            csv = clean_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download FULL Clean Data (CSV)",
                data=csv,
                file_name=f"Cleaned_{uploaded_file.name}",
                mime="text/csv"
            )

        st.markdown("---")

        # --- SECTION B: AI CHAT ---
        st.markdown("### 3. Ask the Intelligence")
        
        if st.session_state.api_key:
            if "messages" not in st.session_state: st.session_state.messages = []
            
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])

            if prompt := st.chat_input("Ask about your data..."):
                st.chat_message("user").markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                # Context
                data_summary = df.head(10).to_string()
                model_map = {
                    "Gemini 1.5 Flash (⭐ Best)": "gemini-1.5-flash",
                    "Gemini 2.0 Flash Exp (⚡ Fast)": "gemini-2.0-flash-exp",
                    "Gemini 1.5 Pro (🎓 Smart)": "gemini-1.5-pro"
                }
                
                try:
                    if st.session_state.api_key: genai.configure(api_key=st.session_state.api_key)
                    # Use the correct model ID from the map
                    selected_model_id = model_map[model_choice] 
                    model = genai.GenerativeModel(selected_model_id)
                    
                    ai_prompt = f"DATA CONTEXT:\n{data_summary}\n\nUSER QUESTION:\n{prompt}"
                    response = model.generate_content(ai_prompt)
                    
                    with st.chat_message("assistant"): st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"AI Error: {e}")
        else:
            st.info("🔒 Connect Key in Sidebar to Chat")

    except Exception as e:
        st.error(f"Error: {e}")
