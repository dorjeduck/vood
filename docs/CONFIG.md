# Vood Configuration Guide

Vood uses TOML-based configuration files to customize default values globally. This allows you to set project-wide preferences without repeating them in every function call.

## Quick Start

Create a `vood.toml` file in your project directory:

```toml
[scene]
width = 1920
height = 1080

[state.visual]
fill_color = "#FDBE02"
stroke_color = "#AA0000"

[logging]
level = "DEBUG"
```

That's it! The config is automatically discovered and used by vood.

## Configuration File Locations

Vood automatically searches for configuration files in the following locations (in priority order):

1. **`./vood.toml`** - Project directory (highest priority)
2. **`~/.config/vood/config.toml`** - User config directory
3. **`~/.vood.toml`** - Home directory
4. **System defaults** - Built-in `vood/config/defaults.toml`

The first file found is used, with values merged on top of system defaults.

## Creating a Configuration File

### Option 1: Manual Creation

Simply create a `vood.toml` file with the options you want to customize:

```toml
[scene]
width = 1920
height = 1080
background_color = "#000000"
```

### Option 2: Generate Template

Use the built-in template generator to create a fully documented config file:

```python
from vood.config import create_config_template

create_config_template('vood.toml')
```

Or from command line:
```bash
python -c "from vood.config import create_config_template; create_config_template()"
```

This creates a `vood.toml` file with all available options and their default values.

## Available Configuration Options

### `[scene]` - Scene Defaults

Controls default values for `VScene` instances.

```toml
[scene]
width = 800                    # Scene width in pixels
height = 800                   # Scene height in pixels
background_color = "none"      # Background color (see Color Formats below)
background_opacity = 1.0       # Background opacity (0.0 to 1.0)
origin_mode = "center"         # Coordinate origin: "center" or "top-left"
```

**Usage:**
```python
from vood.vscene import VScene

# Uses config defaults
scene = VScene()

# Override specific values
scene = VScene(width=1024, height=768)
```

### `[state]` - Common State Properties

Default values for all state classes (inherited by all shapes).

```toml
[state]
x = 0.0          # X position
y = 0.0          # Y position
scale = 1.0      # Scale factor
opacity = 1.0    # Opacity (0.0 to 1.0)
rotation = 0.0   # Rotation in degrees
```

**Usage:**
```python
from vood.component.state import CircleState

# Uses config defaults (x=0.0, y=0.0, scale=1.0, opacity=1.0, rotation=0.0)
circle = CircleState(radius=50)

# Override specific values
circle = CircleState(radius=50, x=100, y=200, opacity=0.5)
```

**Example config:**
```toml
[state]
opacity = 0.8    # All shapes default to 80% opacity
scale = 1.5      # All shapes default to 150% scale
```

### `[state.visual]` - Vertex-Based Shape Properties

Default visual properties for vertex-based shapes (CircleState, EllipseState, StarState, PolygonState, etc.).

```toml
[state.visual]
fill_color = "none"       # Fill color (see Color Formats below)
fill_opacity = 1.0        # Fill opacity (0.0 to 1.0)
stroke_color = "none"     # Stroke color
stroke_opacity = 1.0      # Stroke opacity (0.0 to 1.0)
stroke_width = 1.0        # Stroke width in pixels
num_vertices = 128        # Vertex resolution for morphing
closed = true             # Whether shapes are closed by default
```

**Usage:**
```python
from vood.component.state.circle import CircleState

# Uses config default for num_vertices
circle = CircleState(radius=50)

# Override specific values
circle = CircleState(radius=50, _num_vertices=256)
```

**What uses config:**
- ✅ `_num_vertices` - Read from config if not specified

**What's currently hardcoded:**
- `fill_color`, `stroke_color`, `stroke_width`, etc. - Use hardcoded defaults
- Can be accessed programmatically: `config.get('state.visual.fill_color')`

### `[morphing]` - Morphing/Interpolation Settings

Controls how shapes morph between different states, particularly when hole counts differ.

```toml
[morphing]
# Hole matching strategy for shapes with different hole counts
# Options (ordered by sophistication): "clustering" (default), "hungarian", "greedy", "discrete", "simple"
hole_mapper = "clustering"

[morphing.clustering]
# Clustering-specific settings (only used when hole_mapper = "clustering")
balance_clusters = true      # Enforce balanced cluster sizes (avoids 4-1 splits)
max_iterations = 50          # Maximum k-means iterations
random_seed = 42             # Random seed for reproducible clustering
```

