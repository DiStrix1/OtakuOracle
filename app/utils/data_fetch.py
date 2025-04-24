# app/utils/data_fetch.py

import json
import requests
import time
from pathlib import Path


def fetch_manga_data(pages=20, api_url="https://api.jikan.moe/v4/manga"):
    all_manga = []

    # List of popular newer manga to specifically search for
    newer_manga_titles = [
        "Chainsaw Man",
        "Jujutsu Kaisen",
        "Spy x Family",
        "Demon Slayer",
        "My Hero Academia",
        "Tokyo Revengers",
        "Kaiju No. 8",
        "Solo Leveling",
        "One Punch Man",
        "Sakamoto Days",
        "Blue Lock",
        "Dandadan",
        "Oshi no Ko",
        "Frieren: Beyond Journey's End",
        "Undead Unluck"
    ]

    # First, fetch specific newer manga by title
    print("Fetching newer manga titles...")
    for title in newer_manga_titles:
        print(f"Searching for: {title}")
        try:
            # Search for the specific manga title
            search_url = f"{api_url}?q={title}&limit=5"
            response = requests.get(search_url)

            # Handle rate limiting
            if response.status_code == 429:
                print("Rate limit hit, sleeping for 4 seconds...")
                time.sleep(4)
                # Try again
                response = requests.get(search_url)

            # Check for other errors
            response.raise_for_status()

            data = response.json()

            # Process search results
            for item in data.get("data", []):
                if not item.get("synopsis") or len(item.get("synopsis",""))<20:
                    continue

                # Check if this is actually the manga we're looking for (not just a similar title)
                if title.lower() in item.get("title", "").lower():
                    manga_entry = {
                        "title": item.get("title", ""),
                        "description": item.get("synopsis", "") or "",
                        "genres": [g.get("name", "") for g in item.get("genres", [])],
                        "themes": [t.get("name", "") for t in item.get("themes", [])],
                        "score": item.get("score", 0),
                        "image_url": item.get("images", {}).get("jpg", {}).get("image_url", ""),
                        "popularity": item.get("popularity", 0),
                        "favorites": item.get("favorites", 0),
                        "year": item.get("published", {}).get("from", "").split("-")[0] if item.get("published", {}).get("from") else "",
                        "authors": [a.get("name", "") for a in item.get("authors", [])]
                    }
                    all_manga.append(manga_entry)
                    print(f"Added: {item.get('title', '')}")
                    break  # Found the manga we were looking for

            # Sleep to avoid hitting rate limits
            time.sleep(1.5)

        except Exception as e:
            print(f"Error fetching data for {title}: {e}")
            # Sleep longer if there's an error
            time.sleep(5)
            continue

    # Then fetch regular pages
    for page in range(1, pages + 1):
        print(f"Fetching page {page} of {pages}...")
        try:
            # Add limit parameter to get more results per page
            response = requests.get(f"{api_url}?page={page}&limit=25")

            # Handle rate limiting
            if response.status_code == 429:
                print("Rate limit hit, sleeping for 4 seconds...")
                time.sleep(4)
                # Try the same page again
                page -= 1
                continue

            # Check for other errors
            response.raise_for_status()

            data = response.json()

            for item in data.get("data", []):
                if not item.get("synopsis") or len(item.get("synopsis",""))<20:
                    continue

                # Check if we already have this manga (from our specific search)
                if any(manga["title"] == item.get("title", "") for manga in all_manga):
                    continue

                manga_entry = {
                    "title": item.get("title", ""),
                    "description": item.get("synopsis", "") or "",
                    "genres": [g.get("name", "") for g in item.get("genres", [])],
                    "themes": [t.get("name", "") for t in item.get("themes", [])],
                    "score": item.get("score", 0),
                    "image_url": item.get("images", {}).get("jpg", {}).get("image_url", ""),
                    "popularity": item.get("popularity", 0),
                    "favorites": item.get("favorites", 0),
                    "year": item.get("published", {}).get("from", "").split("-")[0] if item.get("published", {}).get("from") else "",
                    "authors": [a.get("name", "") for a in item.get("authors", [])]
                }
                all_manga.append(manga_entry)

            # Sleep to avoid hitting rate limits
            time.sleep(1.5)

        except Exception as e:
            print(f"Error fetching data: {e}")
            # Sleep longer if there's an error
            time.sleep(5)
            continue

    # Use pathlib for more robust path handling
    # Save to the project root data directory
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data"
    data_path = data_dir / "manga_data.json"

    # Create directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    # Save data to file
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(all_manga, f, indent=4, ensure_ascii=False)

    print(f"Saved {len(all_manga)} manga entries to {data_path}")
    return str(data_path)


if __name__ == "__main__":
    # This will only run when the script is executed directly
    fetch_manga_data(pages=10)
