from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional

import drawsvg as dw

from vood.components import Renderer, State
from vood.utils import to_rgb_string
from vood.transitions import Easing


@dataclass
class MoonPhaseState(State):
    """State class for moon phase renderers"""

    size: float = 50
    color: Tuple[int, int, int] = (255, 255, 255)
    stroke_color: Optional[Tuple[int, int, int]] = None
    stroke_width: float = 1

    # Moon-specific properties
    illumination: float = 100  # 0-100, percentage of moon illuminated
    waxing: bool = True  # True for waxing, False for waning
    northern_hemisphere: bool = True  # True if in northern hemisphere

    DEFAULT_EASING = {
        "x": Easing.in_out,
        "y": Easing.in_out,
        "scale": Easing.in_out,
        "rotation": Easing.in_out,
        "opacity": Easing.linear,
        "size": Easing.in_out,
        "color": Easing.linear,
        "stroke_color": Easing.linear,
        "stroke_width": Easing.in_out,
        "illumination": Easing.in_out,
        "waxing": Easing.linear,
    }


class MoonPhaseRenderer(Renderer):
    """Moon phase renderer with variable illumination"""

    precision: int = 10  # Decimal precision for calculations

    def _render_core(self, state: MoonPhaseState) -> dw.Group:
        """Render the moon phase geometry (renderer only, no transforms)

        Args:
            state: MoonPhaseState containing rendering properties

        Returns:
            drawsvg Group containing the moon phase geometry
        """
        fill_color = to_rgb_string(state.color)
        stroke_color = (
            to_rgb_string(state.stroke_color) if state.stroke_color else fill_color
        )

        # Center geometry at (0, 0); base class handles positioning
        radius = round(state.size / 2, self.precision)
        cx = 0
        cy = 0
        y_top = -radius
        y_bottom = radius
        arcrad = round((abs(state.illumination - 50) / 50) * radius, self.precision)
        sf1 = 1
        sf2 = 0
        sf3 = 0
        if not state.waxing:  # waning
            sf1 = 0
            sf3 = 1
            if state.illumination < 50:
                sf2 = 1
        else:  # waxing
            if state.illumination >= 50:
                sf2 = 1

        # Calculate the arc's x-radius -- i.e. the second radius of the half-ellipse
        arcrad = round((abs(state.illumination - 50) / 50) * radius, self.precision)

        # Set the sweep flag for the 3 arcs
        sf1 = 1
        sf2 = 0
        sf3 = 0

        # Determine moon phase direction
        if not state.waxing:  # waning
            sf1 = 0
            sf3 = 1
            if state.illumination < 50:
                sf2 = 1
        else:  # waxing
            if state.illumination >= 50:
                sf2 = 1

        # Create main group
        main_group = dw.Group()

        if state.illumination == 100:  # full moon -- draw 1 circle
            circle = dw.Circle(
                cx=cx,
                cy=cy,
                r=radius,
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(circle)

        elif state.illumination == 0:  # new moon -- draw 1 circle
            circle = dw.Circle(
                cx=cx,
                cy=cy,
                r=radius,
                fill="none",
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(circle)

        elif state.illumination == 50:  # half moon -- draw 2 circular arcs and a line
            # Background circle
            circle = dw.Circle(
                cx=cx,
                cy=cy,
                r=radius,
                fill="none",
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(circle)

            # Filled half
            path1 = dw.Path(
                d=f"M {cx} {y_top} A {radius},{radius} 0 0 {sf1} {cx},{y_bottom} Z",
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(path1)

            # Border arc
            path2 = dw.Path(
                d=f"M {cx} {y_top} A {radius},{radius} 0 0 {sf3} {cx},{y_bottom}",
                fill="none",
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(path2)

        else:  # crescent or gibbous -- draw 2 circular arcs and an elliptical arc
            # Background circle
            circle = dw.Circle(
                cx=cx,
                cy=cy,
                r=radius,
                fill="none",
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(circle)

            # Filled phase
            path1 = dw.Path(
                d=f"M {cx} {y_top} A {radius},{radius} 0 0 {sf1} {cx},{y_bottom} A {arcrad},{radius} 0 0 {sf2} {cx},{y_top}",
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(path1)

            # Border arc
            path2 = dw.Path(
                d=f"M {cx} {y_top} A {radius},{radius} 0 0 {sf3} {cx},{y_bottom}",
                fill="none",
                stroke=stroke_color,
                stroke_width=state.stroke_width,
                opacity=state.opacity,
            )
            main_group.append(path2)

        # Rotate 180 degrees if southern hemisphere
        if not state.northern_hemisphere:
            main_group.args["transform"] = "rotate(180)"

            super_group = dw.Group()
            super_group.append(main_group)
            return super_group

        return main_group


class MoonPhaseRenderer2(MoonPhaseRenderer):
    """Alternative moon phase renderer with smooth illumination adjustments"""

    def _render_core(self, state: MoonPhaseState) -> dw.Group:
        """Render moon phase geometry with smooth illumination scaling"""

        adjusted_illumination = state.illumination

        # Apply smooth scaling for thin crescents (0-25%) - enhance visibility
        if state.illumination <= 25:
            # Smoothly scale from 1.0 at 25% to 1.8 at 0%
            scale_factor = 1.0 + (25 - state.illumination) / 25 * 0.8
            adjusted_illumination = min(state.illumination * scale_factor, 100)

        # Apply smooth scaling for nearly full moons (75-100%) - add definition
        elif state.illumination >= 75:
            # Smoothly scale from 1.0 at 75% to 0.9 at 100%
            scale_factor = 1.0 - (state.illumination - 75) / 25 * 0.1
            adjusted_illumination = state.illumination * scale_factor

        # Create a new state with adjusted illumination
        adjusted_state = MoonPhaseState(
            x=state.x,
            y=state.y,
            scale=state.scale,
            rotation=state.rotation,
            opacity=state.opacity,
            size=state.size,
            color=state.color,
            stroke_color=state.stroke_color,
            stroke_width=state.stroke_width,
            illumination=adjusted_illumination,
            waxing=state.waxing,
        )

        # Use parent render method with adjusted state
        return super()._render_core(adjusted_state)
