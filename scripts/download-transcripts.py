"""Download VTT files and convert to plain text transcripts."""

import json
import os
import re
import urllib.request


def parse_vtt(vtt_text: str) -> str:
    """Parse VTT content to plain text, removing timestamps and metadata."""
    lines = vtt_text.split("\n")
    text_lines = []
    prev_text = ""

    for line in lines:
        trimmed = line.strip()
        # Skip empty lines, WEBVTT header, timestamps, sequence numbers, metadata
        if not trimmed:
            continue
        if trimmed == "WEBVTT":
            continue
        if "-->" in trimmed:
            continue
        if re.match(r"^\d+$", trimmed):
            continue
        if trimmed.startswith("Kind:") or trimmed.startswith("Language:"):
            continue

        # Remove HTML tags
        clean = re.sub(r"<[^>]+>", "", trimmed)
        if clean and clean != prev_text:
            text_lines.append(clean)
            prev_text = clean

    return " ".join(text_lines)


def main():
    # Load video lectures mapping
    with open("data/video_lectures.json") as f:
        videos = json.load(f)

    # Load VTT URLs
    with open("data/vtt_urls.json") as f:
        vtt_urls = json.load(f)

    # Create transcript directories
    for s in range(1, 13):
        os.makedirs(f"data/transcripts/section-{s:02d}", exist_ok=True)

    success = 0
    errors = []

    for video in videos:
        s = video["s"]
        l = video["l"]
        lecture_id = str(video["id"])
        title = video["title"]

        url = vtt_urls.get(lecture_id)
        if not url:
            errors.append(f"S{s}-L{l} ({lecture_id}): No VTT URL")
            continue

        output_path = f"data/transcripts/section-{s:02d}/lecture-{l:02d}.txt"

        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                vtt_text = resp.read().decode("utf-8")

            transcript = parse_vtt(vtt_text)

            with open(output_path, "w") as f:
                f.write(transcript)

            success += 1
            if success % 10 == 0:
                print(f"Progress: {success}/{len(videos)}")

        except Exception as e:
            errors.append(f"S{s}-L{l} ({lecture_id}): {e}")

    print(f"\nDone: {success} transcripts saved, {len(errors)} errors")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
