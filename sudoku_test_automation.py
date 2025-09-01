#!/usr/bin/env python3
"""
Sudoku Game Test Automation Framework
Specialized test automation for the Sudoku game with visual regression testing.
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from screenshot_bug_detector import ScreenshotBugDetector


class SudokuTestAutomation:
    """Test automation framework specifically for the Sudoku game."""
    
    def __init__(self, base_url: str = "http://localhost:8000", config: Dict = None):
        """Initialize the test automation framework."""
        self.base_url = base_url
        self.detector = ScreenshotBugDetector(config)
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup WebDriver for testing."""
        self.driver = self.detector.setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        return self.driver
    
    def navigate_to_game(self):
        """Navigate to the Sudoku game."""
        self.driver.get(self.base_url)
        self.wait.until(EC.presence_of_element_located((By.ID, "sudoku-board")))
        time.sleep(2)  # Allow for animations
    
    def select_difficulty(self, difficulty: str):
        """Select game difficulty."""
        difficulty_select = self.wait.until(
            EC.element_to_be_clickable((By.ID, "difficulty-select"))
        )
        select = Select(difficulty_select)
        select.select_by_value(difficulty)
        time.sleep(1)
    
    def start_new_game(self):
        """Start a new game."""
        new_game_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "new-game-btn"))
        )
        new_game_btn.click()
        time.sleep(2)  # Allow for game generation
    
    def get_cell_value(self, row: int, col: int) -> Optional[str]:
        """Get the value of a specific cell."""
        try:
            cell = self.driver.find_element(
                By.CSS_SELECTOR, 
                f"#sudoku-board .cell[data-row='{row}'][data-col='{col}']"
            )
            return cell.text.strip() if cell.text.strip() else None
        except NoSuchElementException:
            return None
    
    def click_cell(self, row: int, col: int):
        """Click on a specific cell."""
        cell = self.wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                f"#sudoku-board .cell[data-row='{row}'][data-col='{col}']"
            ))
        )
        cell.click()
        time.sleep(0.5)
    
    def input_number(self, number: int):
        """Input a number using the number pad."""
        if number == 0:
            # Clear button
            clear_btn = self.driver.find_element(
                By.CSS_SELECTOR, 
                ".number-btn.clear"
            )
            clear_btn.click()
        else:
            number_btn = self.driver.find_element(
                By.CSS_SELECTOR, 
                f".number-btn[data-number='{number}']"
            )
            number_btn.click()
        time.sleep(0.5)
    
    def get_timer_value(self) -> str:
        """Get the current timer value."""
        try:
            timer_element = self.driver.find_element(By.ID, "timer")
            return timer_element.text.strip()
        except NoSuchElementException:
            return "00:00"
    
    def get_message(self) -> str:
        """Get the current message."""
        try:
            message_element = self.driver.find_element(By.ID, "message")
            return message_element.text.strip()
        except NoSuchElementException:
            return ""
    
    def click_hint(self):
        """Click the hint button."""
        hint_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "hint-btn"))
        )
        hint_btn.click()
        time.sleep(1)
    
    def click_check(self):
        """Click the check button."""
        check_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "check-btn"))
        )
        check_btn.click()
        time.sleep(1)
    
    def click_solve(self):
        """Click the solve button."""
        solve_btn = self.wait.until(
            EC.element_to_be_clickable((By.ID, "solve-btn"))
        )
        solve_btn.click()
        time.sleep(2)
    
    def get_board_state(self) -> List[List[Optional[str]]]:
        """Get the current state of the entire board."""
        board = []
        for row in range(9):
            board_row = []
            for col in range(9):
                value = self.get_cell_value(row, col)
                board_row.append(value)
            board.append(board_row)
        return board
    
    def test_game_initialization(self) -> Dict:
        """Test that the game initializes correctly."""
        test_name = "game_initialization"
        print(f"Running test: {test_name}")
        
        try:
            self.navigate_to_game()
            
            # Test initial state
            board = self.get_board_state()
            timer = self.get_timer_value()
            message = self.get_message()
            
            # Check that board has some pre-filled cells
            filled_cells = sum(1 for row in board for cell in row if cell is not None)
            
            # Take screenshot
            screenshot = self.detector.capture_screenshot(
                self.base_url, 
                f"{test_name}_initial.png"
            )
            
            bugs = []
            
            # Check for bugs
            if filled_cells == 0:
                bugs.append({
                    'type': 'initialization_error',
                    'severity': 'high',
                    'description': 'No cells are pre-filled in the initial game state'
                })
            
            if timer != "00:00":
                bugs.append({
                    'type': 'timer_issue',
                    'severity': 'medium',
                    'description': f'Timer should start at 00:00, but shows {timer}'
                })
            
            if message:
                bugs.append({
                    'type': 'unexpected_message',
                    'severity': 'low',
                    'description': f'Unexpected message on initialization: {message}'
                })
            
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': len(bugs) > 0,
                'bugs': bugs,
                'screenshots': [{'name': 'Initial State', 'path': screenshot}] if screenshot else [],
                'board_state': board,
                'filled_cells_count': filled_cells,
                'timer_value': timer,
                'message': message
            }
            
        except Exception as e:
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': True,
                'bugs': [{
                    'type': 'test_execution_error',
                    'severity': 'high',
                    'description': f'Test execution failed: {str(e)}'
                }],
                'screenshots': [],
                'error': str(e)
            }
    
    def test_difficulty_selection(self) -> Dict:
        """Test difficulty selection functionality."""
        test_name = "difficulty_selection"
        print(f"Running test: {test_name}")
        
        try:
            self.navigate_to_game()
            
            bugs = []
            screenshots = []
            
            # Test each difficulty level
            difficulties = ['easy', 'medium', 'hard']
            for difficulty in difficulties:
                self.select_difficulty(difficulty)
                self.start_new_game()
                
                # Take screenshot for each difficulty
                screenshot = self.detector.capture_screenshot(
                    self.base_url,
                    f"{test_name}_{difficulty}.png"
                )
                if screenshot:
                    screenshots.append({
                        'name': f'{difficulty.title()} Difficulty',
                        'path': screenshot
                    })
                
                # Check board state
                board = self.get_board_state()
                filled_cells = sum(1 for row in board for cell in row if cell is not None)
                
                # Expected filled cells based on difficulty
                expected_ranges = {
                    'easy': (35, 45),
                    'medium': (25, 35),
                    'hard': (15, 25)
                }
                
                min_expected, max_expected = expected_ranges.get(difficulty, (20, 40))
                if not (min_expected <= filled_cells <= max_expected):
                    bugs.append({
                        'type': 'difficulty_issue',
                        'severity': 'medium',
                        'description': f'{difficulty.title()} difficulty has {filled_cells} filled cells, expected {min_expected}-{max_expected}'
                    })
            
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': len(bugs) > 0,
                'bugs': bugs,
                'screenshots': screenshots
            }
            
        except Exception as e:
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': True,
                'bugs': [{
                    'type': 'test_execution_error',
                    'severity': 'high',
                    'description': f'Test execution failed: {str(e)}'
                }],
                'screenshots': [],
                'error': str(e)
            }
    
    def test_cell_interaction(self) -> Dict:
        """Test cell clicking and number input."""
        test_name = "cell_interaction"
        print(f"Running test: {test_name}")
        
        try:
            self.navigate_to_game()
            self.start_new_game()
            
            bugs = []
            screenshots = []
            
            # Test clicking on empty cell and entering number
            self.click_cell(0, 0)
            self.input_number(1)
            
            # Check if number was entered
            cell_value = self.get_cell_value(0, 0)
            if cell_value != "1":
                bugs.append({
                    'type': 'input_error',
                    'severity': 'high',
                    'description': f'Failed to input number 1 in cell (0,0). Got: {cell_value}'
                })
            
            # Test clearing cell
            self.click_cell(0, 0)
            self.input_number(0)  # Clear button
            
            cell_value = self.get_cell_value(0, 0)
            if cell_value is not None:
                bugs.append({
                    'type': 'clear_error',
                    'severity': 'medium',
                    'description': f'Failed to clear cell (0,0). Still contains: {cell_value}'
                })
            
            # Take screenshot
            screenshot = self.detector.capture_screenshot(
                self.base_url,
                f"{test_name}_interaction.png"
            )
            if screenshot:
                screenshots.append({
                    'name': 'Cell Interaction',
                    'path': screenshot
                })
            
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': len(bugs) > 0,
                'bugs': bugs,
                'screenshots': screenshots
            }
            
        except Exception as e:
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': True,
                'bugs': [{
                    'type': 'test_execution_error',
                    'severity': 'high',
                    'description': f'Test execution failed: {str(e)}'
                }],
                'screenshots': [],
                'error': str(e)
            }
    
    def test_game_controls(self) -> Dict:
        """Test game control buttons (hint, check, solve)."""
        test_name = "game_controls"
        print(f"Running test: {test_name}")
        
        try:
            self.navigate_to_game()
            self.start_new_game()
            
            bugs = []
            screenshots = []
            
            # Test hint button
            initial_message = self.get_message()
            self.click_hint()
            hint_message = self.get_message()
            
            if hint_message == initial_message:
                bugs.append({
                    'type': 'hint_button_issue',
                    'severity': 'medium',
                    'description': 'Hint button does not provide any feedback'
                })
            
            # Test check button
            self.click_check()
            check_message = self.get_message()
            
            if not check_message:
                bugs.append({
                    'type': 'check_button_issue',
                    'severity': 'medium',
                    'description': 'Check button does not provide feedback'
                })
            
            # Test solve button
            self.click_solve()
            time.sleep(3)  # Allow for solving animation
            
            solve_message = self.get_message()
            board = self.get_board_state()
            filled_cells = sum(1 for row in board for cell in row if cell is not None)
            
            if filled_cells < 81:
                bugs.append({
                    'type': 'solve_button_issue',
                    'severity': 'high',
                    'description': f'Solve button did not complete the puzzle. Only {filled_cells}/81 cells filled'
                })
            
            # Take screenshot
            screenshot = self.detector.capture_screenshot(
                self.base_url,
                f"{test_name}_controls.png"
            )
            if screenshot:
                screenshots.append({
                    'name': 'Game Controls Test',
                    'path': screenshot
                })
            
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': len(bugs) > 0,
                'bugs': bugs,
                'screenshots': screenshots,
                'hint_message': hint_message,
                'check_message': check_message,
                'solve_message': solve_message,
                'final_filled_cells': filled_cells
            }
            
        except Exception as e:
            return {
                'test_name': test_name,
                'url': self.base_url,
                'viewport': 'default',
                'bugs_found': True,
                'bugs': [{
                    'type': 'test_execution_error',
                    'severity': 'high',
                    'description': f'Test execution failed: {str(e)}'
                }],
                'screenshots': [],
                'error': str(e)
            }
    
    def test_responsive_design(self) -> Dict:
        """Test responsive design across different viewport sizes."""
        test_name = "responsive_design"
        print(f"Running test: {test_name}")
        
        bugs = []
        screenshots = []
        
        viewport_sizes = [
            {'width': 1920, 'height': 1080, 'name': 'desktop'},
            {'width': 1366, 'height': 768, 'name': 'laptop'},
            {'width': 768, 'height': 1024, 'name': 'tablet'},
            {'width': 375, 'height': 667, 'name': 'mobile'}
        ]
        
        for viewport in viewport_sizes:
            try:
                # Set viewport size
                self.driver.set_window_size(viewport['width'], viewport['height'])
                self.navigate_to_game()
                self.start_new_game()
                
                # Take screenshot
                screenshot = self.detector.capture_screenshot(
                    self.base_url,
                    f"{test_name}_{viewport['name']}.png",
                    viewport
                )
                if screenshot:
                    screenshots.append({
                        'name': f'{viewport["name"].title()} ({viewport["width"]}x{viewport["height"]})',
                        'path': screenshot
                    })
                
                # Check if game board is visible and properly sized
                try:
                    board = self.driver.find_element(By.ID, "sudoku-board")
                    board_rect = board.rect
                    
                    # Check if board is within viewport
                    if (board_rect['x'] < 0 or board_rect['y'] < 0 or 
                        board_rect['x'] + board_rect['width'] > viewport['width'] or
                        board_rect['y'] + board_rect['height'] > viewport['height']):
                        bugs.append({
                            'type': 'layout_issue',
                            'severity': 'medium',
                            'description': f'Game board is not properly contained within {viewport["name"]} viewport'
                        })
                    
                    # Check if board is too small on mobile
                    if viewport['name'] == 'mobile' and board_rect['width'] < 300:
                        bugs.append({
                            'type': 'usability_issue',
                            'severity': 'medium',
                            'description': 'Game board is too small on mobile devices'
                        })
                
                except NoSuchElementException:
                    bugs.append({
                        'type': 'element_not_found',
                        'severity': 'high',
                        'description': f'Game board not found in {viewport["name"]} viewport'
                    })
                
            except Exception as e:
                bugs.append({
                    'type': 'viewport_test_error',
                    'severity': 'high',
                    'description': f'Error testing {viewport["name"]} viewport: {str(e)}'
                })
        
        return {
            'test_name': test_name,
            'url': self.base_url,
            'viewport': 'multiple',
            'bugs_found': len(bugs) > 0,
            'bugs': bugs,
            'screenshots': screenshots
        }
    
    def run_all_tests(self) -> List[Dict]:
        """Run all test cases."""
        print("Starting comprehensive Sudoku game testing...")
        
        if not self.driver:
            self.setup_driver()
        
        test_results = []
        
        # Run individual tests
        tests = [
            self.test_game_initialization,
            self.test_difficulty_selection,
            self.test_cell_interaction,
            self.test_game_controls,
            self.test_responsive_design
        ]
        
        for test_func in tests:
            try:
                result = test_func()
                test_results.append(result)
                print(f"✅ {result['test_name']}: {'PASSED' if not result['bugs_found'] else 'FAILED'}")
            except Exception as e:
                print(f"❌ {test_func.__name__}: ERROR - {str(e)}")
                test_results.append({
                    'test_name': test_func.__name__,
                    'url': self.base_url,
                    'viewport': 'default',
                    'bugs_found': True,
                    'bugs': [{
                        'type': 'test_failure',
                        'severity': 'high',
                        'description': f'Test function failed: {str(e)}'
                    }],
                    'screenshots': [],
                    'error': str(e)
                })
        
        return test_results
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None
        self.detector.cleanup()


def main():
    """Main function for running Sudoku tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sudoku Game Test Automation')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='URL of the Sudoku game')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--test', choices=[
        'initialization', 'difficulty', 'interaction', 'controls', 'responsive', 'all'
    ], default='all', help='Specific test to run')
    
    args = parser.parse_args()
    
    # Load configuration if provided
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    automation = SudokuTestAutomation(args.url, config)
    
    try:
        if args.test == 'all':
            test_results = automation.run_all_tests()
        else:
            automation.setup_driver()
            test_map = {
                'initialization': automation.test_game_initialization,
                'difficulty': automation.test_difficulty_selection,
                'interaction': automation.test_cell_interaction,
                'controls': automation.test_game_controls,
                'responsive': automation.test_responsive_design
            }
            result = test_map[args.test]()
            test_results = [result]
        
        # Generate bug report
        report_path = automation.detector.generate_bug_report(test_results)
        print(f"\n🎯 Testing completed!")
        print(f"📊 Total tests: {len(test_results)}")
        print(f"🐛 Failed tests: {sum(1 for r in test_results if r['bugs_found'])}")
        print(f"📄 Report saved to: {report_path}")
    
    finally:
        automation.cleanup()


if __name__ == "__main__":
    main()