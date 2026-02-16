"""Fetch curriculum data from Udemy Business API and generate data files."""

import json
import os
import sys
import urllib.request

# Udemy Business API configuration
BASE_URL = "https://deloittedevelopment.udemy.com/api-2.0"
COURSE_ID = 4267614

# Category mapping for CUDA course sections
SECTION_CATEGORIES = {
    1: "gpu-hardware",
    2: "setup",
    3: "cuda-basics",
    4: "profiling",
    5: "performance",
    6: "indexing",
    7: "memory-optimization",
    8: "debugging",
    9: "algorithms",
    10: "performance",
    11: "algorithms",
    12: "profiling",
}


def get_token() -> str:
    """Get Udemy Business API token from environment."""
    token = os.environ.get("UDEMY_BEARER_TOKEN")
    if not token:
        print("Error: UDEMY_BEARER_TOKEN environment variable is required.")
        print("Export it with: export UDEMY_BEARER_TOKEN='your-token-here'")
        sys.exit(1)
    return token


def fetch_curriculum(token: str) -> dict:
    """Fetch curriculum data from Udemy Business API."""
    url = (
        f"{BASE_URL}/courses/{COURSE_ID}/cached-subscriber-curriculum-items/"
        f"?page_size=300&fields[lecture]=title,asset,object_index"
        f"&fields[chapter]=title,object_index"
        f"&fields[asset]=title,asset_type,length"
    )

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_curriculum(data: dict) -> tuple[list, list]:
    """Parse curriculum data into all_items and video_lectures lists."""
    all_items = []
    video_lectures = []

    current_section = 0
    lecture_in_section = 0
    current_section_title = ""

    for item in data.get("results", []):
        item_class = item.get("_class", "")

        if item_class == "chapter":
            current_section += 1
            lecture_in_section = 0
            current_section_title = item.get("title", "")
            continue

        if item_class == "lecture":
            lecture_in_section += 1
            asset = item.get("asset", {})
            asset_type = asset.get("asset_type", "Unknown")
            category = SECTION_CATEGORIES.get(current_section, "gpu-hardware")

            entry = {
                "type": "lecture",
                "section": current_section,
                "lecture": lecture_in_section,
                "id": item["id"],
                "title": item.get("title", ""),
                "asset_type": asset_type,
                "section_title": current_section_title,
                "category": category,
            }
            all_items.append(entry)

            if asset_type == "Video":
                video_lectures.append({
                    "s": current_section,
                    "l": lecture_in_section,
                    "id": item["id"],
                    "title": item.get("title", ""),
                })

        if item_class == "quiz":
            lecture_in_section += 1
            category = SECTION_CATEGORIES.get(current_section, "gpu-hardware")
            entry = {
                "type": "quiz",
                "section": current_section,
                "lecture": lecture_in_section,
                "id": item.get("id", 0),
                "title": item.get("title", "Quiz"),
                "asset_type": "Quiz",
                "section_title": current_section_title,
                "category": category,
            }
            all_items.append(entry)

    return all_items, video_lectures


def main():
    token = get_token()

    print("Fetching curriculum...")
    curriculum = fetch_curriculum(token)

    # Save raw curriculum
    os.makedirs("data", exist_ok=True)
    with open("data/curriculum.json", "w") as f:
        json.dump(curriculum, f, indent=2, ensure_ascii=False)
    print(f"Saved curriculum.json ({curriculum.get('count', 0)} items)")

    # Parse into structured data
    all_items, video_lectures = parse_curriculum(curriculum)

    with open("data/all_items.json", "w") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    print(f"Saved all_items.json ({len(all_items)} items)")

    with open("data/video_lectures.json", "w") as f:
        json.dump(video_lectures, f, indent=2, ensure_ascii=False)
    print(f"Saved video_lectures.json ({len(video_lectures)} video lectures)")

    # Print summary
    sections = {}
    for item in all_items:
        s = item["section"]
        if s not in sections:
            sections[s] = {"title": item["section_title"], "count": 0}
        sections[s]["count"] += 1

    print("\nCourse Structure:")
    for s in sorted(sections.keys()):
        info = sections[s]
        print(f"  Section {s}: {info['title']} ({info['count']} items)")


if __name__ == "__main__":
    main()
