import streamlit as st
import pandas as pd
import google.generativeai as genai
import time
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="KinSakin Refinery", page_icon="💎", layout="wide")

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

# --- 3. SESSION STATE SETUP (The Memory Vault) ---
# This ensures data doesn't vanish when you click other buttons
if "clean_df" not in st.session_state:
    st.session_state.clean_df = None
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ SYSTEM STATUS")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Server", "Online", delta="🟢 Ready")
    col_s2.metric("Engine", "V18 Stable", delta="⚡ Persistent")
    
    st.markdown("---")
    
    # API Key Section
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
    
    model_map = {
        "Gemini 1.5 Flash (⭐ Best)": "gemini-1.5-flash",
        "Gemini 2.0 Flash Exp (⚡ Fast)": "gemini-2.0-flash-exp",
        "Gemini 1.5 Pro (🎓 Smart)": "gemini-1.5-pro"
    }
    selected_model_id = model_map[model_choice]

    st.markdown("---")
    
    # Cleaning Protocols
    st.header("🔧 Cleaning Protocols")
    drop_dupes = st.checkbox("Remove Duplicates", value=True)
    fill_strat = st.selectbox("Empty Number Strategy", ["Fill with Average", "Fill with 0", "Drop Rows"])
    
    # Reset Button
    if st.button("🔄 Reset All"):
        st.session_state.clean_df = None
        st.session_state.messages = []
        st.rerun()

# --- 5. OPTIMIZED DATA LOADER (Cache) ---
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
    try:
        # Load Data
        df = load_data(uploaded_file)
        
        # Raw Stats
        st.info(f"📂 File: {uploaded_file.name} | Total Rows: {df.shape[0]}")
        
        # --- SECTION A: CLEANING ---
        st.markdown("### 2. Action Zone")
        
        # The Button Logic
        if st.button("🚀 LAUNCH REFINERY (Clean Data Now)"):
            with st.spinner("Refining... This may take a moment for large files..."):
                # Perform Cleaning
                temp_df = df.copy()
                if drop_dupes: temp_df = temp_df.drop_duplicates()
                num_cols = temp_df.select_dtypes(include=['number']).columns
                if fill_strat == "Fill with Average":
                    temp_df[num_cols] = temp_df[num_cols].fillna(temp_df[num_cols].mean())
                elif fill_strat == "Fill with 0":
                    temp_df = temp_df.fillna(0)
                
                # SAVE TO SESSION STATE (This fixes the disappearing act)
                st.session_state.clean_df = temp_df
                st.success("✨ Data Purified Successfully!")
        
        # DISPLAY RESULT (If it exists in memory)
        if st.session_state.clean_df is not None:
            clean_df = st.session_state.clean_df
            
            c1, c2 = st.columns(2)
            c1.metric("Original Rows", df.shape[0])
            c2.metric("Cleaned Rows", clean_df.shape[0])
            
            # THE FIX FOR LARGE FILES: Only show preview, but confirm full size
            st.warning(f"⚠️ Displaying first 100 rows preview only (to keep browser fast). The download contains all {clean_df.shape[0]} rows.")
            st.dataframe(clean_df.head(100), use_container_width=True)
            
            # Download Button
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
                ai_prompt = f"DATA CONTEXT:\n{data_summary}\n\nUSER QUESTION:\n{prompt}"
                
                try:
                    if st.session_state.api_key: genai.configure(api_key=st.session_state.api_key)
                    model = genai.GenerativeModel(selected_model_id)
                    response = model.generate_content(ai_prompt)
                    
                    with st.chat_message("assistant"): st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"AI Error: {e}")
        else:
            st.info("🔒 Connect Key in Sidebar to Chat")

    except Exception as e:
        st.error(f"Error: {e}")
