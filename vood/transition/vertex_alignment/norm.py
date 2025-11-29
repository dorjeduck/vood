"""Alignment norm types and distance function signatures

This module defines the alignment norm enumeration and type aliases
for custom distance functions used in vertex alignment strategies.
"""

from enum import Enum
from typing import Callable, Union, List

# Avoid circular import by using TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vood.core.point2d import Points2D


class AlignmentNorm(Enum):
    """Built-in alignment norms for vertex matching

    Different norms produce different alignment behaviors:
    - L1: Minimizes sum of distances (economical, may have outliers)
    - L2: Minimizes root-mean-square distance (balanced, statistically optimal)
    - LINF: Minimizes maximum distance (minimax, ensures fairness)
    """
    L1 = "l1"       # Sum of absolute differences
    L2 = "l2"       # Root mean square
    LINF = "linf"   # Maximum (minimax)


# Type alias for angular distance functions
# Signature: (angles1, angles2, offset) -> total_distance
AngularDistanceFn = Callable[[List[float], List[float], int], float]

# Type alias for Euclidean distance functions
# Signature: (verts1, verts2, offset) -> total_distance
EuclideanDistanceFn = Callable[["Points2D", "Points2D", int], float]

# Union type for norm specification (flexible input)
NormSpec = Union[str, AlignmentNorm, Callable]
