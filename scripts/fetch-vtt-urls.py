"""Fetch VTT subtitle URLs for all video lectures from Udemy Business API."""

import json
import os
import sys
import time
import urllib.request

BASE_URL = "https://deloittedevelopment.udemy.com/api-2.0"
COURSE_ID = 4267614


def get_token() -> str:
    """Get Udemy Business API token from environment."""
    token = os.environ.get("UDEMY_BEARER_TOKEN")
    if not token:
        print("Error: UDEMY_BEARER_TOKEN environment variable is required.")
        print("Export it with: export UDEMY_BEARER_TOKEN='your-token-here'")
        sys.exit(1)
    return token


def fetch_lecture_captions(token: str, lecture_id: int) -> str | None:
    """Fetch VTT URL for a specific lecture."""
    url = (
        f"{BASE_URL}/users/me/subscribed-courses/{COURSE_ID}"
        f"/lectures/{lecture_id}/"
        f"?fields[lecture]=asset"
        f"&fields[asset]=captions,title"
    )

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        asset = data.get("asset", {})
        captions = asset.get("captions", [])

        # Prefer English captions
        for caption in captions:
            if caption.get("locale_id") == "en_US" or caption.get("video_label") == "English":
                return caption.get("url")

        # Fallback to first available caption
        if captions:
            return captions[0].get("url")

        return None

    except Exception as e:
        print(f"  Error fetching lecture {lecture_id}: {e}")
        return None


def main():
    token = get_token()

    # Load video lectures
    with open("data/video_lectures.json") as f:
        videos = json.load(f)

    print(f"Fetching VTT URLs for {len(videos)} lectures...")
    vtt_urls = {}
    errors = []

    for i, video in enumerate(videos):
        lecture_id = video["id"]
        s = video["s"]
        l_num = video["l"]

        vtt_url = fetch_lecture_captions(token, lecture_id)

        if vtt_url:
            vtt_urls[str(lecture_id)] = vtt_url
        else:
            errors.append(f"S{s}-L{l_num} ({lecture_id}): No captions")

        if (i + 1) % 5 == 0:
            print(f"  Progress: {i + 1}/{len(videos)}")

        # Rate limiting
        time.sleep(0.3)

    # Save VTT URLs
    with open("data/vtt_urls.json", "w") as f:
        json.dump(vtt_urls, f, indent=2)

    print(f"\nDone: {len(vtt_urls)} VTT URLs saved, {len(errors)} errors")
    if errors:
        print("Missing captions:")
        for err in errors:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
