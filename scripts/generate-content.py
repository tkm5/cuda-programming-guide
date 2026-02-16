"""Generate Japanese MDX content from English transcripts using Claude API."""

import json
import os
import sys
import urllib.request

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

SECTION_TITLES = {
    1: "Introduction to the Nvidia GPUs hardware",
    2: "Installing CUDA and other programs",
    3: "Introduction to CUDA programming",
    4: "Profiling",
    5: "Performance analysis for the previous applications",
    6: "2D Indexing",
    7: "Shared Memory + Warp Divergence",
    8: "Debugging tools",
    9: "Vector Reduction",
    10: "Roofline model",
    11: "Matrix Multiplication (Bonus)",
    12: "Profiling - nsight systems",
}

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

SECTION_DIFFICULTY = {
    1: "beginner",
    2: "beginner",
    3: "beginner",
    4: "intermediate",
    5: "intermediate",
    6: "intermediate",
    7: "advanced",
    8: "intermediate",
    9: "advanced",
    10: "advanced",
    11: "advanced",
    12: "intermediate",
}


def get_api_key() -> str:
    """Get Anthropic API key from environment."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("Error: ANTHROPIC_API_KEY environment variable is required.")
        sys.exit(1)
    return key


SYSTEM_PROMPT = """あなたはCUDAプログラミングの専門家です．英語のUdemyレクチャートランスクリプトを基に，日本語の技術解説MDXコンテンツを生成してください．

ルール:
- 句点は「．」（全角ピリオド），読点は「，」（全角カンマ）を使用
- リストはハイフン（-）を使用
- MDXのfrontmatterは含めない（別途付与する）
- 技術用語は適切にコードブロック（`backtick`）で囲む
- CUDAのコード例がある場合はC/CUDAコードブロックで記述
- Mermaidダイアグラムを適切に含める（アーキテクチャ図，フロー図など）
- 以下のセクション構成で記述:
  1. ## 概要（レクチャーの要約，2-3文）
  2. ## 主要な内容（本文，複数のh3サブセクションに分割）
  3. ## コード例（該当する場合）
  4. ## まとめ（箇条書きで3-5点）
- 各セクションは充実した内容にする（全体で800-1500文字程度）
- トランスクリプトの内容を忠実に反映しつつ，構造化された解説にする"""


def generate_mdx_content(api_key: str, transcript: str, title: str, section_title: str) -> str:
    """Generate Japanese MDX content from transcript using Claude API."""
    user_message = f"""以下のUdemyレクチャーのトランスクリプトを基に，日本語の技術解説MDXコンテンツを生成してください．

レクチャータイトル: {title}
セクション: {section_title}

トランスクリプト:
{transcript}"""

    payload = json.dumps({
        "model": "claude-sonnet-4-5-20250929",
        "max_tokens": 4096,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        method="POST",
    )
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")
    req.add_header("content-type", "application/json")

    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    content = result.get("content", [])
    if content and content[0].get("type") == "text":
        return content[0]["text"]

    return ""


def build_frontmatter(video: dict) -> str:
    """Build MDX frontmatter for a lecture."""
    s = video["s"]
    l_num = video["l"]
    title = video["title"]
    section_title = SECTION_TITLES[s]
    category = SECTION_CATEGORIES[s]
    difficulty = SECTION_DIFFICULTY[s]
    order = s * 100 + l_num

    ja_title = f"S{s}-L{l_num}: {title}"
    desc = f"{section_title} - {title}の解説"

    return f'''---
title: "{ja_title}"
description: "{desc}"
sectionNumber: {s}
sectionTitle: "{section_title}"
lectureNumber: {l_num}
lectureTitle: "{title}"
difficulty: "{difficulty}"
tags: ["{category}", "cuda"]
category: "{category}"
order: {order}
---'''


def main():
    api_key = get_api_key()

    with open("data/video_lectures.json") as f:
        videos = json.load(f)

    # Filter to specific sections if argument provided
    target_sections = None
    if len(sys.argv) > 1:
        target_sections = [int(x) for x in sys.argv[1].split(",")]
        print(f"Processing sections: {target_sections}")

    success = 0
    errors = []

    for video in videos:
        s = video["s"]
        l_num = video["l"]
        title = video["title"]

        if target_sections and s not in target_sections:
            continue

        lecture_id = video["id"]
        transcript_path = f"data/transcripts/{lecture_id}.txt"
        output_path = f"src/data/sections/{s:02d}/lecture-{l_num:02d}.mdx"

        if not os.path.exists(transcript_path):
            errors.append(f"S{s}-L{l_num}: No transcript at {transcript_path}")
            continue

        with open(transcript_path) as f:
            transcript = f.read().strip()

        if not transcript:
            errors.append(f"S{s}-L{l_num}: Empty transcript")
            continue

        print(f"Generating S{s}-L{l_num}: {title}...")

        try:
            section_title = SECTION_TITLES[s]
            content = generate_mdx_content(api_key, transcript, title, section_title)
            frontmatter = build_frontmatter(video)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as f:
                f.write(frontmatter + "\n\n" + content + "\n")

            success += 1
            print(f"  Done ({success})")

        except Exception as e:
            errors.append(f"S{s}-L{l_num}: {e}")
            print(f"  Error: {e}")

    print(f"\nDone: {success} files generated, {len(errors)} errors")
    if errors:
        print("Errors:")
        for err in errors:
            print(f"  - {err}")


if __name__ == "__main__":
    main()
