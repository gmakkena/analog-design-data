import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="Analog IC Design Browser", layout="wide")

# This is the path to your GitHub raw data
BASE_URL = "https://raw.githubusercontent.com/gmakkena/analog-design-data/refs/heads/main/"

# Mapping plot options to your specific filenames
PLOT_MAP = {
    "Efficiency vs. Bias (gm/ID vs VGS)": "gmoverid_vs_vgs.csv",
    "Transconductance (gm vs VGS)": "gm_vs_vgs.csv",
    "Efficiency vs. Density (gm/ID vs ID/W)": "gmoverid_vs_idbyw.csv",
    "Intrinsic Gain vs. Density (gm/gds vs ID/W)": "gmovergds_vs_idbyw.csv",
    "Gain vs. Efficiency (gm/gds vs gm/ID)": "gmovergds_vs_gmoverid.csv",
    "Output Conductance (gds/ID vs ID/W)": "gdsbyid_vs_idbyw.csv"
}

st.sidebar.header("Design Menu")
choice = st.sidebar.selectbox("Select Characterization Plot:", list(PLOT_MAP.keys()))
filename = PLOT_MAP[choice]

@st.cache_data
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(BASE_URL + filename)
    
    # 1. Detect Lengths and map them to column pairs
    lengths = {}
    for i in range(0, df.shape[1], 2):
        header = df.columns[i]
        match = re.search(r'L=([\d\.e-]+)', header)
        if match:
            label = f"{float(match.group(1))*1e9:.0f}nm"
            lengths[label] = i

    # 2. Sidebar Selection
    selected_ls = st.sidebar.multiselect("Select Device Lengths:", 
                                         options=list(lengths.keys()), 
                                         default=list(lengths.keys()))
    
    # Toggle for Raw Data Points (No Interpolation)
    show_pts = st.sidebar.toggle("Show Simulated Points", value=True)

    # 3. Dynamic Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for l_label in selected_ls:
        col_idx = lengths[l_label]
        x = df.iloc[:, col_idx]
        y = df.iloc[:, col_idx + 1]
        mask = x.notna() & y.notna()
        
        fmt = '-o' if show_pts else '-'
        ax.plot(x[mask], y[mask], fmt, label=f"L={l_label}", markersize=3, linewidth=1.2)

    # 4. Smart Scaling (Log vs Linear)
    # If the X-axis involves ID/W, we use a Log scale automatically
    if "idbyw" in filename:
        ax.set_xscale('log')
    # If plotting Gain or gds/ID, a Log Y scale is often clearer
    if "gmovergds" in filename or "gdsbyid" in filename:
        ax.set_yscale('log')

    ax.set_title(f"Simulation Result: {choice}")
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend()
    
    st.pyplot(fig)

    # 5. Data Preview for Students
    with st.expander("View Numerical Data Table"):
        st.write(df)

except Exception as e:
    st.error(f"Error loading {filename}. Please check if the file exists in your GitHub repo.")
    st.info(f"Full URL attempted: {BASE_URL + filename}")
