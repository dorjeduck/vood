# Preview Animation Color Schemes

Vood provides 10 modern, minimal color schemes for the Jupyter notebook preview animation controls. All designs use flat colors (no gradients) to keep focus on the animation itself.

## Configuration

To set a color scheme, add this to your `vood.toml` file:

```toml
[jupyter]
color_scheme = "dark"  # Choose from options below
```

## Available Color Schemes

### 1. **light** (default)
Clean white background with blue accents
- Best for: General use, bright environments

### 2. **dark**
Dark gray background with blue accents
- Best for: Low-light environments, reduced eye strain

### 3. **slate**
Subtle slate gray with muted accents
- Best for: Professional presentations, minimal distraction

### 4. **neutral**
Pure grayscale theme
- Best for: Maximum minimalism, no color preference

### 5. **ocean**
Light blue tones with ocean accents
- Best for: Calming, water-themed content

### 6. **forest**
Light green tones with forest accents
- Best for: Natural, environmental content

### 7. **purple**
Light purple background with vibrant purple accents
- Best for: Creative projects, modern aesthetic

### 8. **rose**
Light rose background with red accents
- Best for: Warm, friendly presentations

### 9. **amber**
Light amber/yellow background with warm accents
- Best for: Energy, optimism

### 10. **monokai**
Dark editor theme (monokai-inspired)
- Best for: Developer environments, matching code editors

## Usage

```python
from vood.vscene import VScene

scene = VScene()
# ... add elements ...

# Color scheme is automatically applied from config
scene.preview_animation(num_frames=20, play_interval_ms=100)
```

## Design Philosophy

All color schemes follow modern, minimal design principles:
- **Flat colors** - No gradients, keeping focus on the animation
- **Subtle shadows** - Minimal use of shadows, clean appearance
- **Rounded corners** - Soft 6-8px border radius for modern feel
- **Compact sizing** - Small 40px buttons, thin 4px slider
- **Accessible contrast** - All themes meet WCAG contrast requirements

## Implementation Details

Each color scheme defines:
- **Background**: Container background color
- **Control background**: Buttons and info panels
- **Control hover**: Hover state for controls
- **Accent**: Play button and slider (primary action color)
- **Accent hover**: Hover state for accent elements
- **Text**: Primary text color
- **Text muted**: Secondary/dimmed text

Color schemes are defined in `vood/vscene/preview_color_schemes.py`.
