# Vood Development Server

The Vood development server provides live browser preview with automatic hot-reload for rapid animation development. Edit your Python animation code, save the file, and see updates instantly in your browser—no manual refresh needed.

## Installation

```bash
pip install vood[devserver]
```

This installs the optional dependencies: FastAPI, Uvicorn, Watchdog, WebSockets, and Jinja2.

## Quick Start

### 1. Create an Animation File

The dev server automatically finds your VScene using flexible detection. You can structure your animation file however you like:

**Simple approach (any variable name)**
```python
# my_animation.py
from vood.vscene import VScene
from vood.component import CircleState
from vood.velement import VElement
from vood.core.color import Color

# Any variable name works!
my_animation = VScene(width=400, height=400, background=Color("#1a1a1a"))

# Define animation
start = CircleState(x=0, y=0, radius=50, fill_color=Color("#3b82f6"))
end = CircleState(x=100, y=0, radius=50, fill_color=Color("#ef4444"))

my_animation.add_element(VElement(keystates=[start, end]))
```

**Optional conventions (if you prefer)**
```python
# Using 'scene' convention
scene = VScene(...)

# Or using 'create_scene()' function
def create_scene():
    return VScene(...)
```

**Multiple scenes? Use @animation decorator**
```python
from vood.server.dev import animation

test_scene = VScene()  # Ignored

@animation  # <-- Marks which one to use
def main_animation():
    return VScene(...)
```

### 2. Start the Server

```bash
vood serve my_animation.py
```

This will:
- Start the development server on `http://localhost:8000`
- Automatically open your browser to the preview page
- Watch `my_animation.py` for changes

### 3. Edit and Watch

Edit `my_animation.py` in your editor, save the file, and watch the browser update automatically. Syntax errors and runtime errors are displayed in the browser—the server keeps running.

## CLI Options

```bash
vood serve <file.py> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--port` | `-p` | 8000 | Server port |
| `--frames` | `-n` | 20 | Number of preview frames |
| `--fps` | `-f` | 10 | Playback framerate (FPS) |
| `--no-browser` | | | Don't auto-open browser |

**Examples:**
```bash
# Basic usage
vood serve my_animation.py

# Custom port and more frames
vood serve my_animation.py --port 8080 --frames 30

# Faster playback (30 FPS)
vood serve my_animation.py --fps 30

# Smooth animation with many frames
vood serve my_animation.py --frames 60 --fps 30

# Don't open browser automatically
vood serve my_animation.py --no-browser
```

## Configuration

Configure defaults in `vood.toml`:

```toml
[devserver]
port = 8000
default_frames = 20
default_fps = 10  # Frames per second
auto_open_browser = true
```

CLI options override config file settings.

## VScene Detection (Priority Order)

The dev server finds your VScene using this priority order:

1. **@animation decorator** (highest priority) - Always wins if present
2. **`scene` variable** - Optional convention for clarity
3. **`create_scene()` function** - Optional convention for functions
4. **Any VScene instance** - Auto-detect (must be only one)
5. **Any function returning VScene** - Auto-detect (not yet implemented)

### Examples

**Auto-detection (simple case)**
```python
# Just works - any variable name
my_cool_animation = VScene(...)
```

**Multiple VScenes (use decorator)**
```python
from vood.server.dev import animation

# This one is ignored
test = VScene()

@animation  # This one is used
def main():
    return VScene(...)

# This one is also ignored
another = VScene()
```

**Multiple VScenes (ambiguous - error)**
```python
scene1 = VScene()
scene2 = VScene()

# Error: Found multiple VScene instances:
#   - scene1
#   - scene2
#
# Solutions:
#   1. Remove unused scenes
#   2. Use @animation decorator
#   3. Rename main scene to 'scene'
```

## How It Works

The development server uses:

1. **File Watcher** (watchdog) - Monitors your animation file for changes with 200ms debouncing
2. **Module Reloader** (importlib) - Safely reloads your Python module on each save
3. **WebSocket** - Pushes updates to connected browsers without page refresh
4. **Jupyter Preview** - Reuses Vood's Jupyter notebook preview system for consistency

**Architecture:**
```
Python File (my_animation.py)
    ↓ (watchdog monitors)
File change detected
    ↓ (debounced)
Module reload (importlib)
    ↓
Extract VScene
    ↓
Generate preview HTML
    ↓
WebSocket broadcast
    ↓
Browser updates (no page refresh)
```

## Error Handling

The dev server is designed for resilience:

- **Syntax errors**: Displayed in browser with line numbers and error message
- **Runtime errors**: Full traceback shown in browser
- **Import errors**: Helpful message about missing dependencies
- **Server keeps running**: Fix the error and save—the server automatically retries

## Browser UI

The preview page features:
- **Status indicator**: Green (connected) / Red (disconnected)
- **Live preview**: Interactive animation with play/pause controls
- **Error display**: Syntax and runtime errors shown with details
- **Auto-reconnect**: WebSocket reconnects if connection drops
- **Export panel**: One-click export to MP4, GIF, or HTML

## Export Features

The dev server includes built-in export functionality accessible directly from the browser:

