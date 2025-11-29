from typing import Any
from vood.path.svg_path import SVGPath
from .base_morpher import BaseMorpher  # Assumed parent class location


class NativeMorpher(BaseMorpher):
    """
    Native path morpher using Python for interpolation, inheriting shared
    caching and initialization from BaseInterpolator.
    """

    @classmethod
    def for_paths(
        cls, path1: SVGPath, path2: SVGPath, **kwargs: Any
    ) -> "NativeMorpher":
        """
        Factory method implementation: simply constructs a new instance
        as there is no instance-level caching required.
        """
        # No caching logic needed, so just call the constructor
        return cls(path1, path2, **kwargs)

    def __init__(self, path1: SVGPath, path2: SVGPath, **kwargs):
        # Initializes self.path1, self.path2, and self._cache
        super().__init__(path1, path2, **kwargs)

    def __call__(self, t: float) -> SVGPath:
        """
        Calculates the interpolated shape at t, utilizing the BaseInterpolator's
        t-value cache helper.
        """

        # 1. Define the unique core logic for native interpolation
        def core_interpolation(t_val):
            return SVGPath.interpolate(self.path1, self.path2, t_val)

        # 2. Use the shared caching logic from the parent class
        return self._interpolate_with_caching(t, core_interpolation)

    def close(self):
        """Clears the result cache via the parent class."""
        # BaseInterpolator.close() will handle self._cache.clear()
        super().close()
