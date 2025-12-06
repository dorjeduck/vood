# ============================================================================
# vood/paths/svg_path.py
# ============================================================================
"""SVG Path Class with Morphing Support"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from .commands import (
    PathCommand,
    MoveTo,
    LineTo,
    QuadraticBezier,
    CubicBezier,
    ClosePath,
    HorizontalLine,  # New
    VerticalLine,  # New
    SmoothCubicBezier,  # New
    SmoothQuadraticBezier,  # New
    Arc,  # New
)
from .parser import tokenize_path, parse_coordinates
from .arc_to_bezier import (
    arc_to_beziers,
)  # New: Function to convert Arc to Cubic Beziers
from vood.core.point2d import Point2D

@dataclass
class SVGPath:
    """Structured representation of an SVG path that supports morphing

    Stores path as a list of command objects (MoveTo, LineTo, etc.) rather
    than a string, enabling smooth interpolation between paths.
    """

    commands: List[PathCommand]
    path_string: Optional[str] = None

    @staticmethod
    def from_string(path_string: str) -> SVGPath:
        """
        Parses an SVG path data string (e.g., "M 0,0 L 100,100") into an SVGPath object.

        Handles absolute (M, L, C, Q, H, V, S, T, A) and relative (m, l, c, q, h, v, s, t, a) commands.

        Args:
            path_string: The raw SVG path data string.

        Returns:
            A new SVGPath instance.

        Raises:
            ValueError: If parsing encounters an unexpected command or missing coordinates.
        """
        
        # 1. Tokenize the input string
        tokens = tokenize_path(path_string)

        if not tokens:
            return SVGPath([])

        parsed_commands: List[PathCommand] = []
        # The current command letter for sequential commands (e.g., L 10 20 30 40)
        current_command_type: str = ""

        # All supported commands (M/m, L/l, H/h, V/v, C/c, S/s, Q/q, T/t, A/a, Z/z)
        SUPPORTED_COMMANDS = "MLHVCSQTAZ"

        while tokens:
            token = tokens.pop(0)

            # 2. Check if the token is a command letter
            if token.upper() in SUPPORTED_COMMANDS:
                current_command_type = token
                absolute = token.isupper()
            else:
                # If it's not a command letter, it must be the first coordinate
                # of a sequence, so we use the last known command type.
                tokens.insert(0, token)  # Put the coordinate back

            # If we don't have a command type yet, the path is malformed (doesn't start with M/m)
            if not current_command_type:
                raise ValueError("Path must start with a MoveTo command (M or m).")

            cmd_type = current_command_type.upper()
            absolute = current_command_type.isupper()

            # --- Command Handling ---

            if cmd_type == "M":
                # M/m requires 2 args (x, y)
                coords, tokens = parse_coordinates(tokens, 2)
                x, y = coords
                parsed_commands.append(MoveTo(x, y, absolute))

                # After the first MoveTo, subsequent coordinate pairs without a new
                # command are implicitly LineTo commands (l or L).
                current_command_type = "L" if absolute else "l"

            elif cmd_type == "L":
                # L/l requires 2 args (x, y)
                coords, tokens = parse_coordinates(tokens, 2)
                x, y = coords
                parsed_commands.append(LineTo(x, y, absolute))

            elif cmd_type == "H":  # New: Horizontal Line
                # H/h requires 1 arg (x)
                coords, tokens = parse_coordinates(tokens, 1)
                x = coords.x
                parsed_commands.append(HorizontalLine(x, absolute))

            elif cmd_type == "V":  # New: Vertical Line
                # V/v requires 1 arg (y)
                coords, tokens = parse_coordinates(tokens, 1)
                y = coords.y
                parsed_commands.append(VerticalLine(y, absolute))

            elif cmd_type == "Q":
                # Q/q requires 4 args (cx, cy, x, y)
                coords, tokens = parse_coordinates(tokens, 4)
                cx, cy, x, y = coords
                parsed_commands.append(QuadraticBezier(cx, cy, x, y, absolute))

            elif cmd_type == "T":  # New: Smooth Quadratic Bezier
                # T/t requires 2 args (x, y)
                coords, tokens = parse_coordinates(tokens, 2)
                x, y = coords
                parsed_commands.append(SmoothQuadraticBezier(x, y, absolute))

            elif cmd_type == "C":
                # C/c requires 6 args (cx1, cy1, cx2, cy2, x, y)
                coords, tokens = parse_coordinates(tokens, 6)
                cx1, cy1, cx2, cy2, x, y = coords
                parsed_commands.append(CubicBezier(cx1, cy1, cx2, cy2, x, y, absolute))

            elif cmd_type == "S":  # New: Smooth Cubic Bezier
                # S/s requires 4 args (cx2, cy2, x, y)
                coords, tokens = parse_coordinates(tokens, 4)
                cx2, cy2, x, y = coords
                parsed_commands.append(SmoothCubicBezier(cx2, cy2, x, y, absolute))

            elif cmd_type == "A":  # New: Arc
                # A/a requires 7 args (rx, ry, x_rot, large_arc, sweep, x, y)
                coords, tokens = parse_coordinates(tokens, 7)
                rx, ry, x_axis_rotation, large_arc_flag, sweep_flag, x, y = coords

                # The flags must be integers (0 or 1) in the path data
                if large_arc_flag not in (0, 1) or sweep_flag not in (0, 1):
                    raise ValueError(
                        "Arc flags (large_arc_flag, sweep_flag) must be 0 or 1."
                    )

                parsed_commands.append(
                    Arc(
                        rx,
                        ry,
                        x_axis_rotation,
                        int(large_arc_flag),
                        int(sweep_flag),
                        x,
                        y,
                        absolute,
                    )
                )

            elif cmd_type == "Z":
                # Z/z requires 0 args
                parsed_commands.append(ClosePath())
                # Reset command type after Z, as subsequent path data must start new subpath
                current_command_type = ""

            else:
                # Should not be reachable if SUPPORTED_COMMANDS is comprehensive
                raise ValueError(f"Unknown path command token: '{token}'")

        return SVGPath(parsed_commands, path_string)

    def to_string(self) -> str:
        """Convert to SVG path data string

        Returns:
            SVG path data string (e.g., "M 0,0 L 100,100")
        """
        ## print types of all self.commands
        if self.path_string is None:
            self.path_string = " ".join(cmd.to_string() for cmd in self.commands)
        return self.path_string

    def to_absolute(self) -> SVGPath:
        """Convert all commands to absolute coordinates

        Returns:
            New SVGPath with all absolute commands
        """
        absolute_commands = []
        current_pos = (0.0, 0.0)

        # We need to track the MoveTo position for Z commands
        # and the last control point for S and T commands
        subpath_start_pos = (0.0, 0.0)

        for cmd in self.commands:
            abs_cmd = cmd.to_absolute(current_pos)
            absolute_commands.append(abs_cmd)

            # Track positions
            if isinstance(abs_cmd, MoveTo):
                current_pos = abs_cmd.get_end_point(current_pos)
                subpath_start_pos = current_pos  # Start of new subpath
            elif isinstance(abs_cmd, ClosePath):
                # ClosePath returns to the start of the subpath
                current_pos = subpath_start_pos
            else:
                current_pos = abs_cmd.get_end_point(current_pos)

        return SVGPath(absolute_commands)

    def is_compatible_for_morphing(self, other: SVGPath) -> bool:
        """Check if two paths can be morphed

        Paths are compatible if they have:
        - Same number of commands
        - Same command types in same order

        Args:
            other: Path to check compatibility with

        Returns:
            True if paths can be morphed
        """
        if len(self.commands) != len(other.commands):
            return False

        for cmd1, cmd2 in zip(self.commands, other.commands):
            if type(cmd1) != type(cmd2):
                return False

        return True

    def to_cubic_beziers(self) -> "SVGPath":
        """Convert all curve commands to cubic Bezier curves

        This enables morphing between different curve types by converting
        everything to the most general form (cubic Bezier).
        """
        normalized = []
        current_pos = (0.0, 0.0)

        # Track previous curve's control point for S/T smooth commands
        # Stores the control point P2/C1 of the previous C/S command, or P1/C1 of Q/T command.
        # This point is required to calculate the reflection point for the smooth command.
        previous_control_point  = (0.0, 0.0)

        for cmd in self.commands:
            # 1. Ensure command is absolute for easy calculation
            abs_cmd = cmd.to_absolute(current_pos)

            new_commands: List[PathCommand] = [abs_cmd]  # Default is the command itself

            # 2. Handle Conversion
            if isinstance(abs_cmd, MoveTo):
                previous_control_point = abs_cmd.get_end_point(
                    current_pos
                )  # Reset for safety

            elif isinstance(abs_cmd, (LineTo, HorizontalLine, VerticalLine)):
                # Convert LineTo/H/V to CubicBezier (straight line)

                # First, ensure we have a standard LineTo object
                if isinstance(abs_cmd, (HorizontalLine, VerticalLine)):
                    # Get the LineTo equivalent
                    line_cmd = abs_cmd.to_absolute(current_pos)
                else:
                    line_cmd = abs_cmd

                x1, y1 = current_pos
                x2, y2 = line_cmd.x, line_cmd.y

                # Control points at 1/3 and 2/3 along the line
                cx1 = x1 + (x2 - x1) / 3
                cy1 = y1 + (y2 - y1) / 3
                cx2 = x1 + 2 * (x2 - x1) / 3
                cy2 = y1 + 2 * (y2 - y1) / 3

                new_commands = [CubicBezier(cx1, cy1, cx2, cy2, x2, y2)]
                previous_control_point = (
                    x2,
                    y2,
                )  # End point is the effective control point

            elif isinstance(abs_cmd, QuadraticBezier):
                # Convert QuadraticBezier to CubicBezier
                x1, y1 = current_pos
                qcx, qcy = abs_cmd.cx, abs_cmd.cy
                x2, y2 = abs_cmd.x, abs_cmd.y

                # Formula: cubic control points = (2/3 * quad_control + 1/3 * start/end)
                cx1 = x1 + 2 / 3 * (qcx - x1)
                cy1 = y1 + 2 / 3 * (qcy - y1)
                cx2 = x2 + 2 / 3 * (qcx - x2)
                cy2 = y2 + 2 / 3 * (qcy - y2)

                new_commands = [CubicBezier(cx1, cy1, cx2, cy2, x2, y2)]
                previous_control_point = (
                    qcx,
                    qcy,
                )  # Control point for potential T command

            elif isinstance(abs_cmd, SmoothQuadraticBezier):
                # Convert Smooth Quadratic (T) to QuadraticBezier, then CubicBezier
                p1 = previous_control_point  # Last control point of Q or T
                p2 = abs_cmd.get_end_point(current_pos)

                # Calculate reflected control point (qc_reflected)
                # Reflection formula: P' = 2*End - Control (where 'End' is the start of T command)
                # Reflected control point (Pq1)
                qc_reflected_x = current_pos.x + (current_pos.x - p1.x)
                qc_reflected_y = current_pos.y + (current_pos.y - p1.y)

                # Convert to Q
                q_cmd = QuadraticBezier(qc_reflected_x, qc_reflected_y, p2.x, p2.y)

                # Now convert Q to C (using logic from QuadraticBezier handling)
                qcx, qcy = q_cmd.cx, q_cmd.cy

                cx1 = current_pos.x + 2 / 3 * (qcx - current_pos.x)
                cy1 = current_pos.y + 2 / 3 * (qcy - current_pos.y)
                cx2 = p2.x + 2 / 3 * (qcx - p2.x)
                cy2 = p2.y + 2 / 3 * (qcy - p2.y)

                new_commands = [CubicBezier(cx1, cy1, cx2, cy2, p2.x, p2.y)]
                previous_control_point = (qc_reflected_x, qc_reflected_y)

            elif isinstance(abs_cmd, CubicBezier):
                # Already cubic
                new_commands = [abs_cmd]
                previous_control_point = (
                    abs_cmd.cx2,
                    abs_cmd.cy2,
                )  # Control point for potential S command

            elif isinstance(abs_cmd, SmoothCubicBezier):
                # Convert Smooth Cubic (S) to CubicBezier
                px, py = previous_control_point  # Last control point 2 of C or S
                x2, y2 = abs_cmd.get_end_point(current_pos)

                # Calculate reflected control point (P1_reflected)
                # Reflection formula: P1 = 2*Start - P2_prev
                cx1 = current_pos.x + (current_pos.x - px)
                cy1 = current_pos.y + (current_pos.y - py)

                # Control point 2 is explicitly given in the S command
                cx2, cy2 = abs_cmd.cx2, abs_cmd.cy2

                new_commands = [CubicBezier(cx1, cy1, cx2, cy2, x2, y2)]
                previous_control_point = (
                    cx2,
                    cy2,
                )  # Control point 2 for next potential S command

            elif isinstance(abs_cmd, Arc):
                # Convert Arc to multiple Cubic Beziers
                # Note: arc_to_beziers is assumed to be an existing function imported.
                beziers = arc_to_beziers(
                    current_pos.x,
                    current_pos.y,
                    abs_cmd.rx,
                    abs_cmd.ry,
                    abs_cmd.x_axis_rotation,
                    abs_cmd.large_arc_flag,
                    abs_cmd.sweep_flag,
                    abs_cmd.x,
                    abs_cmd.y,
                )
                new_commands = beziers  # This is a list of CubicBezier objects

                # Update control point to the last control point 2 of the final segment
                if beziers:
                    last_bezier = beziers[-1]
                    previous_control_point = (last_bezier.cx2, last_bezier.cy2)
                else:
                    # If arc is degenerate (0-length), use the end point as the control point
                    previous_control_point = abs_cmd.get_end_point(current_pos)

            elif isinstance(abs_cmd, ClosePath):
                # ClosePath stays as-is, reset control point tracker
                new_commands = [abs_cmd]
                previous_control_point = current_pos

            else:
                # Unknown command type - keep as-is
                new_commands = [abs_cmd]

            # 3. Add to normalized list and update current position
            normalized.extend(new_commands)
            # Update current_pos based on the last command that was executed (either the original
            # command or the last generated bezier segment).
            current_pos = (
                new_commands[-1].get_end_point(current_pos)
                if new_commands
                else current_pos
            )

        return SVGPath(normalized)

    # --- Interpolation and Normalization logic remains unchanged (but now relies on the new logic above) ---

    def normalize_for_morphing(self, other: "SVGPath") -> tuple["SVGPath", "SVGPath"]:
        """Normalize two paths to be compatible for morphing

        Steps:
        1. Convert both to absolute coordinates
        2. Convert all curves to cubic Beziers
        3. Ensure same number of commands (future: subdivide if needed)

        Args:
            other: Path to normalize with

        Returns:
            Tuple of (normalized_self, normalized_other)

        Raises:
            ValueError: If paths can't be made compatible
        """
        # Step 1: Convert to absolute coordinates
        abs_self = self.to_absolute()
        abs_other = other.to_absolute()

        # Step 2: Convert to cubic Beziers (This handles H, V, S, T, A commands now!)
        cubic_self = abs_self.to_cubic_beziers()
        cubic_other = abs_other.to_cubic_beziers()

        # Step 3: Check if compatible now
        if len(cubic_self.commands) != len(cubic_other.commands):
            raise ValueError(
                f"Paths have different number of commands after normalization. "
                f"Path 1: {len(cubic_self.commands)}, Path 2: {len(cubic_other.commands)}. "
                f"Cannot morph between paths with different structure."
            )

        # Verify all command types match
        for i, (cmd1, cmd2) in enumerate(
            zip(cubic_self.commands, cubic_other.commands)
        ):
            if type(cmd1) != type(cmd2):
                raise ValueError(
                    f"Command type mismatch at index {i}: "
                    f"{type(cmd1).__name__} vs {type(cmd2).__name__}"
                )

        return cubic_self, cubic_other

    @staticmethod
    def interpolate(
        path1: "SVGPath", path2: "SVGPath", t: float, auto_normalize: bool = True
    ) -> "SVGPath":
        """Interpolate between two paths with automatic normalization

        Args:
            path1: Starting path
            path2: Ending path
            t: Interpolation factor (0.0 to 1.0)
            auto_normalize: If True, automatically normalize paths for morphing

        Returns:
            Interpolated path at time t

        Raises:
            ValueError: If paths are incompatible and auto_normalize fails
        """

        """
        if auto_normalize:
            # NOTE: We are removing the external dependency on 'vood.paths.normalization'
            # and using the local normalize_for_morphing() method.
            try:
                norm_path1, norm_path2 = path1.normalize_for_morphing(path2)
            except ValueError as e:
                raise ValueError(f"Cannot normalize paths for morphing: {e}")
        else:
            norm_path1 = path1.to_absolute()
            norm_path2 = path2.to_absolute()

        # Verify compatibility
        if not norm_path1.is_compatible_for_morphing(norm_path2):
            raise ValueError(
                f"Paths are not compatible for morphing. "
                f"Path 1 has {len(norm_path1.commands)} commands, "
                f"Path 2 has {len(norm_path2.commands)} commands. "
                f"Command types must match."
            )

        # Interpolate each command
        interpolated_commands = []
        for cmd1, cmd2 in zip(norm_path1.commands, norm_path2.commands):
            interpolated_commands.append(cmd1.interpolate(cmd2, t))

        return SVGPath(interpolated_commands)
        """

        from vood.path.morphing import polymorph_interpolate

        return polymorph_interpolate(path1, path2, t)

    def __eq__(self, other: object) -> bool:
        """Check equality of two paths"""
        if not isinstance(other, SVGPath):
            return False
        return self.commands == other.commands
