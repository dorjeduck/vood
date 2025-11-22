# Playwright Render Server

The Playwright Render Server is an optional HTTP service that provides high-quality SVG-to-PNG/PDF conversion using Playwright's headless Chromium browser.

## Overview

While Vood includes several built-in converters (CairoSVG, Inkscape, local Playwright), the HTTP-based Playwright server offers:

- **Best rendering quality**: Uses real Chromium browser for pixel-perfect output
- **Lightweight Python process**: Offloads heavy rendering work to separate server process
- **Background operation**: Runs as a daemon, doesn't block your Python process
- **Cross-platform**: Works on Linux, macOS, and Windows
- **Optional auto-start**: Can automatically start when needed
- **Easy management**: Simple CLI commands for control

**Performance Note:** The HTTP server provides similar wall-clock rendering times to local Playwright, but significantly reduces CPU usage in your main Python process (typically 85-95% reduction). This makes it ideal for service architectures, multi-app environments, or when you need your main process to remain responsive. For detailed performance analysis, see **[BENCHMARK.md](BENCHMARK.md)**.

## Installation

### 1. Install Server Dependencies

```bash
pip install vood[playwright-server]
```

This installs:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `playwright` - Browser automation
- `psutil` - Process management
- `click` - CLI framework

### 2. Install Chromium Browser

```bash
playwright install chromium
```

This downloads the Chromium browser used for rendering.

## Quick Start

### Manual Server Management (Default)

```bash
# Start the server
vood playwright-server start

# Check status
vood playwright-server status

# Stop the server
vood playwright-server stop
```

Then use it in your code:

```python
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter

scene = VScene(width=800, height=800)
# ... add elements ...

exporter = VSceneExporter(scene)
exporter.export("output.png", converter="playwright_http")
```

### Auto-Start Mode (Optional)

Enable auto-start in your `vood.toml`:

```toml
[playwright_server]
auto_start = true
```

Now the server starts automatically when needed:

```python
# No need to manually start the server!
exporter.export("output.png", converter="playwright_http")
```

## CLI Commands

### Start Server

```bash
vood playwright-server start
```

Starts the server in the background. Output:
```
✓ Playwright server started successfully
  Host: localhost
  Port: 4000
  PID file: ~/.vood/playwright-server.pid
  Log file: ~/.vood/playwright-server.log
```

### Stop Server

```bash
vood playwright-server stop
```

Gracefully stops the running server.

### Check Status

```bash
vood playwright-server status
```

Shows detailed status:
```
✓ Playwright server is running
  PID: 12345
  Uptime: 3600.5s
  Memory: 45.2 MB
  Host: localhost
  Port: 4000
```

### Restart Server

```bash
vood playwright-server restart
```

Stops then starts the server (useful after config changes).

### View Logs

```bash
vood playwright-server logs           # Last 50 lines
vood playwright-server logs -n 100    # Last 100 lines
```

## Configuration

Configure the server in `vood.toml`:

```toml
[playwright_server]
host = "localhost"       # Server host (default: localhost)
port = 4000             # Server port (default: 4000)
auto_start = false      # Auto-start if not running (default: false)
log_level = "INFO"      # Log level: DEBUG, INFO, WARNING, ERROR
```

## Advanced Usage

### Programmatic Control

```python
from vood.playwright_server.process_manager import ProcessManager

# Create manager
manager = ProcessManager(host="localhost", port=4000)

# Start server
if not manager.is_running():
    manager.start()

# Get detailed status
status = manager.status()
print(f"Server running: {status['running']}")
print(f"Uptime: {status['uptime_seconds']}s")
print(f"Memory: {status['memory_mb']} MB")

# Stop server
manager.stop()
```

### Custom Host/Port

```python
from vood.converter.playwright_http_svg_converter import PlaywrightHttpSvgConverter

# Connect to custom server
converter = PlaywrightHttpSvgConverter(host="localhost", port=5000)
```

Or via config:

```toml
[playwright_server]
host = "0.0.0.0"  # Listen on all interfaces
port = 5000       # Custom port
```

### Explicit Auto-Start Control

```python
# Force auto-start regardless of config
converter = PlaywrightHttpSvgConverter(auto_start=True)

# Disable auto-start regardless of config
converter = PlaywrightHttpSvgConverter(auto_start=False)
```

## Running as System Service

### Linux (systemd)

Create `/etc/systemd/system/vood-playwright-server.service`:

```ini
[Unit]
Description=Vood Playwright Render Server
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser
ExecStart=/usr/bin/python -m uvicorn vood.playwright_server.render_server:app --host localhost --port 4000
Restart=always
RestartSec=5
Environment=PATH=/home/youruser/.local/bin:/usr/bin

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable vood-playwright-server
sudo systemctl start vood-playwright-server
sudo systemctl status vood-playwright-server
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.vood.playwright-server.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vood.playwright-server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>-m</string>
        <string>uvicorn</string>
        <string>vood.playwright_server.render_server:app</string>
        <string>--host</string>
        <string>localhost</string>
        <string>--port</string>
        <string>4000</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/vood-playwright-server.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/vood-playwright-server.err</string>
</dict>
</plist>
```

