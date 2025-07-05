import os
import requests
from tqdm import tqdm


def download_hour(year, month, day, hour, save_dir="data/raw"):
    os.makedirs(save_dir, exist_ok=True)
    url = f"https://data.gharchive.org/{year}-{month:02d}-{day:02d}-{hour}.json.gz"
    filename = os.path.join(save_dir, os.path.basename(url))

    if os.path.exists(filename):
        print(f"File already exists: {filename}")
        return

    print(f"Downloading: {url}")
    response = requests.get(url, stream=True)

    if response.status_code != 200:
        print(f"Failed to download: {url}")
        return

    with open(filename, "wb") as f:
        for chunk in tqdm(response.iter_content(chunk_size=1024)):
            if chunk:
                f.write(chunk)

    print(f"Saved: {filename}")


if __name__ == "__main__":
    # Example: download Jan 1, 2024 at 15:00 UTC
    download_hour(2024, 1, 1, 15)
