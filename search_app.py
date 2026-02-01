import streamlit as st
import pandas as pd
import urllib.parse
import easyocr
import numpy as np
from PIL import Image

# Initialize OCR reader
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('SortCart.csv')
    unique_streets = sorted(df['StreetName'].unique())
    return df, unique_streets

df, street_list = load_data()

def make_map_link(row, specific_no=None):
    num = specific_no if specific_no else row['StreetNoMin']
    address = f"{num} {row['StreetName']}, {row['Suburb']}, NSW {row['Postcode']}, Australia"
    query = urllib.parse.quote(address)
    return f"https://www.google.com/maps/search/?api=1&query={query}"

st.set_page_config(page_title="Leightonfield", layout="wide")

st.title("📍 Sorting App with Photo Scan")

# --- Camera Input Section ---
with st.expander("📸 Scan Address from Photo"):
    img_file = st.camera_input("Take a photo of the address label")
    
    scanned_street = None
    scanned_no = None

    if img_file:
        img = Image.open(img_file)
        img_np = np.array(img)
        
        # Perform OCR
        with st.spinner("Reading address..."):
            results_ocr = reader.readtext(img_np)
            full_text = " ".join([res[1].upper() for res in results_ocr])
            st.info(f"Detected Text: {full_text}")

            # Simple logic to find street name in text
            for street in street_list:
                if street in full_text:
                    scanned_street = street
                    # Try to find a number near the street name
                    words = full_text.split()
                    for word in words:
                        if word.isdigit():
                            scanned_no = word
                    break

# --- Search Settings ---
option = st.sidebar.selectbox("Search by:", ["Street Address", "Beat Number", "Suburb"])

results = pd.DataFrame()
searched_no = None

if option == "Street Address":
    col1, col2 = st.columns([3, 1])
    with col1:
        # If OCR found a street, set it as default
        st_name = st.selectbox(
            "Street Name",
            options=street_list,
            index=street_list.index(scanned_street) if scanned_street in street_list else None,
            placeholder="Select or scan a street"
        )
    with col2:
        default_no = scanned_no if scanned_no else ""
        st_no_str = st.text_input("Number (optional)", value=default_no)
        if st_no_str.isdigit():
            searched_no = int(st_no_str)

    if st_name:
        if searched_no is not None:
            parity = 2 if searched_no % 2 == 0 else 1
            mask = (df['StreetName'] == st_name) & (df['EvenOdd'] == parity) & \
                   (df['StreetNoMin'] <= searched_no) & (df['StreetNoMax'] >= searched_no)
            results = df[mask].copy()
        else:
            results = df[df['StreetName'] == st_name].copy()

# ... (Rest of your existing Beat/Suburb logic and sorting/display code) ...
    
 

 














