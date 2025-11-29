#!/usr/bin/env python3
"""
Comprehensive test runner script for Vood project.

Usage:
    python run_tests.py                    # Run all fast tests
    python run_tests.py --all              # Run all tests including slow
    python run_tests.py --slow             # Run only slow tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --coverage         # Run with detailed coverage report
    python run_tests.py --benchmark        # Run performance benchmarks
    python run_tests.py --quick            # Quick test run (no coverage)
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*70}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*70}\n")

    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run Vood tests")
    parser.add_argument("--all", action="store_true", help="Run all tests including slow")
    parser.add_argument("--slow", action="store_true", help="Run only slow tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmarks")
    parser.add_argument("--coverage", action="store_true", help="Generate detailed coverage report")
    parser.add_argument("--quick", action="store_true", help="Quick run without coverage")
    parser.add_argument("--parallel", "-n", type=int, help="Run tests in parallel (number of workers)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--failfast", "-x", action="store_true", help="Stop on first failure")

    args = parser.parse_args()

    # Base pytest command
    base_cmd = ["pytest"]

    # Add verbosity
    if args.verbose:
        base_cmd.append("-vv")
    else:
        base_cmd.append("-v")

    # Add fail-fast
    if args.failfast:
        base_cmd.append("-x")

    # Add parallel execution
    if args.parallel:
        base_cmd.extend(["-n", str(args.parallel)])

    # Determine test selection
    test_paths = []
    markers = []

    if args.benchmark:
        # Run benchmarks
        test_paths.append("tests/benchmark")
        base_cmd.append("--benchmark-only")
        return run_command(base_cmd + test_paths, "Performance Benchmarks")

    if args.slow:
        # Run only slow tests
        test_paths.append("tests")
        markers.append("-m")
        markers.append("slow")
        description = "Slow Tests Only"
    elif args.unit:
        test_paths.append("tests/unit")
        description = "Unit Tests"
    elif args.integration:
        test_paths.append("tests/integration")
        description = "Integration Tests"
    else:
        test_paths.append("tests")
        description = "All Tests"

    # Handle markers for slow tests
    # Only exclude slow tests when running all tests without --all flag
    # When explicitly running --unit or --integration, include all tests in that category
    if not args.all and not args.unit and not args.integration and not args.slow:
        markers.append("-m")
        markers.append("not slow")

    # Coverage settings
    if args.quick:
        # No coverage for quick runs
        coverage_args = []
    elif args.coverage:
        # Detailed coverage
        coverage_args = [
            "--cov=vood",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-report=xml",
        ]
    else:
        # Standard coverage
        coverage_args = [
            "--cov=vood",
            "--cov-report=term-missing:skip-covered",
        ]

    # Combine all arguments
    full_cmd = base_cmd + test_paths + markers + coverage_args

    # Run tests
    returncode = run_command(full_cmd, description)

    # Print coverage summary if generated
    if args.coverage and returncode == 0:
        print(f"\n{'='*70}")
        print("Coverage report generated:")
        print("  - Terminal: See output above")
        print("  - HTML: Open htmlcov/index.html in browser")
        print("  - XML: coverage.xml (for CI/CD)")
        print(f"{'='*70}\n")

    return returncode


if __name__ == "__main__":
    sys.exit(main())
