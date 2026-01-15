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

st.title("📞 Call Log Analyzer")
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

        # Detect datetime
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

        # Detect duration if present
        dur_match = re.search(r"(\d{2}:\d{2}:\d{2})", line)
        duration = None

        if dur_match:
            h, m, s = map(int, dur_match.group(1).split(":"))
            duration = h * 3600 + m * 60 + s

        calls.append({
            "start": start,
            "duration": duration
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

        # Hour bucket Ω
        df["hour"] = df["start"].dt.floor("H")

        # Talk time (connected calls only)
        df["talk_time"] = df["duration"].fillna(0)

        # Aggregate per hour
        table = (
            df.groupby("hour")
            .agg(
                t_i=("talk_time", "sum"),
                d_i=("start", "count")
            )
            .sort_index()
            .reset_index()
        )

        # Cumulative metrics
        table["T_i"] = table["t_i"].cumsum()
        table["D_i"] = table["d_i"].cumsum()

        # Peak hour Ω★
        peak_hour = table.loc[table["t_i"].idxmax(), "hour"]

        # Summary metrics
        total_calls = len(df)
        connected_calls = df["duration"].notna().sum()
        not_connected_calls = total_calls - connected_calls
        total_talk_time = int(table["t_i"].sum())

        # -----------------------------
        # Display Summary
        # -----------------------------
        st.subheader("📊 Summary")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Calls", total_calls)
        c2.metric("Connected Calls", connected_calls)
        c3.metric("Not Connected Calls", not_connected_calls)
        c4.metric("Total Talk Time (sec)", total_talk_time)

        st.write(f"**Peak Hour (Ω★):** {peak_hour.strftime('%I:%M %p')}")

        # -----------------------------
        # Display Table
        # -----------------------------
        st.subheader("🕒 Hour-wise Call Table")

        display_table = table.copy()
        display_table["hour"] = display_table["hour"].dt.strftime("%I:%M %p")

        display_table.rename(
            columns={
                "hour": "Hour",
                "t_i": "Talk Time (sec)",
                "T_i": "Talk Time So Far (sec)",
                "d_i": "Dials",
                "D_i": "Dials So Far"
            },
            inplace=True
        )

        st.dataframe(display_table, use_container_width=True)

        # -----------------------------
        # Debug (optional, can remove)
        # -----------------------------
        st.caption(f"Parsed {len(df)} call records successfully.")
