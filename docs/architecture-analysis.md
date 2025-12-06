# Architectural Analysis: Splitting Vood into Static and Animation Layers

## Executive Summary

**Verdict: Architecturally feasible but NOT recommended as a hard split**

The codebase has clear conceptual boundaries between static SVG generation and animation, but tight integration in the State layer creates significant refactoring challenges. A **layered architecture within a single package** is recommended over splitting into separate packages.

---

## Current Architecture Overview

### Module Classification

**Pure Static (No Animation Dependencies):**
- `vood/core/` - Color, Point2D, Logger
- `vood/component/vertex/` - Vertex geometry generators
- `vood/component/registry.py` - Renderer registration
- `vood/layout/` - Layout functions (circle, grid, wave, etc.)
- `vood/path/` - SVG path manipulation
- `vood/converter/` - SVG→PNG/PDF conversion
- `vood/config/` - Configuration system

**Pure Animation (Temporal/Interpolation):**
- `vood/transition/` - Easing, interpolation, morphing
- `vood/velement/` - Animation orchestration
- `vood/animation/` - Animation helpers
- `vood/server/` - Dev server
- `vood/cli/` - CLI tools

**Mixed/Problematic:**
- `vood/component/state/` - **States hardcode easing references**
- `vood/component/renderer/` - Static rendering but morphing detection
- `vood/vscene/` - Composition for both static + animated

---

## Critical Blocker: Easing in State Classes

### The Problem

Every state class imports animation concepts:

```python
# vood/component/state/base.py
from vood.transition import easing  # ← ANIMATION DEPENDENCY

@dataclass(frozen=True)
class State(ABC):
    DEFAULT_EASING = {
        "x": easing.in_out,
        "y": easing.in_out,
        "rotation": easing.in_out,
        ...
    }
```

**All 34 state files** follow this pattern. States cannot exist in a "static-only" library while maintaining current API.

### Impact

- States are conceptually static (immutable geometry + visual properties)
- Implementation is animation-aware (easing priority system)
- Static rendering never uses `DEFAULT_EASING`, but it's always imported
- Removal breaks animation's 4-level easing resolution

---

## Dependency Analysis

### What Cleanly Separates

| Module | Static? | Animation Deps? | Verdict |
|--------|---------|-----------------|---------|
| core/ | ✅ | ❌ | Clean |
| layout/ | ✅ | ❌ | Clean |
| path/ | ✅ | ❌ | Clean |
| vertex/ | ✅ | ❌ | Clean |
| converter/ | ✅ | ❌ (TYPE_CHECKING only) | Clean |
| config/ | ✅ | ❌ | Clean |

### What Requires Refactoring

| Component | Issue | Solution |
|-----------|-------|----------|
| **State classes** | Import easing functions | Extract to separate module, lazy-load |
| **VertexState** | `_aligned_contours` field for morphing | Use projection pattern, add in animation layer |
| **Renderer base** | Morphing detection logic | Strategy pattern, dependency injection |
| **VScene** | Mixed static/animation rendering | Create separate StaticScene vs AnimatedScene |

### What Cannot Separate

- **VElement** - Fundamentally temporal (keystates, interpolation)
- **InterpolationEngine** - Core animation abstraction
- **EasingResolver** - Animation-specific logic
- **Dev server** - Depends on animation rendering

---

## Architectural Options

### Option 1: Hard Split (Two Packages)

**svgpy (static layer):**
```
svgpy/
├── core/              # Color, Point2D, Logger
├── component/
│   ├── state/         # States WITHOUT easing references
│   ├── renderer/      # Renderers (static primitives only)
│   └── vertex/        # Vertex generators
├── layout/            # Layout functions
├── path/              # Path manipulation
├── converter/         # Rasterization
└── scene/             # StaticScene for single-frame rendering
```

**vood (animation layer):**
```
vood/
├── transition/        # Easing, interpolation
├── velement/          # VElement + keystates
├── animation/         # Helpers
├── server/            # Dev server
└── [depends on svgpy] # Re-exports + extends
```

**Pros:**
- Clean separation for static-only users
- Smaller dependency footprint
- Independent versioning

**Cons:**
- Major refactoring (remove easing from all states)
- Breaking API change
- Maintenance burden (two packages)
- Installation complexity (vood requires svgpy)
- Risk of API drift between packages

### Option 2: Layered Architecture (Single Package)

Keep vood unified but create clear internal layers:

```python
# Static-only imports
from vood.static import State, Renderer, layout, VScene
scene = VScene(...)
scene.export("output.svg")  # Static rendering only

# Animation imports
from vood import VElement, easing
from vood.static import CircleState  # Re-exported
element = VElement(keystates=[...])
```

**Pros:**
- No breaking changes
- Clearer conceptual organization
- Users can choose static-only imports
- Single package to maintain