Load service:

```bash
launchctl load ~/Library/LaunchAgents/com.vood.playwright-server.plist
launchctl start com.vood.playwright-server
```

### Windows (NSSM - Non-Sucking Service Manager)

1. Download NSSM from https://nssm.cc/
2. Install as service:

```cmd
nssm install VoodPlaywrightServer "C:\Python311\python.exe" "-m uvicorn vood.playwright_server.render_server:app --host localhost --port 4000"
nssm set VoodPlaywrightServer AppDirectory "C:\Users\YourUser"
nssm start VoodPlaywrightServer
```

## Troubleshooting

### Server Won't Start

**Check if port is in use:**
```bash
# Linux/macOS
lsof -i :4000

# Windows
netstat -ano | findstr :4000
```

**Check logs:**
```bash
vood playwright-server logs
```

**Try running directly:**
```bash
python -m uvicorn vood.playwright_server.render_server:app --host localhost --port 4000
```

### Connection Refused

**Verify server is running:**
```bash
vood playwright-server status
```

**Test health endpoint:**
```bash
curl http://localhost:4000/health
```

Should return: `{"status":"ok","service":"playwright-render-server"}`

### Rendering Fails

**Check Chromium is installed:**
```bash
playwright install chromium
```

**Verify permissions:**
- Linux: May need `--no-sandbox` flag (already included)
- Docker: Requires additional dependencies

**Check server logs:**
```bash
vood playwright-server logs -n 200
```

### Auto-Start Not Working

**Verify config:**
```python
from vood.config import get_config
config = get_config()
print(config.get("playwright_server.auto_start"))  # Should be True
```

**Check for errors:**
Enable debug logging in `vood.toml`:

```toml
[logging]
level = "DEBUG"
```

### High Memory Usage

Chromium instances can use significant memory. The server closes browsers after each render, but if you're doing high-volume rendering, consider:

1. **Restart periodically:**
   ```bash
   vood playwright-server restart
   ```

2. **Monitor memory:**
   ```bash
   vood playwright-server status
   ```

3. **Run in Docker** with memory limits

## Docker Deployment

Example `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Vood with playwright-server
RUN pip install vood[playwright-server]

# Install Chromium
RUN playwright install chromium --with-deps

# Expose port
EXPOSE 4000

# Run server
CMD ["uvicorn", "vood.playwright_server.render_server:app", "--host", "0.0.0.0", "--port", "4000"]
```

Build and run:

```bash
docker build -t vood-playwright-server .
docker run -p 4000:4000 vood-playwright-server
```

## API Reference

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "service": "playwright-render-server"
}
```

### Render SVG

**Endpoint:** `POST /render`

**Request:**
```json
{
  "svg": "<svg>...</svg>",
  "type": "png",
  "width": 1920,
  "height": 1080
}
```

**Parameters:**
- `svg` (string, required): SVG content to render
- `type` (string, required): Output format - `"png"` or `"pdf"`
- `width` (integer, required): Output width in pixels
- `height` (integer, required): Output height in pixels

**Response:** Binary PNG or PDF data

**Example with curl:**
```bash
curl -X POST http://localhost:4000/render \
  -H "Content-Type: application/json" \
  -d '{
    "svg": "<svg width=\"100\" height=\"100\"><circle cx=\"50\" cy=\"50\" r=\"40\" fill=\"red\"/></svg>",
    "type": "png",
    "width": 100,
    "height": 100
  }' \
  --output output.png
```

## Performance Tips

1. **Keep server running**: Starting/stopping frequently adds overhead
2. **Use auto-start for dev**: Convenient for development workflows
3. **Manual start for production**: More control and predictability
4. **Monitor logs**: Watch for errors or warnings
5. **Batch renders**: If doing many renders, keep server alive between them

## Comparison with Other Converters

| Feature | Playwright HTTP | Playwright Local | CairoSVG | Inkscape |
|---------|----------------|------------------|----------|----------|
| Quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Wall-Clock Speed | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Process CPU Load | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Setup | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Fonts | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Background | ✅ | ❌ | ❌ | ❌ |
| Multi-App | ✅ | ❌ | ❌ | ❌ |

**Use Playwright HTTP when:**
- Building service/microservice architectures
- Multiple applications need rendering
- You need your main process to stay lightweight (85-95% less CPU)
- Running long-lived applications that need to stay responsive
- Distributed systems (render on different machine)

**Use Playwright Local when:**
- Simple single-script batch rendering
- One-off render jobs
- Want minimal complexity (no server management)
- Can't run background services

**Use other converters when:**
- You want simpler setup (CairoSVG)
- You need maximum speed (CairoSVG)
- Lower quality is acceptable

## See Also

- [BENCHMARK.md](BENCHMARK.md) - Performance comparison benchmark
- [CONFIG.md](CONFIG.md) - Configuration reference
- [Examples](examples/) - Code examples
- [Playwright Documentation](https://playwright.dev/python/) - Playwright Python docs
