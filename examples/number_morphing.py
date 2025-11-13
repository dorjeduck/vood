"""Example: Number morphing animation

Demonstrates morphing between digits 0-9 using the NumberState class.
Each digit has a beautiful monospaced vertex representation with proper holes
(0, 6, 8, 9) that smoothly transitions into the next digit.
"""

from vood.animation.atomic import sequential_transition, trim
from vood.component import NumberState
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging
from vood.velement import VElement
from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter
from vood.core.color import Color

configure_logging(level="INFO")


def main():
    """Create a morphing animation through all digits 0-9"""
    # Create the scene with dark background
    scene = VScene(width=256, height=256, background=Color("#1a1a2e"))

    # Create keystates for morphing through all digits 0-9
    states = [
        NumberState(
            digit=i,
            width=40,
            height=60,
            fill_color=Color("#16c79a"),
            stroke_color=Color("#11998e"),
            stroke_width=2,
            fill_opacity=0.9,
            _num_vertices=128,  # Smooth curves
        )
        for i in [0, 2,4,6,7,9]
    ]

    keystates = sequential_transition(states, trim, 0.8)

    # Create element that morphs through all digits
    element = VElement(keystates=keystates)

    # Add to scene
    scene.add_element(element)

    # Create exporter
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.INKSCAPE,
        output_dir="output/",
    )

    # Export static SVG of first digit
    exporter.export(filename="number_static", formats=["svg"])

    # Export animation
    exporter.to_mp4(
        filename="number_morphing",
        total_frames=len(states) * 30,  # 20 frames per digit transition
        framerate=30,
        png_width_px=1024,
    )

    print("✓ Number morphing animation created!")
    print("  Static: output/number_static.svg")
    print("  Animation: output/number_morphing.mp4")


def countdown_example():
    """Alternative example: 3-2-1 countdown with timing"""
    scene = VScene(width=256, height=256, background=Color("#000000"))

    # Create countdown keystates with explicit timing
    # Hold each number for longer, quick transition
    keystates = [
        (
            NumberState(
                digit=3,
                width=60,
                height=90,
                fill_color=Color("#ff6b6b"),
                _num_vertices=128,
            ),
            0.0,
        ),
        (
            NumberState(
                digit=3,
                width=60,
                height=90,
                fill_color=Color("#ff6b6b"),
                _num_vertices=128,
            ),
            0.3,
        ),
        (
            NumberState(
                digit=2,
                width=60,
                height=90,
                fill_color=Color("#ffd93d"),
                _num_vertices=128,
            ),
            0.4,
        ),
        (
            NumberState(
                digit=2,
                width=60,
                height=90,
                fill_color=Color("#ffd93d"),
                _num_vertices=128,
            ),
            0.65,
        ),
        (
            NumberState(
                digit=1,
                width=60,
                height=90,
                fill_color=Color("#6bcf7f"),
                _num_vertices=128,
            ),
            0.75,
        ),
        (
            NumberState(
                digit=1,
                width=60,
                height=90,
                fill_color=Color("#6bcf7f"),
                _num_vertices=128,
            ),
            1.0,
        ),
    ]

    element = VElement(keystates=keystates)
    scene.add_element(element)

    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    exporter.to_mp4(
        filename="countdown_321",
        total_frames=90,
        framerate=30,
        png_width_px=1024,
    )

    print("✓ Countdown animation created!")
    print("  Animation: output/countdown_321.mp4")


def showcase_holes_example():
    """Example showcasing digits with holes (0, 6, 8, 9)"""
    scene = VScene(width=512, height=256, background=Color("#2d2d44"))

    # Create four elements showing digits with holes
    digits_with_holes = [0, 6, 8, 9]
    x_positions = [-150, -50, 50, 150]

    for digit, x_pos in zip(digits_with_holes, x_positions):
        state = NumberState(
            digit=digit,
            x=x_pos,
            width=35,
            height=55,
            fill_color=Color("#ff6b9d"),
            stroke_color=Color("#c44569"),
            stroke_width=3,
            fill_opacity=0.8,
            _num_vertices=128,
        )
        element = VElement(state=state)
        scene.add_element(element)

    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/",
    )

    exporter.export(filename="numbers_with_holes", formats=["svg", "png"])

    print("✓ Showcase created!")
    print("  Output: output/numbers_with_holes.svg/png")


if __name__ == "__main__":
    main()

    # Uncomment to also generate additional examples:
    # countdown_example()
    # showcase_holes_example()
