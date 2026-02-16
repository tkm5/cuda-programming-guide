"""Generate MDX skeleton files from video_lectures.json."""

import json
import os

# Section titles mapping
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

# Category mapping
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

# Difficulty mapping
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


def generate_mdx(video: dict) -> str:
    """Generate MDX content for a lecture."""
    s = video["s"]
    l_num = video["l"]
    title = video["title"]
    section_title = SECTION_TITLES[s]
    category = SECTION_CATEGORIES[s]
    difficulty = SECTION_DIFFICULTY[s]
    order = s * 100 + l_num

    # Generate Japanese title
    ja_title = f"S{s}-L{l_num}: {title}"

    frontmatter = f'''---
title: "{ja_title}"
description: "{section_title} - {title}の解説"
sectionNumber: {s}
sectionTitle: "{section_title}"
lectureNumber: {l_num}
lectureTitle: "{title}"
difficulty: "{difficulty}"
tags: ["{category}", "cuda"]
category: "{category}"
order: {order}
---'''

    body = f"""

## 概要

このレクチャーでは，{title}について解説します．

## 主要なポイント

- ポイント1（トランスクリプトから生成予定）
- ポイント2
- ポイント3

## まとめ

- {title}の基本概念を理解した
- 実践的な応用方法を学んだ
"""

    return frontmatter + body


def main():
    with open("data/video_lectures.json") as f:
        videos = json.load(f)

    for video in videos:
        s = video["s"]
        l_num = video["l"]

        dir_path = f"src/data/sections/{s:02d}"
        os.makedirs(dir_path, exist_ok=True)

        file_path = f"{dir_path}/lecture-{l_num:02d}.mdx"
        content = generate_mdx(video)

        with open(file_path, "w") as f:
            f.write(content)

    print(f"Generated {len(videos)} MDX files")


if __name__ == "__main__":
    main()
