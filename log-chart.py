import json 
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

processed = []

with open("pingapp.log") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        try:
            entry = json.loads(line)  # Parse the line as JSON
        except json.JSONDecodeError as e:
            print(f"Skipping malformed line: {e}")
            continue

        result = entry.get("result")
        if not result:
            continue

        ip = result.get("ip")
        name = result.get("name")
        status = result.get("status")
        delay = result.get("delay")
        timestamp = result.get("timestamp")
        dt = datetime.utcfromtimestamp(timestamp)

        # Normalize status
        if status == "failed":
            norm_status = "disconnected"
        elif delay is not None and delay > 200:
            norm_status = "slow"
        else:
            norm_status = "connected"

        processed.append({
            "ip": ip,
            "name": name,
            "status": norm_status,
            "timestamp": dt
        })

# Convert to DataFrame
df = pd.DataFrame(processed)
df.sort_values(by=["ip", "timestamp"], inplace=True)

# Add end_time as the next timestamp per IP
df["end_time"] = df.groupby("ip")["timestamp"].shift(-1)
df["end_time"].fillna(df["timestamp"] + timedelta(minutes=1), inplace=True)

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
# commit