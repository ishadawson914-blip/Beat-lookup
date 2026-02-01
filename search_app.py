import streamlit as st
import pandas as pd
import urllib.parse
import numpy as np
import re
from PIL import Image

# We use easyocr for the address reading
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Initialize OCR reader
@st.cache_resource
def load_ocr():
    if OCR_AVAILABLE:
        return easyocr.Reader(['en'])
    return None

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('SortCart.csv')
    unique_streets = sorted(df['StreetName'].unique())
    return df, unique_streets

df, street_list = load_data()
reader = load_ocr()

def make_map_link(row, specific_no=None):
    num = specific_no if specific_no else row['StreetNoMin']
    address = f"{num} {row['StreetName']}, {row['Suburb']}, NSW {row['Postcode']}, Australia"
    query = urllib.parse.quote(address)
    return f"https://www.google.com/maps/search/?api=1&query={query}"

st.set_page_config(page_title="Leightonfield", layout="wide", initial_sidebar_state="expanded")

st.title("📍 Sorting App with Photo Scan")

# --- OCR Camera Section ---
scanned_street = None
scanned_no = None

if OCR_AVAILABLE:
    with st.expander("📸 Scan Address from Photo"):
        img_file = st.camera_input("Take a photo of the address label")
        if img_file:
            img = Image.open(img_file)
            img_np = np.array(img)
            with st.spinner("Analyzing address..."):
                results_ocr = reader.readtext(img_np)
                results_ocr.sort(key=lambda x: (x[0][0][1], x[0][0][0]))
                full_text = " ".join([res[1].upper() for res in results_ocr])
                st.info(f"Detected Text: {full_text}")

                # 1. Find the street name
                found_street = None
                for street in street_list:
                    if street in full_text:
                        if found_street is None or len(street) > len(found_street):
                            found_street = street
                
                if found_street:
                    scanned_street = found_street
                    idx = full_text.find(found_street)
                    prefix = full_text[max(0, idx-35):idx]
                    
                    # Logic for Unit/Number and Number//Number
                    # Captures the second number if a / or // is present
                    pattern = re.compile(r'(?:UNIT\s*\d+\s*/*\s*|(?:\d+)\s*//?\s*)(\d+[A-Z]?)|(\d+[A-Z]?)')
                    matches = pattern.findall(prefix)
                    if matches:
                        last_match = matches[-1]
                        scanned_no = last_match[0] if last_match[0] else last_match[1]

# --- Search Settings ---
st.sidebar.header("Search Settings")
option = st.sidebar.selectbox("Search by:", ["Street Address", "Beat Number", "Suburb"])

results = pd.DataFrame()
final_display_no = None

if option == "Street Address":
    col1, col2 = st.columns([3, 1])
    with col1:
        st_name = st.selectbox(
            "Street Name",
            options=street_list,
            index=street_list.index(scanned_street) if scanned_street in street_list else None
        )
    with col2:
        st_no_input = st.text_input("Number", value=scanned_no if scanned_no else "")
   
    if st_name and st_no_input:
        # CLEANING: If user enters '1A', we use '1' for the query
        final_display_no = st_no_input
        numeric_only = re.sub(r'\D', '', st_no_input)
        
        if numeric_only:
            searched_no = int(numeric_only)
            parity = 2 if searched_no % 2 == 0 else 1
            mask = (
                (df['StreetName'] == st_name) &
                (df['EvenOdd'] == parity) &
                (df['StreetNoMin'] <= searched_no) &
                (df['StreetNoMax'] >= searched_no)
            )
            results = df[mask].copy()

elif option == "Beat Number":
    beat_val = st.sidebar.number_input("Enter Beat Number", min_value=1, value=1011)
    results = df[df['BeatNo'] == beat_val].copy()

elif option == "Suburb":
    suburb_list = sorted(df['Suburb'].unique())
    sub_val = st.selectbox("Select Suburb", suburb_list)
    results = df[df['Suburb'] == sub_val].copy()

# --- Display Results ---
if not results.empty:
    results = results.sort_values(by=['Suburb', 'StreetName', 'StreetNoMin'])
    results['Map Link'] = results.apply(lambda row: make_map_link(row, final_display_no), axis=1)
   
    st.success(f"Found {len(results)} record(s)")
    
    display_cols = ['Suburb', 'StreetName', 'StreetNoMin', 'StreetNoMax', 'BeatNo', 'TeamNo', 'Postcode', 'Map Link']
    st.dataframe(
        results[display_cols],
        column_config={
            "Map Link": st.column_config.LinkColumn("Maps", display_text="📍 View"),
            "BeatNo": "Beat", "TeamNo": "Team",
            "StreetNoMin": "Min No", "StreetNoMax": "Max No"
        },
        use_container_width=True,
        hide_index=True
    )
    
 

 

















