import pandas as pd
import matplotlib
# Set a non-GTK backend to avoid GTK4 issue
matplotlib.use('Agg')  # Use 'Agg' for non-interactive plotting; change to 'TkAgg' if GUI is needed
import matplotlib.pyplot as plt
import json

# File path for the JSON log data (adjust as needed)
LOG_FILE = "pingapp.log"  # Replace with your actual log file path

# Load JSON log data
def load_log_data(file_path):
    try:
        with open(file_path, 'r') as f:
            # Assume each line is a JSON object
            log_data = [json.loads(line) for line in f if line.strip()]
        return log_data
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

# Process the DataFrame
def process_dataframe(log_data):
    # Convert to DataFrame
    df = pd.DataFrame(log_data)
    
    # Rename '@time' to 'timestamp' if present
    if '@time' in df.columns:
        df.rename(columns={'@time': 'timestamp'}, inplace=True)
    
    # Ensure 'timestamp' column exists and is in datetime format
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    else:
        print("Warning: 'timestamp' column not found in data.")
        df['timestamp'] = pd.NaT
    
    # Ensure 'ip' column exists; fill missing values with empty string
    if 'ip' not in df.columns:
        df['ip'] = ''
    else:
        df['ip'] = df['ip'].fillna('')
    
    # Ensure 'avg_delay' is numeric
    if 'avg_delay' in df.columns:
        df['avg_delay'] = pd.to_numeric(df['avg_delay'], errors='coerce')
    
    # Ensure 'target_name' exists; fill missing values with empty string
    if 'target_name' not in df.columns:
        df['target_name'] = ''
    else:
        df['target_name'] = df['target_name'].fillna('')
    
    return df

# Plot Internet ping delays
def plot_internet_delays(df):
    # Filter for Internet ping results with valid avg_delay
    internet_df = df[(df['target_name'] == 'Internet') & (df['avg_delay'].notna())]
    
    if internet_df.empty:
        print("No valid Internet ping data to plot.")
        return
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(internet_df['timestamp'], internet_df['avg_delay'], marker='o', color='blue', label='Internet Avg Delay')
    plt.title('Internet Ping Average Delay Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Average Delay (ms)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    # Save the plot (no display for Agg backend)
    plt.savefig('internet_ping_delay.png')
    plt.close()  # Close the figure to free memory
    print("Plot saved as 'internet_ping_delay.png'")

# Main function
def main():
    # Load the data
    log_data = load_log_data(LOG_FILE)
    if not log_data:
        print("No data to process. Exiting.")
        return
    
    # Process the DataFrame
    df = process_dataframe(log_data)
    
    # Sort by 'ip' and 'timestamp' for rows with non-empty 'ip'
    df_filtered = df[df['ip'] != ''].copy()  # Use .copy() to avoid SettingWithCopyWarning
    if not df_filtered.empty:
        df_filtered = df_filtered.sort_values(by=["ip", "timestamp"])  # Avoid inplace=True
        print("Sorted DataFrame with 'ip' values:")
        print(df_filtered[['timestamp', 'ip', 'target_name', 'avg_delay']].head())
    else:
        print("No rows with 'ip' values to sort.")
    
    # Plot the data
    plot_internet_delays(df)

if __name__ == "__main__":
    main()