**Available Strategies:**

| Strategy | Best For | Requires | Balance | Performance |
|----------|----------|----------|---------|-------------|
| `clustering` (default) | Visual quality, balanced morphing | Pure Python | ✅ Yes | Fast |
| `hungarian` | Optimal distance (globally minimal) | scipy | ✅ Yes | Slower (O(n³)) |
| `greedy` | Speed, simplicity | Pure Python | ⚠️ Maybe | Very Fast |
| `discrete` | Mixed transitions (some move, some appear/disappear) | Pure Python | N/A | Fast |
| `simple` | Complete independence (all old disappear, all new appear) | Pure Python | N/A | Very Fast |

**Usage:**
```python
from vood.component.state import PerforatedShapeState

# Automatically uses config strategy (default: clustering)
state1 = PerforatedShapeState(
    outer_shape={"type": "circle", "radius": 100},
    holes=[
        {"type": "circle", "radius": 20, "x": -30, "y": 0},
        {"type": "circle", "radius": 20, "x": 30, "y": 0},
    ]
)
```

**Programmatic override:**
```python
from vood.transition.interpolation.align_vertices import get_aligned_vertices
from vood.transition.interpolation.hole_matching import HungarianMapper

# Use different matcher for specific alignment
contours1, contours2 = get_aligned_vertices(
    state1, state2,
    hole_mapper=HungarianMapper()
)
```

**Strategy Details:**

- **`clustering`** (Recommended): Uses k-means spatial clustering with optional balancing
  - Groups N holes into M clusters based on proximity
  - `balance_clusters=true` ensures roughly equal distribution (e.g., 2-3 instead of 1-4)
  - `max_iterations` controls k-means convergence
  - `random_seed` ensures reproducible results

- **`hungarian`**: Globally optimal assignment
  - Minimizes total distance across all pairings
  - Most sophisticated matching algorithm
  - Requires scipy: `pip install scipy`
  - No additional configuration options

- **`greedy`**: Fast nearest-centroid matching
  - Each hole independently finds closest destination
  - May produce unbalanced groupings depending on geometry
  - No additional configuration options

- **`discrete`**: Discrete transitions with selective matching
  - Some holes move to new positions (matched pairs)
  - Excess holes shrink to zero at their current positions
  - New holes grow from zero at their final positions
  - Good for UI-style discrete animations
  - No additional configuration options

- **`simple`**: Complete independence between old and new
  - ALL old holes shrink to zero at their positions
  - ALL new holes grow from zero at their positions
  - No matching or movement between old and new
  - Simplest strategy (O(N+M) performance)
  - Best for completely different hole layouts
  - No additional configuration options

**Example - Disable Balancing:**
```toml
[morphing]
hole_matcher = "clustering"

[morphing.clustering]
balance_clusters = false  # Pure k-means without rebalancing
```

**Example - Use Hungarian (requires scipy):**
```toml
[morphing]
hole_mapper = "hungarian"
```

**Example - Use Greedy:**
```toml
[morphing]
hole_mapper = "greedy"
```

**Example - Use Discrete (selective matching):**
```toml
[morphing]
hole_mapper = "discrete"
```

**Example - Use Simple (all disappear/appear):**
```toml
[morphing]
hole_mapper = "simple"
```

**Per-Segment Alignment Overrides:**

You can override hole matchers for specific animation segments using either tuple formats or the explicit KeyState class:

**Using tuple format:**
```python
from vood.velement import VElement
from vood.transition.interpolation.hole_matching import SimpleMapper, DiscreteMapper
from vood.transition import easing

element = VElement(
    keystates=[
        (0.0, state_a),
        # Segment 1: Use SimpleMapper for this specific transition
        (0.33, state_b, None, {"hole_mapper": SimpleMapper()}),
        # Segment 2: Both easing and custom matcher
        (0.66, state_c, {"opacity": easing.bounce}, {
            "hole_mapper": DiscreteMapper()
        }),
        # Segment 3: Uses config default (no override)
        (1.0, state_d),
    ]
)
```

