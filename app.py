import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="KinSakin Refinery", layout="wide")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3 { color: #333333 !important; font-family: 'Helvetica', sans-serif; }
    
    /* Main Action Button */
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
    
    /* Connect Button Specifics (Sidebar) */
    div[data-testid="stSidebar"] .stButton>button {
        background-color: #28a745; /* Green for Connect */
    }
    
    [data-testid="stFileUploader"] { border: 2px dashed #0066CC; background-color: #F0F8FF; padding: 20px; }
    .stChatMessage { background-color: #F7F7F7; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE SETUP ---
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.title("⚙️ SYSTEM STATUS")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Server", "Online", delta="🟢 Ready")
    col_s2.metric("Engine", "V17 Final", delta="⚡ Active")
    
    st.markdown("---")
    
    # --- A. API KEY SECTION (With Button) ---
    st.header("🔑 AI Access")
    
    # Input box
    user_key_input = st.text_input("Enter Google Gemini Key", type="password", help="Get free at aistudio.google.com")
    
    # The "Enter" Button
    if st.button("🔌 Connect Key"):
        if user_key_input:
            st.session_state.api_key = user_key_input
            st.success("✅ Key Connected!")
            time.sleep(1) # Brief pause for effect
            st.rerun() # Refresh to lock it in
        else:
            st.error("⚠️ Please enter a key first.")

    # Show connection status
    if st.session_state.api_key:
        st.caption("Status: Connected to Google Cloud")
        genai.configure(api_key=st.session_state.api_key)
    else:
        st.caption("Status: Disconnected")

    st.markdown("---")
    
    # --- B. MODEL SELECTOR (User Choice) ---
    st.header("🧠 AI Model")
    
    model_choice = st.selectbox(
        "Select Intelligence Level:",
        [
            "Gemini 1.5 Flash (⭐ Best/Stable)", 
            "Gemini 2.0 Flash Exp (⚡ Newest/Fast)", 
            "Gemini 1.5 Pro (🎓 High IQ)"
        ]
    )
    
    # Map the friendly names to the actual API ID
    model_map = {
        "Gemini 1.5 Flash (⭐ Best/Stable)": "gemini-1.5-flash",
        "Gemini 2.0 Flash Exp (⚡ Newest/Fast)": "gemini-2.0-flash-exp",
        "Gemini 1.5 Pro (🎓 High IQ)": "gemini-1.5-pro"
    }
    
    selected_model_id = model_map[model_choice]
    st.info(f"Engine Loaded: {model_choice.split('(')[0]}")

    st.markdown("---")
    
    # --- C. CLEANING TOOLS ---
    st.header("🔧 Cleaning Protocols")
    drop_dupes = st.checkbox("Remove Duplicates", value=True)
    fill_strat = st.selectbox("Empty Number Strategy", ["Fill with Average", "Fill with 0", "Drop Rows"])

# --- 5. MAIN WORKSPACE ---
st.title("KinSakin Data Refinery")
st.markdown("### 1. Upload Raw Data")
uploaded_file = st.file_uploader("", type=['csv', 'xlsx'])

# --- 6. OPTIMIZED ENGINE LOGIC ---

# A. THE CACHING FUNCTION (The Speed Boost)
@st.cache_data(ttl=3600) # Keep in memory for 1 hour
def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        # 'engine'='openpyxl' is faster for xlsx
        return pd.read_excel(file, engine='openpyxl') 

if uploaded_file is not None:
    # B. USE THE FUNCTION
    try:
        # Instead of reading directly, we ask the cache
        df = load_data(uploaded_file)
        
        st.success(f"📂 Loaded: {uploaded_file.name}")

        # ... (Rest of your code: Stats, Cleaning, etc.) ...
        
    except Exception as e:
        st.error(f"Error loading file: {e}")
    
    # RAW STATS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", df.isnull().sum().sum())
    c4.metric("Duplicates", df.duplicated().sum())

    # --- SECTION A: CLEANING ---
    st.markdown("### 2. Action Zone")
    if st.button("🚀 LAUNCH REFINERY (Clean Data Now)"):
        with st.spinner("Refining..."):
            time.sleep(1)
            clean_df = df.copy()
            
            # Cleaning Logic
            if drop_dupes: clean_df = clean_df.drop_duplicates()
            num_cols = clean_df.select_dtypes(include=['number']).columns
            if fill_strat == "Fill with Average":
                clean_df[num_cols] = clean_df[num_cols].fillna(clean_df[num_cols].mean())
            elif fill_strat == "Fill with 0":
                clean_df = clean_df.fillna(0)
            
            st.success("✨ Data Purified!")
            st.dataframe(clean_df)
            
            # Download
            csv = clean_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Clean CSV", csv, "clean_data.csv", "text/csv")

    st.markdown("---")

    # --- SECTION B: AI CHAT ---
    st.markdown("### 3. Ask the Intelligence (AI Chat)")
    
    if st.session_state.api_key:
        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ask your data anything..."):
            # 1. User Message
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 2. Context Logic
            data_summary = df.head(10).to_string()
            ai_prompt = f"""
            DATA CONTEXT:
            {data_summary}
            
            USER QUESTION:
            {prompt}
            
            Respond concisely.
            """

            # 3. AI Generation
            # 3. Get AI Response
            try:
                # USE THIS MODEL NAME - IT IS THE SAFE "FREE TIER" ROUTE
                model = genai.GenerativeModel('gemini-flash-latest') 
                
                response = model.generate_content(ai_prompt)
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI Connection Error: {e}")
    else:
        st.info("🔒 Connect your API Key in the Sidebar (Top Left) to unlock Chat.")
