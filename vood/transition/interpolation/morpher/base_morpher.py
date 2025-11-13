import abc
from vood.path.svg_path import SVGPath
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseMorpher(abc.ABC):
    """
    Abstract Base Class (ABC) for all shape interpolators.

    A specific interpolator instance is responsible for the morph
    between two specific shapes. Includes built-in LRU caching for
    interpolation results at different t values.

    Args:
        path1: Start shape
        path2: End shape
        max_cache_size: Maximum number of t-values to cache (None = unlimited)
        **kwargs: Additional arguments for specific morpher implementations
    """

    def __init__(
        self,
        path1: SVGPath,
        path2: SVGPath,
        max_cache_size: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize the interpolator with the start and end shapes,
        and set up the shared t-value cache.
        """
        self.path1 = path1
        self.path2 = path2
        self._cache: Dict[float, SVGPath] = {}
        self._max_cache_size = max_cache_size
        self._cache_order: List[float] = []  # Track access order for LRU
        self._cache_hits = 0
        self._cache_misses = 0

    @abc.abstractmethod
    def __call__(self, t: float) -> SVGPath:
        """
        Calculates the interpolated shape at factor t (0.0 to 1.0).
        This method should handle t-value caching internally.

        Args:
            t: Interpolation factor between 0.0 and 1.0

        Returns:
            Interpolated SVGPath at position t
        """
        pass

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support - calls close() on exit."""
        self.close()
        return False

    @abc.abstractmethod
    def close(self):
        """
        Cleans up any long-lived resources (e.g., caches, subprocesses).
        Subclasses should call super().close() to clear the t-value cache.
        """
        self._cache.clear()
        self._cache_order.clear()

    def _interpolate_with_caching(self, t: float, core_interpolation_func) -> SVGPath:
        """
        Helper to manage the t-value cache with LRU eviction.

        Args:
            t: Interpolation factor
            core_interpolation_func: Function that computes interpolation for t

        Returns:
            Cached or newly computed SVGPath
        """
        # Validate input
        if not isinstance(t, (int, float)):
            raise TypeError(f"t must be a number, got {type(t).__name__}")

        # Warn if out of typical range (but don't error - might be intentional)
        if not 0.0 <= t <= 1.0:
            logger.debug(f"t={t} is outside typical [0.0, 1.0] range")

        # Check cache
        if t in self._cache:
            self._cache_hits += 1
            logger.debug(f"Cache hit for t={t}")

            # Move to end (most recently used)
            self._cache_order.remove(t)
            self._cache_order.append(t)

            return self._cache[t]

        # Cache miss - compute result
        self._cache_misses += 1
        logger.debug(f"Cache miss for t={t}, computing...")

        # Enforce cache size limit (LRU eviction)
        if self._max_cache_size is not None:
            while len(self._cache) >= self._max_cache_size:
                if self._cache_order:
                    # Evict least recently used
                    oldest = self._cache_order.pop(0)
                    if oldest in self._cache:
                        del self._cache[oldest]
                        logger.debug(f"Evicted t={oldest} from cache (LRU)")
                else:
                    break

        # Compute and cache result
        result = core_interpolation_func(t)
        self._cache[t] = result
        self._cache_order.append(t)

        return result

    def clear_cache(self):
        """
        Clear the t-value interpolation cache.
        Useful for freeing memory without closing the morpher.
        """
        self._cache.clear()
        self._cache_order.clear()
        logger.debug("Cleared t-value cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the t-value cache performance.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "max_size": self._max_cache_size,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cached_t_values": (
                sorted(self._cache.keys()) if len(self._cache) < 20 else None
            ),
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"cache_size={len(self._cache)}, "
            f"max_cache_size={self._max_cache_size})"
        )
