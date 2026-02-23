import pandas as pd
import re
import panel as pn
import hvplot.pandas
import holoviews as hv
from bokeh.models import CrosshairTool

# Initialize
pn.extension('bokeh', comms='colab')
hv.extension('bokeh')

BASE_URL = "https://raw.githubusercontent.com/gmakkena/analog-design-data/main/"

# --- Full File Mapping (All 6 plots restored) ---
FILES = {
    'NMOS': {
        'gm/ID vs. VGS': 'gmoverid_vs_vgs.csv',
        'gm/ID vs. ID/W': 'gmoverid_vs_idbyw.csv',
        'gm/gds vs. ID/W': 'gmovergds_vs_idbyw.csv',
        'gm/gds vs. gm/ID': 'gmovergds_vs_gmoverid.csv',
        'gds/ID vs. ID/W': 'gdsbyid_vs_idbyw.csv',
        'gm vs. VGS': 'gm_vs_vgs.csv'
    },
    'PMOS': {
        'gm/ID vs. VGS': 'pmos_gmoverid_vs_vgs.csv',
        'gm/ID vs. ID/W': 'pmos_gmoverid_vs_idbyw.csv',
        'gm/gds vs. ID/W': 'pmos_gmovergds_vs_idbyw.csv',
        'gm/gds vs. gm/ID': 'pmos_gmovergds_vs_gmoverid.csv',
        'gds/ID vs. ID/W': 'pmos_gdsbyid_vs_idbyw.csv',
        'gm vs. VGS': 'pmos_gm_vs_vgs.csv'
    }
}

# 1. UI Widgets (Back to standard responsive buttons)
device_select = pn.widgets.RadioButtonGroup(name='Device', options=['NMOS', 'PMOS'], button_type='primary', width=200)
plot_select = pn.widgets.Select(name='Select Parameter:', options=list(FILES['NMOS'].keys()), width=350)

# 2. Reactive Plotting Function
@pn.depends(device_select, plot_select)
def get_plot(device, plot_name):
    filename = FILES[device][plot_name]
    url = f"{BASE_URL}{filename}"
    
    try:
        df = pd.read_csv(url)
        plot_list = []
        
        # Define clean labels for Axes and Tooltips
        x_label, y_label = "X-Axis", "Y-Axis"
        if 'vgs' in filename: x_label = "Vgs (V)"
        elif 'idbyw' in filename: x_label = "Id/W (A/m)"
        elif 'gmoverid' in filename: x_label = "gm/Id (1/V)"

        if 'gmoverid' in filename and 'vgs' in filename: y_label = "gm/Id (1/V)"
        elif 'gmovergds' in filename: y_label = "gm/gds"
        elif 'gdsbyid' in filename: y_label = "gds/Id (1/V)"
        elif 'gm_vs' in filename: y_label = "gm (S)"
        elif 'idbyw' in filename and 'gmoverid' in filename: y_label = "gm/Id (1/V)"

        # Plot all column pairs
        for i in range(0, len(df.columns), 2):
            x_col, y_col = df.columns[i], df.columns[i+1]
            
            l_match = re.search(r'L=([\d\.eE\-\+]+)', x_col)
            l_label = f"L={float(l_match.group(1))*1e9:.0f}nm" if l_match else f"Trace {i//2}"
            
            # Using redim.label to clear "Wave vs Wave" in hover
            p = df.hvplot.line(x=x_col, y=y_col, label=l_label, grid=True).redim.label(
                **{x_col: x_label, y_col: y_label}
            )
            plot_list.append(p)
            
        overlay = hv.Overlay(plot_list).opts(
            title=f"{device}: {plot_name}",
            xlabel=x_label, ylabel=y_label,
            width=850, height=550,
            legend_position='right',
            default_tools=['pan', 'wheel_zoom', 'box_zoom', 'save', 'reset', CrosshairTool()],
            click_policy='hide',
            show_grid=True,
            fontscale=1.1
        )
        
        # Axis scaling logic
        if 'idbyw' in filename:
            overlay = overlay.redim.range(**{df.columns[0]: (0, 300)})
            
        return overlay
    except Exception as e:
        return pn.pane.Alert(f"Data Fetch Error: {e}", alert_type="danger")

# 3. Assemble Dashboard
dashboard = pn.Column(
    pn.pane.Markdown("# 🚀 Analog Device Explorer"),
    pn.Row(pn.pane.Markdown("**Device Type:**"), device_select, plot_select),
    get_plot
)

dashboard.servable()
