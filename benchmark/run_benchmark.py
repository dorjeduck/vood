"""Benchmark comparing all available PNG converters

This script renders the same scene N times using all available converters and provides
detailed performance metrics including CPU usage, memory, and timing.

Generates both console output and a markdown report file.
"""

import time
import psutil
import os
import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from vood.vscene import VScene
from vood.vscene.vscene_exporter import VSceneExporter, ConverterType
from vood.velement import VElement
from vood.component.state import CircleState, TextState
from vood.component.renderer import CircleRenderer, TextRenderer
from vood.core.color import Color
from vood.playwright_server.process_manager import ProcessManager


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run"""
    converter_name: str
    converter_type: ConverterType
    num_frames: int
    total_time: float
    avg_time_per_frame: float
    cpu_percent: float
    memory_mb: float
    process_user_time: float
    process_system_time: float
    total_cpu_time: float
    success: bool = True
    error: Optional[str] = None


def create_test_scene() -> VScene:
    """Create a simple but non-trivial test scene

    Returns a scene with multiple elements to ensure realistic rendering load.
    """
    scene = VScene(width=800, height=600, background=Color("#1a1a2e"))

    # Add some circles
    circle_renderer = CircleRenderer()
    colors = [Color("#FF6B6B"), Color("#4ECDC4"), Color("#45B7D1"), Color("#FFA07A")]

    for i, color in enumerate(colors):
        x = -250 + i * 166
        circle = CircleState(
            x=x, y=-100, radius=60,
            fill_color=color,
            stroke_color=Color("#FFFFFF"),
            stroke_width=3
        )
        scene.add_element(VElement(renderer=circle_renderer, state=circle))

    # Add text
    text_renderer = TextRenderer()
    text = TextState(
        x=0, y=150,
        text="Benchmark Test Scene",
        font_family="Arial",
        font_size=32,
        fill_color=Color("#FFFFFF")
    )
    scene.add_element(VElement(renderer=text_renderer, state=text))

    return scene


def benchmark_converter(
    converter_type: ConverterType,
    num_frames: int,
    output_dir: Path
) -> BenchmarkResult:
    """Benchmark a specific converter

    Args:
        converter_type: The converter to benchmark
        num_frames: Number of frames to render
        output_dir: Directory for output files

    Returns:
        BenchmarkResult with performance metrics (or error info if failed)
    """
    converter_name = converter_type.value
    print(f"\n{'='*60}")
    print(f"Benchmarking: {converter_name}")
    print(f"Frames: {num_frames}")
    print(f"{'='*60}")

    try:
        # Get process for monitoring
        process = psutil.Process(os.getpid())

        # Record initial state
        cpu_times_start = process.cpu_times()

        # Create scene once (reused for all frames)
        scene = create_test_scene()
        exporter = VSceneExporter(scene, converter=converter_type, output_dir=str(output_dir))

        # Start monitoring
        cpu_percent_samples = []
        memory_samples = []

        # Warm up (single render to initialize everything)
        print("Warming up...")
        exporter.export("warmup.png", formats=["png"])

        # Start benchmark
        print(f"Rendering {num_frames} frames...")
        start_time = time.time()

        for i in range(num_frames):
            # Monitor resources periodically
            if i % max(1, num_frames // 10) == 0:
                cpu_percent_samples.append(process.cpu_percent(interval=0))
                memory_samples.append(process.memory_info().rss / 1024 / 1024)  # MB
                progress = (i / num_frames) * 100
                print(f"  Progress: {progress:.1f}% ({i}/{num_frames} frames)", end='\r')

            # Render frame
            exporter.export(f"frame_{i:04d}.png", formats=["png"])

        end_time = time.time()

        # Final resource measurements
        cpu_times_end = process.cpu_times()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Calculate metrics
        total_time = end_time - start_time
        avg_time = total_time / num_frames
        user_time = cpu_times_end.user - cpu_times_start.user
        system_time = cpu_times_end.system - cpu_times_start.system
        total_cpu = user_time + system_time

        # Average CPU and memory
        avg_cpu = sum(cpu_percent_samples) / len(cpu_percent_samples) if cpu_percent_samples else 0
        avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else final_memory

        print(f"\n  Completed in {total_time:.2f}s")

        return BenchmarkResult(
            converter_name=converter_name,
            converter_type=converter_type,
            num_frames=num_frames,
            total_time=total_time,
            avg_time_per_frame=avg_time,
            cpu_percent=avg_cpu,
            memory_mb=avg_memory,
            process_user_time=user_time,
            process_system_time=system_time,
            total_cpu_time=total_cpu,
            success=True
        )

    except Exception as e:
        print(f"\n  ✗ Failed: {str(e)}")
        return BenchmarkResult(
            converter_name=converter_name,
            converter_type=converter_type,
            num_frames=num_frames,
            total_time=0,
            avg_time_per_frame=0,
            cpu_percent=0,
            memory_mb=0,
            process_user_time=0,
            process_system_time=0,
            total_cpu_time=0,
            success=False,
            error=str(e)
        )


def print_comparison(results: List[BenchmarkResult]):
    """Print detailed comparison of benchmark results"""

    print("\n" + "="*80)
    print("BENCHMARK RESULTS")
    print("="*80)

    # Filter successful results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    if not successful:
        print("\n✗ All converters failed!")
        for r in failed:
            print(f"  {r.converter_name}: {r.error}")
        return

    # Summary table
    print("\n" + "-"*100)
    header = f"{'Converter':<20} {'Total Time':>12} {'Per Frame':>12} {'CPU %':>10} {'CPU Time':>12} {'Memory':>12}"
    print(header)
    print("-"*100)

    for r in successful:
        print(f"{r.converter_name:<20} {r.total_time:>10.2f}s {r.avg_time_per_frame:>10.3f}s "
              f"{r.cpu_percent:>9.1f}% {r.total_cpu_time:>10.2f}s {r.memory_mb:>10.1f}MB")

    print("-"*100)

    # Failed converters
    if failed:
        print("\n" + "-"*100)
        print("FAILED CONVERTERS:")
        print("-"*100)
        for r in failed:
            print(f"  {r.converter_name}: {r.error}")
        print("-"*100)

    print("\n" + "="*80)


def generate_markdown_report(results: List[BenchmarkResult], output_file: str):
    """Generate markdown report from benchmark results

    Args:
        results: List of benchmark results
        output_file: Path to output markdown file
    """
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    with open(output_file, "w") as f:
        f.write("# Vood PNG Converter Benchmark Results\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Frames rendered:** {results[0].num_frames if results else 0}\n\n")

        if not successful:
            f.write("## ✗ All Converters Failed\n\n")
            for r in failed:
                f.write(f"- **{r.converter_name}**: {r.error}\n")
            return

        # Performance table
        f.write("## Performance Comparison\n\n")
        f.write("| Converter | Total Time | Per Frame | CPU % | CPU Time | Memory |\n")
        f.write("|-----------|------------|-----------|-------|----------|--------|\n")

        for r in successful:
            f.write(f"| {r.converter_name} | {r.total_time:.2f}s | {r.avg_time_per_frame:.3f}s | "
                   f"{r.cpu_percent:.1f}% | {r.total_cpu_time:.2f}s | {r.memory_mb:.1f}MB |\n")

        # Detailed metrics
        f.write("\n## Detailed Metrics\n\n")
        for r in successful:
            f.write(f"### {r.converter_name}\n\n")
            f.write(f"- **Total Time:** {r.total_time:.2f}s\n")
            f.write(f"- **Average Time per Frame:** {r.avg_time_per_frame:.3f}s\n")
            f.write(f"- **Process CPU Usage:** {r.cpu_percent:.1f}%\n")
            f.write(f"- **User CPU Time:** {r.process_user_time:.2f}s\n")
            f.write(f"- **System CPU Time:** {r.process_system_time:.2f}s\n")
            f.write(f"- **Total CPU Time:** {r.total_cpu_time:.2f}s\n")
            f.write(f"- **Memory Usage:** {r.memory_mb:.1f}MB\n\n")

        # Failed converters
        if failed:
            f.write("## Failed Converters\n\n")
            for r in failed:
                f.write(f"- **{r.converter_name}**: {r.error}\n")


def main():
    """Run the benchmark"""
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark all PNG converters")
    parser.add_argument(
        "-n", "--frames",
        type=int,
        default=50,
        help="Number of frames to render (default: 50)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep generated PNG files after benchmark"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="BENCHMARK_RESULTS.md",
        help="Output markdown file (default: BENCHMARK_RESULTS.md)"
    )

    args = parser.parse_args()

    # Create temporary directory for outputs
    temp_dir = Path(tempfile.mkdtemp(prefix="vood_benchmark_"))
    print(f"Output directory: {temp_dir}")

    # List of all converters to test
    converters = [
        ConverterType.CAIROSVG,
        ConverterType.INKSCAPE,
        ConverterType.PLAYWRIGHT,
        ConverterType.PLAYWRIGHT_HTTP,
    ]

    try:
        # Check if HTTP server is running for PLAYWRIGHT_HTTP, start it if not
        manager = ProcessManager()
        server_was_running = manager.is_running()

        if not server_was_running:
            print("\nStarting HTTP server for PLAYWRIGHT_HTTP benchmark...")
            try:
                manager.start()
                time.sleep(3)  # Wait for server to be ready
                print("Server started")
            except Exception as e:
                print(f"Failed to start server: {e}")
                print("PLAYWRIGHT_HTTP benchmark will be skipped")
                converters.remove(ConverterType.PLAYWRIGHT_HTTP)
        else:
            print("\nHTTP server already running")

        results = []

        # Benchmark each converter
        for converter_type in converters:
            converter_dir = temp_dir / converter_type.value.replace("_", "-")
            converter_dir.mkdir()

            result = benchmark_converter(
                converter_type,
                args.frames,
                converter_dir
            )
            results.append(result)

            # Short pause between benchmarks
            time.sleep(2)

        # Print comparison
        print_comparison(results)

        # Generate markdown report
        output_path = Path(args.output)
        generate_markdown_report(results, str(output_path))
        print(f"\n✓ Markdown report generated: {output_path}")

        # Stop server if we started it
        if not server_was_running and ConverterType.PLAYWRIGHT_HTTP in converters:
            print("\nStopping HTTP server...")
            manager.stop()

    finally:
        # Cleanup
        if not args.no_cleanup:
            import shutil
            print(f"\nCleaning up temporary files...")
            shutil.rmtree(temp_dir)
            print(f"Removed {temp_dir}")
        else:
            print(f"\nTemporary files kept in: {temp_dir}")


if __name__ == "__main__":
    main()
