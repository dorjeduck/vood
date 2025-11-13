"""Test per-segment alignment configuration

Tests all format variations and ensures backward compatibility with 3-tuple format.
"""

from vood.component.state import PerforatedShapeState, CircleState
from vood.velement import VElement
from vood.transition.interpolation.hole_mapping import (
    SimpleMapper,
    DiscreteMapper,
    GreedyNearestMapper,
)
from vood.transition import easing


def test_backward_compatibility_3tuple():
    """Test that old 3-tuple format still works"""
    print("\n" + "=" * 60)
    print("Test: Backward compatibility with 3-tuple format")
    print("=" * 60)

    state1 = CircleState(radius=50)
    state2 = CircleState(radius=100)
    state3 = CircleState(radius=75)

    # Old format: (time, state, easing_dict)
    try:
        element = VElement(keystates=[
            (0.0, state1),
            (0.5, state2, {"x": easing.in_out_sine}),  # 3-tuple
            (1.0, state3),
        ])

        # Verify parsing worked
        assert len(element.keystates) == 3
        assert all(len(ks) == 4 for ks in element.keystates)  # All converted to 4-tuple
        assert element.keystates[1][2] is not None  # Easing dict preserved
        assert element.keystates[1][3] is None  # Alignment dict is None (not specified)

        print("✅ 3-tuple format works (backward compatible)")
        print(f"   Parsed {len(element.keystates)} keystates")
        print(f"   All converted to 4-tuple format internally")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def test_4tuple_alignment_only():
    """Test 4-tuple format with alignment config only"""
    print("\n" + "=" * 60)
    print("Test: 4-tuple format with alignment config only")
    print("=" * 60)

    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 12, "x": -30, "y": 0},
            {"type": "circle", "radius": 12, "x": 30, "y": 0},
        ],
    )

    try:
        element = VElement(keystates=[
            state1,
            (state2, None, {"hole_mapper": SimpleMapper()}),  # alignment only
        ])

        assert len(element.keystates) == 2
        assert element.keystates[1][2] is None  # No easing dict
        assert element.keystates[1][3] is not None  # Alignment dict present
        assert "hole_mapper" in element.keystates[1][3]

        print("✅ Alignment-only format works")
        print(f"   Alignment config: {list(element.keystates[1][3].keys())}")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def test_4tuple_both_easing_and_alignment():
    """Test 4-tuple with both easing and alignment configs"""
    print("\n" + "=" * 60)
    print("Test: 4-tuple with both easing and alignment")
    print("=" * 60)

    state1 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 15, "x": 0, "y": 0},
            {"type": "circle", "radius": 15, "x": -40, "y": 0},
            {"type": "circle", "radius": 15, "x": 40, "y": 0},
        ],
    )

    state2 = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 18, "x": -50, "y": -50},
            {"type": "circle", "radius": 18, "x": 50, "y": 50},
        ],
    )

    try:
        element = VElement(keystates=[
            (0.0, state1),
            (1.0, state2, {"opacity": easing.in_out_cubic}, {
                "hole_mapper": DiscreteMapper()
            }),
        ])

        assert len(element.keystates) == 2
        assert element.keystates[1][2] is not None  # Easing dict present
        assert element.keystates[1][3] is not None  # Alignment dict present
        assert "opacity" in element.keystates[1][2]
        assert "hole_mapper" in element.keystates[1][3]

        print("✅ Combined easing + alignment format works")
        print(f"   Easing for: {list(element.keystates[1][2].keys())}")
        print(f"   Alignment config: {list(element.keystates[1][3].keys())}")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def test_multiple_segments_different_matchers():
    """Test multiple segments with different hole matchers"""
    print("\n" + "=" * 60)
    print("Test: Multiple segments with different matchers")
    print("=" * 60)

    state_a = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[{"type": "circle", "radius": 15, "x": 0, "y": 0}],
    )

    state_b = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 12, "x": -40, "y": 0},
            {"type": "circle", "radius": 12, "x": 40, "y": 0},
        ],
    )

    state_c = PerforatedShapeState(
        outer_shape={"type": "circle", "radius": 100},
        holes=[
            {"type": "circle", "radius": 10, "x": -30, "y": -30},
            {"type": "circle", "radius": 10, "x": 30, "y": -30},
            {"type": "circle", "radius": 10, "x": 0, "y": 30},
        ],
    )

    try:
        element = VElement(keystates=[
            (0.0, state_a),
            (0.33, state_b, None, {"hole_mapper": SimpleMapper()}),
            (0.66, state_c, None, {"hole_mapper": DiscreteMapper()}),
            (1.0, state_a, None, {"hole_mapper": GreedyNearestMapper()}),
        ])

        assert len(element.keystates) == 4

        # Check each alignment config
        assert element.keystates[0][3] is None  # First state has no override
        assert isinstance(element.keystates[1][3]["hole_mapper"], SimpleMapper)
        assert isinstance(element.keystates[2][3]["hole_mapper"], DiscreteMapper)
        assert isinstance(element.keystates[3][3]["hole_mapper"], GreedyNearestMapper)

        print("✅ Multiple segments with different matchers work")
        print(f"   Segment 1: No override (uses config default)")
        print(f"   Segment 2: {type(element.keystates[1][3]['hole_mapper']).__name__}")
        print(f"   Segment 3: {type(element.keystates[2][3]['hole_mapper']).__name__}")
        print(f"   Segment 4: {type(element.keystates[3][3]['hole_mapper']).__name__}")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


