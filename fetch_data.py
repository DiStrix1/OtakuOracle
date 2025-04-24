# fetch_data.py
# Script to fetch manga data from the API

from app.utils.data_fetch import fetch_manga_data

if __name__ == "__main__":
    print("Fetching manga data from API...")
    # Fetch 5 pages of manga data (adjust as needed)
    data_path = fetch_manga_data(pages=5)
    print(f"Data fetched successfully and saved to {data_path}")
