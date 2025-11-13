"""Test the new Shape class hierarchy"""

from vood.component.state import PerforatedShapeState, Circle, Ellipse, Rectangle, Polygon

print("Test 1: Creating shape objects...")
try:
    circle = Circle(radius=20, x=-30, y=0)
    print(f"✓ Circle: {circle}")

    ellipse = Ellipse(rx=50, ry=40, x=-70, y=-80, rotation=45)
    print(f"✓ Ellipse: {ellipse}")

    rect = Rectangle(width=40, height=30, x=50, y=0, rotation=15)
    print(f"✓ Rectangle: {rect}")

    poly = Polygon(num_sides=6, radius=25, x=0, y=60)
    print(f"✓ Polygon: {poly}")

except Exception as e:
    print(f"✗ Failed to create shape objects: {e}")
    exit(1)

print("\nTest 2: Creating PerforatedShapeState with Shape objects...")
try:
    state = PerforatedShapeState(
        outer_shape=Circle(radius=100),
        holes=[
            Circle(radius=20, x=-30, y=0),
            Ellipse(rx=30, ry=20, x=30, y=0, rotation=45),
            Rectangle(width=25, height=25, x=0, y=-40, rotation=30),
        ]
    )
    print(f"✓ PerforatedShapeState created with {len(state.holes)} holes")
    print(f"  Hole types: {[type(h).__name__ for h in state.holes]}")

except Exception as e:
    print(f"✗ Failed to create PerforatedShapeState: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\nTest 3: Generating contours...")
try:
    contours = state._generate_contours()
    print(f"✓ Contours generated")
    print(f"  Outer vertices: {len(contours.outer.vertices)}")
    print(f"  Number of holes: {len(contours.holes)}")
    print(f"  Hole vertex counts: {[len(h.vertices) for h in contours.holes]}")

except Exception as e:
    print(f"✗ Failed to generate contours: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*50)
print("All tests passed! ✓")
print("="*50)
