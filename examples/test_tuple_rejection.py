"""Test that complex tuple formats are rejected with helpful errors"""

from vood.velement import VElement, KeyState
from vood.component.state.circle import CircleState
from vood.component.renderer.circle import CircleRenderer
from vood.transition import easing

print("Testing that complex tuples are rejected...\n")

circle1 = CircleState(radius=50)
circle2 = CircleState(radius=100)

# Test 1: Try 3-tuple with easing (should fail)
print("Test 1: 3-tuple with easing should be rejected...")
try:
    element = VElement(
        renderer=CircleRenderer(),
        keystates=[
            (0.0, circle1, {"radius": easing.linear}),  # 3-tuple
            (1.0, circle2)
        ]
    )
    print("✗ FAILED - 3-tuple was accepted (should have been rejected)")
except ValueError as e:
    if "For easing or alignment, use KeyState" in str(e):
        print(f"✓ PASSED - Rejected with helpful message")
        print(f"  Error: {e}")
    else:
        print(f"✗ FAILED - Wrong error message: {e}")

# Test 2: Show the correct way
print("\nTest 2: Correct way using KeyState...")
try:
    element = VElement(
        renderer=CircleRenderer(),
        keystates=[
            KeyState(state=circle1, time=0.0, easing={"radius": easing.linear}),
            KeyState(state=circle2, time=1.0)
        ]
    )
    print("✓ PASSED - KeyState format works correctly")
except Exception as e:
    print(f"✗ FAILED - KeyState format should work: {e}")

print("\n" + "="*60)
print("Complex tuples correctly rejected, KeyState works!")
print("="*60)
