"""Base classes and interfaces for vertex alignment strategies

This module defines the abstract base class and context for all vertex
alignment strategies used during morph interpolation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple
from dataclasses import dataclass
from vood.core.point2d import Points2D,Point2D

@dataclass
class AlignmentContext:
    """Context information for vertex alignment

    Attributes:
        rotation1: Rotation of first shape in degrees
        rotation2: Rotation of second shape in degrees
        closed1: Whether first shape is closed
        closed2: Whether second shape is closed
    """
    rotation1: float = 0
    rotation2: float = 0
    closed1: bool = True
    closed2: bool = True


class VertexAligner(ABC):
    """Abstract base for vertex alignment strategies

    Alignment strategies determine how to rotate/reorder vertices of the
    second shape to best match the first shape for smooth morphing.
    """

    @abstractmethod
    def align(
        self,
        verts1: Points2D,
        verts2: Points2D,
        context: AlignmentContext
    ) -> Tuple[Points2D, Points2D]:
        """Align two vertex lists for optimal morphing

        Args:
            verts1: First vertex list
            verts2: Second vertex list (must have same length as verts1)
            context: Alignment context with rotation and closure info

        Returns:
            Tuple of (verts1, verts2_aligned) where verts2 is rotated for best match

        Raises:
            ValueError: If vertex lists have different lengths
        """
        pass


def get_aligner(closed1: bool, closed2: bool, norm: str = None) -> VertexAligner:
    """Factory function to select appropriate aligner based on shape closure

    Args:
        closed1: Whether first shape is closed
        closed2: Whether second shape is closed
        norm: Optional norm to use (overrides config defaults)
            - "l1", "l2", "linf" for built-in norms
            - If None, reads from config

    Returns:
        Appropriate VertexAligner instance:
        - SequentialAligner for open ↔ open
        - AngularAligner for closed ↔ closed (with norm from config or parameter)
        - EuclideanAligner for open ↔ closed or closed ↔ open (with norm from config or parameter)
    """
    from .angular import AngularAligner
    from .euclidean import EuclideanAligner
    from .sequential import SequentialAligner
    from vood.config import get_config, ConfigKey

    config = get_config()

    if not closed1 and not closed2:
        # Open ↔ Open: Sequential (no norm needed)
        return SequentialAligner()
    elif closed1 and closed2:
        # Closed ↔ Closed: Angular alignment
        if norm is None:
            # Try aligner-specific config first, then fall back to global
            norm = config.get(
                ConfigKey.MORPHING_ANGULAR_ALIGNMENT_NORM,
                config.get(ConfigKey.MORPHING_VERTEX_ALIGNMENT_NORM, "l1")
            )
        return AngularAligner(norm=norm)
    else:
        # Open ↔ Closed: Euclidean alignment
        if norm is None:
            # Try aligner-specific config first, then fall back to global
            norm = config.get(
                ConfigKey.MORPHING_EUCLIDEAN_ALIGNMENT_NORM,
                config.get(ConfigKey.MORPHING_VERTEX_ALIGNMENT_NORM, "l1")
            )
        return EuclideanAligner(norm=norm)