**Cons:**
- Still includes animation code in installation
- Requires internal refactoring (less than hard split)
- Doesn't reduce dependency footprint

### Option 3: Status Quo with Documentation

Document current static capabilities more clearly:

```python
# Static usage (already works!)
from vood import CircleState, VElement, VScene

# Single state = static rendering
static_circle = VElement(state=CircleState(radius=50))
scene = VScene(elements=[static_circle])
scene.export("static.svg")  # No animation
```

**Pros:**
- No refactoring needed
- Already works today
- Simple mental model

**Cons:**
- Full dependency installation even for static use
- Less discoverable for static-only users

---

## Recommended Approach

### Short-term (Pre-v1.0): Option 3 + Better Docs

1. **Document static usage pattern** prominently in README
2. **Add examples/** showing static-only workflows
3. **Label animation dependencies** as optional in docs
4. Monitor user feedback for static vs. animation usage patterns

### Medium-term (v1.0): Option 2 - Layered Architecture

If static usage emerges as common pattern:

1. **Create `vood/static/` namespace**
   - Re-export: State, Renderer, layout, path, converter
   - Provide StaticScene (subset of VScene)

2. **Extract easing from State classes**
   - Create `vood/animation/easing_registry.py`
   - States become pure geometry + visual properties
   - Easing resolution stays in animation layer

3. **Maintain backwards compatibility**
   - `from vood import CircleState` still works (default import)
   - `from vood.static import CircleState` for explicit static-only

### Long-term (v2.0+): Option 1 - Hard Split

Only if demand justifies maintenance burden:

1. Extract svgpy as separate package
2. Provide migration guide
3. vood becomes thin wrapper + animation engine

---

## Technical Challenges in Detail

### 1. Easing Extraction Strategy

**Current:**
```python
@dataclass(frozen=True)
class CircleState(VertexState):
    radius: float = 50
    DEFAULT_EASING = {"radius": easing.in_out}
```

**After refactoring:**
```python
# vood/static/state/circle.py
@dataclass(frozen=True)
class CircleState(VertexState):
    radius: float = 50
    # No easing references

# vood/animation/easing_registry.py
EASING_DEFAULTS = {
    CircleState: {"radius": easing.in_out},
    ...
}
```

**Impact:** All 34 state files need updating

### 2. VertexState Morphing Metadata

**Current:**
```python
@dataclass(frozen=True)
class VertexState(State):
    _aligned_contours: Optional[VertexContours] = None  # Added during interpolation
```

**After refactoring:**
- Base VertexState stays in static layer (pure geometry)
- Animation layer adds `_aligned_contours` via projection
- Use `attrs` or custom `__setattr__` for post-construction annotation

### 3. VScene Dual-Mode Rendering

**Current:**
```python
class VScene:
    def render_at_frame_time(self, t: float): ...  # Animation
    def export(self, filename): ...  # Static (t=0.0)
```

**After refactoring:**
```python
# vood/static/scene.py
class StaticScene:
    def render(self): ...  # No time parameter
    def export(self, filename): ...

# vood/vscene/vscene.py (animation)
class VScene(StaticScene):
    def render_at_frame_time(self, t: float): ...
    def to_mp4(self, ...): ...
```

---

## Key Metrics

**Lines of Code by Category:**
- Static-eligible: ~40% (core, layout, path, vertex, config)
- Animation-only: ~35% (transition, velement, animation, server)
- Mixed/Problematic: ~25% (component/state, component/renderer, vscene)

**Refactoring Effort Estimate:**
- Easing extraction: 34 state files (moderate)
- VertexState projection: 1 base class (complex)
- VScene split: 1 class (moderate)
- Testing/validation: All examples + tests (high)

**Breaking Changes:**
- Hard split: Major (requires user migration)
- Layered architecture: Minor (opt-in static imports)
- Status quo: None

---

## Decision Criteria

Split makes sense if:
- ✅ Strong demand for static-only usage emerges
- ✅ Animation dependencies become heavyweight (ML models, GPU acceleration)
- ✅ Static library could serve broader audience (e.g., scientific plotting)
- ❌ Maintenance burden justifies benefits (currently: no)
- ❌ User base large enough to support two packages (currently: no)

---

## Conclusion

**Recommendation: Defer splitting until v1.0+**

The architecture is well-layered conceptually, but the tight integration in the State layer creates non-trivial refactoring work. Given the alpha status (v0.5.0) and unclear demand for static-only usage, the cost-benefit doesn't justify a split yet.

**Immediate action:**
- Document static usage patterns prominently
- Monitor user feedback on static vs. animation needs
- Keep architecture clean for potential future split

**Revisit when:**
- User base grows significantly
- Clear static-only user segment emerges
- Animation layer adds heavyweight dependencies