**Using KeyState class (recommended for clarity):**
```python
from vood.velement import VElement, KeyState
from vood.transition.interpolation.hole_matching import SimpleMapper
from vood.transition import easing

element = VElement(
    keystates=[
        KeyState(state=state_a, time=0.0),
        KeyState(
            state=state_b,
            time=0.33,
            morphing={"hole_mapper": SimpleMapper()}
        ),
        KeyState(
            state=state_c,
            time=0.66,
            easing={"opacity": easing.bounce},
            morphing={"hole_mapper": DiscreteMapper()}
        ),
        KeyState(state=state_d, time=1.0),
    ]
)
```

**Keystate formats:**

*Simple animations:*
```python
# Bare states (auto-timed evenly across 0.0 to 1.0)
keystates=[state1, state2, state3]

# Explicit timing with tuples (clean and readable)
keystates=[(0.0, state1), (0.3, state2), (1.0, state3)]
```

*Advanced animations (with easing, alignment overrides):*
```python
# Use KeyState class for clarity
keystates=[
    KeyState(state=state1, time=0.0),
    KeyState(
        state=state2,
        time=0.5,
        easing={"opacity": easing.sine}
    ),
    KeyState(
        state=state3,
        time=1.0,
        morphing={"hole_mapper": SimpleMapper()}
    )
]
```

*Mixed format (combine as needed):*
```python
keystates=[
    (0.0, state1),                    # Simple tuple
    KeyState(                          # KeyState for advanced features
        state=state2,
        time=0.5,
        easing={"x": easing.bounce}
    ),
    (1.0, state3)                     # Back to simple tuple
]
```

**KeyState class fields:**
- `state`: State object (required)
- `time`: Normalized time 0.0-1.0 (optional, None = auto-timed)
- `easing`: Per-segment easing overrides dict (optional)
- `morphing`: Morphing configuration dict (optional)

**Morphing dict keys:**
- `"hole_mapper"`: HoleMapper instance (SimpleMapper, DiscreteMapper, etc.)
- `"vertex_aligner"`: VertexAligner instance (future use)

See `examples/segment_hole_matcher.py` for complete example.

**See also:** [HOLE_MATCHING.md](HOLE_MATCHING.md) for detailed strategy comparison and examples.

### `[export]` - Export Defaults

Default settings for exporting scenes.

```toml
[export]
default_framerate = 30              # Video framerate (fps)
default_converter = "playwright"    # Converter: "playwright", "cairosvg", "inkscape"
png_width_px = 1920                # PNG width in pixels
```

**Note:** These are currently documentary. VSceneExporter uses hardcoded defaults.

### `[playwright_server]` - Playwright Render Server

Configuration for the optional Playwright HTTP render server used for high-quality SVG-to-PNG/PDF conversion.

```toml
[playwright_server]
host = "localhost"       # Server host (default: localhost)
port = 4000             # Server port (default: 4000)
auto_start = false      # Automatically start server if not running
log_level = "INFO"      # Server log level: DEBUG, INFO, WARNING, ERROR
```

**Installation:**
```bash
pip install vood[playwright-server]
playwright install chromium
```

**Usage:**
```python
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

scene = VScene()
# ... add elements ...

exporter = VSceneExporter(scene)

# Manual mode: Start server first
# $ vood playwright-server start
exporter.export("output.png", converter="playwright_http")
```

**Auto-start mode (optional):**
```toml
# vood.toml
[playwright_server]
auto_start = true  # Server starts automatically when needed
```

**Server management commands:**
```bash
vood playwright-server start    # Start server in background
vood playwright-server stop     # Stop server
vood playwright-server status   # Check if running
vood playwright-server logs     # View recent logs
vood playwright-server restart  # Restart server
```

**See also:** [PLAYWRIGHT_SERVER.md](PLAYWRIGHT_SERVER.md) for detailed setup and troubleshooting guide.

### `[logging]` - Logging Configuration

Controls the default logging level.

```toml
[logging]
level = "INFO"    # Log level: "DEBUG", "INFO", "WARNING", "ERROR"
```

**Usage:**
```python
from vood.core.logger import configure_logging

# Uses config default
configure_logging()

# Override
configure_logging(level="DEBUG")
```

## Color Formats

Colors can be specified in multiple formats:

```toml
# Hex color
background_color = "#FF0000"

# RGB array
background_color = [255, 0, 0]

# Color name (standard web colors)
background_color = "red"

# Transparent/no color
background_color = "none"
```

All color values are automatically normalized to `Color` objects.

## Programmatic Usage

### Loading Configuration

```python
from vood.config import load_config

# Load specific config file
load_config('my_project.toml')

# Load from specific path
load_config('/path/to/config.toml')
```

