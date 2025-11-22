# PNG Converter Benchmark

Compares CairoSVG, Inkscape, Playwright (local), and Playwright HTTP Server.

## Quick Start

```bash
python benchmark/run_benchmark.py              # 50 frames (default)
python benchmark/run_benchmark.py -n 100       # 100 frames
python benchmark/run_benchmark.py --no-cleanup # Keep generated files
```

Generates console output + `BENCHMARK_RESULTS.md` with detailed metrics.

## Vood PNG Converter Benchmark Results

**Generated:** 2025-11-22 11:47:37

**Frames rendered:** 100

## Performance Comparison

| Converter | Total Time | Per Frame | CPU % | CPU Time | Memory |
|-----------|------------|-----------|-------|----------|--------|
| cairosvg | 1.34s | 0.013s | 89.0% | 1.37s | 125.5MB |
| inkscape | 31.89s | 0.319s | 1.0% | 0.36s | 126.3MB |
| playwright | 87.76s | 0.878s | 2.0% | 1.98s | 115.7MB |
| playwright_http | 88.40s | 0.884s | 0.6% | 0.57s | 119.2MB |

## Detailed Metrics

### cairosvg

- **Total Time:** 1.34s
- **Average Time per Frame:** 0.013s
- **Process CPU Usage:** 89.0%
- **User CPU Time:** 1.31s
- **System CPU Time:** 0.06s
- **Total CPU Time:** 1.37s
- **Memory Usage:** 125.5MB

### inkscape

- **Total Time:** 31.89s
- **Average Time per Frame:** 0.319s
- **Process CPU Usage:** 1.0%
- **User CPU Time:** 0.07s
- **System CPU Time:** 0.29s
- **Total CPU Time:** 0.36s
- **Memory Usage:** 126.3MB

### playwright

- **Total Time:** 87.76s
- **Average Time per Frame:** 0.878s
- **Process CPU Usage:** 2.0%
- **User CPU Time:** 1.30s
- **System CPU Time:** 0.68s
- **Total CPU Time:** 1.98s
- **Memory Usage:** 115.7MB

### playwright_http

- **Total Time:** 88.40s
- **Average Time per Frame:** 0.884s
- **Process CPU Usage:** 0.6%
- **User CPU Time:** 0.40s
- **System CPU Time:** 0.17s
- **Total CPU Time:** 0.57s
- **Memory Usage:** 119.2MB



## Converter Trade-offs

| Converter | Speed | Quality | Process CPU | Setup |
|-----------|-------|---------|-------------|-------|
| **CairoSVG** | Fastest | Good (font limits) | Moderate | `pip install cairosvg` |
| **Inkscape** | Moderate | Good | Low | Download from inkscape.org |
| **Playwright** | Slow | Best | High | `pip install playwright` |
| **Playwright HTTP** | Slow | Best | Very Low | `pip install vood[playwright-server]` |

**Key insight:** Playwright HTTP has same wall-clock time as local Playwright, but offloads CPU/memory to server process (85-95% reduction in your process).

## Options

```bash
-n FRAMES       # Number of frames (default: 50)
--no-cleanup    # Keep generated PNG files
-o OUTPUT       # Custom markdown output file (default: BENCHMARK_RESULTS.md)
```

## Notes

- Benchmark auto-skips converters that aren't installed
- Edit `create_test_scene()` in `run_benchmark.py` to test with custom graphics
- Playwright HTTP requires server running: `vood playwright-server start`