def test_invalid_alignment_key():
    """Test that invalid alignment dict keys are rejected"""
    print("\n" + "=" * 60)
    print("Test: Invalid alignment dict keys are rejected")
    print("=" * 60)

    state1 = CircleState(radius=50)
    state2 = CircleState(radius=100)

    try:
        element = VElement(keystates=[
            state1,
            (state2, None, {
                "invalid_key": "some_value",  # Should be rejected
                "hole_mapper": SimpleMapper()
            }),
        ])
        print("❌ FAILED: Should have raised ValueError for invalid key")
        raise AssertionError("Invalid key should have been rejected")

    except ValueError as e:
        if "invalid_key" in str(e).lower():
            print("✅ Invalid alignment keys properly rejected")
            print(f"   Error message: {e}")
        else:
            print(f"❌ FAILED: Wrong error message: {e}")
            raise


def test_mixed_old_and_new_formats():
    """Test mixing old 3-tuple and new 4-tuple formats"""
    print("\n" + "=" * 60)
    print("Test: Mixing old and new tuple formats")
    print("=" * 60)

    state1 = CircleState(radius=50)
    state2 = CircleState(radius=75)
    state3 = CircleState(radius=100)
    state4 = CircleState(radius=60)

    try:
        element = VElement(keystates=[
            state1,  # Bare state
            (0.33, state2, {"x": easing.in_out_sine}),  # Old 3-tuple
            (0.66, state3, None, {"hole_mapper": SimpleMapper()}),  # New 4-tuple
            state4,  # Bare state
        ])

        assert len(element.keystates) == 4
        assert all(len(ks) == 4 for ks in element.keystates)

        print("✅ Mixing old and new formats works")
        print(f"   All normalized to 4-tuple internally")

    except Exception as e:
        print(f"❌ FAILED: {e}")
        raise


if __name__ == "__main__":
    test_backward_compatibility_3tuple()
    test_4tuple_alignment_only()
    test_4tuple_both_easing_and_alignment()
    test_multiple_segments_different_matchers()
    test_invalid_alignment_key()
    test_mixed_old_and_new_formats()

    print("\n" + "=" * 60)
    print("✅ All per-segment alignment tests PASSED!")
    print("=" * 60 + "\n")
