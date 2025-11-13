import math


def make_cosine_radius_fn(element_per_cycle=8, amplitude=20, start_num=0):
    """
    Factory for a cosine oscillation radius function for circle layouts.

    Args:
        element_per_cycle: Number of elements per full cosine cycle
        amplitude: Amplitude of the cosine wave (added/subtracted from default radius)^
        start_num: Starting index in the cycle

    Returns:
        radius_fn(index, default_radius): function for use in circle layouts
    """

    def radius_fn(index, default_radius):
        cycle_pos = (index + start_num) % element_per_cycle
        return default_radius + amplitude * math.cos(
            2 * math.pi * cycle_pos / element_per_cycle
        )

    return radius_fn
