# Jupyter Notebook Support

Vood provides comprehensive support for Jupyter notebooks, making it easy to create, preview, and test SVG animations interactively.

## Static Scenes

Display static scenes directly in Jupyter by simply evaluating the scene object:

```python
from vood.core.color import Color
from vood.vscene import VScene
from vood.velement import VElement
from vood.component.state import CircleState

# Create a scene
scene = VScene(width=400, height=400, background=Color("#000033"))
scene.add_element(VElement(state=CircleState(radius=50, fill_color=Color(255, 0, 0))))

# Display it - just evaluate the scene
scene
```

The scene will automatically display inline using the `_repr_svg_()` method. All dimensions and the centered coordinate system (0,0 at center) are properly respected.

You can also explicitly control the display:

```python
# Display inline (same as just typing 'scene')
scene.display_inline()

# Display in an iframe
scene.display_iframe()

# Display as an image
scene.display_image()
```

## Animation Preview

Vood offers two ways to preview animations in Jupyter without exporting to video - perfect for fast iteration and testing.

### Grid Layout

The grid layout displays multiple frames simultaneously, giving you an instant overview of the entire animation:

```python
from vood.velement import VElement
from vood.component.state import CircleState
from vood.core.color import Color

# Create animated scene
scene = VScene(width=400, height=400, background=Color("#000033"))

# Circle that moves and changes color
circle = VElement(keystates=[
    (0.0, CircleState(x=-100, radius=20, fill_color=Color(255, 0, 0))),
    (0.5, CircleState(x=0, radius=50, fill_color=Color(0, 255, 0))),
    (1.0, CircleState(x=100, radius=20, fill_color=Color(0, 0, 255)))
])
scene.add_element(circle)

# Preview with grid - shows all frames at once
scene.preview_animation(num_frames=10, layout="grid")

# For large scenes, scale down the frames
scene.preview_animation(num_frames=10, layout="grid", scale=0.5)  # Half size
scene.preview_animation(num_frames=10, layout="grid", scale=0.3)  # Even smaller
```

**Grid Layout Features:**
- Shows all frames simultaneously
- Each frame labeled with its time (t=0.00, t=0.11, etc.)
- Frames arranged in a flexible grid
- `scale` parameter to make frames smaller (useful for large scenes or many frames)
- Best for: Quick visual overview, comparing frames side-by-side

### Navigator Layout

The navigator layout displays one frame at a time with interactive navigation buttons:

```python
# Preview with navigator - click through frames
scene.preview_animation(num_frames=20, layout="navigator")
```

**Navigator Layout Features:**
- Shows one frame at a time at full size
- ◀ Previous and Next ▶ buttons to navigate
- Frame counter (Frame X / Total)
- Current time display (t=0.00)
- Buttons disable at start/end
- Smooth transitions between frames
- Best for: Detailed inspection, animations with many frames, large scenes

**Example with more frames:**
```python
# Complex animation with many keyframes
scene.preview_animation(num_frames=30, layout="navigator")
```

The navigator works perfectly even with 20+ frames since you just click through them one at a time.

## Video Export

For smooth playback and final output, export animations to MP4 format:

```python
from IPython.display import Video

# Export to MP4
scene.export("animation.mp4", total_frames=60, framerate=30)

# Display the video inline in Jupyter
Video("animation.mp4", embed=True, width=400)
```

**Export Options:**

```python
# Control quality and size
scene.export(
    "animation.mp4",
    total_frames=120,      # More frames = smoother animation
    framerate=30,          # FPS (24, 30, or 60 common)
    png_width_px=1920      # Resolution (higher = better quality, slower)
)
```

**When to use video export:**
- Final output for presentations or sharing
- Smooth continuous playback
- Complex animations with vertex morphing
- When you need a specific framerate
- For embedding in other documents/websites

**When to use preview methods:**
- Fast iteration during development
- Quick checks of animation timing
- Testing different keystate configurations
- When MP4 encoding would be too slow

## Coordinate System

Vood uses a **centered coordinate system** by default:
- Origin (0,0) is at the center of the scene
- X increases to the right, Y increases upward
- Specified via `origin="center"` (default)

```python
# Center-based coordinates (default)
scene = VScene(width=400, height=400, origin="center")
circle = CircleState(x=0, y=0, radius=50)  # Circle at center

# Top-left coordinates (if needed)
scene = VScene(width=400, height=400, origin="top-left")
circle = CircleState(x=200, y=200, radius=50)  # Circle at center
```

The centered coordinate system is configured via `vood.toml` and applies consistently across all display methods.

## Tips for Jupyter Workflow

1. **Start with grid preview** to get a quick overview of your animation
2. **Use navigator** to inspect specific frames or transitions in detail
3. **Scale down grid frames** when working with large scenes: `scale=0.3`
4. **Export to MP4** only when you need smooth playback or final output
5. **Restart kernel** after updating Vood code to clear cached display methods

## Common Patterns

**Quick animation test:**
```python
# Create, preview, iterate
scene = create_my_scene()
scene.preview_animation(num_frames=8, layout="grid", scale=0.4)
# Adjust keystates, run again
```

**Detailed inspection:**
```python
# Use navigator for frame-by-frame checking
scene.preview_animation(num_frames=20, layout="navigator")
```

**Final export:**
```python
# Export and display
scene.export("final.mp4", total_frames=90, framerate=30)
Video("final.mp4", embed=True, width=600)
```

## Examples

See the `examples/` directory for complete Jupyter notebook examples demonstrating:
- Basic static scenes
- Keystate animations
- Complex morphing animations
- Layout compositions
- Easing functions
- Property animations

---

For more information about Vood's animation system, see the main [README](../README.md).
