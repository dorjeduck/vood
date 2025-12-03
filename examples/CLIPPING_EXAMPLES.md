# SVG Clipping and Masking Examples

This directory contains comprehensive examples demonstrating all aspects of Vood's clipping and masking features.

## Feature Coverage

### Basic Clipping

**`clipping_basic.py`** - Simple static clip-path
- Rectangle clipped by a circle
- State property approach
- SVG output

### Animated Clipping

**`clipping_animated.py`** - Clip expands over time
- Property keystates approach
- Clip radius animates from 30 to 100
- MP4 output (60 frames)

**`clipping_morphing.py`** - Clip shape morphs between types
- Circle → Square → Triangle
- Vertex-based morphing
- MP4 output (90 frames)

### VElement Composition

**`clipping_composition.py`** - Animated clip element
- Circle morphs to square
- VElement composition approach
- MP4 output (60 frames)

**`clipping_reusable.py`** - One clip, multiple elements
- Single clip definition
- Applied to two rectangles
- SVG output

### Multiple Clips

**`clipping_multiple.py`** - Intersection of two clips
- Circle AND rectangle clips
- Nested groups approach
- SVG output

### Clip Transforms

**`clipping_transforms.py`** - Clips with position/rotation/scale
- Clip offset and scaled
- Demonstrates clip transform support
- SVG output

### Scene-Level Clipping

**`clipping_scene.py`** - Viewport clipping
- Circular viewport
- Applied to entire scene
- 9 circles in grid, all clipped
- SVG output

### Masking

**`masking_basic.py`** - Opacity-based transparency
- Rectangle with circular mask
- Partial opacity (0.7)
- SVG output

**`masking_animated.py`** - Fading mask effect
- Mask opacity animates 0.0 → 1.0
- Fade-in effect
- MP4 output (60 frames)

## Running Examples

```bash
# Static examples (SVG)
python examples/clipping_basic.py
python examples/clipping_multiple.py
python examples/clipping_reusable.py
python examples/clipping_transforms.py
python examples/clipping_scene.py
python examples/masking_basic.py

# Animated examples (MP4)
python examples/clipping_animated.py
python examples/clipping_composition.py
python examples/clipping_morphing.py
python examples/masking_animated.py
```

## Feature Matrix

| Feature | Example File | Output |
|---------|--------------|--------|
| Static clip (state property) | `clipping_basic.py` | SVG |
| Animated clip (property keystates) | `clipping_animated.py` | MP4 |
| Morphing clip shapes | `clipping_morphing.py` | MP4 |
| Clip element (composition) | `clipping_composition.py` | MP4 |
| Reusable clips | `clipping_reusable.py` | SVG |
| Multiple clips (intersection) | `clipping_multiple.py` | SVG |
| Clip transforms | `clipping_transforms.py` | SVG |
| Scene-level clipping | `clipping_scene.py` | SVG |
| Basic masking | `masking_basic.py` | SVG |
| Animated masking | `masking_animated.py` | MP4 |

## API Patterns Demonstrated

### State Property Approach
```python
VElement(state=RectangleState(
    clip_state=CircleState(radius=80)
))
```

### Property Keystates
```python
VElement(
    state=RectangleState(...),
    property_keystates={
        "clip_state": [
            (CircleState(radius=40), 0.0),
            (CircleState(radius=80), 1.0),
        ]
    }
)
```

### VElement Composition
```python
clip = VElement(keystates=[...])
VElement(state=RectangleState(...), clip_element=clip)
```

### Multiple Clips
```python
VElement(state=RectangleState(
    clip_states=[
        CircleState(...),
        RectangleState(...)
    ]
))
```

### Scene-Level
```python
VScene(clip_state=CircleState(radius=150))
```
