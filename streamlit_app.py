# streamlit_app_enhanced.py

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="GitHub Anomaly Dashboard", layout="wide")
st.title("🚨 GitHub Anomaly Detection Dashboard")

# --- Paths ---
data_dir = Path("data/features")
report_dir = Path("reports")
prediction_files = sorted(data_dir.glob("actor_predictions_*.parquet"))
drift_json_files = sorted(report_dir.glob("*.json"))

# --- Section 1: Select Prediction File ---
st.sidebar.header("🔧 Settings")
selected_file = st.sidebar.selectbox(
    "Select Prediction File",
    options=[f.name for f in prediction_files],
    index=len(prediction_files) - 1 if prediction_files else 0,
)

threshold = st.sidebar.slider("Anomaly Score Threshold", -1.0, 1.0, 0.0, step=0.01)

# --- Section 2: Latest Anomalies ---
st.header("📌 Latest Anomalies")

if selected_file:
    file_path = data_dir / selected_file
    df_pred = pd.read_parquet(file_path)
    df_anomalies = df_pred[df_pred["anomaly_score"] >= threshold]

    st.caption(f"Using file: `{selected_file}`")
    st.metric("Total Anomalies Detected", len(df_anomalies))

    # Actor anomaly count
    actor_counts = df_anomalies["actor"].value_counts().head(10)
    st.subheader("Top Actors with Anomalies")
    st.bar_chart(actor_counts)

    # Show top anomalies
    st.subheader("Top 10 Anomalous Events")
    st.dataframe(
        df_anomalies[["actor", "anomaly_score"]]
        .sort_values("anomaly_score", ascending=False)
        .head(10)
    )
else:
    st.warning("No prediction files found.")

# --- Section 3: Drift Report ---
st.header("📊 Latest Drift Report")

if drift_json_files:
    latest_json = drift_json_files[-1]
    st.caption(f"Drift JSON: `{latest_json.name}`")

    with open(latest_json) as f:
        try:
            drift_data = json.load(f)
            if isinstance(drift_data, str):
                drift_data = json.loads(drift_data)
        except Exception as e:
            st.error(f"Error loading drift JSON: {e}")
            drift_data = {}

    drift_metrics = {
        m["metric_id"]: m["value"]
        for m in drift_data.get("metrics", [])
        if "metric_id" in m
    }

    st.subheader("Metric-wise Drift Values")
    for metric, value in drift_metrics.items():
        # For count/share dicts
        if isinstance(value, dict) and "share" in value:
            color = "🔴" if value["share"] > 0 else "🟢"
            st.write(f"{color} **{metric}**: {value}")
        else:
            st.write(f"**{metric}**: {value}")
else:
    st.warning("No drift reports found.")

# --- Section 4: Anomaly Trend (last 48 runs) ---
st.header("📈 Anomaly Trend Over Time (Last 48 Predictions)")

if prediction_files:
    df_trend = []
    for file in prediction_files[-48:]:
        timestamp = file.stem.split("_")[-1]
        try:
            df = pd.read_parquet(file)
            count = (df["anomaly_score"] >= threshold).sum()
            df_trend.append({"timestamp": timestamp, "anomaly_count": count})
        except Exception:
            continue

    df_trend = pd.DataFrame(df_trend)
    df_trend["timestamp"] = pd.to_datetime(df_trend["timestamp"], format="%Y-%m-%d-%H")
    df_trend.set_index("timestamp", inplace=True)

    st.line_chart(df_trend)
else:
    st.info("No anomaly trend data available.")

# --- Section 5: Last 48 Hours Actor Activity ---
st.header("🕒 Last 48 Hours Event Summary")

last_48h = datetime.now(timezone.utc) - timedelta(hours=48)
activity_files = [
    f
    for f in prediction_files
    if datetime.strptime(f.stem.split("_")[-1], "%Y-%m-%d-%H").replace(
        tzinfo=timezone.utc
    )
    > last_48h
]

if activity_files:
    df_recent = pd.concat([pd.read_parquet(f) for f in activity_files])
    top_actors = df_recent["actor"].value_counts().head(10)
    st.bar_chart(top_actors)
else:
    st.info("No event data in the last 48 hours.")
