import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="Analog Design Toolkit", layout="wide")

# Correct Raw URL for your specific repository
BASE_URL = "https://raw.githubusercontent.com/gmakkena/analog-design-data/main/"

# The exact filenames from your repo
PLOT_OPTIONS = {
    "Efficiency vs. Bias (gm/ID vs VGS)": "gmoverid_vs_vgs.csv",
    "Efficiency vs. Density (gm/ID vs ID/W)": "gmoverid_vs_idbyw.csv",
    "Intrinsic Gain vs. Density (gm/gds vs ID/W)": "gmovergds_vs_idbyw.csv",
    "Gain vs. Efficiency (gm/gds vs gm/ID)": "gmovergds_vs_gmoverid.csv",
    "Output Conductance (gds/ID vs ID/W)": "gdsbyid_vs_idbyw.csv",
    "Transconductance (gm vs VGS)": "gm_vs_vgs.csv"
}

st.title("🔌 Analog IC Characterization Tool")
st.sidebar.header("Plot Settings")

# 1. Selection
choice = st.sidebar.selectbox("Select Characterization Plot:", list(PLOT_OPTIONS.keys()))
filename = PLOT_OPTIONS[choice]

@st.cache_data
def load_data(url):
    # Handling potential parsing errors from Cadence exports
    return pd.read_csv(url, on_bad_lines='skip')

try:
    df = load_data(BASE_URL + filename)
    
    # 2. Extract Lengths (L) from headers
    # Cadence headers are long; we look for the (L=...) part
    length_map = {}
    for i in range(0, df.shape[1], 2):
        header = df.columns[i]
        match = re.search(r'L=([\d\.e-]+)', header)
        if match:
            # Convert 1.8e-07 to "180nm"
            l_nm = f"{float(match.group(1))*1e9:.0f}nm"
            length_map[l_nm] = i
        else:
            length_map[f"Trace {i//2 + 1}"] = i

    # 3. Sidebar Filter
    selected_ls = st.sidebar.multiselect("Select Lengths:", 
                                         options=list(length_map.keys()), 
                                         default=list(length_map.keys()))
    
    # 4. Plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for l_label in selected_ls:
        idx = length_map[l_label]
        x_raw = df.iloc[:, idx]
        y_raw = df.iloc[:, idx+1]
        
        # Clean data: remove NaNs
        mask = x_raw.notna() & y_raw.notna()
        x, y = x_raw[mask], y_raw[mask]
        
        # Use markers to ensure NO INTERPOLATION visibility
        ax.plot(x, y, '-o', label=f"L={l_label}", markersize=3, linewidth=1.2)

    # 5. Axis Formatting Logic
    ax.set_title(f"{choice} (Raw Spectre Data)", fontsize=14)
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    
    # Log scales for specific plots
    if "idbyw" in filename: ax.set_xscale('log')
    if "gds" in filename or "gmovergds" in filename: ax.set_yscale('log')
    
    ax.legend()
    st.pyplot(fig)

    # 6. Design Table
    with st.expander("Show Data Table"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Error loading {filename}. Check your GitHub file names.")
    st.write(f"Direct link attempted: {BASE_URL + filename}")
