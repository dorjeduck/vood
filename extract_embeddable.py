#!/usr/bin/env python3
"""
Extract embeddable content from Vood HTML exports.
This creates a version that can be directly embedded into a webpage.
"""

import sys
import re
from pathlib import Path


def extract_embeddable_content(html_file: str, output_file: str = None):
    """
    Extract just the content between <body> tags for embedding.

    Args:
        html_file: Path to the full HTML export
        output_file: Optional output file (defaults to {input}_embed.html)
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract everything between <body> and </body>
    match = re.search(r'<body>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
    if not match:
        print("Error: Could not find <body> tags in HTML file")
        return

    embeddable_content = match.group(1).strip()

    # Determine output filename
    if output_file is None:
        input_path = Path(html_file)
        output_file = input_path.parent / f"{input_path.stem}_embed.html"

    # Write embeddable content
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(embeddable_content)

    print(f"✓ Extracted embeddable content to: {output_file}")
    print(f"\nTo use in your webpage:")
    print(f"1. Copy the contents of {output_file}")
    print(f"2. Paste it into your HTML where you want the animation")
    print(f"\nExample:")
    print(f"  <div class=\"vood-animation\">")
    print(f"    <!-- Paste content here -->")
    print(f"  </div>")

    return str(output_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_embeddable.py <html_file> [output_file]")
        print("\nExample:")
        print("  python extract_embeddable.py animation_20251204_123456_interactive.html")
        sys.exit(1)

    html_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    extract_embeddable_content(html_file, output_file)
