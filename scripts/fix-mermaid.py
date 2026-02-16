"""Fix mermaid syntax errors in MDX files.

Wraps unquoted Japanese text and special characters in mermaid node labels,
subgraph names, and arrow labels with double quotes.
"""

import glob
import re


def needs_quoting(text: str) -> bool:
    """Check if text contains characters that need quoting in mermaid."""
    # Japanese characters (Hiragana, Katakana, CJK)
    if re.search(r'[\u3000-\u9fff\uff00-\uffef]', text):
        return True
    # Special characters that cause issues
    if any(c in text for c in [':', '=', '/', '+', '*', '?', '（', '）', '→', '←', '×', '✓', '<', '>']):
        return True
    return False


def fix_node_labels(line: str) -> str:
    """Fix unquoted node labels like A[text] -> A["text"]."""
    # Match node labels: ID[text] or ID{text} or ID(text)
    # But skip if already quoted: ID["text"]
    def fix_bracket(match):
        prefix = match.group(1)
        open_br = match.group(2)
        content = match.group(3)
        close_br = match.group(4)

        # Skip if already quoted
        if content.startswith('"') and content.endswith('"'):
            return match.group(0)

        if needs_quoting(content):
            # Escape any existing quotes in content
            escaped = content.replace('"', "'")
            return f'{prefix}{open_br}"{escaped}"{close_br}'
        return match.group(0)

    # Fix [...] labels (but not [...|...|...] which is arrow label syntax)
    line = re.sub(
        r'(\w+)\[([^\]"]*?)\](?!\()',
        lambda m: fix_bracket_simple(m, '[', ']'),
        line
    )

    # Fix {...} labels (diamond nodes)
    line = re.sub(
        r'(\w+)\{([^}"]*?)\}',
        lambda m: fix_bracket_simple(m, '{', '}'),
        line
    )

    return line


def fix_bracket_simple(match, open_br, close_br):
    """Fix a single bracket match."""
    prefix = match.group(1)
    content = match.group(2)

    # Skip if already quoted
    if content.startswith('"') and content.endswith('"'):
        return match.group(0)

    if needs_quoting(content):
        escaped = content.replace('"', "'")
        return f'{prefix}{open_br}"{escaped}"{close_br}'
    return match.group(0)


def fix_subgraph(line: str) -> str:
    """Fix unquoted subgraph names."""
    # Match: subgraph name (not already quoted)
    m = re.match(r'^(\s*subgraph\s+)(?!")(.*?)$', line)
    if m and needs_quoting(m.group(2).strip()):
        prefix = m.group(1)
        name = m.group(2).strip()
        # Skip if it has an ID like: subgraph ID["label"]
        if re.match(r'\w+\[', name):
            return line
        escaped = name.replace('"', "'")
        return f'{prefix}"{escaped}"'
    return line


def fix_arrow_labels(line: str) -> str:
    """Fix unquoted arrow labels like |text| -> |"text"|."""
    def fix_label(match):
        content = match.group(1)
        # Skip if already quoted
        if content.startswith('"') and content.endswith('"'):
            return match.group(0)
        if needs_quoting(content):
            escaped = content.replace('"', "'")
            return f'|"{escaped}"|'
        return match.group(0)

    line = re.sub(r'\|([^|"]+?)\|', fix_label, line)
    return line


def fix_mermaid_block(block: str) -> str:
    """Fix all issues in a mermaid block."""
    lines = block.split('\n')
    fixed_lines = []

    for line in lines:
        stripped = line.strip()

        # Skip empty lines and mermaid type declaration
        if not stripped or stripped in ('graph TD', 'graph LR', 'graph TB',
                                        'flowchart TD', 'flowchart LR', 'flowchart TB',
                                        'sequenceDiagram', 'classDiagram', 'end'):
            fixed_lines.append(line)
            continue

        # Skip style lines
        if stripped.startswith('style '):
            fixed_lines.append(line)
            continue

        # Fix subgraph
        if stripped.startswith('subgraph'):
            line = fix_subgraph(line)

        # Fix arrow labels |text|
        line = fix_arrow_labels(line)

        # Fix node labels [text], {text}
        line = fix_node_labels(line)

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def process_file(filepath: str) -> bool:
    """Process a single MDX file and fix mermaid blocks."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all mermaid blocks
    pattern = r'(```mermaid\n)(.*?)(```)'
    matches = list(re.finditer(pattern, content, re.DOTALL))

    if not matches:
        return False

    modified = False
    new_content = content

    # Process in reverse order to preserve positions
    for match in reversed(matches):
        block = match.group(2)
        fixed = fix_mermaid_block(block)
        if fixed != block:
            new_content = (
                new_content[:match.start(2)]
                + fixed
                + new_content[match.end(2):]
            )
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

    return modified


def main():
    files = sorted(glob.glob('src/data/sections/**/*.mdx', recursive=True))
    fixed_count = 0

    for filepath in files:
        if process_file(filepath):
            fixed_count += 1
            print(f'Fixed: {filepath}')

    print(f'\nTotal files fixed: {fixed_count}/{len(files)}')


if __name__ == '__main__':
    main()
