#!/usr/bin/env python3
"""
Test Runner - Main entry point for running screenshot bug detection tests
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

from screenshot_bug_detector import ScreenshotBugDetector
from sudoku_test_automation import SudokuTestAutomation


class TestRunner:
    """Main test runner for coordinating different types of tests."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the test runner with configuration."""
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            print(f"Warning: Config file {self.config_path} not found. Using defaults.")
            return {}
    
    def run_visual_regression_test(self, url: str, test_name: str = None) -> str:
        """Run visual regression testing."""
        print(f"🔍 Running visual regression test for: {url}")
        
        detector = ScreenshotBugDetector(self.config)
        
        try:
            test_result = detector.run_comprehensive_test(url, test_name)
            report_path = detector.generate_bug_report(test_result['results'])
            
            print(f"✅ Visual regression test completed")
            print(f"📄 Report saved to: {report_path}")
            
            return report_path
            
        finally:
            detector.cleanup()
    
    def run_sudoku_tests(self, url: str = None) -> str:
        """Run Sudoku-specific tests."""
        if not url:
            url = self.config.get('test_scenarios', {}).get('sudoku_game', {}).get('url', 'http://localhost:8000')
        
        print(f"🎯 Running Sudoku game tests for: {url}")
        
        automation = SudokuTestAutomation(url, self.config)
        
        try:
            test_results = automation.run_all_tests()
            report_path = automation.detector.generate_bug_report(test_results)
            
            print(f"✅ Sudoku tests completed")
            print(f"📄 Report saved to: {report_path}")
            
            return report_path
            
        finally:
            automation.cleanup()
    
    def create_reference_images(self, url: str, test_name: str = None) -> str:
        """Create reference images for future comparisons."""
        print(f"📸 Creating reference images for: {url}")
        
        detector = ScreenshotBugDetector(self.config)
        
        try:
            detector.create_reference_images(url, test_name)
            print(f"✅ Reference images created successfully")
            return "Reference images created"
            
        finally:
            detector.cleanup()
    
    def run_custom_test(self, test_type: str, **kwargs) -> str:
        """Run custom test based on type."""
        if test_type == "visual_regression":
            return self.run_visual_regression_test(
                kwargs.get('url'),
                kwargs.get('test_name')
            )
        elif test_type == "sudoku":
            return self.run_sudoku_tests(kwargs.get('url'))
        elif test_type == "create_reference":
            return self.create_reference_images(
                kwargs.get('url'),
                kwargs.get('test_name')
            )
        else:
            raise ValueError(f"Unknown test type: {test_type}")
    
    def run_all_tests(self, url: str = None) -> list:
        """Run all available tests."""
        if not url:
            url = self.config.get('test_scenarios', {}).get('sudoku_game', {}).get('url', 'http://localhost:8000')
        
        print(f"🚀 Running all tests for: {url}")
        
        results = []
        
        # Run visual regression tests
        try:
            visual_report = self.run_visual_regression_test(url, "comprehensive_visual_test")
            results.append(("Visual Regression", visual_report))
        except Exception as e:
            print(f"❌ Visual regression test failed: {e}")
            results.append(("Visual Regression", f"Failed: {e}"))
        
        # Run Sudoku-specific tests
        try:
            sudoku_report = self.run_sudoku_tests(url)
            results.append(("Sudoku Tests", sudoku_report))
        except Exception as e:
            print(f"❌ Sudoku tests failed: {e}")
            results.append(("Sudoku Tests", f"Failed: {e}"))
        
        return results


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Screenshot Bug Detection Test Runner')
    parser.add_argument('--config', default='config.json', help='Path to configuration file')
    parser.add_argument('--url', help='URL to test')
    parser.add_argument('--test-type', choices=[
        'visual_regression', 'sudoku', 'create_reference', 'all'
    ], default='all', help='Type of test to run')
    parser.add_argument('--test-name', help='Name for the test')
    parser.add_argument('--output-dir', help='Output directory for reports')
    
    args = parser.parse_args()
    
    # Override config if output directory is specified
    if args.output_dir:
        config = {}
        if os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = json.load(f)
        config['reports_dir'] = args.output_dir
        with open('temp_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        args.config = 'temp_config.json'
    
    runner = TestRunner(args.config)
    
    try:
        if args.test_type == 'all':
            results = runner.run_all_tests(args.url)
            print(f"\n🎉 All tests completed!")
            print(f"📊 Results:")
            for test_name, result in results:
                print(f"  • {test_name}: {result}")
        else:
            result = runner.run_custom_test(
                args.test_type,
                url=args.url,
                test_name=args.test_name
            )
            print(f"\n🎉 Test completed: {result}")
    
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
    
    finally:
        # Clean up temporary config file
        if args.output_dir and os.path.exists('temp_config.json'):
            os.remove('temp_config.json')


if __name__ == "__main__":
    main()