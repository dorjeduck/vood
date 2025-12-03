"""Vertex alignment and preprocessing for morph interpolation

This module orchestrates vertex alignment logic that happens once per
morph segment during keystate preprocessing. The alignment is stored
directly in the state via the _aligned_contours field.

This is the main entry point - uses pluggable strategies from:
- vertex_alignment/: Strategies for aligning outer vertex loops
- hole_mapping/: Strategies for matching and aligning  vertex_loops
"""

from __future__ import annotations
from typing import Tuple, Optional, TYPE_CHECKING

from vood.component.vertex import VertexContours, VertexLoop
from vood.config import get_config, ConfigKey

from .vertex_alignment import (
    VertexAligner,
    get_aligner,
    AlignmentContext,
    AngularAligner,
)
from .vertex_loop_mapping import (
    VertexLoopMapper,
    GreedyNearestMapper,
    ClusteringMapper,
    HungarianMapper,
    DiscreteMapper,
    SimpleMapper,
)

from vood.component.state.base_vertex import VertexState


def _get_vertex_loop_mapper_from_config() -> VertexLoopMapper:
    """Get hole matcher instance based on config settings

    Returns:
        HoleMapper instance configured from vood.toml settings
    """
    config = get_config()
    strategy = config.get(ConfigKey.MORPHING_VERTEX_LOOP_MAPPER, "clustering")

    if strategy == "greedy":
        return GreedyNearestMapper()
    elif strategy == "clustering":
        balance = config.get(ConfigKey.MORPHING_CLUSTERING_BALANCE_CLUSTERS, True)
        max_iter = config.get(ConfigKey.MORPHING_CLUSTERING_MAX_ITERATIONS, 50)
        seed = config.get(ConfigKey.MORPHING_CLUSTERING_RANDOM_SEED, 42)
        return ClusteringMapper(
            max_iterations=max_iter, random_seed=seed, balance_clusters=balance
        )
    elif strategy == "hungarian":
        return HungarianMapper()  # Requires scipy
    elif strategy == "discrete":
        return DiscreteMapper()
    elif strategy == "simple":
        return SimpleMapper()
    else:
        raise ValueError(
            f"Unknown hole matching strategy: '{strategy}'. "
            f"Valid options: 'clustering', 'greedy', 'hungarian', 'discrete', 'simple'"
        )


def get_aligned_vertices(
    state1: VertexState,
    state2: VertexState,
    vertex_aligner: Optional[VertexAligner] = None,
    vertex_loop_mapper: Optional[VertexLoopMapper] = None,
    rotation_target: Optional[float] = None,
) -> Tuple[VertexContours, VertexContours]:
    """Align vertex contours and return aligned contours

    This is called once per segment during keystate preprocessing.
    Returns new VertexContours instances with aligned outer vertices
    and matched  vertex_loops .

    Uses pluggable strategies:
    - VertexAligner: How to align outer vertex loops (auto-selected by default)
    - HoleMapper: How to match vertex loops between states (from config by default)

    Args:
        state1: First state in the transition
        state2: Second state in the transition
        vertex_aligner: Custom vertex alignment strategy (default: auto-select based on closure)
        vertex_loop_mapper: Custom hole matching strategy (default: from config [morphing.vertex_loop_mapper])
        rotation_target: Target rotation for dynamic alignment (default: None, uses state2.rotation)

    Returns:
        Tuple of (contours1_aligned, contours2_aligned)

    Raises:
        ValueError: If states have different num_vertices
    """
    if state1._num_vertices != state2._num_vertices:
        raise ValueError(
            f"Cannot morph shapes with different num_points: "
            f"{state1._num_vertices} != {state2._num_vertices}. "
            f"Both shapes must have the same vertex resolution."
        )

    # Get raw contours (using _generate_contours to avoid recursion)
    contours1 = state1._generate_contours()
    contours2 = state2._generate_contours()

    # Select strategies (use defaults if not provided)
    if vertex_aligner is None:
        vertex_aligner = get_aligner(state1.closed, state2.closed)

    if vertex_loop_mapper is None:
        vertex_loop_mapper = (
            _get_vertex_loop_mapper_from_config()
        )  # Use strategy from config

    # Align outer vertices
    context = AlignmentContext(
        rotation1=state1.rotation,
        rotation2=state2.rotation,
        closed1=state1.closed,
        closed2=state2.closed,
    )
    verts1_aligned, verts2_aligned = vertex_aligner.align(
        contours1.outer.vertices,
        contours2.outer.vertices,
        context,
        rotation_target=rotation_target,
    )

    # Match and align  vertex_loops
    matched_vertex_loops1, matched_vertex_loops2 = vertex_loop_mapper.map(
        contours1.holes, contours2.holes
    )

    # Align vertices within each matched hole pair
    aligned_vertex_loops1 = []
    aligned_vertex_loops2 = []

    # Create a hole-specific aligner (always use angular for closed  vertex_loops )
    hole_aligner = AngularAligner()
    hole_context = AlignmentContext(
        rotation1=0, rotation2=0, closed1=True, closed2=True
    )

    for hole1, hole2 in zip(matched_vertex_loops1, matched_vertex_loops2):
        h1_verts = hole1.vertices
        h2_verts = hole2.vertices

        # Both vertex loops should be closed and have matching lengths
        if len(h1_verts) == len(h2_verts) and len(h1_verts) > 0:
            h1_aligned, h2_aligned = hole_aligner.align(
                h1_verts, h2_verts, hole_context
            )
            aligned_vertex_loops1.append(VertexLoop(h1_aligned, closed=True))
            aligned_vertex_loops2.append(VertexLoop(h2_aligned, closed=True))
        else:
            # Keep as-is if lengths don't match (shouldn't happen with our matching)
            aligned_vertex_loops1.append(hole1)
            aligned_vertex_loops2.append(hole2)

    # Create new VertexContours with aligned outer loops and aligned  vertex_loops
    contours1_aligned = VertexContours(
        outer=VertexLoop(verts1_aligned, closed=contours1.outer.closed),
        holes=aligned_vertex_loops1,
    )
    contours2_aligned = VertexContours(
        outer=VertexLoop(verts2_aligned, closed=contours2.outer.closed),
        holes=aligned_vertex_loops2,
    )

    return contours1_aligned, contours2_aligned
