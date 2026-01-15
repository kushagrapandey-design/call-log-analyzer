import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(page_title="Call Log Analyzer", layout="wide")

st.title("📞 Call Log Analyzer")
st.write("Paste your call log below and click **Generate Table**")

raw = st.text_area("Call Log Input", height=300)

def parse_calls(raw):
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    calls = []
    i = 0

    while i < len(lines) - 1:
        number = lines[i]
        meta = lines[i + 1]

        time_match = re.search(r"(\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} [AP]M)", meta)
        dur_match = re.search(r"(\d{2}:\d{2}:\d{2})", meta)

        if time_match:
            start = datetime.strptime(time_match.group(1), "%m/%d/%Y %I:%M %p")
            duration = None

            if dur_match:
                h, m, s = map(int, dur_match.group(1).split(":"))
                duration = h * 3600 + m * 60 + s

            calls.append({
                "start": start,
                "duration": duration
            })
        i += 2

    return calls

if st.button("Generate Table") and raw:
    calls = parse_calls(raw)

    if not calls:
        st.error("No valid call records found.")
    else:
        df = pd.DataFrame(calls)
        df["hour"] = df["start"].dt.floor("H")
        df["talk_time"] = df["duration"].fillna(0)

        table = (
            df.groupby("hour")
            .agg(
                t_i=("talk_time", "sum"),
                d_i=("start", "count")
            )
            .sort_index()
            .reset_index()
        )

        table["T_i"] = table["t_i"].cumsum()
        table["D_i"] = table["d_i"].cumsum()

        peak_hour = table.loc[table["t_i"].idxmax(), "hour"]

        st.subheader("📊 Summary")
        st.write(f"**Total Talk Time:** {int(table['t_i'].sum())} seconds")
        st.write(f"**Peak Hour:** {peak_hour.strftime('%I:%M %p')}")

        st.subheader("🕒 Hour-wise Table")
        st.dataframe(table, use_container_width=True)
