# 🔍 Generic Bug Detection Tool

A universal image comparison tool that works with any application to detect visual bugs and generate comprehensive Excel reports. Simply provide reference and current images, and get detailed analysis of visual differences.

## 🎯 Features

- **Universal Compatibility**: Works with any application (web, mobile, desktop)
- **Advanced Image Comparison**: Uses SSIM and computer vision algorithms
- **Excel Report Generation**: Comprehensive reports with multiple worksheets
- **Batch Processing**: Compare multiple image pairs at once
- **Difference Visualization**: Highlights changed areas in images
- **Severity Classification**: Critical, High, Medium, Low bug categorization
- **Flexible Configuration**: Customizable thresholds and settings
- **Command-line Interface**: Easy to integrate into CI/CD pipelines

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
./run_generic_tests.sh setup
```

### 📥 Download Locations

**Mac Users:** `/Users/[username]/Downloads/generic_bug_detection_tool.zip`  
**Windows Users:** `C:\Users\[username]\Downloads\generic_bug_detection_tool.zip`  
**Linux Users:** `/home/[username]/Downloads/generic_bug_detection_tool.zip`  

See [DOWNLOAD-LOCATIONS.md](DOWNLOAD-LOCATIONS.md) for complete path information.

### Basic Usage

```bash
# Compare two images
./run_generic_tests.sh compare --reference ref.png --current current.png --test-name "my_test"

# View Excel report in bug_reports/ directory
```

## 📋 Usage Examples

### Single Image Comparison

```bash
# Basic comparison
./run_generic_tests.sh compare --reference reference_images/app_ref.png --current screenshots/app_current.png

# With custom test name and Excel filename
./run_generic_tests.sh compare --reference ref.png --current current.png --test-name "homepage_test" --excel "homepage_report.xlsx"

# Without saving difference images
./run_generic_tests.sh compare --reference ref.png --current current.png --no-diff
```

### Batch Processing

```bash
# Using simple batch file
./run_generic_tests.sh batch --batch simple_batch.json

# Using custom batch file
./run_generic_tests.sh batch --batch my_tests.json --excel "comprehensive_report.xlsx"
```

### Direct Python Usage

```bash
# Single comparison
python3 generic_bug_detector.py reference.png current.png --test-name "my_test"

# Batch processing
python3 generic_bug_detector.py --batch batch_file.json
```

## 📁 File Formats

### Simple Batch Format (simple_batch.json)
```json
[
  ["reference_images/homepage_ref.png", "screenshots/homepage_current.png", "homepage_test"],
  ["reference_images/login_ref.png", "screenshots/login_current.png", "login_test"],
  ["reference_images/dashboard_ref.png", "screenshots/dashboard_current.png", "dashboard_test"]
]
```

### Detailed Batch Format (batch_config.json)
```json
{
  "batch_tests": [
    {
      "test_name": "homepage_desktop",
      "reference_image": "reference_images/homepage_desktop_ref.png",
      "current_image": "screenshots/homepage_desktop_current.png"
    }
  ]
}
```

## ⚙️ Configuration

Edit `generic_config.json` to customize:

```json
{
  "threshold": 0.95,
  "min_contour_area": 100,
  "severity_levels": {
    "critical": 0.7,
    "high": 0.8,
    "medium": 0.9,
    "low": 0.95
  },
  "include_difference_images": true,
  "detailed_analysis": true
}
```

## 📊 Excel Report Structure

The tool generates comprehensive Excel reports with multiple worksheets:

### 1. Summary Worksheet
- Total tests and pass/fail statistics
- Success rate percentage
- Severity breakdown (Critical, High, Medium, Low)
- Average similarity scores

### 2. Detailed Results Worksheet
- Individual test results with color-coded severity
- Similarity scores and difference percentages
- File paths and timestamps
- Contour counts and bug information

### 3. Bug Analysis Worksheet
- Detailed bug descriptions and types
- Severity levels and locations
- Area measurements and analysis

### 4. Statistics Worksheet
- Severity distribution percentages
- Bug type breakdown
- Comprehensive metrics

## 🔬 Bug Detection Algorithms

### Structural Similarity Index (SSIM)
- Measures structural similarity between images
- Range: 0.0 to 1.0 (higher is more similar)
- Accounts for luminance, contrast, and structure

### Contour Detection
- Identifies areas of difference using OpenCV
- Filters noise with minimum area threshold
- Provides precise location of changes

### Severity Classification
- **Critical**: < 70% similarity (major layout changes)
- **High**: < 80% similarity (significant differences)
- **Medium**: < 90% similarity (moderate changes)
- **Low**: < 95% similarity (minor differences)

### Bug Categories
- **Layout Shifts**: Large area differences
- **Multiple Differences**: Many small changes
- **Color/Contrast Issues**: Minor visual changes
- **Text Rendering Issues**: Font or text problems

## 🎨 Difference Visualization

The tool creates difference images that:
- Highlight changed areas in red
- Show precise locations of differences
- Save as PNG files for easy review
- Include contour analysis

## 🔧 Advanced Features

### Custom Severity Levels
```json
{
  "severity_levels": {
    "critical": 0.6,
    "high": 0.75,
    "medium": 0.85,
    "low": 0.92
  }
}
```

### Batch Processing Options
- Process multiple image pairs
- Generate consolidated reports
- Custom output directories
- Flexible naming conventions

### Integration Examples

#### CI/CD Pipeline
```bash
# In your CI script
./run_generic_tests.sh batch --batch regression_tests.json
if [ $? -ne 0 ]; then
    echo "Visual regression tests failed"
    exit 1
