from vood.path import SVGPath
from typing import Dict, Optional, Tuple, Any
import hashlib
import logging

from vood.transition.interpolation.morpher.base_morpher import BaseMorpher

logger = logging.getLogger(__name__)


def _hash_shape(shape_str: str) -> str:
    """Create hash of path string for caching"""
    return hashlib.md5(shape_str.encode()).hexdigest()


class FlubberMorpher(BaseMorpher):
    """
    Flubber-based shape interpolator with reference-counted caching.

    Uses the static 'for_paths' factory method to manage a global instance cache.
    Multiple calls to for_paths() with the same shapes return the same instance,
    and the instance is only cleaned up when all references call close().
    """

    # --- Global Class Attributes ---
    _morpher_cache: Dict[Tuple[str, str, str], "FlubberMorpher"] = {}
    _reference_counts: Dict[Tuple[str, str, str], int] = {}

    @classmethod
    def for_paths(
        cls, path1: SVGPath, path2: SVGPath, **kwargs: Any
    ) -> "FlubberMorpher":
        """
        Factory method that returns a cached morpher instance.

        Multiple calls with the same paths (and kwargs) return the same instance.
        Each call increments a reference count. Call close() when done to decrement.

        Args:
            path1: Start shape
            path2: End shape
            **kwargs: Options passed to FlubberNodeBridge (e.g., flubber_path)

        Returns:
            FlubberMorpher instance (possibly cached)
        """
        key1 = _hash_shape(path1.to_string())
        key2 = _hash_shape(path2.to_string())
        # Include kwargs in cache key to handle different options
        import json

        kwargs_key = json.dumps(kwargs, sort_keys=True) if kwargs else ""
        cache_key = (key1, key2, kwargs_key)

        # Check cache
        if cache_key not in cls._morpher_cache:
            # Cache miss: create new instance
            morpher = cls(path1, path2, cache_key=cache_key, **kwargs)
            cls._morpher_cache[cache_key] = morpher
            cls._reference_counts[cache_key] = 0

        # Increment reference count
        cls._reference_counts[cache_key] += 1

        return cls._morpher_cache[cache_key]

    def __init__(
        self,
        path1: SVGPath,
        path2: SVGPath,
        cache_key: Tuple[str, str, str],
        max_cache_size: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Constructor. Executes the expensive Node.js bridge initialization.

        Note: This should only be called via for_paths(), not directly.

        Args:
            path1: Start shape
            path2: End shape
            cache_key: Tuple used for cache lookup
            **kwargs: Options for FlubberNodeBridge
        """
        # Initialize base class (sets self.path1, self.path2, self._cache)
        super().__init__(path1, path2, **kwargs)

        # Store cache key for reference counting
        self._cache_key = cache_key
        self._is_closed = False

        from .flubber_node_bridge import FlubberNodeBridge

        # Initialize the Node.js process
        self._flubber_node_bridge = FlubberNodeBridge(
            self.path1.to_string(), self.path2.to_string(), **kwargs
        )

    def __call__(self, t: float) -> SVGPath:
        """
        Calculates the interpolated shape at t (0.0 to 1.0).

        Args:
            t: Interpolation factor

        Returns:
            Interpolated SVGPath

        Raises:
            RuntimeError: If morpher has been fully closed
        """
        if self._is_closed:
            raise RuntimeError(
                "Cannot interpolate: this morpher has been closed. "
                "All references have called close()."
            )

        def core_interpolation(t_val):
            shape_string = self._flubber_node_bridge.interpolate(t_val)
            return SVGPath.from_string(shape_string)

        return self._interpolate_with_caching(t, core_interpolation)

    def close(self):
        """
        Decrement reference count and cleanup if this is the last reference.

        Safe to call multiple times. Only closes the Node.js process when
        all references have called close().
        """
        # Skip if already fully closed
        if self._is_closed:
            return

        # Decrement reference count
        if self._cache_key in self._reference_counts:
            self._reference_counts[self._cache_key] -= 1

            # Only truly close when no references remain
            if self._reference_counts[self._cache_key] <= 0:
                self._actually_close()

    def _actually_close(self):
        """Internal method that performs the actual cleanup."""
        # Close the Node.js process
        if self._flubber_node_bridge:
            self._flubber_node_bridge.close()

        # Clear the t-value cache
        self._cache.clear()

        # Remove from global caches
        if self._cache_key in self._morpher_cache:
            del self._morpher_cache[self._cache_key]
        if self._cache_key in self._reference_counts:
            del self._reference_counts[self._cache_key]

        # Mark as closed
        self._is_closed = True

    @classmethod
    def cleanup(cls):
        """
        Force cleanup of all cached morphers regardless of reference counts.

        Use this for emergency cleanup or at application shutdown.
        Does not affect reference counts - resets everything.
        """
        for morpher in list(cls._morpher_cache.values()):
            if not morpher._is_closed:
                morpher._actually_close()

        cls._morpher_cache.clear()
        cls._reference_counts.clear()

    @classmethod
    def clear_cache(cls):
        """
        Alias for cleanup(). Clear all cached morphers.
        """
        cls.cleanup()

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support - calls close() on exit."""
        self.close()
        return False

    def __del__(self):
        """Destructor - ensure cleanup happens."""
        if not self._is_closed:
            self.close()

    @classmethod
    def cache_stats(cls) -> Dict[str, Any]:
        """
        Get statistics about the global morpher cache.

        Returns:
            Dict with cache size, active instances, total references
        """
        return {
            "cached_instances": len(cls._morpher_cache),
            "total_references": sum(cls._reference_counts.values()),
            "instances": [
                {
                    "cache_key": f"{key[0][:8]}...{key[1][:8]}",
                    "references": cls._reference_counts[key],
                    "t_cache_size": len(cls._morpher_cache[key]._cache),
                    "t_cache_stats": cls._morpher_cache[key].get_cache_stats(),
                }
                for key in cls._morpher_cache
            ],
        }
