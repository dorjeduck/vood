"""Demonstration of different alignment norms (L1, L2, L∞)

This example shows how different distance norms affect vertex alignment
during morphing. Each norm produces different alignment strategies:

- L1: Minimizes sum of distances (economical, may have outliers)
- L2: Minimizes root-mean-square distance (balanced, statistically optimal)
- L∞: Minimizes maximum distance (minimax, ensures fairness)
"""

from vood.component.state import PolygonState, TriangleState
from vood.core.color import Color
from vood.vscene import VScene
from vood.velement import VElement
from vood.velement.keystate import KeyState, Morphing
from vood.transition.vertex_alignment import AngularAligner, AlignmentNorm

# Colors
START_COLOR = Color("#FDBE02")
END_COLOR = Color("#AA0000")

# Create three scenes to compare different norms

# Scene 1: L1 norm (default - sum of distances)
scene_l1 = VScene(width=400, height=400, background=Color("#000033"))
element_l1 = VElement(
    keystates=[
        KeyState(
            state=PolygonState(x=-80, num_sides=5, size=100, fill_color=START_COLOR),
            time=0.0,
        ),
        KeyState(
            state=TriangleState(x=80, rotation=180, size=100, fill_color=END_COLOR),
            time=1.0,
            morphing=Morphing(vertex_aligner=AngularAligner(norm="l1")),
        ),
    ]
)
scene_l1.add_element(element_l1)

# Scene 2: L2 norm (root mean square)
scene_l2 = VScene(width=400, height=400, background=Color("#000033"))
element_l2 = VElement(
    keystates=[
        KeyState(
            state=PolygonState(x=-80, num_sides=5, size=100, fill_color=START_COLOR),
            time=0.0,
        ),
        KeyState(
            state=TriangleState(x=80, rotation=180, size=100, fill_color=END_COLOR),
            time=1.0,
            morphing=Morphing(vertex_aligner=AngularAligner(norm=AlignmentNorm.L2)),
        ),
    ]
)
scene_l2.add_element(element_l2)

# Scene 3: L∞ norm (minimax - minimizes worst-case distance)
scene_linf = VScene(width=400, height=400, background=Color("#000033"))
element_linf = VElement(
    keystates=[
        KeyState(
            state=PolygonState(x=-80, num_sides=5, size=100, fill_color=START_COLOR),
            time=0.0,
        ),
        KeyState(
            state=TriangleState(x=80, rotation=180, size=100, fill_color=END_COLOR),
            time=1.0,
            morphing=Morphing(vertex_aligner=AngularAligner(norm="linf")),
        ),
    ]
)
scene_linf.add_element(element_linf)

# Export to compare visually
if __name__ == "__main__":
    from vood.vscene import VSceneExporter

    # Export mid-frame (t=0.5) for each norm to compare alignment
    exporter_l1 = VSceneExporter(scene_l1)
    exporter_l1.export("output/norm_l1", total_frames=10, formats=["svg"])

    exporter_l2 = VSceneExporter(scene_l2)
    exporter_l2.export("output/norm_l2", total_frames=10, formats=["svg"])

    exporter_linf = VSceneExporter(scene_linf)
    exporter_linf.export("output/norm_linf", total_frames=10, formats=["svg"])

    print("✅ Exported norm comparison to output/ directory")
    print("   - norm_l1_frame_*.svg (sum of distances)")
    print("   - norm_l2_frame_*.svg (RMS distance)")
    print("   - norm_linf_frame_*.svg (minimax)")
    print("\nCompare frame_05 (mid-morph) to see alignment differences!")
