import json
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Settings
SLOW_THRESHOLD_MS = 200      # >200ms = slow
DISCONNECT_TIMEOUT_SEC = 5   # Missing for >5s = disconnected

processed = []
last_seen = {}  # {ip: last_timestamp}

with open("ping_monitor.log") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        # Skip non-JSON Python-style dict lines
        if line.startswith("{'") or line.startswith("'"):
            continue

        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        result = entry.get("result")
        if not result:
            continue

        ip = result.get("target")
        name = result.get("name")
        status = result.get("status")
        delay_s = result.get("delay_ms")
        timestamp = result.get("timestamp")

        # Parse timestamp
        dt = None
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                continue
        else:
            continue

        # Convert delay from seconds to ms if not None
        delay_ms = delay_s * 1000 if delay_s is not None else None

        # Detect status
        if status == "failed":
            norm_status = "disconnected"
        elif delay_ms is not None and delay_ms > SLOW_THRESHOLD_MS:
            norm_status = "slow"
        else:
            norm_status = "connected"

        processed.append({
            "ip": ip,
            "name": name,
            "status": norm_status,
            "timestamp": dt
        })

        # Check for disconnection due to missing pings
        if ip in last_seen:
            gap = (dt - last_seen[ip]).total_seconds()
            if gap > DISCONNECT_TIMEOUT_SEC:
                processed.append({
                    "ip": ip,
                    "name": name,
                    "status": "disconnected",
                    "timestamp": last_seen[ip] + timedelta(seconds=1)
                })
        last_seen[ip] = dt

# Convert to DataFrame
df = pd.DataFrame(processed)
df.sort_values(by=["ip", "timestamp"], inplace=True)

# Add end_time as the next timestamp per IP
df["end_time"] = df.groupby("ip")["timestamp"].shift(-1)
df["end_time"] = df["end_time"].fillna(df["timestamp"] + timedelta(minutes=1))

# Plot timeline
fig = px.timeline(
    df,
    x_start="timestamp",
    x_end="end_time",
    y="ip",
    color="status",
    title="Network Status Timeline per IP"
)
fig.update_yaxes(autorange="reversed")
fig.show()
