#!/usr/bin/env python3
"""
Generic Bug Detection Tool
A universal tool for comparing reference and current images to detect visual bugs
and generate comprehensive Excel reports for any application.
"""

import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import argparse
import json
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell


class GenericBugDetector:
    """Generic bug detection tool for comparing any two images."""
    
    def __init__(self, config: Dict = None):
        """Initialize the bug detector with configuration."""
        self.config = config or self._default_config()
        self.results = []
        
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'threshold': 0.95,  # Image similarity threshold
            'min_contour_area': 100,  # Minimum area for significant differences
            'output_dir': 'bug_reports',
            'screenshots_dir': 'screenshots',
            'excel_filename': 'bug_report.xlsx',
            'include_difference_images': True,
            'detailed_analysis': True,
            'severity_levels': {
                'critical': 0.7,  # Below 70% similarity
                'high': 0.8,      # Below 80% similarity
                'medium': 0.9,    # Below 90% similarity
                'low': 0.95       # Below 95% similarity
            }
        }
    
    def compare_images(self, reference_path: str, current_path: str, 
                      test_name: str = None) -> Dict:
        """
        Compare two images and return detailed analysis.
        
        Args:
            reference_path: Path to reference image
            current_path: Path to current image
            test_name: Name for this test case
            
        Returns:
            Dictionary with comparison results and bug analysis
        """
        if not os.path.exists(reference_path):
            return {'error': f'Reference image not found: {reference_path}'}
        
        if not os.path.exists(current_path):
            return {'error': f'Current image not found: {current_path}'}
        
        try:
            # Load images
            ref_img = cv2.imread(reference_path)
            cur_img = cv2.imread(current_path)
            
            if ref_img is None or cur_img is None:
                return {'error': 'Could not load one or both images'}
            
            # Store original dimensions
            ref_height, ref_width = ref_img.shape[:2]
            cur_height, cur_width = cur_img.shape[:2]
            
            # Resize images to same dimensions if needed
            if ref_img.shape != cur_img.shape:
                cur_img = cv2.resize(cur_img, (ref_width, ref_height))
            
            # Convert to grayscale for comparison
            ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
            cur_gray = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
            
            # Calculate structural similarity
            similarity = ssim(ref_gray, cur_gray)
            
            # Calculate difference
            diff = cv2.absdiff(ref_gray, cur_gray)
            diff_percentage = (np.sum(diff > 0) / diff.size) * 100
            
            # Find contours of differences
            thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)[1]
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area
            significant_contours = [c for c in contours if cv2.contourArea(c) > self.config['min_contour_area']]
            
            # Create difference visualization
            diff_visual = ref_img.copy()
            cv2.drawContours(diff_visual, significant_contours, -1, (0, 0, 255), 2)
            
            # Determine severity
            severity = self._determine_severity(similarity)
            
            # Analyze differences
            bugs = self._analyze_differences(ref_img, cur_img, significant_contours, similarity)
            
            result = {
                'test_name': test_name or f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'reference_path': reference_path,
                'current_path': current_path,
                'timestamp': datetime.now().isoformat(),
                'similarity': float(similarity),
                'difference_percentage': float(diff_percentage),
                'contours_count': len(significant_contours),
                'total_contours': len(contours),
                'severity': severity,
                'bugs_found': len(bugs) > 0,
                'bugs': bugs,
                'image_dimensions': {
                    'reference': {'width': ref_width, 'height': ref_height},
                    'current': {'width': cur_width, 'height': cur_height}
                },
                'difference_visualization': diff_visual,
                'contours': significant_contours
            }
            
            return result
            
        except Exception as e:
            return {'error': f'Image comparison failed: {str(e)}'}
    
    def _determine_severity(self, similarity: float) -> str:
        """Determine bug severity based on similarity score."""
        for severity, threshold in self.config['severity_levels'].items():
            if similarity < threshold:
                return severity
        return 'none'
    
    def _analyze_differences(self, ref_img: np.ndarray, cur_img: np.ndarray, 
                           contours: List, similarity: float) -> List[Dict]:
        """Analyze differences and categorize bugs."""
        bugs = []
        
        if similarity < self.config['threshold']:
            # Calculate difference regions
            diff_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                diff_regions.append({
                    'area': area,
                    'bounding_box': (x, y, w, h),
                    'center': (x + w//2, y + h//2)
                })
            
            # Sort by area (largest first)
            diff_regions.sort(key=lambda x: x['area'], reverse=True)
            
            # Categorize bugs
            if len(diff_regions) > 0:
                largest_region = diff_regions[0]
                
                # Layout shift detection
                if largest_region['area'] > 10000:  # Large area difference
                    bugs.append({
                        'type': 'layout_shift',
                        'severity': self._determine_severity(similarity),
                        'description': f'Major layout shift detected. Largest difference area: {largest_region["area"]:.0f} pixels',
                        'area': largest_region['area'],
                        'location': largest_region['center']
                    })
                
                # Missing elements detection
                if len(diff_regions) > 5:
                    bugs.append({
                        'type': 'multiple_differences',
                        'severity': self._determine_severity(similarity),
                        'description': f'Multiple visual differences detected ({len(diff_regions)} regions)',
                        'region_count': len(diff_regions)
                    })
                
                # Color/contrast issues
                if similarity > 0.8 and len(diff_regions) < 3:
                    bugs.append({
                        'type': 'color_contrast_issue',
                        'severity': 'low',
                        'description': 'Minor color or contrast differences detected',
                        'similarity': similarity
                    })
                
                # Text rendering issues
                if self._detect_text_issues(ref_img, cur_img):
                    bugs.append({
                        'type': 'text_rendering_issue',
                        'severity': 'medium',
                        'description': 'Text rendering differences detected'
                    })
        
        return bugs
    
    def _detect_text_issues(self, ref_img: np.ndarray, cur_img: np.ndarray) -> bool:
        """Detect potential text rendering issues."""
        # Convert to grayscale
        ref_gray = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY)
        cur_gray = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        ref_edges = cv2.Canny(ref_gray, 50, 150)
        cur_edges = cv2.Canny(cur_gray, 50, 150)
        
        # Compare edge patterns
        edge_diff = cv2.absdiff(ref_edges, cur_edges)
        edge_diff_percentage = (np.sum(edge_diff > 0) / edge_diff.size) * 100
        
        return edge_diff_percentage > 5  # Threshold for text differences
    
    def save_difference_image(self, diff_visual: np.ndarray, output_path: str):
        """Save difference visualization image."""
        cv2.imwrite(output_path, diff_visual)
    
    def compare_image_pair(self, reference_path: str, current_path: str, 
                          test_name: str = None, save_diff: bool = True) -> Dict:
        """
        Compare a pair of images and optionally save difference visualization.
        
        Args:
            reference_path: Path to reference image
            current_path: Path to current image
            test_name: Name for this test case
            save_diff: Whether to save difference visualization
            
        Returns:
            Comparison result dictionary
        """
        result = self.compare_images(reference_path, current_path, test_name)
        
        if 'error' not in result and save_diff and self.config['include_difference_images']:
            # Create output directory
            output_dir = Path(self.config['output_dir'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save difference image
            diff_filename = f"diff_{result['test_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            diff_path = output_dir / diff_filename
            self.save_difference_image(result['difference_visualization'], str(diff_path))
            result['difference_image_path'] = str(diff_path)
        
        # Store result for batch processing
        self.results.append(result)
        
        return result
    
    def compare_batch(self, image_pairs: List[Tuple[str, str, str]], 
                     save_diffs: bool = True) -> List[Dict]:
        """
        Compare multiple pairs of images in batch.
        
        Args:
            image_pairs: List of tuples (reference_path, current_path, test_name)
            save_diffs: Whether to save difference visualizations
            
        Returns:
            List of comparison results
        """
        results = []
        
        for ref_path, cur_path, test_name in image_pairs:
            print(f"Comparing: {test_name}")
            result = self.compare_image_pair(ref_path, cur_path, test_name, save_diffs)
            results.append(result)
            
            if 'error' in result:
                print(f"  ❌ Error: {result['error']}")
            else:
                status = "✅ PASS" if not result['bugs_found'] else f"❌ FAIL ({result['severity']})"
                print(f"  {status} - Similarity: {result['similarity']:.3f}")
        
        return results
    
    def generate_excel_report(self, results: List[Dict] = None, 
                            filename: str = None) -> str:
        """
        Generate comprehensive Excel bug report.
        
        Args:
            results: List of comparison results (uses self.results if None)
            filename: Output filename (uses config default if None)
            
        Returns:
            Path to generated Excel file
        """
        if results is None:
            results = self.results
        
        if not results:
            raise ValueError("No results to generate report from")
        
        # Create output directory
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bug_report_{timestamp}.xlsx"
        
        filepath = output_dir / filename
        
        # Create workbook and worksheets
        workbook = xlsxwriter.Workbook(str(filepath))
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        critical_format = workbook.add_format({
            'bg_color': '#FF6B6B',
            'font_color': 'white',
            'bold': True
        })
        
        high_format = workbook.add_format({
            'bg_color': '#FF8E53',
            'font_color': 'white',
            'bold': True
        })
        
        medium_format = workbook.add_format({
            'bg_color': '#FFD93D',
            'font_color': 'black'
        })
        
        low_format = workbook.add_format({
            'bg_color': '#6BCF7F',
            'font_color': 'white'
        })
        
        pass_format = workbook.add_format({
            'bg_color': '#4ECDC4',
            'font_color': 'white',
            'bold': True
        })
        
        # Summary worksheet
        self._create_summary_worksheet(workbook, results, header_format)
        
        # Detailed results worksheet
        self._create_detailed_worksheet(workbook, results, header_format, 
                                      critical_format, high_format, medium_format, 
                                      low_format, pass_format)
        
        # Bug analysis worksheet
        self._create_bug_analysis_worksheet(workbook, results, header_format)
        
        # Statistics worksheet
        self._create_statistics_worksheet(workbook, results, header_format)
        
        workbook.close()
        
        print(f"📊 Excel report generated: {filepath}")
        return str(filepath)
    
    def _create_summary_worksheet(self, workbook, results, header_format):
        """Create summary worksheet."""
        worksheet = workbook.add_worksheet('Summary')
        
        # Headers
        headers = ['Metric', 'Value', 'Details']
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Calculate summary statistics
        total_tests = len(results)
        failed_tests = sum(1 for r in results if r.get('bugs_found', False))
        passed_tests = total_tests - failed_tests
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        for result in results:
            severity = result.get('severity', 'none')
            severity_counts[severity] += 1
        
        avg_similarity = np.mean([r.get('similarity', 0) for r in results])
        avg_diff_percentage = np.mean([r.get('difference_percentage', 0) for r in results])
        
        # Summary data
        summary_data = [
            ['Total Tests', total_tests, ''],
            ['Passed Tests', passed_tests, f'{passed_tests/total_tests*100:.1f}%'],
            ['Failed Tests', failed_tests, f'{failed_tests/total_tests*100:.1f}%'],
            ['Success Rate', f'{passed_tests/total_tests*100:.1f}%', ''],
            ['', '', ''],
            ['Critical Issues', severity_counts['critical'], ''],
            ['High Issues', severity_counts['high'], ''],
            ['Medium Issues', severity_counts['medium'], ''],
            ['Low Issues', severity_counts['low'], ''],
            ['', '', ''],
            ['Average Similarity', f'{avg_similarity:.3f}', ''],
            ['Average Difference %', f'{avg_diff_percentage:.1f}%', ''],
            ['', '', ''],
            ['Report Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ''],
            ['Tool Version', 'Generic Bug Detector v1.0', '']
        ]
        
        # Write data
        for row, (metric, value, details) in enumerate(summary_data, 1):
            worksheet.write(row, 0, metric)
            worksheet.write(row, 1, value)
            worksheet.write(row, 2, details)
        
        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 20)
    
    def _create_detailed_worksheet(self, workbook, results, header_format, 
                                 critical_format, high_format, medium_format, 
                                 low_format, pass_format):
        """Create detailed results worksheet."""
        worksheet = workbook.add_worksheet('Detailed Results')
        
        # Headers
        headers = [
            'Test Name', 'Status', 'Severity', 'Similarity', 'Difference %',
            'Contours', 'Bugs Found', 'Reference Image', 'Current Image',
            'Difference Image', 'Timestamp'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Data rows
        for row, result in enumerate(results, 1):
            # Status and severity formatting
            if result.get('bugs_found', False):
                status = 'FAIL'
                severity = result.get('severity', 'unknown')
                if severity == 'critical':
                    status_format = critical_format
                elif severity == 'high':
                    status_format = high_format
                elif severity == 'medium':
                    status_format = medium_format
                elif severity == 'low':
                    status_format = low_format
                else:
                    status_format = medium_format
            else:
                status = 'PASS'
                severity = 'none'
                status_format = pass_format
            
            # Write data
            worksheet.write(row, 0, result.get('test_name', ''))
            worksheet.write(row, 1, status, status_format)
            worksheet.write(row, 2, severity.upper())
            worksheet.write(row, 3, f"{result.get('similarity', 0):.3f}")
            worksheet.write(row, 4, f"{result.get('difference_percentage', 0):.1f}%")
            worksheet.write(row, 5, result.get('contours_count', 0))
            worksheet.write(row, 6, len(result.get('bugs', [])))
            worksheet.write(row, 7, result.get('reference_path', ''))
            worksheet.write(row, 8, result.get('current_path', ''))
            worksheet.write(row, 9, result.get('difference_image_path', ''))
            worksheet.write(row, 10, result.get('timestamp', ''))
        
        # Set column widths
        column_widths = [20, 10, 12, 12, 12, 10, 12, 30, 30, 30, 20]
        for col, width in enumerate(column_widths):
            worksheet.set_column(col, col, width)
    
    def _create_bug_analysis_worksheet(self, workbook, results, header_format):
        """Create bug analysis worksheet."""
        worksheet = workbook.add_worksheet('Bug Analysis')
        
        # Headers
        headers = [
            'Test Name', 'Bug Type', 'Severity', 'Description', 'Area', 'Location'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        row = 1
        for result in results:
            test_name = result.get('test_name', '')
            bugs = result.get('bugs', [])
            
            if bugs:
                for bug in bugs:
                    worksheet.write(row, 0, test_name)
                    worksheet.write(row, 1, bug.get('type', ''))
                    worksheet.write(row, 2, bug.get('severity', '').upper())
                    worksheet.write(row, 3, bug.get('description', ''))
                    worksheet.write(row, 4, bug.get('area', ''))
                    worksheet.write(row, 5, str(bug.get('location', '')))
                    row += 1
            else:
                worksheet.write(row, 0, test_name)
                worksheet.write(row, 1, 'No bugs found')
                worksheet.write(row, 2, 'PASS')
                worksheet.write(row, 3, 'No visual differences detected')
                row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 12)
        worksheet.set_column('D:D', 50)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 20)
    
    def _create_statistics_worksheet(self, workbook, results, header_format):
        """Create statistics worksheet."""
        worksheet = workbook.add_worksheet('Statistics')
        
        # Headers
        headers = ['Metric', 'Value', 'Percentage']
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
        
        # Calculate statistics
        total_tests = len(results)
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'none': 0}
        bug_types = {}
        
        for result in results:
            severity = result.get('severity', 'none')
            severity_counts[severity] += 1
            
            for bug in result.get('bugs', []):
                bug_type = bug.get('type', 'unknown')
                bug_types[bug_type] = bug_types.get(bug_type, 0) + 1
        
        # Write statistics
        row = 1
        for severity, count in severity_counts.items():
            percentage = (count / total_tests * 100) if total_tests > 0 else 0
            worksheet.write(row, 0, f'{severity.title()} Severity')
            worksheet.write(row, 1, count)
            worksheet.write(row, 2, f'{percentage:.1f}%')
            row += 1
        
        row += 1
        worksheet.write(row, 0, 'Bug Types')
        row += 1
        
        for bug_type, count in bug_types.items():
            percentage = (count / sum(bug_types.values()) * 100) if bug_types else 0
            worksheet.write(row, 0, bug_type.replace('_', ' ').title())
            worksheet.write(row, 1, count)
            worksheet.write(row, 2, f'{percentage:.1f}%')
            row += 1
        
        # Set column widths
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 15)


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Generic Bug Detection Tool')
    parser.add_argument('reference', help='Path to reference image')
    parser.add_argument('current', help='Path to current image')
    parser.add_argument('--test-name', help='Name for the test')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--output', help='Output directory for reports')
    parser.add_argument('--excel', help='Excel filename')
    parser.add_argument('--batch', help='Path to batch file with image pairs')
    parser.add_argument('--no-diff', action='store_true', help='Do not save difference images')
    
    args = parser.parse_args()
    
    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Override output directory if specified
    if args.output:
        config['output_dir'] = args.output
    
    detector = GenericBugDetector(config)
    
    try:
        if args.batch:
            # Batch processing
            with open(args.batch, 'r') as f:
                batch_data = json.load(f)
            
            image_pairs = []
            for item in batch_data:
                if len(item) >= 2:
                    test_name = item[2] if len(item) > 2 else None
                    image_pairs.append((item[0], item[1], test_name))
            
            print(f"Processing {len(image_pairs)} image pairs...")
            results = detector.compare_batch(image_pairs, not args.no_diff)
            
        else:
            # Single comparison
            result = detector.compare_image_pair(
                args.reference, 
                args.current, 
                args.test_name,
                not args.no_diff
            )
            results = [result]
            
            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                return
            else:
                status = "✅ PASS" if not result['bugs_found'] else f"❌ FAIL ({result['severity']})"
                print(f"{status} - Similarity: {result['similarity']:.3f}")
        
        # Generate Excel report
        excel_path = detector.generate_excel_report(results, args.excel)
        print(f"📊 Excel report saved to: {excel_path}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()