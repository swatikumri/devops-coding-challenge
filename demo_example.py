#!/usr/bin/env python3
"""
Demo Example for Generic Bug Detection Tool
This script demonstrates how to use the tool programmatically.
"""

import os
import numpy as np
from PIL import Image
from generic_bug_detector import GenericBugDetector


def create_demo_images():
    """Create demo images for testing."""
    print("Creating demo images...")
    
    # Create directories
    os.makedirs("reference_images", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    
    # Create a simple reference image (blue background with white text)
    ref_img = Image.new('RGB', (400, 300), color='blue')
    ref_img.save("reference_images/demo_ref.png")
    
    # Create a current image with slight differences (red background with white text)
    cur_img = Image.new('RGB', (400, 300), color='red')
    cur_img.save("screenshots/demo_current.png")
    
    # Create another current image with minor differences (blue background with different text)
    cur_img2 = Image.new('RGB', (400, 300), color='blue')
    cur_img2.save("screenshots/demo_current_minor.png")
    
    print("✅ Demo images created successfully!")


def run_demo():
    """Run a demonstration of the bug detection tool."""
    print("🔍 Generic Bug Detection Tool - Demo")
    print("=" * 50)
    
    # Create demo images
    create_demo_images()
    
    # Initialize detector
    detector = GenericBugDetector()
    
    print("\n1. Single Image Comparison (Major Difference)")
    print("-" * 50)
    
    # Compare images with major difference
    result1 = detector.compare_image_pair(
        "reference_images/demo_ref.png",
        "screenshots/demo_current.png",
        "demo_major_difference"
    )
    
    if 'error' not in result1:
        print(f"✅ Test: {result1['test_name']}")
        print(f"   Similarity: {result1['similarity']:.3f}")
        print(f"   Severity: {result1['severity']}")
        print(f"   Bugs Found: {result1['bugs_found']}")
        print(f"   Difference %: {result1['difference_percentage']:.1f}%")
    else:
        print(f"❌ Error: {result1['error']}")
    
    print("\n2. Single Image Comparison (Minor Difference)")
    print("-" * 50)
    
    # Compare images with minor difference
    result2 = detector.compare_image_pair(
        "reference_images/demo_ref.png",
        "screenshots/demo_current_minor.png",
        "demo_minor_difference"
    )
    
    if 'error' not in result2:
        print(f"✅ Test: {result2['test_name']}")
        print(f"   Similarity: {result2['similarity']:.3f}")
        print(f"   Severity: {result2['severity']}")
        print(f"   Bugs Found: {result2['bugs_found']}")
        print(f"   Difference %: {result2['difference_percentage']:.1f}%")
    else:
        print(f"❌ Error: {result2['error']}")
    
    print("\n3. Batch Processing")
    print("-" * 50)
    
    # Batch comparison
    image_pairs = [
        ("reference_images/demo_ref.png", "screenshots/demo_current.png", "batch_test_1"),
        ("reference_images/demo_ref.png", "screenshots/demo_current_minor.png", "batch_test_2")
    ]
    
    batch_results = detector.compare_batch(image_pairs)
    
    print(f"✅ Processed {len(batch_results)} image pairs")
    for result in batch_results:
        if 'error' not in result:
            status = "PASS" if not result['bugs_found'] else f"FAIL ({result['severity']})"
            print(f"   {result['test_name']}: {status} - Similarity: {result['similarity']:.3f}")
        else:
            print(f"   {result['test_name']}: ERROR - {result['error']}")
    
    print("\n4. Excel Report Generation")
    print("-" * 50)
    
    # Generate Excel report
    try:
        excel_path = detector.generate_excel_report()
        print(f"✅ Excel report generated: {excel_path}")
        print(f"   📊 Check the bug_reports/ directory for the Excel file")
    except Exception as e:
        print(f"❌ Error generating Excel report: {e}")
    
    print("\n5. Summary")
    print("-" * 50)
    
    total_tests = len(detector.results)
    failed_tests = sum(1 for r in detector.results if r.get('bugs_found', False))
    passed_tests = total_tests - failed_tests
    
    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    # Show severity breakdown
    severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'none': 0}
    for result in detector.results:
        severity = result.get('severity', 'none')
        severity_counts[severity] += 1
    
    print(f"\n🐛 Severity Breakdown:")
    for severity, count in severity_counts.items():
        if count > 0:
            print(f"   {severity.title()}: {count}")
    
    print(f"\n🎉 Demo completed! Check the bug_reports/ directory for the Excel report.")


if __name__ == "__main__":
    run_demo()