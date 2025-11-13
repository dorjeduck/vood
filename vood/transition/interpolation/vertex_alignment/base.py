"""Base classes and interfaces for vertex alignment strategies

This module defines the abstract base class and context for all vertex
alignment strategies used during morph interpolation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple
from dataclasses import dataclass


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
        verts1: List[Tuple[float, float]],
        verts2: List[Tuple[float, float]],
        context: AlignmentContext
    ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
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


def get_aligner(closed1: bool, closed2: bool) -> VertexAligner:
    """Factory function to select appropriate aligner based on shape closure

    Args:
        closed1: Whether first shape is closed
        closed2: Whether second shape is closed

    Returns:
        Appropriate VertexAligner instance:
        - NullAligner for open ↔ open
        - AngularAligner for closed ↔ closed
        - EuclideanAligner for open ↔ closed or closed ↔ open
    """
    from .angular import AngularAligner
    from .euclidean import EuclideanAligner
    from .null import NullAligner

    if not closed1 and not closed2:
        return NullAligner()
    elif closed1 and closed2:
        return AngularAligner()
    else:
        return EuclideanAligner()
