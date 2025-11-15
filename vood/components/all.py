"""
Complete morph system implementation with proper integration.

Files to create/modify:
1. vood/components/states/morph.py - State definitions
2. vood/components/renderer/morph.py - Renderer
3. vood/interpolation/morph.py - Alignment logic
4. Modifications to InterpolationEngine and BaseVElement
"""

# ============================================================================
# FILE 1: vood/components/states/morph.py
# ============================================================================

"""Morph states for geometric primitives with vertex-based morphing"""

from __future__ import annotations
import math
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional

from vood.components.states.base import State
from vood.transitions import easing
from vood.core.color import Color



# ============================================================================
# FILE 2: vood/components/renderer/morph.py
# ============================================================================

"""Renderer for morphable geometric shapes"""

from __future__ import annotations
import drawsvg as dw
from vood.components.renderer.base import Renderer
from vood.components.states.morph import MorphState


# ============================================================================
# FILE 3: vood/interpolation/morph.py
# ============================================================================

"""Vertex alignment and preprocessing for morph interpolation"""



# ============================================================================
# FILE 4: Modifications to BaseVElement (vood/velements/base_velement.py)
# ============================================================================

"""
Add this method to BaseVElement class:
"""

def _preprocess_morph_segments(self) -> None:
    """
    Convert MorphState segments to MorphRawState with aligned vertices.
    
    This happens once when keystates are set, not on every frame.
    After this, normal field-by-field interpolation works correctly.
    """
    from vood.components.states.morph import MorphState
    
    for i in range(len(self.keystates) - 1):
        t1, state1, easing1 = self.keystates[i]
        t2, state2, easing2 = self.keystates[i + 1]
        
        # Check if this is a MorphState → MorphState segment
        if isinstance(state1, MorphState) and isinstance(state2, MorphState):
            from vood.interpolation.morph import align_and_convert_to_raw
            
            # Convert both states to MorphRawState with aligned vertices
            aligned_state1 = align_and_convert_to_raw(state1, state2, is_start=True)
            aligned_state2 = align_and_convert_to_raw(state1, state2, is_start=False)
            
            # Replace in the keystates list
            self.keystates[i] = (t1, aligned_state1, easing1)
            self.keystates[i + 1] = (t2, aligned_state2, easing2)


"""
And call it at the end of set_keystates():
"""

def set_keystates(self, keystates: List[FlexibleKeystateInput]) -> None:
    """Set keystates using the flexible combined format"""
    if not keystates:
        raise ValueError("keystates cannot be empty")

    self.keystates = parse_element_keystates(keystates)

    if not self.keystates:
        raise ValueError("Keystates list could not be parsed.")
    
    # Preprocess MorphState segments for vertex alignment
    self._preprocess_morph_segments()


# ============================================================================
# FILE 5: Modifications to InterpolationEngine
# ============================================================================

"""
Add this case to interpolate_value() method in InterpolationEngine:
"""

def interpolate_value(
    self,
    state: State,
    field_name: str,
    start_value: Any,
    end_value: Any,
    eased_t: float,
) -> Any:
    """
    Interpolate a single value based on its type and context.
    """
    # 0. Vertex list interpolation (for MorphRawState)
    if field_name == 'vertices' and isinstance(start_value, list) and isinstance(end_value, list):
        if len(start_value) != len(end_value):
            raise ValueError(f"Vertex lists must have same length: {len(start_value)} != {len(end_value)}")
        return [
            (
                interpolation.lerp(v1[0], v2[0], eased_t),
                interpolation.lerp(v1[1], v2[1], eased_t)
            )
            for v1, v2 in zip(start_value, end_value)
        ]
    
    # 1. SVG Path interpolation
    if isinstance(start_value, SVGPath):
        return self._interpolate_path(state, start_value, end_value, eased_t)

    # ... rest of existing code ...