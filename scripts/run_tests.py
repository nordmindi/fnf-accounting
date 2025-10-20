#!/usr/bin/env python3
"""Test runner script for comprehensive testing."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified options."""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    cmd.append("tests/")
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.append("--cov=src")
        cmd.append("--cov-report=html")
        cmd.append("--cov-report=term")
    
    # Filter by test type
    if test_type == "unit":
        cmd.extend(["tests/test_natural_language_service.py", "tests/test_policy_engine.py"])
    elif test_type == "integration":
        cmd.extend(["tests/test_integration.py"])
    elif test_type == "all":
        pass  # Run all tests
    else:
        print(f"Unknown test type: {test_type}")
        return False
    
    # Add additional options
    cmd.extend([
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "--disable-warnings",  # Disable warnings for cleaner output
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    return result.returncode == 0


def run_specific_scenario(scenario_name):
    """Run tests for a specific scenario."""
    
    scenarios = {
        "representation_meal": "tests/test_natural_language_service.py::TestNaturalLanguageService::test_representation_meal_processing",
        "saas_reverse_charge": "tests/test_natural_language_service.py::TestNaturalLanguageService::test_saas_reverse_charge_processing",
        "mobile_phone": "tests/test_natural_language_service.py::TestNaturalLanguageService::test_mobile_phone_installment_processing",
        "fallback": "tests/test_natural_language_service.py::TestNaturalLanguageService::test_fallback_intent_detection",
        "policy_engine": "tests/test_policy_engine.py::TestRuleEngine::test_policy_application",
        "migration": "tests/test_policy_engine.py::TestPolicyMigration::test_policy_migration_different_version",
        "integration": "tests/test_integration.py::TestEndToEndScenarios::test_representation_meal_complete_flow"
    }
    
    if scenario_name not in scenarios:
        print(f"Unknown scenario: {scenario_name}")
        print(f"Available scenarios: {', '.join(scenarios.keys())}")
        return False
    
    cmd = ["python", "-m", "pytest", "-v", scenarios[scenario_name]]
    
    print(f"Running scenario: {scenario_name}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def run_performance_tests():
    """Run performance tests."""
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_integration.py::TestEndToEndScenarios::test_multiple_scenarios_consistency",
        "-v",
        "--durations=10"  # Show 10 slowest tests
    ]
    
    print("Running performance tests...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def run_lint_tests():
    """Run linting tests."""
    cmd = [
        "python", "-m", "pytest",
        "tests/",
        "--flake8",
        "--mypy",
        "-v"
    ]
    
    print("Running linting tests...")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for Fire & Forget Accounting")
    
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration"], 
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--scenario",
        help="Run specific scenario test"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance tests"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting tests"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    success = True
    
    if args.scenario:
        success = run_specific_scenario(args.scenario)
    elif args.performance:
        success = run_performance_tests()
    elif args.lint:
        success = run_lint_tests()
    else:
        success = run_tests(args.type, args.verbose, args.coverage)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
