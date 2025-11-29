"""Benchmark vertex interpolation performance

This script measures the performance impact of vertex interpolation optimizations,
specifically tracking Point2D allocations and frame generation speed.
"""

import time
import tracemalloc
from vood.vscene import VScene
from vood.velement import VElement
from vood.component import CircleState, SquareState
from vood.vscene.vscene_exporter import VSceneExporter
from vood.converter.converter_type import ConverterType
from vood.core.logger import configure_logging


def benchmark_animation(name: str, total_frames: int = 120):
    """Benchmark a simple morphing animation

    Args:
        name: Output filename
        total_frames: Number of frames to generate

    Returns:
        Dictionary with performance metrics
    """
    scene = VScene(width=400, height=400)

    # Create morphing shapes (circle to square)
    circle = CircleState(radius=60)
    square = SquareState(size=100)

    element = VElement(keystates=[circle, square])
    scene.add_elements([element])

    # Memory tracking
    tracemalloc.start()
    start_mem_current, start_mem_peak = tracemalloc.get_traced_memory()

    # Time tracking
    start_time = time.perf_counter()

    # Generate frames
    exporter = VSceneExporter(
        scene=scene,
        converter=ConverterType.PLAYWRIGHT,
        output_dir="output/"
    )
    exporter.to_mp4(
        filename=name,
        total_frames=total_frames,
        framerate=30,
        png_width_px=800
    )

    # Collect metrics
    end_time = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    total_time = end_time - start_time
    mem_delta = (peak_mem - start_mem_peak) / (1024 * 1024)  # MB

    return {
        "total_time": total_time,
        "peak_memory_mb": peak_mem / (1024 * 1024),
        "memory_delta_mb": mem_delta,
        "frames_per_second": total_frames / total_time if total_time > 0 else 0,
        "time_per_frame_ms": (total_time / total_frames * 1000) if total_frames > 0 else 0
    }


def main():
    """Run baseline benchmark"""
    configure_logging(level="INFO")

    print("=" * 60)
    print("VERTEX INTERPOLATION BENCHMARK - BASELINE")
    print("=" * 60)
    print()
    print("Test configuration:")
    print("  - Shape: Circle → Square morphing")
    print("  - Vertices: 128 per shape")
    print("  - Frames: 120 frames")
    print("  - Converter: Playwright")
    print()
    print("Running benchmark...")
    print()

    baseline = benchmark_animation("vertex_baseline_benchmark", total_frames=120)

    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total time:        {baseline['total_time']:.2f} seconds")
    print(f"Time per frame:    {baseline['time_per_frame_ms']:.1f} ms")
    print(f"Frames per second: {baseline['frames_per_second']:.1f} fps")
    print(f"Peak memory:       {baseline['peak_memory_mb']:.2f} MB")
    print(f"Memory delta:      {baseline['memory_delta_mb']:.2f} MB")
    print("=" * 60)
    print()
    print("Benchmark complete! Output saved to:")
    print("  output/vertex_baseline_benchmark.mp4")
    print()


if __name__ == "__main__":
    main()
