"""Vertex module for multi-contour shape support"""

from .vertex_loop import VertexLoop
from .vertex_contours import VertexContours
from .vertex_astroid import VertexAstroid
from .vertex_ellipse import VertexEllipse
from .vertex_circle import VertexCircle
from .vertex_rectangle import VertexRectangle
from .vertex_square import VertexSquare
from .vertex_star import VertexStar
from .vertex_triangle import VertexTriangle
from .vertex_line import VertexLine
from .vertex_polygon import VertexPolygon
from .vertex_regular_polygon import VertexRegularPolygon
from .vertex_point import VertexPoint
from .vertex_utils import (
    centroid,
    angle_from_centroid,
    angle_distance,
    rotate_vertices,
    rotate_vertices_inplace,
    rotate_list_inplace,
)

__all__ = [
    "VertexLoop",
    "VertexContours",
    "VertexAstroid",
    "VertexEllipse",
    "VertexCircle",
    "VertexRectangle",
    "VertexSquare",
    "VertexStar",
    "VertexTriangle",
    "VertexLine",
    "VertexPolygon",
    "VertexRegularPolygon",
    "VertexPoint",
    "centroid",
    "angle_from_centroid",
    "angle_distance",
    "rotate_vertices",
    "rotate_vertices_inplace",
    "rotate_list_inplace",
]
