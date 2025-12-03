"""Shared pytest fixtures for vood tests"""

import pytest
from pathlib import Path
from dataclasses import dataclass

from vood.core.color import Color
from vood.core.point2d import Point2D
from vood.component.state.circle import CircleState
from vood.component.state.rectangle import RectangleState
from vood.component.vertex.vertex_loop import VertexLoop
from vood.component.vertex.vertex_contours import VertexContours
from vood.transition.easing import linear


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary directory for config files"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def sample_circle_state():
    """Create a sample circle state for testing"""
    return CircleState(
        x=100,
        y=100,
        radius=50,
        fill_color=Color("#FF0000"),
        stroke_color=Color("#000000"),
        stroke_width=2.0,
    )


@pytest.fixture
def sample_rectangle_state():
    """Create a sample rectangle state for testing"""
    return RectangleState(
        x=100,
        y=100,
        width=100,
        height=60,
        fill_color=Color("#00FF00"),
        stroke_color=Color("#000000"),
        stroke_width=2.0,
    )


@pytest.fixture
def simple_vertex_loop():
    """Create a simple closed vertex loop (square)"""
    vertices = [
        Point2D(0, 0),
        Point2D(100, 0),
        Point2D(100, 100),
        Point2D(0, 100),
        Point2D(0, 0),  # Closed
    ]
    return VertexLoop(vertices, closed=True)


@pytest.fixture
def simple_vertex_contours():
    """Create simple vertex contours with outer loop and no  vertex_loops"""
    vertices = [
        Point2D(0, 0),
        Point2D(100, 0),
        Point2D(100, 100),
        Point2D(0, 100),
        Point2D(0, 0),
    ]
    outer = VertexLoop(vertices, closed=True)
    return VertexContours(outer=outer, holes=[])


@pytest.fixture
def vertex_contours_with_hole():
    """Create vertex contours with outer loop and one hole"""
    # Outer square
    outer_vertices = [
        Point2D(0, 0),
        Point2D(100, 0),
        Point2D(100, 100),
        Point2D(0, 100),
        Point2D(0, 0),
    ]
    outer = VertexLoop(outer_vertices, closed=True)

    # Inner hole (reversed for clockwise winding)
    hole_vertices = [
        Point2D(25, 25),
        Point2D(25, 75),
        Point2D(75, 75),
        Point2D(75, 25),
        Point2D(25, 25),
    ]
    hole = VertexLoop(hole_vertices, closed=True)

    return VertexContours(outer=outer, holes=[hole])


@pytest.fixture
def vertex_contours_with_multiple_holes():
    """Create vertex contours with outer loop and multiple  holes="""
    # Outer square
    outer_vertices = [
        Point2D(0, 0),
        Point2D(200, 0),
        Point2D(200, 200),
        Point2D(0, 200),
        Point2D(0, 0),
    ]
    outer = VertexLoop(outer_vertices, closed=True)

    # First hole
    hole1_vertices = [
        Point2D(25, 25),
        Point2D(25, 75),
        Point2D(75, 75),
        Point2D(75, 25),
        Point2D(25, 25),
    ]
    hole1 = VertexLoop(hole1_vertices, closed=True)

    # Second hole
    hole2_vertices = [
        Point2D(125, 125),
        Point2D(125, 175),
        Point2D(175, 175),
        Point2D(175, 125),
        Point2D(125, 125),
    ]
    hole2 = VertexLoop(hole2_vertices, closed=True)

    return VertexContours(outer=outer, holes=[hole1, hole2])


@pytest.fixture
def linear_easing():
    """Return linear easing function"""
    return linear


@pytest.fixture
def sample_colors():
    """Sample colors for testing color interpolation"""
    return {
        "red": Color("#FF0000"),
        "green": Color("#00FF00"),
        "blue": Color("#0000FF"),
        "yellow": Color("#FFFF00"),
        "transparent": Color.NONE,
    }