fi
```

#### Automated Testing
```bash
# Daily regression testing
./run_generic_tests.sh compare --reference daily_ref.png --current daily_current.png --test-name "daily_regression"
```

## 📈 Use Cases

### Web Applications
- Compare before/after screenshots
- Test responsive design changes
- Validate UI updates
- Cross-browser compatibility testing

### Mobile Applications
- App store screenshot validation
- UI update verification
- Device-specific testing
- Version comparison

### Desktop Applications
- Software update validation
- UI regression testing
- Feature comparison
- Cross-platform testing

### Design Systems
- Component library validation
- Design consistency checking
- Brand guideline compliance
- Asset comparison

## 🚨 Troubleshooting

### Common Issues

1. **Image Loading Errors**
   ```bash
   # Check file paths
   ls -la reference_images/
   ls -la screenshots/
   ```

2. **Memory Issues**
   - Reduce image sizes
   - Process in smaller batches
   - Check system memory

3. **Configuration Errors**
   - Validate JSON syntax
   - Check file paths
   - Ensure required fields

4. **Output Issues**
   - Check write permissions
   - Ensure disk space
   - Close Excel files

## 📚 API Reference

### GenericBugDetector Class

```python
from generic_bug_detector import GenericBugDetector

# Initialize detector
detector = GenericBugDetector(config)

# Compare single pair
result = detector.compare_image_pair("ref.png", "current.png", "test_name")

# Batch comparison
results = detector.compare_batch([
    ("ref1.png", "current1.png", "test1"),
    ("ref2.png", "current2.png", "test2")
])

# Generate Excel report
excel_path = detector.generate_excel_report(results)
```

### Key Methods

- `compare_images()`: Core comparison algorithm
- `compare_image_pair()`: Single image pair comparison
- `compare_batch()`: Multiple image pair comparison
- `generate_excel_report()`: Create comprehensive Excel report
- `save_difference_image()`: Save difference visualization

## 🔒 Security Considerations

- Images may contain sensitive information
- Implement proper access controls
- Consider data retention policies
- Secure configuration files

## 🚀 Performance Tips

1. **Image Optimization**
   - Use appropriate image sizes
   - Consider compression for large images
   - Balance quality vs processing time

2. **Batch Processing**
   - Process in reasonable batch sizes
   - Use SSD storage for better I/O
   - Monitor system resources

3. **Memory Management**
   - Close unused applications
   - Process sequentially for large batches
   - Monitor memory usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the execution steps document
3. Create an issue in the repository

---

**Key Benefits:**
- ✅ Works with any application type
- ✅ No need for web automation setup
- ✅ Comprehensive Excel reporting
- ✅ Advanced computer vision algorithms
- ✅ Easy integration into existing workflows
- ✅ Flexible configuration options
- ✅ Batch processing capabilities
- ✅ Professional difference visualizations