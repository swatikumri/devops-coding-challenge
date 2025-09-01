# 🐛 Screenshot Bug Detection Tool

A comprehensive testing framework for visual regression testing and bug detection in web applications, specifically designed for the Sudoku game but extensible to any web application.

## 🎯 Features

- **Screenshot Capture**: Automated screenshot capture across multiple viewport sizes
- **Visual Regression Testing**: Compare current screenshots with reference images
- **Bug Detection**: Advanced image comparison algorithms to detect visual differences
- **Automated Bug Reports**: Generate detailed HTML reports with screenshots and analysis
- **Sudoku Game Testing**: Specialized test automation for Sudoku game functionality
- **Responsive Design Testing**: Test across desktop, laptop, tablet, and mobile viewports
- **Docker Support**: Containerized testing environment for consistency
- **Configuration Management**: Flexible configuration for different test scenarios

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Chrome or Chromium
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd screenshot-bug-detector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Make scripts executable**
   ```bash
   chmod +x run_tests.sh
   ```

### Basic Usage

1. **Setup environment**
   ```bash
   ./run_tests.sh setup
   ```

2. **Start the Sudoku application**
   ```bash
   ./run_tests.sh start-app
   ```

3. **Create reference images (first time only)**
   ```bash
   ./run_tests.sh create-ref
   ```

4. **Run all tests**
   ```bash
   ./run_tests.sh test-all
   ```

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `setup` | Setup the testing environment |
| `start-app` | Start the Sudoku application |
| `create-ref` | Create reference images |
| `test-visual` | Run visual regression tests |
| `test-sudoku` | Run Sudoku-specific tests |
| `test-all` | Run all tests |
| `docker-setup` | Setup using Docker |
| `docker-test` | Run tests using Docker |
| `clean` | Clean up generated files |

## 🧪 Test Types

### 1. Visual Regression Testing
- Captures screenshots across multiple viewport sizes
- Compares with reference images using structural similarity
- Detects layout changes, missing elements, and visual bugs
- Generates difference visualizations

### 2. Sudoku Game Testing
- **Game Initialization**: Verifies proper game setup
- **Difficulty Selection**: Tests easy, medium, and hard modes
- **Cell Interaction**: Tests clicking and number input
- **Game Controls**: Tests hint, check, and solve buttons
- **Responsive Design**: Tests across different screen sizes

### 3. Responsive Design Testing
- Desktop (1920x1080)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

## 🐳 Docker Usage

### Setup
```bash
./run_tests.sh docker-setup
```

### Run Tests
```bash
./run_tests.sh docker-test
```

### Manual Docker Commands
```bash
# Build images
docker-compose build

# Run specific test
docker-compose up bug-detector

# Run visual regression tests
docker-compose up visual-regression

# Create reference images
docker-compose up create-reference
```

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "threshold": 0.95,
  "viewport_sizes": [
    {"width": 1920, "height": 1080, "name": "desktop"},
    {"width": 375, "height": 667, "name": "mobile"}
  ],
  "wait_timeout": 10,
  "screenshot_delay": 2
}
```

## 📊 Output

### Screenshots
- Location: `screenshots/` directory
- Format: PNG files with timestamps
- Naming: `{test_name}_{viewport}_{timestamp}.png`

### Reference Images
- Location: `reference_images/` directory
- Used for comparison in visual regression tests

### Bug Reports
- Location: `bug_reports/` directory
- Format: HTML files with detailed analysis
- Includes screenshots, metrics, and bug descriptions

## 🔧 Advanced Usage

### Manual Test Execution
```bash
# Run specific test type
python3 test_runner.py --url http://localhost:8000 --test-type visual_regression

# Run with custom configuration
python3 test_runner.py --url http://localhost:8000 --config custom_config.json

# Run specific Sudoku test
python3 sudoku_test_automation.py --url http://localhost:8000 --test initialization
```

### Custom Test Scenarios
```python
from screenshot_bug_detector import ScreenshotBugDetector

detector = ScreenshotBugDetector()
result = detector.run_comprehensive_test("http://example.com", "my_test")
report = detector.generate_bug_report(result['results'])
```

## 🐛 Bug Detection Algorithm

The tool uses advanced computer vision techniques:

1. **Structural Similarity Index (SSIM)**: Measures structural similarity between images
2. **Contour Detection**: Identifies areas of difference
3. **Threshold-based Analysis**: Configurable similarity thresholds
4. **Difference Visualization**: Highlights changed areas

## 📈 Metrics and Analysis

The tool provides detailed metrics:
- **Similarity Score**: 0.0 to 1.0 (higher is more similar)
- **Difference Percentage**: Percentage of pixels that differ
- **Contour Count**: Number of distinct difference areas
- **Severity Classification**: High, Medium, Low based on impact

## 🔒 Security Considerations

- Runs in headless mode by default
- Screenshots may contain sensitive information
- Use HTTPS URLs for production testing
- Implement proper access controls on output directories

## 🚨 Troubleshooting

### Common Issues

1. **Chrome/Chromium not found**
   ```bash
   # Install Chrome
   sudo apt-get install google-chrome-stable
   ```

2. **Permission errors**
   ```bash
   chmod +x run_tests.sh
   chmod +x *.py
   ```

3. **Port already in use**
   ```bash
   # Stop existing server
   kill $(cat .server.pid)
   ```

4. **Docker issues**
   ```bash
   # Clean up containers
   docker-compose down --rmi all --volumes
   ```

## 📚 API Reference

### ScreenshotBugDetector Class

```python
detector = ScreenshotBugDetector(config)
screenshot = detector.capture_screenshot(url, filename, viewport)
comparison = detector.compare_images(image1, image2)
bugs = detector.detect_visual_bugs(current, reference)
report = detector.generate_bug_report(test_results)
```

### SudokuTestAutomation Class

```python
automation = SudokuTestAutomation(url, config)
automation.navigate_to_game()
automation.select_difficulty("medium")
automation.start_new_game()
result = automation.test_game_initialization()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the execution steps document
3. Create an issue in the repository

---

**Time Spent**: Approximately 8 hours for complete implementation including:
- Core screenshot capture and comparison functionality
- Sudoku-specific test automation
- Docker containerization
- Configuration management
- Comprehensive documentation
- Bug report generation with HTML templates