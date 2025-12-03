# Vood Test Suite

This directory contains the test suite for the Vood library.

## Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests for individual components
│   ├── transition/         # Tests for transition/interpolation system
│   ├── velement/           # Tests for VElement and keystate parsing
│   └── config/             # Tests for configuration loading
├── integration/            # Integration tests for complete workflows
└── benchmark/              # Performance benchmarks
```

## Running Tests

### Install test dependencies

```bash
pip install -e ".[dev]"
```

### Run all tests

```bash
pytest
```

### Run specific test categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Benchmarks only
pytest -m benchmark

# Exclude slow tests
pytest -m "not slow"
```

### Run with coverage

```bash
pytest --cov=vood --cov-report=html
# View HTML report: open htmlcov/index.html
```

### Run in parallel (faster)

```bash
pytest -n auto
```

## Test Markers

- `unit`: Unit tests for individual components
- `integration`: Integration tests for complete workflows
- `benchmark`: Performance benchmarks
- `slow`: Tests that take longer to run

## Writing Tests

### Unit Tests

Unit tests should focus on testing individual functions and classes in isolation:

```python
import pytest
from vood.transition.interpolation import lerp

@pytest.mark.unit
def test_lerp_midpoint():
    assert lerp(0, 100, 0.5) == 50
```

### Integration Tests

Integration tests should verify complete workflows:

```python
import pytest
from vood.velement import VElement
from vood.vscene import VScene

@pytest.mark.integration
def test_animation_export():
    # Test complete animation workflow
    pass
```

### Benchmarks

Benchmarks measure performance:

```python
import pytest

@pytest.mark.benchmark
def test_vertex_interpolation_performance(benchmark):
    result = benchmark(vertex_interpolation_func, args)
    assert result is not None
```

## Fixtures

Common fixtures are defined in `conftest.py`:

- `temp_config_dir`: Temporary directory for config files
- `sample_circle_state`: Pre-configured CircleState
- `sample_rectangle_state`: Pre-configured RectangleState
- `simple_vertex_loop`: Basic vertex loop
- `simple_vertex_contours`: Vertex contours without  vertex_loops 
- `vertex_contours_with_hole`: Vertex contours with one hole
- `vertex_contours_with_multiple_vertex_loops `: Vertex contours with multiple  vertex_loops 
- `sample_colors`: Collection of Color objects
