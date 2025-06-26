#!/usr/bin/env python
"""
Script to run all tests in the project.
"""
import os
import sys
import subprocess

def run_tests():
    """
    Run all tests in the project.
    """
    # List of test modules to run
    test_modules = [
        'desafio_codeflix.tests.test_models',
        'desafio_codeflix.tests.test_videos',
        'desafio_codeflix.tests.test_auth',
    ]
    
    # Run each test module
    for module in test_modules:
        print(f"Running tests in {module}...")
        result = subprocess.run(['python', 'manage.py', 'test', module], check=False)
        if result.returncode != 0:
            print(f"Tests in {module} failed with exit code {result.returncode}")
            return result.returncode
    
    print("All tests passed!")
    return 0

if __name__ == '__main__':
    sys.exit(run_tests())