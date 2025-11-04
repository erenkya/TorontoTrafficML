import os
import requests

# CSV link
CSV_URL = "https://data.torontopolice.on.ca/datasets/TorontoPS::traffic-collisions-open-data-asr-t-tbl-001.csv"

# Save Folder
DEST_FOLDER = "data"
os.makedirs(DEST_FOLDER, exist_ok=True)

# File name
DEST_FILE = os.path.join(DEST_FOLDER, "traffic_collisions.csv")

# Download 
try:
    print(f"Downloading: {CSV_URL}")
    response = requests.get(CSV_URL, stream=True)
    response.raise_for_status()
    with open(DEST_FILE, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Cmpleted. Saved: {DEST_FILE}")
except Exception as e:
    print(f"Error: {e}")
