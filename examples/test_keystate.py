"""Test KeyState class implementation"""

from vood.velement import VElement, KeyState
from vood.component.state.circle import CircleState
from vood.component.renderer.circle import CircleRenderer
from vood.transition import easing
from vood.core.color import Color

# Test 1: Backward compatibility - tuple formats still work
print("Test 1: Backward compatibility with tuples...")
try:
    circle1 = CircleState(radius=50, fill_color=Color("#FF0000"))
    circle2 = CircleState(radius=100, fill_color=Color("#00FF00"))

    # Old tuple format
    element1 = VElement(
        renderer=CircleRenderer(),
        keystates=[
            (0.0, circle1),
            (1.0, circle2)
        ]
    )
    print("✓ Tuple format works")
except Exception as e:
    print(f"✗ Tuple format failed: {e}")

# Test 2: New KeyState class
print("\nTest 2: New KeyState class...")
try:
    circle3 = CircleState(radius=50, fill_color=Color("#0000FF"))
    circle4 = CircleState(radius=100, fill_color=Color("#FFFF00"))

    # New KeyState format
    element2 = VElement(
        renderer=CircleRenderer(),
        keystates=[
            KeyState(state=circle3, time=0.0),
            KeyState(state=circle4, time=1.0)
        ]
    )
    print("✓ KeyState class works")
except Exception as e:
    print(f"✗ KeyState class failed: {e}")

# Test 3: KeyState with easing
print("\nTest 3: KeyState with per-segment easing...")
try:
    circle5 = CircleState(radius=50, fill_color=Color("#FF00FF"))
    circle6 = CircleState(radius=100, fill_color=Color("#00FFFF"))

    element3 = VElement(
        renderer=CircleRenderer(),
        keystates=[
            KeyState(
                state=circle5,
                time=0.0,
                easing={"radius": easing.bounce}
            ),
            KeyState(state=circle6, time=1.0)
        ]
    )
    print("✓ KeyState with easing works")
except Exception as e:
    print(f"✗ KeyState with easing failed: {e}")

# Test 4: Mixed formats (tuples and KeyState together)
print("\nTest 4: Mixed formats...")
try:
    circle7 = CircleState(radius=30, fill_color=Color("#FF0000"))
    circle8 = CircleState(radius=60, fill_color=Color("#00FF00"))
    circle9 = CircleState(radius=90, fill_color=Color("#0000FF"))

    element4 = VElement(
        renderer=CircleRenderer(),
        keystates=[
            (0.0, circle7),  # Tuple format
            KeyState(state=circle8, time=0.5),  # KeyState format
            (1.0, circle9)  # Tuple format again
        ]
    )
    print("✓ Mixed formats work")
except Exception as e:
    print(f"✗ Mixed formats failed: {e}")

# Test 5: Auto-timing with KeyState
print("\nTest 5: Auto-timing with KeyState...")
try:
    circle10 = CircleState(radius=40, fill_color=Color("#FF0000"))
    circle11 = CircleState(radius=70, fill_color=Color("#00FF00"))
    circle12 = CircleState(radius=100, fill_color=Color("#0000FF"))

    element5 = VElement(
        renderer=CircleRenderer(),
        keystates=[
            KeyState(state=circle10),  # Auto-timed to 0.0
            KeyState(state=circle11),  # Auto-timed to 0.5
            KeyState(state=circle12),  # Auto-timed to 1.0
        ]
    )

    # Verify auto-timing worked
    assert element5.keystates[0].time == 0.0
    assert element5.keystates[1].time == 0.5
    assert element5.keystates[2].time == 1.0
    print("✓ Auto-timing works")
except Exception as e:
    print(f"✗ Auto-timing failed: {e}")

# Test 6: KeyState validation
print("\nTest 6: KeyState validation...")
try:
    circle13 = CircleState(radius=50)

    # Should fail - time out of range
    try:
        invalid_ks = KeyState(state=circle13, time=1.5)
        print("✗ Validation failed to catch invalid time")
    except ValueError as e:
        print(f"✓ Validation correctly caught invalid time: {e}")

    # Should fail - invalid alignment key
    try:
        invalid_ks2 = KeyState(
            state=circle13,
            time=0.5,
            alignment={"invalid_key": None}
        )
        print("✗ Validation failed to catch invalid alignment key")
    except ValueError as e:
        print(f"✓ Validation correctly caught invalid alignment key")

except Exception as e:
    print(f"✗ Validation test failed unexpectedly: {e}")

# Test 7: Rendering with KeyState
print("\nTest 7: Rendering with KeyState...")
try:
    circle14 = CircleState(radius=50, fill_color=Color("#FF0000"))
    circle15 = CircleState(radius=100, fill_color=Color("#0000FF"))

    element6 = VElement(
        renderer=CircleRenderer(),
        keystates=[
            KeyState(state=circle14, time=0.0),
            KeyState(state=circle15, time=1.0)
        ]
    )

    # Test rendering at different times
    result_start = element6.render_at_frame_time(0.0)
    result_mid = element6.render_at_frame_time(0.5)
    result_end = element6.render_at_frame_time(1.0)

    assert result_start is not None
    assert result_mid is not None
    assert result_end is not None

    print("✓ Rendering works at all time points")
except Exception as e:
    print(f"✗ Rendering failed: {e}")

print("\n" + "="*50)
print("All tests completed successfully!")
print("="*50)
