"""
Test Runner for SOLID Architecture

Runs the test suite with proper configuration and reports results.
"""

import sys
import subprocess
from pathlib import Path


def run_tests(args=None):
    """
    Run pytest with configuration
    
    Args:
        args: Additional pytest arguments (list)
    """
    print("\n" + "="*60)
    print("SOLID ARCHITECTURE TEST SUITE")
    print("="*60 + "\n")
    
    # Base command
    cmd = ["pytest"]
    
    # Add arguments
    if args:
        cmd.extend(args)
    else:
        # Default: run all tests with coverage
        cmd.extend([
            "-v",              # Verbose
            "--tb=short",      # Short traceback
            "tests/"           # Test directory
        ])
    
    print(f"Running: {' '.join(cmd)}\n")
    
    # Run pytest
    result = subprocess.run(cmd)
    
    return result.returncode


def run_unit_tests():
    """Run only unit tests (fast)"""
    print("\n🧪 Running UNIT TESTS (fast, isolated)...\n")
    return run_tests(["-v", "-m", "unit", "tests/unit/"])


def run_integration_tests():
    """Run only integration tests"""
    print("\n🔗 Running INTEGRATION TESTS...\n")
    return run_tests(["-v", "-m", "integration", "tests/integration/"])


def run_quick_tests():
    """Run quick smoke tests"""
    print("\n⚡ Running QUICK SMOKE TESTS...\n")
    return run_tests([
        "-v",
        "--tb=line",
        "-x",  # Stop on first failure
        "-k", "test_init or test_health",  # Only run init/health tests
        "tests/"
    ])


def run_all_tests():
    """Run all tests"""
    print("\n🚀 Running ALL TESTS...\n")
    return run_tests(["-v", "tests/"])


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run SOLID architecture tests")
    parser.add_argument(
        "--mode",
        choices=["all", "unit", "integration", "quick"],
        default="all",
        help="Test mode to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    # Run selected tests
    if args.mode == "unit":
        exit_code = run_unit_tests()
    elif args.mode == "integration":
        exit_code = run_integration_tests()
    elif args.mode == "quick":
        exit_code = run_quick_tests()
    else:
        exit_code = run_all_tests()
    
    # Print summary
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60 + "\n")
    
    sys.exit(exit_code)

