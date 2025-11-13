from typing import List, Tuple, Union
import re

# Regex to match a command letter or a number (including signs, decimals, and exponents)
# This handles the complex, comma-less, space-optional SVG syntax like M100-20L10,30
COMMAND_OR_COORD_RE = re.compile(
    r"([MLHVZCQSTAmlhvzcqst])|((?:[-+]?)(?:[0-9]*\.)?[0-9]+(?:[eE][-+]?[0-9]+)?)"
)


def tokenize_path(path_string: str) -> List[str]:
    """
    Tokenizes an SVG path string into a list of command letters and coordinate values (as strings).

    This function is crucial for handling the compressed nature of SVG path data,
    where numbers and commands often run together without separators (e.g., M100-20L50).
    """
    # Use the regex to find all command letters and coordinate numbers
    tokens = COMMAND_OR_COORD_RE.findall(path_string.strip())

    # Flatten the list of tuples returned by findall
    # Each match is ('Command', '') or ('', 'Coordinate')
    result = []
    for cmd, coord in tokens:
        if cmd:
            result.append(cmd)
        elif coord:
            result.append(coord)

    return result


def parse_coordinates(
    tokens: List[str], num_args: int
) -> Tuple[List[float], List[str]]:
    """
    Extracts a specified number of coordinates from the beginning of a token list.

    Args:
        tokens: The remaining tokens in the path string.
        num_args: The number of coordinate values expected (e.g., 2 for L, 4 for Q, 6 for C).

    Returns:
        A tuple: ([parsed_floats], [remaining_tokens])

    Raises:
        ValueError: If not enough numeric tokens are found.
    """
    if len(tokens) < num_args:
        raise ValueError(
            f"Expected {num_args} coordinates but found only {len(tokens)}"
        )

    coords = []
    remaining_tokens = tokens[:]

    for _ in range(num_args):
        try:
            # We assume the tokens are already clean strings representing numbers
            coords.append(float(remaining_tokens.pop(0)))
        except (IndexError, ValueError):
            # If the token is not a number, or the list runs out, something is wrong
            raise ValueError(
                f"Invalid path data: Expected numeric coordinate, got '{remaining_tokens[0] if remaining_tokens else 'END'}'"
            )

    return coords, remaining_tokens