### Accessing Configuration

```python
from vood.config import get_config

config = get_config()

# Get values with dot notation
width = config.get('scene.width')
fill_color = config.get('state.visual.fill_color')

# Get with default fallback
custom_value = config.get('my.custom.value', default=42)
```

### Resetting Configuration

```python
from vood.config import reset_config

# Reset to system defaults
reset_config()
```

## Examples

### Example 1: Project-Specific Defaults

**vood.toml:**
```toml
[scene]
width = 1920
height = 1080
background_color = "#000000"

[state.visual]
num_vertices = 256  # Higher quality morphing
```

**Python code:**
```python
from vood.vscene import VScene
from vood.component.state.circle import CircleState

# Automatically uses 1920x1080 from config
scene = VScene()

# Automatically uses 256 vertices from config
circle = CircleState(radius=50)
```

### Example 2: Debug Configuration

**vood-debug.toml:**
```toml
[logging]
level = "DEBUG"

[state.visual]
stroke_width = 2.0    # Thicker strokes for debugging
stroke_color = "#FF0000"
```

**Python code:**
```python
from vood.config import load_config
from vood.core.logger import configure_logging

# Load debug config
load_config('vood-debug.toml')

# Apply debug logging
configure_logging()  # Uses "DEBUG" from config
```

### Example 3: Multiple Projects

```bash
project-a/
├── vood.toml          # Project A defaults
└── animation.py

project-b/
├── vood.toml          # Project B defaults
└── animation.py
```

Each project automatically uses its own `vood.toml` when you run scripts from that directory.

## Best Practices

1. **Keep it minimal** - Only override values you actually need to change
2. **One per project** - Use `./vood.toml` in each project directory
3. **Version control** - Commit `vood.toml` to share settings with team
4. **Templates** - Use `create_config_template()` as starting point
5. **Explicit overrides** - When you need different values, pass them explicitly in code

## Priority System

When the same value is defined in multiple places, vood uses this priority order:

1. **Explicit values in code** (highest priority)
   ```python
   VScene(width=1024)  # Always wins
   ```

2. **Manually loaded config**
   ```python
   load_config('custom.toml')
   ```

3. **`./vood.toml`** (project directory)

4. **`~/.config/vood/config.toml`** (user config)

5. **`~/.vood.toml`** (home directory)

6. **System defaults** (lowest priority)

## Complete Example

**vood.toml:**
```toml
# Scene defaults
[scene]
width = 1920
height = 1080
background_color = "#1a1a1a"
background_opacity = 1.0
origin_mode = "center"

# State defaults (documentary)
[state]
x = 0.0
y = 0.0
scale = 1.0
opacity = 1.0
rotation = 0.0

# Visual state defaults
[state.visual]
fill_color = "#FDBE02"
stroke_color = "#AA0000"
stroke_width = 2.0
num_vertices = 256
closed = true

# Morphing/interpolation settings
[morphing]
hole_mapper = "clustering"

[morphing.clustering]
balance_clusters = true
max_iterations = 50
random_seed = 42

# Export defaults (documentary)
[export]
default_framerate = 30
default_converter = "playwright"
png_width_px = 1920

# Logging
[logging]
level = "INFO"
```

## Troubleshooting

**Config not being loaded?**
- Check file is named exactly `vood.toml`
- Ensure it's in current directory or one of the search paths
- Verify TOML syntax is valid

**Values not applying?**
- Some values are documentary only (see individual sections above)
- Explicit values in code always override config
- Check priority order (manual loading > project file > user file > system defaults)

**Invalid color format?**
- Use hex: `"#FF0000"`
- Or RGB array: `[255, 0, 0]`
- Or color name: `"red"`
- Or transparent: `"none"`

## Future Enhancements

The configuration system is designed to be extensible. Potential future additions:

- State factory methods using config defaults
- Environment variable overrides (`VOOD_SCENE_WIDTH=1920`)
- Theme presets (`load_config(theme='dark')`)
- Per-state-type configurations
- Animation timing defaults
- Layout defaults
- Vertex alignment strategy configuration
- Easing function defaults

## See Also

- [`vood/config/defaults.toml`](vood/config/defaults.toml) - System defaults reference
- [HOLE_MATCHING.md](HOLE_MATCHING.md) - Detailed hole matching strategy guide
- [Examples](examples/) - Working code examples
- [CLAUDE.md](CLAUDE.md) - Developer documentation
