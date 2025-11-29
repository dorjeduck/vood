"""Focused benchmark for vertex interpolation only (no rendering)

This benchmark isolates just the vertex interpolation performance without
the overhead of rendering, rasterization, and video encoding.
"""

import time
import tracemalloc
from vood.velement import VElement
from vood.component import CircleState, SquareState


def benchmark_interpolation_only(total_frames: int = 120):
    """Benchmark just the interpolation step

    Args:
        total_frames: Number of frames to interpolate

    Returns:
        Dictionary with performance metrics
    """
    # Create morphing element
    circle = CircleState(radius=60)
    square = SquareState(size=100)
    element = VElement(keystates=[circle, square])

    # Memory tracking
    tracemalloc.start()
    start_mem_current, start_mem_peak = tracemalloc.get_traced_memory()

    # Time tracking
    start_time = time.perf_counter()

    # Interpolate frames (no rendering)
    for i in range(total_frames):
        t = i / (total_frames - 1) if total_frames > 1 else 0
        _ = element._get_state_at_time(t)

    # Collect metrics
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()

    # Get allocation stats
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    tracemalloc.stop()

    total_time = end_time - start_time
    mem_delta = (peak_mem - start_mem_peak) / (1024 * 1024)  # MB

    # Find Point2D allocations
    point2d_allocs = sum(
        stat.count for stat in top_stats
        if 'point2d' in stat.traceback.format()[0].lower()
    )

    return {
        "total_time": total_time,
        "peak_memory_mb": peak_mem / (1024 * 1024),
        "memory_delta_mb": mem_delta,
        "frames_per_second": total_frames / total_time if total_time > 0 else 0,
        "time_per_frame_ms": (total_time / total_frames * 1000) if total_frames > 0 else 0,
        "point2d_allocations": point2d_allocs,
        "total_allocations": sum(stat.count for stat in top_stats[:10]),
    }


def main():
    """Run focused interpolation benchmark"""

    print("=" * 70)
    print("VERTEX INTERPOLATION BENCHMARK - INTERPOLATION ONLY (NO RENDERING)")
    print("=" * 70)
    print()
    print("Test configuration:")
    print("  - Shape: Circle → Square morphing")
    print("  - Vertices: 128 per shape")
    print("  - Frames: 1000 interpolations")
    print("  - Measured: Interpolation only (no rendering/rasterization)")
    print()
    print("Running benchmark...")
    print()

    result = benchmark_interpolation_only(total_frames=1000)

    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Total time:          {result['total_time']:.4f} seconds")
    print(f"Time per frame:      {result['time_per_frame_ms']:.3f} ms")
    print(f"Frames per second:   {result['frames_per_second']:.1f} fps")
    print(f"Peak memory:         {result['peak_memory_mb']:.2f} MB")
    print(f"Memory delta:        {result['memory_delta_mb']:.2f} MB")
    print(f"Point2D allocations: {result['point2d_allocations']}")
    print(f"Total allocations:   {result['total_allocations']}")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
