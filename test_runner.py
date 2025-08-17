#!/usr/bin/env python3
"""
Simple test runner script for YT-Tutor project.
Usage: python test_runner.py [--coverage]
"""

import sys
import subprocess
import argparse


def run_tests(with_coverage=False):
    """Run the test suite with optional coverage reporting"""
    
    if with_coverage:
        cmd = [
            "uv", "run", "pytest", "tests/", 
            "--cov=main", 
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v"
        ]
        print("Running tests with coverage...")
    else:
        cmd = ["uv", "run", "pytest", "tests/", "-v"]
        print("Running tests...")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ All tests passed!")
        
        if with_coverage:
            print("\n📊 Coverage report generated:")
            print("  - Terminal report displayed above")
            print("  - HTML report: htmlcov/index.html")
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("\n❌ Error: 'uv' command not found. Please install uv first.")
        print("Visit: https://docs.astral.sh/uv/getting-started/installation/")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run YT-Tutor tests")
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run tests with coverage reporting"
    )
    
    args = parser.parse_args()
    
    print("YT-Tutor Test Runner")
    print("=" * 50)
    
    return run_tests(with_coverage=args.coverage)


if __name__ == "__main__":
    sys.exit(main())