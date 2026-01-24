import streamlit as st
import pandas as pd
import io

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="KinSakin Refinery",
    page_icon="⚡",
    layout="centered"
)

# --- 2. DARK THEME CSS (Simple & Clean) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    h1 {
        color: #D4AF37; /* Gold Title */
    }
    .stButton>button {
        width: 100%;
        background-color: #D4AF37;
        color: black;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. APP HEADER ---
st.title("KINSAKIN")
st.write("The AI-Powered Data Refinery")
st.markdown("---")

# --- 4. FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload your messy data (CSV or Excel)", type=['csv', 'xlsx'])

# --- 5. MAIN LOGIC ---
if uploaded_file is not None:
    try:
        # Load the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Show Raw Data
        st.subheader("1. Raw Data (The Mess)")
        st.write(f"Rows: {df.shape[0]} | Columns: {df.shape[1]}")
        st.dataframe(df.head())

        # Show Missing Values
        missing_count = df.isnull().sum().sum()
        if missing_count > 0:
            st.warning(f"⚠️ Detected {missing_count} missing values.")
        else:
            st.success("✅ Data looks clean.")

        st.markdown("---")

        # --- THE CLEANING BUTTON ---
        if st.button("🚀 LAUNCH REFINERY (Clean Data)"):
            
            # Cleaning Logic (Auto-Fix)
            clean_df = df.copy()
            
            # 1. Fill numeric empty cells with the Average
            numeric_cols = clean_df.select_dtypes(include=['number']).columns
            clean_df[numeric_cols] = clean_df[numeric_cols].fillna(clean_df[numeric_cols].mean())
            
            # 2. Fill text empty cells with "Unknown"
            clean_df = clean_df.fillna("Unknown")
            
            # 3. Remove Duplicates
            clean_df = clean_df.drop_duplicates()

            st.success("✨ Data Successfully Refined!")
            
            # Show Clean Data
            st.subheader("2. Refined Gold (Clean Data)")
            st.dataframe(clean_df.head())

            # --- DOWNLOAD BUTTON ---
            csv = clean_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Clean CSV",
                data=csv,
                file_name="kinsakin_refined.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")

else:
    st.info("Upload a file to start the engine.")
