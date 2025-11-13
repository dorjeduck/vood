"""KeyState class for explicit keystate specification

Provides a clear, typed alternative to tuple-based keystate specification.
All tuple formats are converted to KeyState objects internally.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Callable, Any, Union

from vood.component import State


@dataclass
class Morphing:
    """Morphing strategy configuration for vertex-based shape transitions

    Specifies strategies for mapping and aligning vertices during shape morphing.
    Used in KeyState to override default morphing behavior for specific transitions.

    Args:
        hole_mapper: Strategy for mapping holes between states (SimpleMapper,
                    GreedyNearestMapper, DiscreteMapper, ClusteringMapper, etc.)
        vertex_aligner: Strategy for aligning vertices within matched shapes
                       (AngularAligner, EuclideanAligner, NullAligner, etc.)

    Examples:
        Hole mapping only:
        >>> Morphing(hole_mapper=SimpleMapper())

        Both hole mapping and vertex alignment:
        >>> Morphing(
        ...     hole_mapper=DiscreteMapper(),
        ...     vertex_aligner=EuclideanAligner()
        ... )

        Usage in KeyState:
        >>> KeyState(
        ...     state=perforated_state,
        ...     time=0.5,
        ...     morphing=Morphing(hole_mapper=ClusteringMapper())
        ... )
    """

    hole_mapper: Optional[Any] = None  # HoleMapper type (avoid circular import)
    vertex_aligner: Optional[Any] = None  # VertexAligner type (avoid circular import)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict format for internal processing

        Returns dict with 'hole_mapper' and 'vertex_aligner' keys for backward compatibility.
        """
        result = {}
        if self.hole_mapper is not None:
            result["hole_mapper"] = self.hole_mapper
        if self.vertex_aligner is not None:
            result["vertex_aligner"] = self.vertex_aligner
        return result


@dataclass
class KeyState:
    """Explicit keystate specification with time, state, and override configs

    Provides a clear, IDE-friendly way to specify keystates as an alternative
    to the flexible tuple format. After parsing, all keystates (both tuples
    and KeyState instances) are converted to KeyState objects internally.

    Args:
        state: The State object for this keystate
        time: Normalized time (0.0-1.0), or None for auto-timing
        easing: Per-segment easing overrides {property_name: easing_function}
        morphing: Morphing strategy configuration (Morphing instance or dict)

    Examples:
        Basic usage:
        >>> KeyState(state=circle_state, time=0.5)

        With easing:
        >>> KeyState(
        ...     state=circle_state,
        ...     time=0.5,
        ...     easing={"x": easing.in_out_sine}
        ... )

        With morphing override (using Morphing class):
        >>> KeyState(
        ...     state=perforated_state,
        ...     time=0.75,
        ...     morphing=Morphing(hole_mapper=SimpleMapper())
        ... )

        With morphing override (using dict - deprecated):
        >>> KeyState(
        ...     state=perforated_state,
        ...     time=0.75,
        ...     morphing={"hole_mapper": SimpleMapper()}
        ... )

        Full specification:
        >>> KeyState(
        ...     state=perforated_state,
        ...     time=0.5,
        ...     easing={"opacity": easing.bounce},
        ...     morphing=Morphing(hole_mapper=DiscreteMapper())
        ... )

        Auto-timing (time=None):
        >>> KeyState(state=circle_state)  # Will be auto-timed during parsing
    """

    state: State
    time: Optional[float] = None
    easing: Optional[Dict[str, Callable[[float], float]]] = None
    morphing: Optional[Union[Morphing, Dict[str, Any]]] = None

    def __post_init__(self):
        """Validate time range and morphing configuration"""
        # Validate time if provided
        if self.time is not None:
            if not isinstance(self.time, (int, float)):
                raise TypeError(f"time must be a number, got {type(self.time).__name__}")
            if not (0.0 <= self.time <= 1.0):
                raise ValueError(f"time must be between 0.0 and 1.0, got {self.time}")

        # Validate state
        if not isinstance(self.state, State):
            raise TypeError(f"state must be a State instance, got {type(self.state).__name__}")

        # Validate easing dict if provided
        if self.easing is not None and not isinstance(self.easing, dict):
            raise TypeError(f"easing must be a dict, got {type(self.easing).__name__}")

        # Validate morphing configuration if provided
        if self.morphing is not None:
            if isinstance(self.morphing, Morphing):
                # Morphing class - all good
                pass
            elif isinstance(self.morphing, dict):
                # Dict format (deprecated but supported) - validate keys
                valid_keys = {"hole_mapper", "vertex_aligner"}
                invalid_keys = set(self.morphing.keys()) - valid_keys
                if invalid_keys:
                    raise ValueError(
                        f"Invalid morphing keys: {invalid_keys}. "
                        f"Valid keys are: {valid_keys}"
                    )
            else:
                raise TypeError(
                    f"morphing must be a Morphing instance or dict, "
                    f"got {type(self.morphing).__name__}"
                )

    def with_time(self, time: float) -> KeyState:
        """Create a new KeyState with updated time (immutable update)

        Used internally during time distribution to assign calculated times
        to auto-timed keystates.

        Args:
            time: New time value (0.0-1.0)

        Returns:
            New KeyState instance with updated time
        """
        return KeyState(
            state=self.state,
            time=time,
            easing=self.easing,
            morphing=self.morphing
        )

    def __repr__(self) -> str:
        """Readable representation showing only non-None fields"""
        parts = [f"state={self.state.__class__.__name__}(...)"]
        if self.time is not None:
            parts.append(f"time={self.time}")
        if self.easing is not None:
            parts.append(f"easing={{{', '.join(self.easing.keys())}}}")
        if self.morphing is not None:
            if isinstance(self.morphing, Morphing):
                morph_parts = []
                if self.morphing.hole_mapper is not None:
                    morph_parts.append(f"hole_mapper={type(self.morphing.hole_mapper).__name__}")
                if self.morphing.vertex_aligner is not None:
                    morph_parts.append(f"vertex_aligner={type(self.morphing.vertex_aligner).__name__}")
                parts.append(f"morphing=Morphing({', '.join(morph_parts)})")
            else:
                parts.append(f"morphing={{{', '.join(self.morphing.keys())}}}")
        return f"KeyState({', '.join(parts)})"
