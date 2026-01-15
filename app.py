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
# Top-left Branding (Base64 Image + White Text)
# -----------------------------
st.markdown(
    """
    <style>
        .brand-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }

        .brand-container img {
            height: 45px;
            cursor: pointer;
        }

        .brand-container span {
            font-size: 16px;
            color: white;
            font-weight: 400;
        }
    </style>

    <div class="brand-container">
        <a href="https://www.google.com/search?q=%40yourkushagra&rlz=1C1JJTC_enIN1182IN1182&oq=%40y&gs_lcrp=EgZjaHJvbWUqBggCEEUYOzIJCAAQRRg5GIAEMgcIARAAGIAEMgYIAhBFGDsyBggDEEUYQDIHCAQQABiABDIHCAUQABiABDIHCAYQABiABDIHCAcQABiABNIBCDM2MzBqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8"
           target="_blank">
            <img src="data:image/jpeg;base64,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" alt="Developer Logo">
        </a>
        <span>Developer</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

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

        df["hour"] = df["start"].dt.floor("H")
        df["talk_time_min"] = df["duration_sec"] / 60

        table = (
            df.groupby("hour")
            .agg(
                t_i=("talk_time_min", "sum"),
                d_i=("start", "count")
            )
            .sort_index()
            .reset_index()
        )

        table["T_i"] = table["t_i"].cumsum()
        table["D_i"] = table["d_i"].cumsum()

        peak_hour = table.loc[table["t_i"].idxmax(), "hour"]

        total_calls = len(df)
        connected_calls = (df["duration_sec"] > 0).sum()
        not_connected_calls = total_calls - connected_calls
        total_talk_time_min = round(table["t_i"].sum(), 2)

        st.subheader("📊 Summary")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Calls", total_calls)
        c2.metric("Connected Calls", connected_calls)
        c3.metric("Not Connected Calls", not_connected_calls)
        c4.metric("Total Talk Time (min)", total_talk_time_min)

        st.write(f"**Peak Hour (Ω★):** {peak_hour.strftime('%I:%M %p')}")

        st.subheader("🕒 Hour-wise Call Table")

        display_table = table.copy()
        display_table["Hour"] = display_table["hour"].dt.strftime("%I:%M %p")
        display_table["Talk Time (min)"] = display_table["t_i"].round(2)
        display_table["Talk Time So Far (min)"] = display_table["T_i"].round(2)
        display_table["Dials"] = display_table["d_i"]
        display_table["Dials So Far"] = display_table["D_i"]

        display_table = display_table[
            ["Hour", "Talk Time (min)", "Talk Time So Far (min)", "Dials", "Dials So Far"]
        ]

        st.dataframe(display_table, use_container_width=True)
        st.caption(f"Parsed {len(df)} call records successfully.")
