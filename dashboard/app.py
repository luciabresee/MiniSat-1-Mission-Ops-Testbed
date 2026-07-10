"""
MiniSat-1 Mission Operations Dashboard
Streamlit app for telemetry review and anomaly monitoring.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Make src/ importable when running from project root
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from anomaly_detector import detect

st.set_page_config(page_title="MiniSat-1 Mission Ops", layout="wide")

STATUS_COLORS = {"GREEN": "#21ba45", "YELLOW": "#fbbd08", "RED": "#db2828"}

RECOMMENDATIONS = {
    "GREEN": "All subsystems nominal. Continue routine operations and "
             "monitor next ground pass.",
    "YELLOW": "Caution: off-nominal trend detected. Increase monitoring "
              "cadence, review recent telemetry, and prepare the applicable "
              "operator procedure.",
    "RED": "CRITICAL: Execute Operator Procedure - Battery Temperature "
           "Anomaly. Shed non-essential loads, command SAFE mode if "
           "criteria met, and notify the mission director.",
}


@st.cache_data
def load(dataset):
    df = pd.read_csv(f"data/{dataset}_telemetry.csv")
    checked, events = detect(df)
    return checked, events


# ---- Sidebar controls ----
st.sidebar.title("MiniSat-1 Mission Ops")
dataset = st.sidebar.radio("Telemetry dataset", ["nominal", "anomaly"])
df, events = load(dataset)

t_max = int(df["time_min"].max())
t_now = st.sidebar.slider("Mission time (min)", 0, t_max, t_max)

view = df[df["time_min"] <= t_now]
current = view.iloc[-1]

# ---- Header: mode and subsystem status ----
st.title("MiniSat-1 Mission Operations Dashboard")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Mission time", f"{int(current['time_min'])} min")
c2.metric("Mode", current["mode"])
c3.metric("Eclipse", "YES" if current["in_eclipse"] else "NO")
c4.metric("Comm link", "LOCKED" if current["comm_link"] else "NO CONTACT")

st.subheader("Subsystem status")
s1, s2 = st.columns(2)
for col, name, status in [(s1, "EPS (Power/Thermal)", current["eps_status"]),
                          (s2, "ADCS (Attitude)", current["adcs_status"])]:
    col.markdown(
        f"<div style='background:{STATUS_COLORS[status]};color:white;"
        f"padding:14px;border-radius:8px;text-align:center;"
        f"font-size:20px;font-weight:bold'>{name}: {status}</div>",
        unsafe_allow_html=True,
    )

# ---- Operator recommendation ----
worst_now = "RED" if "RED" in (current["eps_status"], current["adcs_status"]) \
    else "YELLOW" if "YELLOW" in (current["eps_status"], current["adcs_status"]) \
    else "GREEN"
st.subheader("Operator recommendation")
st.info(RECOMMENDATIONS[worst_now])

# ---- Telemetry plots ----
st.subheader("Telemetry")
plots = [
    ("batt_temp_C", "Battery temperature (C)"),
    ("batt_voltage_V", "Battery voltage (V)"),
    ("batt_current_A", "Battery current (A)"),
    ("solar_current_A", "Solar array current (A)"),
    ("pointing_error_deg", "Pointing error (deg)"),
    ("wheel_speed_rpm", "Wheel speed (rpm)"),
]
p1, p2 = st.columns(2)
for i, (field, label) in enumerate(plots):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=view["time_min"], y=view[field],
                             mode="lines", name=label))
    fig.update_layout(title=label, height=250,
                      margin=dict(l=40, r=20, t=40, b=30))
    (p1 if i % 2 == 0 else p2).plotly_chart(fig, use_container_width=True)

# ---- Event log ----
st.subheader("Mission event log")
past_events = [e for e in events if e["time_min"] <= t_now]
if past_events:
    st.table(pd.DataFrame(past_events))
else:
    st.write("No status events. All subsystems GREEN.")
