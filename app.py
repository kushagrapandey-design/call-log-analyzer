import streamlit as st
import pandas as pd
from datetime import datetime
import re

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Call Log Analyzer",
    layout="wide"
)

# -----------------------------
# Watermark / Header
# -----------------------------
st.markdown(
    """
    <div style="
        padding:12px;
        border-radius:8px;
        background-color:#f5f7fb;
        border:1px solid #e0e3eb;
        margin-bottom:20px;
    ">
        <h3 style="margin:0;">📞 Call Log Analyzer</h3>
        <p style="margin:4px 0 0 0; font-size:14px; color:#555;">
            Frontend: <b>Figma</b> &nbsp;|&nbsp;
            Backend: <b>Google Colab</b> &nbsp;|&nbsp;
            Deployed on: <b>Streamlit</b><br>
            Developer: <b>Kushagra</b> &nbsp;|&nbsp;
            Performance Score: <b>1022ER</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Paste your call log data below and click **Generate Table**")

# -----------------------------
# Input
# -----------------------------
raw = st.text_area("Call Log Input", height=350)

# -----------------------------
# Robust Parser
# -----------------------------
def parse_calls(raw_text):
    calls = []

    for line in raw_text.splitlines():
        line = line.strip()

        time_match = re.search(
            r"(\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} [AP]M)",
            line
        )

        if not time_match:
            continue

        start = datetime.strptime(
            time_match.group(1),
            "%m/%d/%Y %I:%M %p"
        )

        dur_match = re.search(r"(\d{2}:\d{2}:\d{2})", line)
        duration_sec = 0

        if dur_match:
            h, m, s = map(int, dur_match.group(1).split(":"))
            duration_sec = h * 3600 + m * 60 + s

        calls.append({
            "start": start,
            "duration_sec": duration_sec
        })

    return calls

# -----------------------------
# Processing & Output
# -----------------------------
if st.button("Generate Table") and raw:

    calls = parse_calls(raw)

    if not calls:
        st.error("No valid call records found.")
    else:
        df = pd.DataFrame(calls)

        # Hour bucket
        df["hour"] = df["start"].dt.floor("H")

        # Seconds → Minutes
        df["talk_time_min"] = df["duration_sec"] / 60

        # Per-hour aggregation
        table = (
            df.groupby("hour")
            .agg(
                t_i=("talk_time_min", "sum"),
                d_i=("start", "count")
            )
            .sort_index()
            .reset_index()
        )

        # Cumulative metrics
        table["T_i"] = table["t_i"].cumsum()
        table["D_i"] = table["d_i"].cumsum()

        # Peak hour
        peak_hour = table.loc[table["t_i"].idxmax(), "hour"]

        # Summary metrics
        total_calls = len(df)
        connected_calls = (df["duration_sec"] > 0).sum()
        not_connected_calls = total_calls - connected_calls
        total_talk_time_min = round(table["t_i"].sum(), 2)

        # -----------------------------
        # Summary Section
        # -----------------------------
        st.subheader("📊 Summary")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Calls", total_calls)
        c2.metric("Connected Calls", connected_calls)
        c3.metric("Not Connected Calls", not_connected_calls)
        c4.metric("Total Talk Time (min)", total_talk_time_min)

        st.write(f"**Peak Hour (Ω★):** {peak_hour.strftime('%I:%M %p')}")

        # -----------------------------
        # Table Display
        # -----------------------------
        st.subheader("🕒 Hour-wise Call Table")

        display_table = table.copy()
        display_table["Hour"] = display_table["hour"].dt.strftime("%I:%M %p")
        display_table["Talk Time (min)"] = display_table["t_i"].round(2)
        display_table["Talk Time So Far (min)"] = display_table["T_i"].round(2)
        display_table["Dials"] = display_table["d_i"]
        display_table["Dials So Far"] = display_table["D_i"]

        display_table = display_table[
            [
                "Hour",
                "Talk Time (min)",
                "Talk Time So Far (min)",
                "Dials",
                "Dials So Far"
            ]
        ]

        st.dataframe(display_table, use_container_width=True)

        st.caption(f"Parsed {len(df)} call records successfully.")
