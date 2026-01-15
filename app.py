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
# Top-left Branding (Image + White Text)
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
            <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhUSEhMVFhUXFxcaGBcXGBUYFxcYGBcXFxgWFxgY..."
                 alt="Developer Logo">
        </a>
        <span>Developer</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
st.title("📞 Call Log Analyzer")
st.write("Paste your call log data below and click **Generate Graph**")

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
# Processing & Graph
# -----------------------------
if st.button("Generate Graph") and raw:

    calls = parse_calls(raw)

    if not calls:
        st.error("No valid call records found.")
    else:
        df = pd.DataFrame(calls)

        # Hour bucket
        df["hour"] = df["start"].dt.floor("H")
        df["talk_time_min"] = df["duration_sec"] / 60

        # Hour-wise (NOT cumulative)
        hourly = (
            df.groupby("hour")
            .agg(
                Talk_Time_Minutes=("talk_time_min", "sum"),
                Dials=("start", "count")
            )
            .sort_index()
        )

        hourly.index = hourly.index.strftime("%I:%M %p")

        st.subheader("📈 Hour-wise Call Activity (Per Hour)")
        st.line_chart(hourly)
