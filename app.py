import streamlit as st
import pandas as pd
import google.generativeai as genai
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="KinSakin Refinery", page_icon="🧬", layout="wide")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    h1, h2, h3 { color: #333333 !important; font-family: 'Helvetica', sans-serif; }
    .stButton>button {
        width: 100%;
        background-color: #0066CC;
        color: white;
        font-size: 20px;
        font-weight: bold;
        padding: 15px;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #004C99; transform: scale(1.02); }
    [data-testid="stFileUploader"] { border: 2px dashed #0066CC; background-color: #F0F8FF; padding: 20px; }
    
    /* Chat Styling */
    .stChatMessage { background-color: #F7F7F7; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SIDEBAR (API KEY INPUT) ---
with st.sidebar:
    st.title("⚙️ SYSTEM STATUS")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("Server", "Online", delta="🟢 Ready")
    col_s2.metric("Engine", "Hybrid V15", delta="⚡ AI+Python")
    
    st.markdown("---")
    st.header("🔑 AI Access Key")
    # We ask for the key here so it's secure
    api_key = st.text_input("Enter Google Gemini API Key", type="password", help="Get free at aistudio.google.com")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ AI Connected")
    else:
        st.warning("⚠️ AI Disconnected")

    st.markdown("---")
    st.header("🔧 Cleaning Protocols")
    drop_dupes = st.checkbox("Remove Duplicates", value=True)
    fill_strat = st.selectbox("Empty Number Strategy", ["Fill with Average", "Fill with 0", "Drop Rows"])

# --- 4. MAIN WORKSPACE ---
st.title("KinSakin Data Refinery")
st.markdown("### 1. Upload Raw Data")
uploaded_file = st.file_uploader("", type=['csv', 'xlsx'])

# --- 5. ENGINE LOGIC ---
if uploaded_file is not None:
    # LOAD DATA
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success(f"📂 Loaded: {uploaded_file.name}")
    
    # RAW STATS
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", df.shape[0])
    c2.metric("Columns", df.shape[1])
    c3.metric("Missing", df.isnull().sum().sum())
    c4.metric("Duplicates", df.duplicated().sum())

    # --- SECTION A: THE ACTION (CLEANING) ---
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
            st.dataframe(clean_df.head())
            
            # Download
            csv = clean_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Clean CSV", csv, "clean_data.csv", "text/csv")

    st.markdown("---")

    # --- SECTION B: THE INSIGHT (CHAT WITH VECTORS) ---
    st.markdown("### 3. Ask the Analyst (AI Chat)")
    
    if api_key:
        # Initialize Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ask a question about your data (e.g., 'What is the trend?')"):
            # 1. Show User Message
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 2. Prepare Data Context (The Vector Input)
            # We send a summary of the data, not the whole thing (to save tokens)
            data_summary = df.head(10).to_string()
            stats_summary = df.describe().to_string()
            
            ai_prompt = f"""
            Act as a Senior Data Analyst. Here is a sample of the dataset:
            {data_summary}
            
            Here are the statistics:
            {stats_summary}
            
            User Question: {prompt}
            
            Answer concisely and professionally.
            """

            # 3. Get AI Response
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(ai_prompt)
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"AI Error: {e}")
    else:
        st.info("🔒 Enter your API Key in the Sidebar to unlock the Chat feature.")
