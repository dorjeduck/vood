#!/usr/bin/env python3
"""Test script to visualize all digits 0-9"""

from vood.component import NumberState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")

def main():
    """Create a grid showing all 10 digits"""
    scene = VScene(width=512, height=256, background=Color("#2d2d44"))

    # Create 10 elements for digits 0-9 in two rows
    positions = [
        # Top row: 0-4
        (-200, -60), (-100, -60), (0, -60), (100, -60), (200, -60),
        # Bottom row: 5-9
        (-200, 60), (-100, 60), (0, 60), (100, 60), (200, 60),
    ]

    for digit in range(10):
        x, y = positions[digit]
        state = NumberState(
            digit=digit,
            x=x,
            y=y,
            width=30,
            height=50,
            fill_color=Color("#16c79a"),
            stroke_color=Color("#11998e"),
            stroke_width=2,
            fill_opacity=0.9,
            _num_vertices=64,  # Lower for faster testing
        )
        element = VElement(state=state)
        scene.add_element(element)

    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    exporter.export(filename="all_digits_test", formats=["svg"])
    print("✓ All digits rendered to output/all_digits_test.svg")
    print("  Check the SVG to verify all shapes look correct")

if __name__ == "__main__":
    main()
