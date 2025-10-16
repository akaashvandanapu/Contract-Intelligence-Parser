#!/usr/bin/env python3
"""
Test runner for all project tests
"""

import os
import sys

import pytest


def run_all_tests():
    """Run all tests in the project"""
    print("🧪 Running Contract Intelligence Parser Tests")
    print("=" * 50)
    
    # Test categories
    test_categories = [
        ("Main System Tests", "test_main.py"),
        ("System Integration Tests", "test_system.py")
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category, test_file in test_categories:
        print(f"\n📋 {category}")
        print("-" * 30)
        
        if os.path.exists(test_file):
            try:
                # Run the specific test file
                result = pytest.main([test_file, "-v", "--tb=short"])
                
                if result == 0:
                    print(f"✅ {category} - PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {category} - FAILED")
                    failed_tests += 1
                    
            except Exception as e:
                print(f"❌ {category} - ERROR: {e}")
                failed_tests += 1
        else:
            print(f"⚠️  {category} - File not found: {test_file}")
            failed_tests += 1
        
        total_tests += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed_tests} test categories failed")
        return 1

def run_specific_tests(test_pattern):
    """Run specific tests matching a pattern"""
    print(f"🔍 Running tests matching: {test_pattern}")
    return pytest.main(["-k", test_pattern, "-v"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific tests
        pattern = sys.argv[1]
        exit_code = run_specific_tests(pattern)
    else:
        # Run all tests
        exit_code = run_all_tests()
    
    sys.exit(exit_code)