### Export Formats

**MP4 Video**
- Professional quality video output
- Configurable frames, FPS, and resolution
- Uses ffmpeg for encoding
- Perfect for presentations and social media

**Animated GIF**
- Lightweight animated format
- Universally supported
- Configurable framerate and optimization
- Great for quick sharing and web embeds

**Interactive HTML**
- Self-contained single HTML file
- Embedded SVG frames with JavaScript controls
- No external dependencies
- Perfect for embedding in websites or documentation
- Includes play/pause, slider, and loop controls

### Export Settings

Configure your export in the browser:
- **Frames**: Number of frames to render (10-300)
- **FPS**: Animation framerate (1-60)
- **Width**: Output width in pixels for MP4/GIF (256-3840)

### Export Process

1. **Configure**: Set frames, FPS, and width in the export panel
2. **Click**: Choose MP4, GIF, or HTML export button
3. **Wait**: Progress indicator shows export status
4. **Download**: Download link appears when complete

Exports run in the background - the server keeps running and you can continue editing your animation while exporting.

### Export Output

Exported files are saved to `exports/` directory next to your animation file:
```
my_animation.py
exports/
  ├── animation_abc123.mp4
  ├── animation_def456.gif
  └── animation_ghi789.html
```

## Tips

1. **Use logging**: Set `logging.level = "DEBUG"` in `vood.toml` to see detailed server logs
2. **Multiple browsers**: Open the preview URL in multiple browser windows—all update simultaneously
3. **Share preview**: Use `--port` to run on a specific port, access from other devices on your network
4. **Fast iteration**: The dev server is optimized for rapid development—changes appear within 200ms
5. **Jupyter alternative**: While Jupyter notebooks are great for exploration, the dev server is ideal for focused animation development

## Comparison: Dev Server vs Jupyter

| Feature | Dev Server | Jupyter Notebook |
|---------|------------|------------------|
| **Hot-reload** | ✓ Automatic | ✗ Manual re-run |
| **External editor** | ✓ Use any editor | ✗ Notebook cells only |
| **Version control** | ✓ Clean .py files | △ .ipynb files |
| **Error recovery** | ✓ Auto-retry | ✗ Manual re-run |
| **Best for** | Focused development | Exploration & documentation |

Both tools complement each other—use the dev server for rapid iteration and Jupyter for interactive exploration.

## Troubleshooting

### Server won't start: "Address already in use"

Another process is using port 8000. Use a different port:
```bash
vood serve my_animation.py --port 8001
```

### "No VScene found in module"

Your animation file needs to contain a VScene instance. The dev server will find it automatically:

```python
# Any of these work:
my_animation = VScene(...)  # Simple
scene = VScene(...)         # Convention (optional)

def create_scene():         # Function (optional)
    return VScene(...)
```

### "Found multiple VScene instances"

If you have multiple VScenes in your file, use the `@animation` decorator to mark which one to use:

```python
from vood.server.dev import animation

test = VScene()  # Test scene, ignored

@animation       # Main scene, used by dev server
def main():
    return VScene(...)
```

### Dependencies not installed

If you get import errors, install the dev server dependencies:
```bash
pip install vood[devserver]
```

### Browser doesn't auto-open

Use `--no-browser` and manually navigate to `http://localhost:8000`, or check your system's default browser settings.

## Architecture Details

### File Watching
- Uses **watchdog** library for cross-platform file monitoring
- Watches the parent directory (watchdog can't watch individual files)
- **Debouncing**: 200ms delay prevents rapid successive reloads during save operations
- Only triggers on `.py` file modifications

### Module Reloading
- Removes module from `sys.modules` to force clean reload
- Uses `importlib.util.spec_from_file_location()` for isolated loading
- Generates unique module names to avoid conflicts
- Gracefully captures syntax errors, import errors, and runtime exceptions

### WebSocket Protocol
Messages sent to browser:

**Update message:**
```json
{
  "type": "update",
  "html": "<div>...</div>",
  "frame_count": 20,
  "error": null
}
```

**Error message:**
```json
{
  "type": "error",
  "error": "SyntaxError: ...",
  "traceback": "..."
}
```

### Preview Generation
- Reuses `PreviewRenderer._render_navigator()` from preview system
- Self-contained HTML with embedded CSS, JavaScript, and SVG frames
- Same UI/UX as Jupyter notebook preview for consistency
- Configurable color schemes via `[preview]` section in `vood.toml`

## Future Enhancements (Phase 2+)

Planned features for future releases:
- Export buttons in UI (MP4, GIF) without stopping the server
- Frame caching for better performance with large animations
- Directory watching mode (watch multiple files)
- Parameter playground (auto-generate sliders for animation parameters)
- Timeline scrubbing for precise frame inspection
- Share preview URLs for collaborative development

## Related Documentation

- **[docs/JUPYTER_SUPPORT.md](docs/JUPYTER_SUPPORT.md)** - Jupyter notebook integration
- **[CONFIG.md](CONFIG.md)** - Configuration system documentation
- **[README.md](README.md)** - Main Vood documentation
