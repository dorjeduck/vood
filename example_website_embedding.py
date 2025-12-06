#!/usr/bin/env python3
"""
Example: How to embed Vood animations into websites

This demonstrates three approaches:
1. Standalone HTML file (open directly in browser)
2. Embeddable HTML fragment (paste into existing webpage)
3. iframe embedding (reference the standalone file)
"""

from vood.vscene import VScene, VSceneExporter
from vood.velement import VElement
from vood.component import CircleState, SquareState
from vood.core import Color

# Create an animated scene
scene = VScene(width=400, height=400)

# Morphing circle to square
morph = VElement(keystates=[
    CircleState(radius=50, fill_color=Color("#FDBE02")),
    SquareState(size=80, fill_color=Color("#4ECDC4"))
])
scene.add_element(morph)

# Create exporter
exporter = VSceneExporter(scene, output_dir="website_exports")

print("Generating Vood animations for website embedding...")
print("=" * 70)

# ============================================================================
# Approach 1: Standalone HTML (full document)
# ============================================================================
print("\n1. STANDALONE HTML (full document)")
print("   Use case: Open directly in browser or embed via iframe")

standalone_file = exporter.to_html(
    filename="animation_standalone",
    total_frames=60,
    framerate=30,
    interactive=True,
    embeddable=False  # Full HTML document
)
print(f"   ✓ Created: {standalone_file}")
print(f"   Opens as: Full webpage with controls")

# ============================================================================
# Approach 2: Embeddable HTML (fragment only)
# ============================================================================
print("\n2. EMBEDDABLE HTML (fragment only)")
print("   Use case: Paste directly into your existing webpage")

embeddable_file = exporter.to_html(
    filename="animation_embeddable",
    total_frames=60,
    framerate=30,
    interactive=True,
    embeddable=True  # Just the content, no <html> wrapper
)
print(f"   ✓ Created: {embeddable_file}")
print(f"   Contains: Only <style>, <div>, and <script> tags")

# ============================================================================
# Approach 3: Auto-play animation (no controls)
# ============================================================================
print("\n3. AUTO-PLAY ANIMATION (embeddable)")
print("   Use case: Simple looping animation in your page")

autoplay_file = exporter.to_html(
    filename="animation_autoplay",
    total_frames=60,
    framerate=30,
    interactive=False,  # No controls, just auto-play
    embeddable=True     # Fragment for embedding
)
print(f"   ✓ Created: {autoplay_file}")
print(f"   Contains: Auto-playing loop animation")

# ============================================================================
# Create example HTML page showing all approaches
# ============================================================================
print("\n4. Creating example webpage...")

example_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vood Animation Embedding Examples</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
            background: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4ECDC4;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 40px;
        }}
        .example {{
            background: white;
            padding: 30px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .code {{
            background: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            overflow-x: auto;
            margin: 15px 0;
        }}
        .animation-container {{
            display: flex;
            justify-content: center;
            padding: 20px;
            background: #fafafa;
            border-radius: 4px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <h1>Vood Animation Embedding Examples</h1>
    <p>This page demonstrates different ways to embed Vood animations in your website.</p>

    <!-- Example 1: iframe embedding -->
    <div class="example">
        <h2>Method 1: iframe Embedding (Easiest)</h2>
        <p>Simply reference the standalone HTML file in an iframe:</p>
        <div class="code">
&lt;iframe src="animation_standalone.html"
        width="500" height="600"
        frameborder="0"&gt;
&lt;/iframe&gt;
        </div>
        <div class="animation-container">
            <iframe src="animation_standalone.html"
                    width="500" height="600"
                    frameborder="0"
                    style="border: 1px solid #ddd; border-radius: 4px;">
            </iframe>
        </div>
        <p><strong>Pros:</strong> Simple, isolated, no CSS/JS conflicts<br>
           <strong>Cons:</strong> Fixed size, less flexible styling</p>
    </div>

    <!-- Example 2: Direct embedding -->
    <div class="example">
        <h2>Method 2: Direct Embedding (Most Flexible)</h2>
        <p>Paste the embeddable HTML content directly into your page:</p>
        <div class="code">
&lt;div class="my-animation"&gt;
    &lt;!-- Paste contents of animation_embeddable.html here --&gt;
&lt;/div&gt;
        </div>
        <div class="animation-container">
            <!-- The embeddable content would go here -->
            <div style="text-align: center; padding: 40px; color: #999;">
                📄 Embeddable content from animation_embeddable.html goes here
            </div>
        </div>
        <p><strong>Pros:</strong> Full control over styling and layout<br>
           <strong>Cons:</strong> Requires manual copy-paste</p>
    </div>

    <!-- Example 3: Auto-play animation -->
    <div class="example">
        <h2>Method 3: Auto-Play Animation</h2>
        <p>For simple looping animations without controls:</p>
        <div class="code">
&lt;div class="auto-animation"&gt;
    &lt;!-- Paste contents of animation_autoplay.html here --&gt;
&lt;/div&gt;
        </div>
        <div class="animation-container">
            <!-- Auto-play content would go here -->
            <div style="text-align: center; padding: 40px; color: #999;">
                ▶️ Auto-playing animation from animation_autoplay.html goes here
            </div>
        </div>
        <p><strong>Pros:</strong> Clean, minimal, auto-plays and loops<br>
           <strong>Cons:</strong> No user controls</p>
    </div>

    <hr style="margin: 40px 0; border: none; border-top: 2px solid #eee;">

    <p style="text-align: center; color: #666;">
        Generated with <a href="https://github.com/dorjeduck/vood"
                          style="color: #4ECDC4; text-decoration: none;">Vood</a>
    </p>
</body>
</html>
"""

example_page_path = "website_exports/embedding_examples.html"
with open(example_page_path, 'w', encoding='utf-8') as f:
    f.write(example_page)

print(f"   ✓ Created: {example_page_path}")

print("\n" + "=" * 70)
print("✅ All files created successfully!")
print("\nNext steps:")
print("1. Open embedding_examples.html in your browser to see the demos")
print("2. For direct embedding, copy content from animation_embeddable.html")
print("3. For iframe embedding, use animation_standalone.html")
print("=" * 70)
