# github_pipeline/monitor.py

import argparse
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timezone
from evidently import Report
from evidently.presets import DataDriftPreset
from alerts.alerting import send_slack_alert, send_email_alert
from glob import glob
import re


def run_monitoring(reference_ts: str, current_ts: str):
    """
    Checks for data drift (via Evidently) and anomaly spikes between two timestamps.
    Triggers Slack and Email alerts if drift or anomalies are detected.

    Inputs:
      - actor_features_{reference_ts}.parquet
      - actor_features_{current_ts}.parquet
      - actor_predictions_{current_ts}.parquet (optional for anomaly alert)

    Outputs:
      - JSON and HTML drift reports in the 'reports/' directory
    """

    # === Feature Columns ===
    feature_cols = [
        "event_count",
        "pr_count",
        "issue_open_count",
        "fork_count",
        "repo_diversity",
    ]

    # === File Paths ===
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True, parents=True)

    ref_file = f"data/features/actor_features_{reference_ts}.parquet"
    cur_file = f"data/features/actor_features_{current_ts}.parquet"
    pred_file = f"data/features/actor_predictions_{current_ts}.parquet"

    if not Path(ref_file).exists():
        raise FileNotFoundError(f"[ERROR] Reference file not found: {ref_file}")
    if not Path(cur_file).exists():
        raise FileNotFoundError(f"[ERROR] Current file not found: {cur_file}")

    # === Load Data ===
    df_ref = pd.read_parquet(ref_file)[feature_cols].fillna(0)
    df_cur = pd.read_parquet(cur_file)[feature_cols].fillna(0)

    # === Run Evidently Report ===
    report = Report(metrics=[DataDriftPreset()])
    result = report.run(current_data=df_cur, reference_data=df_ref)

    # === Save as JSON + HTML (manually) ===
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    html_path = report_dir / f"drift_report_{timestamp}.html"
    json_path = report_dir / f"drift_report_{timestamp}.json"

    data = result.json()

    with open(json_path, "w") as f_json:
        json.dump(data, f_json, indent=2)

    with open(html_path, "w") as f_html:
        f_html.write("<html><body><pre>\n")
        json.dump(data, f_html, indent=2)
        f_html.write("\n</pre></body></html>")

    print(f"[INFO] Drift report saved:\n - {html_path}\n - {json_path}")

    # === Trigger Drift Alert ===
    drift_info = json.loads(data)
    drift_detected = False

    for metric in drift_info.get("metrics", []):
        if metric.get("metric_id", "").startswith("DriftedColumnsCount"):
            share = metric.get("value", {}).get("share", 0.0)
            drift_detected = share > 0
            break

    if drift_detected:
        msg = f"🚨 Data drift detected between {reference_ts} and {current_ts}"
        print("[ALERT] " + msg)
        send_slack_alert(msg)
        send_email_alert("Drift Alert", msg)

    # === Trigger Anomaly Score Alert ===
    if Path(pred_file).exists():
        df_pred = pd.read_parquet(pred_file)
        if "anomaly_score" in df_pred.columns:
            mean_score = df_pred["anomaly_score"].mean()
            threshold = -0.1  # Customize this based on your model

            if mean_score < threshold:
                msg = f"🚨 Anomaly spike detected at {current_ts}. Mean score: {mean_score:.4f}"
                print("[ALERT] " + msg)
                send_slack_alert(msg)
                send_email_alert("Anomaly Alert", msg)

    # TEMPORARY MANUAL ALERT TEST (remove after confirming)
    # send_slack_alert("✅ Test: Slack alert works!")
    # send_email_alert("✅ Test Email Alert", "This is a test alert to confirm email configuration.")


def main():
    # === Find All Timestamps ===
    files = glob("data/features/actor_features_*.parquet")
    timestamps = []

    for f in files:
        match = re.search(r"actor_features_(\d{4}-\d{2}-\d{2}-\d{2})\.parquet", f)
        if match:
            timestamps.append(match.group(1))

    timestamps = sorted(timestamps)
    if len(timestamps) < 2:
        raise RuntimeError("[ERROR] Need at least 2 parquet files to compute drift.")

    # === Use Latest Two Timestamps ===
    reference_ts = timestamps[-2]
    current_ts = timestamps[-1]
    print(f"[INFO] Comparing reference={reference_ts} → current={current_ts}")

    run_monitoring(reference_ts, current_ts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", help="Reference timestamp (YYYY-MM-DD-HH)")
    parser.add_argument("--current", help="Current timestamp (YYYY-MM-DD-HH)")
    args = parser.parse_args()

    if args.reference and args.current:
        run_monitoring(args.reference, args.current)
    else:
        main()
