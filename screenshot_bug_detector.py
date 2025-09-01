#!/usr/bin/env python3
"""
Screenshot Bug Detection Tool
A comprehensive tool for capturing screenshots, comparing them with reference images,
and generating detailed bug reports for web applications.
"""

import os
import time
import json
import base64
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import matplotlib.pyplot as plt
from jinja2 import Template


class ScreenshotBugDetector:
    """Main class for screenshot capture, comparison, and bug detection."""
    
    def __init__(self, config: Dict = None):
        """Initialize the bug detector with configuration."""
        self.config = config or self._default_config()
        self.driver = None
        self.screenshots_dir = Path(self.config['screenshots_dir'])
        self.reference_dir = Path(self.config['reference_dir'])
        self.reports_dir = Path(self.config['reports_dir'])
        self._setup_directories()
        
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'screenshots_dir': 'screenshots',
            'reference_dir': 'reference_images',
            'reports_dir': 'bug_reports',
            'threshold': 0.95,  # Image similarity threshold
            'viewport_sizes': [
                {'width': 1920, 'height': 1080, 'name': 'desktop'},
                {'width': 1366, 'height': 768, 'name': 'laptop'},
                {'width': 768, 'height': 1024, 'name': 'tablet'},
                {'width': 375, 'height': 667, 'name': 'mobile'}
            ],
            'wait_timeout': 10,
            'screenshot_delay': 2
        }
    
    def _setup_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.screenshots_dir, self.reference_dir, self.reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def setup_driver(self) -> webdriver.Chrome:
        """Setup and return a Chrome WebDriver instance."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        return self.driver
    
    def capture_screenshot(self, url: str, filename: str = None, 
                          viewport: Dict = None) -> str:
        """Capture a screenshot of the given URL."""
        if not self.driver:
            self.setup_driver()
        
        # Set viewport size if specified
        if viewport:
            self.driver.set_window_size(viewport['width'], viewport['height'])
        
        try:
            self.driver.get(url)
            time.sleep(self.config['screenshot_delay'])
            
            # Wait for page to load
            WebDriverWait(self.driver, self.config['wait_timeout']).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                viewport_name = viewport['name'] if viewport else 'default'
                filename = f"screenshot_{viewport_name}_{timestamp}.png"
            
            screenshot_path = self.screenshots_dir / filename
            
            # Take screenshot
            self.driver.save_screenshot(str(screenshot_path))
            
            print(f"Screenshot captured: {screenshot_path}")
            return str(screenshot_path)
            
        except TimeoutException:
            print(f"Timeout waiting for page to load: {url}")
            return None
        except WebDriverException as e:
            print(f"WebDriver error: {e}")
            return None
    
    def compare_images(self, image1_path: str, image2_path: str) -> Dict:
        """Compare two images and return similarity metrics and differences."""
        try:
            # Load images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                return {'error': 'Could not load one or both images'}
            
            # Resize images to same dimensions if needed
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale for comparison
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            from skimage.metrics import structural_similarity as ssim
            similarity = ssim(gray1, gray2)
            
            # Calculate difference
            diff = cv2.absdiff(gray1, gray2)
            diff_percentage = (np.sum(diff > 0) / diff.size) * 100
            
            # Find contours of differences
            thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Create difference visualization
            diff_visual = img1.copy()
            cv2.drawContours(diff_visual, contours, -1, (0, 0, 255), 2)
            
            return {
                'similarity': similarity,
                'difference_percentage': diff_percentage,
                'contours_count': len(contours),
                'is_similar': similarity >= self.config['threshold'],
                'difference_visualization': diff_visual,
                'contours': contours
            }
            
        except Exception as e:
            return {'error': f'Image comparison failed: {str(e)}'}
    
    def detect_visual_bugs(self, current_screenshot: str, reference_screenshot: str) -> Dict:
        """Detect visual bugs by comparing current screenshot with reference."""
        comparison_result = self.compare_images(current_screenshot, reference_screenshot)
        
        if 'error' in comparison_result:
            return comparison_result
        
        bugs = []
        
        # Check for significant differences
        if not comparison_result['is_similar']:
            bug = {
                'type': 'visual_difference',
                'severity': 'high' if comparison_result['similarity'] < 0.8 else 'medium',
                'description': f"Visual difference detected. Similarity: {comparison_result['similarity']:.2f}",
                'difference_percentage': comparison_result['difference_percentage'],
                'contours_count': comparison_result['contours_count']
            }
            bugs.append(bug)
        
        # Check for layout issues
        if comparison_result['contours_count'] > 10:
            bug = {
                'type': 'layout_issue',
                'severity': 'medium',
                'description': f"Multiple layout differences detected ({comparison_result['contours_count']} areas)",
                'difference_percentage': comparison_result['difference_percentage']
            }
            bugs.append(bug)
        
        return {
            'bugs_found': len(bugs) > 0,
            'bugs': bugs,
            'comparison_metrics': comparison_result
        }
    
    def generate_bug_report(self, test_results: List[Dict], output_file: str = None) -> str:
        """Generate a comprehensive bug report."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"bug_report_{timestamp}.html"
        
        report_path = self.reports_dir / output_file
        
        # Prepare report data
        total_tests = len(test_results)
        total_bugs = sum(len(result.get('bugs', [])) for result in test_results)
        failed_tests = sum(1 for result in test_results if result.get('bugs_found', False))
        
        report_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_tests': total_tests,
            'total_bugs': total_bugs,
            'failed_tests': failed_tests,
            'success_rate': ((total_tests - failed_tests) / total_tests * 100) if total_tests > 0 else 0,
            'test_results': test_results
        }
        
        # Generate HTML report
        html_template = self._get_html_template()
        template = Template(html_template)
        html_content = template.render(**report_data)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Bug report generated: {report_path}")
        return str(report_path)
    
    def _get_html_template(self) -> str:
        """Return HTML template for bug report."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bug Report - {{ timestamp }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #e0e0e0; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }
        .summary-card.error { border-left-color: #dc3545; }
        .summary-card.warning { border-left-color: #ffc107; }
        .summary-card.success { border-left-color: #28a745; }
        .test-result { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .test-result.failed { border-color: #dc3545; background-color: #fff5f5; }
        .test-result.passed { border-color: #28a745; background-color: #f8fff8; }
        .bug-item { background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #ffc107; }
        .bug-item.high { background: #f8d7da; border-left-color: #dc3545; }
        .bug-item.medium { background: #fff3cd; border-left-color: #ffc107; }
        .bug-item.low { background: #d1ecf1; border-left-color: #17a2b8; }
        .screenshot { max-width: 100%; height: auto; border: 1px solid #ddd; margin: 10px 0; }
        .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0; }
        .metric { background: #e9ecef; padding: 10px; border-radius: 5px; text-align: center; }
        h1 { color: #333; }
        h2 { color: #555; margin-top: 0; }
        h3 { color: #666; }
        .severity-high { color: #dc3545; font-weight: bold; }
        .severity-medium { color: #ffc107; font-weight: bold; }
        .severity-low { color: #17a2b8; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐛 Bug Detection Report</h1>
            <p>Generated on: {{ timestamp }}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Tests</h3>
                <h2>{{ total_tests }}</h2>
            </div>
            <div class="summary-card {% if failed_tests > 0 %}error{% else %}success{% endif %}">
                <h3>Failed Tests</h3>
                <h2>{{ failed_tests }}</h2>
            </div>
            <div class="summary-card {% if total_bugs > 0 %}warning{% else %}success{% endif %}">
                <h3>Total Bugs</h3>
                <h2>{{ total_bugs }}</h2>
            </div>
            <div class="summary-card {% if success_rate >= 90 %}success{% elif success_rate >= 70 %}warning{% else %}error{% endif %}">
                <h3>Success Rate</h3>
                <h2>{{ "%.1f"|format(success_rate) }}%</h2>
            </div>
        </div>
        
        {% for result in test_results %}
        <div class="test-result {% if result.bugs_found %}failed{% else %}passed{% endif %}">
            <h2>Test: {{ result.test_name }}</h2>
            <p><strong>URL:</strong> {{ result.url }}</p>
            <p><strong>Viewport:</strong> {{ result.viewport }}</p>
            <p><strong>Status:</strong> 
                <span class="{% if result.bugs_found %}severity-high{% else %}severity-low{% endif %}">
                    {% if result.bugs_found %}❌ FAILED{% else %}✅ PASSED{% endif %}
                </span>
            </p>
            
            {% if result.comparison_metrics %}
            <div class="metrics">
                <div class="metric">
                    <strong>Similarity</strong><br>
                    {{ "%.2f"|format(result.comparison_metrics.similarity) }}
                </div>
                <div class="metric">
                    <strong>Difference %</strong><br>
                    {{ "%.1f"|format(result.comparison_metrics.difference_percentage) }}%
                </div>
                <div class="metric">
                    <strong>Contours</strong><br>
                    {{ result.comparison_metrics.contours_count }}
                </div>
            </div>
            {% endif %}
            
            {% if result.screenshots %}
            <div>
                <h3>Screenshots</h3>
                {% for screenshot in result.screenshots %}
                <div>
                    <h4>{{ screenshot.name }}</h4>
                    <img src="{{ screenshot.path }}" alt="{{ screenshot.name }}" class="screenshot">
                </div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if result.bugs %}
            <div>
                <h3>Bugs Found ({{ result.bugs|length }})</h3>
                {% for bug in result.bugs %}
                <div class="bug-item {{ bug.severity }}">
                    <h4 class="severity-{{ bug.severity }}">{{ bug.type|title }} - {{ bug.severity|upper }}</h4>
                    <p>{{ bug.description }}</p>
                    {% if bug.difference_percentage %}
                    <p><strong>Difference:</strong> {{ "%.1f"|format(bug.difference_percentage) }}%</p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
        """
    
    def run_comprehensive_test(self, url: str, test_name: str = None) -> Dict:
        """Run comprehensive visual testing across different viewports."""
        if not test_name:
            test_name = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        test_results = []
        
        for viewport in self.config['viewport_sizes']:
            print(f"Testing viewport: {viewport['name']} ({viewport['width']}x{viewport['height']})")
            
            # Capture current screenshot
            current_screenshot = self.capture_screenshot(
                url, 
                f"{test_name}_{viewport['name']}_current.png",
                viewport
            )
            
            if not current_screenshot:
                continue
            
            # Look for reference screenshot
            reference_screenshot = self.reference_dir / f"{test_name}_{viewport['name']}_reference.png"
            
            test_result = {
                'test_name': f"{test_name}_{viewport['name']}",
                'url': url,
                'viewport': f"{viewport['width']}x{viewport['height']} ({viewport['name']})",
                'current_screenshot': current_screenshot,
                'reference_screenshot': str(reference_screenshot) if reference_screenshot.exists() else None,
                'bugs_found': False,
                'bugs': [],
                'comparison_metrics': None
            }
            
            # Compare with reference if it exists
            if reference_screenshot.exists():
                bug_detection = self.detect_visual_bugs(current_screenshot, str(reference_screenshot))
                test_result.update(bug_detection)
                
                # Save difference visualization if bugs found
                if bug_detection.get('bugs_found') and 'comparison_metrics' in bug_detection:
                    diff_path = self.screenshots_dir / f"{test_name}_{viewport['name']}_diff.png"
                    cv2.imwrite(str(diff_path), bug_detection['comparison_metrics']['difference_visualization'])
                    test_result['difference_visualization'] = str(diff_path)
            else:
                print(f"No reference image found for {viewport['name']}. Consider creating one.")
                test_result['bugs'] = [{
                    'type': 'missing_reference',
                    'severity': 'low',
                    'description': 'No reference image available for comparison'
                }]
            
            test_results.append(test_result)
        
        return {
            'test_name': test_name,
            'url': url,
            'results': test_results
        }
    
    def create_reference_images(self, url: str, test_name: str = None):
        """Create reference images for future comparisons."""
        if not test_name:
            test_name = f"reference_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"Creating reference images for: {url}")
        
        for viewport in self.config['viewport_sizes']:
            reference_path = self.reference_dir / f"{test_name}_{viewport['name']}_reference.png"
            
            screenshot = self.capture_screenshot(
                url,
                f"{test_name}_{viewport['name']}_reference.png",
                viewport
            )
            
            if screenshot:
                # Move to reference directory
                import shutil
                shutil.move(screenshot, reference_path)
                print(f"Reference image created: {reference_path}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Screenshot Bug Detection Tool')
    parser.add_argument('url', help='URL to test')
    parser.add_argument('--test-name', help='Name for the test')
    parser.add_argument('--create-reference', action='store_true', 
                       help='Create reference images instead of testing')
    parser.add_argument('--config', help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    detector = ScreenshotBugDetector(config)
    
    try:
        if args.create_reference:
            detector.create_reference_images(args.url, args.test_name)
        else:
            test_result = detector.run_comprehensive_test(args.url, args.test_name)
            report_path = detector.generate_bug_report(test_result['results'])
            print(f"Test completed. Report saved to: {report_path}")
    
    finally:
        detector.cleanup()


if __name__ == "__main__":
    main()