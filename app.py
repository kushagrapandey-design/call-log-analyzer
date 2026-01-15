import streamlit as st
import pandas as pd
from datetime import datetime
import re
import matplotlib.pyplot as plt

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
            <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhUSEhMVFhUXFxcaGBcXGBUYFxcYGBcXFxgWFxgYHSggGBolHRcVITEhJSkrLi4uFx8zODMsNygtLisBCgoKDg0OGhAQGi0fHyUtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tNy0tNy0tN//AABEIAOEA4QMBIgACEQEDEQH/..."
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

        # Per-hour aggregation (NOT cumulative)
        hourly = (
            df.groupby("hour")
            .agg(
                talk_time=("talk_time_min", "sum"),
                dials=("start", "count")
            )
            .sort_index()
            .reset_index()
        )

        hourly["hour_label"] = hourly["hour"].dt.strftime("%I:%M %p")

        # -----------------------------
        # Plot
        # -----------------------------
        fig, ax1 = plt.subplots(figsize=(12, 5))

        ax1.plot(
            hourly["hour_label"],
            hourly["talk_time"],
            marker="o",
            label="Talk Time (min)"
        )

        ax1.set_xlabel("Hour")
        ax1.set_ylabel("Talk Time (minutes)")
        ax1.tick_params(axis="x", rotation=45)

        ax2 = ax1.twinx()
        ax2.plot(
            hourly["hour_label"],
            hourly["dials"],
            marker="s",
            linestyle="--",
            label="Dials"
        )

        ax2.set_ylabel("Dials")

        # Legends
        lines_1, labels_1 = ax1.get_legend_handles_labels()
        lines_2, labels_2 = ax2.get_legend_handles_labels()
        ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

        st.subheader("📈 Hour-wise Call Activity")
        st.pyplot(fig)
