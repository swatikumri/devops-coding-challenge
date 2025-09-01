/**
 * Configuration constants for the Sudoku game
 */
const SUDOKU_CONFIG = {
    BOARD_SIZE: 9,
    GRID_SIZE: 81,
    DIFFICULTY_LEVELS: {
        easy: { cellsToRemove: 40, maxHints: 5 },
        medium: { cellsToRemove: 50, maxHints: 3 },
        hard: { cellsToRemove: 60, maxHints: 2 },
        expert: { cellsToRemove: 70, maxHints: 1 }
    },
    MAX_MOVE_HISTORY: 50,
    TIMER_INTERVAL: 1000,
    MESSAGE_TIMEOUT: 3000,
    TOAST_TIMEOUT: 3000,
    ANIMATION_TIMEOUT: 1000
};

/**
 * Enhanced Sudoku Game class with performance optimizations and error handling
 */
class SudokuGame {
    /**
     * Initialize the Sudoku game
     */
    constructor() {
        try {
            // Game state
            this.board = Array(SUDOKU_CONFIG.BOARD_SIZE).fill().map(() => Array(SUDOKU_CONFIG.BOARD_SIZE).fill(0));
            this.solution = Array(SUDOKU_CONFIG.BOARD_SIZE).fill().map(() => Array(SUDOKU_CONFIG.BOARD_SIZE).fill(0));
            this.originalBoard = Array(SUDOKU_CONFIG.BOARD_SIZE).fill().map(() => Array(SUDOKU_CONFIG.BOARD_SIZE).fill(0));
            
            // UI state
            this.selectedCell = null;
            this.cellElements = null;
            this.isGameActive = false;
            
            // Timer state
            this.startTime = null;
            this.timerInterval = null;
            
            // Game features
            this.hintsUsed = 0;
            this.maxHints = SUDOKU_CONFIG.DIFFICULTY_LEVELS.medium.maxHints;
            this.moveHistory = [];
            this.moveIndex = -1;
            
            // Settings and stats
            this.gameStats = this.loadStats();
            this.settings = this.loadSettings();
            this.currentTheme = localStorage.getItem('theme') || 'light';
            
            // Event listener references for cleanup
            this.eventListeners = new Map();
            
            this.initializeGame();
            this.setupEventListeners();
            this.applyTheme();
            
        } catch (error) {
            this.handleError(error, 'constructor');
            this.showFallbackError();
        }
    }

    /**
     * Initialize the game components
     */
    initializeGame() {
        try {
            this.createBoard();
            this.generateNewGame();
            this.updateDisplay();
            this.startTimer();
            this.isGameActive = true;
        } catch (error) {
            this.handleError(error, 'initializeGame');
            this.showMessage('Failed to initialize game. Please refresh the page.', 'error');
        }
    }

    /**
     * Create the Sudoku board DOM elements with optimized performance
     */
    createBoard() {
        try {
            const boardElement = this.getElementById('sudoku-board');
            boardElement.innerHTML = '';
            
            // Create document fragment for better performance
            const fragment = document.createDocumentFragment();
            const cells = [];
            
            for (let i = 0; i < SUDOKU_CONFIG.GRID_SIZE; i++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                cell.dataset.index = i;
                cell.setAttribute('role', 'gridcell');
                cell.setAttribute('tabindex', '0');
                cell.setAttribute('aria-label', `Cell ${Math.floor(i / 9) + 1}, ${(i % 9) + 1}`);
                
                const clickHandler = () => this.selectCell(i);
                const keydownHandler = (e) => this.handleCellKeydown(e, i);
                
                cell.addEventListener('click', clickHandler);
                cell.addEventListener('keydown', keydownHandler);
                
                // Store event listeners for cleanup
                this.eventListeners.set(`cell-${i}-click`, { element: cell, event: 'click', handler: clickHandler });
                this.eventListeners.set(`cell-${i}-keydown`, { element: cell, event: 'keydown', handler: keydownHandler });
                
                fragment.appendChild(cell);
                cells.push(cell);
            }
            
            boardElement.appendChild(fragment);
            
            // Cache DOM elements for better performance
            this.cellElements = cells;
            
        } catch (error) {
            this.handleError(error, 'createBoard');
            throw new Error('Failed to create game board');
        }
    }

    /**
     * Generate a new Sudoku puzzle with error handling
     */
    generateNewGame() {
        try {
            // Generate a complete solution first
            this.generateSolution();
            
            // Copy solution to board using optimized method
            this.copyBoard(this.board, this.solution);
            
            // Remove numbers based on difficulty
            this.removeNumbers();
            
            // Store original board (given numbers)
            this.copyBoard(this.originalBoard, this.board);
            
        } catch (error) {
            this.handleError(error, 'generateNewGame');
            this.generateFallbackPuzzle();
        }
    }

    generateSolution() {
        // Clear the board
        this.board = Array(9).fill().map(() => Array(9).fill(0));
        
        // Fill diagonal 3x3 boxes first (they are independent)
        this.fillDiagonalBoxes();
        
        // Fill remaining cells
        this.solveSudoku();
    }

    fillDiagonalBoxes() {
        for (let i = 0; i < 9; i += 3) {
            this.fillBox(i, i);
        }
    }

    fillBox(row, col) {
        const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
        this.shuffleArray(numbers);
        
        let index = 0;
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                this.board[row + i][col + j] = numbers[index++];
            }
        }
    }

    shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
    }

    solveSudoku() {
        for (let row = 0; row < 9; row++) {
            for (let col = 0; col < 9; col++) {
                if (this.board[row][col] === 0) {
                    const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9];
                    this.shuffleArray(numbers);
                    
                    for (let num of numbers) {
                        if (this.isValidMove(row, col, num)) {
                            this.board[row][col] = num;
                            
                            if (this.solveSudoku()) {
                                return true;
                            }
                            
                            this.board[row][col] = 0;
                        }
                    }
                    return false;
                }
            }
        }
        return true;
    }

    /**
     * Remove numbers from the completed puzzle based on difficulty
     */
    removeNumbers() {
        try {
            const difficulty = this.getElementById('difficulty-select').value;
            const config = SUDOKU_CONFIG.DIFFICULTY_LEVELS[difficulty] || SUDOKU_CONFIG.DIFFICULTY_LEVELS.medium;
            this.maxHints = config.maxHints;
            
            // Generate all positions more efficiently
            const positions = [];
            for (let i = 0; i < SUDOKU_CONFIG.GRID_SIZE; i++) {
                positions.push([Math.floor(i / SUDOKU_CONFIG.BOARD_SIZE), i % SUDOKU_CONFIG.BOARD_SIZE]);
            }
            
            this.shuffleArray(positions);
            
            // Remove numbers
            for (let i = 0; i < config.cellsToRemove && i < positions.length; i++) {
                const [row, col] = positions[i];
                this.board[row][col] = 0;
            }
            
        } catch (error) {
            this.handleError(error, 'removeNumbers');
            // Use default medium difficulty as fallback
            this.maxHints = SUDOKU_CONFIG.DIFFICULTY_LEVELS.medium.maxHints;
        }
    }

    isValidMove(row, col, num) {
        // Check row
        for (let x = 0; x < 9; x++) {
            if (this.board[row][x] === num) return false;
        }
        
        // Check column
        for (let x = 0; x < 9; x++) {
            if (this.board[x][col] === num) return false;
        }
        
        // Check 3x3 box
        const startRow = Math.floor(row / 3) * 3;
        const startCol = Math.floor(col / 3) * 3;
        
        for (let i = 0; i < 3; i++) {
            for (let j = 0; j < 3; j++) {
                if (this.board[startRow + i][startCol + j] === num) return false;
            }
        }
        
        return true;
    }

    selectCell(index) {
        // Remove previous selection
        if (this.selectedCell !== null) {
            const prevCell = document.querySelector(`[data-index="${this.selectedCell}"]`);
            if (prevCell && !prevCell.classList.contains('given')) {
                prevCell.classList.remove('selected');
            }
        }
        
        this.selectedCell = index;
        const cell = document.querySelector(`[data-index="${index}"]`);
        
        if (!cell.classList.contains('given')) {
            cell.classList.add('selected');
        }
    }

    /**
     * Update the display with optimized DOM access
     */
    updateDisplay() {
        try {
            if (!this.isGameStateValid()) {
                console.warn('Invalid game state during display update');
                return;
            }
            
            // Use requestAnimationFrame for smooth updates
            requestAnimationFrame(() => {
                for (let i = 0; i < SUDOKU_CONFIG.BOARD_SIZE; i++) {
                    for (let j = 0; j < SUDOKU_CONFIG.BOARD_SIZE; j++) {
                        const index = i * SUDOKU_CONFIG.BOARD_SIZE + j;
                        const cell = this.getCellElement(index);
                        
                        if (!cell) continue;
                        
                        const value = this.board[i][j];
                        
                        cell.textContent = value === 0 ? '' : value;
                        cell.className = 'cell';
                        
                        if (this.originalBoard[i][j] !== 0) {
                            cell.classList.add('given');
                        }
                    }
                }
                
                this.updateProgress();
                this.updateHintsDisplay();
            });
            
        } catch (error) {
            this.handleError(error, 'updateDisplay');
        }
    }

    setupEventListeners() {
        // Number pad buttons
        document.querySelectorAll('.number-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const number = parseInt(btn.dataset.number);
                this.inputNumber(number);
            });
        });
        
        // Keyboard input
        document.addEventListener('keydown', (e) => {
            if (e.key >= '1' && e.key <= '9') {
                this.inputNumber(parseInt(e.key));
            } else if (e.key === '0' || e.key === 'Backspace' || e.key === 'Delete') {
                this.inputNumber(0);
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || 
                      e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                this.moveSelection(e.key);
            }
        });
        
        // Action buttons
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.newGame();
        });
        
        document.getElementById('hint-btn').addEventListener('click', () => {
            this.getHint();
        });
        
        document.getElementById('check-btn').addEventListener('click', () => {
            this.checkSolution();
        });
        
        document.getElementById('solve-btn').addEventListener('click', () => {
            this.solveGame();
        });
        
        // Difficulty change
        document.getElementById('difficulty-select').addEventListener('change', () => {
            this.newGame();
        });
    }

    inputNumber(number) {
        if (this.selectedCell === null) {
            this.showMessage('Please select a cell first!', 'error');
            return;
        }
        
        const row = Math.floor(this.selectedCell / 9);
        const col = this.selectedCell % 9;
        
        // Don't allow editing given numbers
        if (this.originalBoard[row][col] !== 0) {
            this.showMessage('Cannot edit given numbers!', 'error');
            return;
        }
        
        // Clear the cell
        if (number === 0) {
            this.board[row][col] = 0;
        } else {
            // Check if the move is valid
            if (this.isValidMove(row, col, number)) {
                this.board[row][col] = number;
            } else {
                this.showMessage('Invalid move!', 'error');
                const cell = document.querySelector(`[data-index="${this.selectedCell}"]`);
                cell.classList.add('error');
                setTimeout(() => cell.classList.remove('error'), 1000);
                return;
            }
        }
        
        this.updateDisplay();
        this.selectCell(this.selectedCell); // Re-select the cell
        
        // Check if game is complete
        if (this.isGameComplete()) {
            this.gameWon();
        }
    }

    moveSelection(direction) {
        if (this.selectedCell === null) {
            this.selectedCell = 0;
        } else {
            const row = Math.floor(this.selectedCell / 9);
            const col = this.selectedCell % 9;
            
            switch (direction) {
                case 'ArrowUp':
                    if (row > 0) this.selectedCell -= 9;
                    break;
                case 'ArrowDown':
                    if (row < 8) this.selectedCell += 9;
                    break;
                case 'ArrowLeft':
                    if (col > 0) this.selectedCell -= 1;
                    break;
                case 'ArrowRight':
                    if (col < 8) this.selectedCell += 1;
                    break;
            }
        }
        
        this.selectCell(this.selectedCell);
    }

    newGame() {
        this.stopTimer();
        this.selectedCell = null;
        this.hintsUsed = 0;
        this.generateNewGame();
        this.updateDisplay();
        this.startTimer();
        this.showMessage('New game started!', 'info');
    }

    getHint() {
        if (this.hintsUsed >= this.maxHints) {
            this.showMessage(`You've used all ${this.maxHints} hints!`, 'error');
            return;
        }
        
        // Find empty cells
        const emptyCells = [];
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (this.board[i][j] === 0) {
                    emptyCells.push([i, j]);
                }
            }
        }
        
        if (emptyCells.length === 0) {
            this.showMessage('No empty cells to hint!', 'info');
            return;
        }
        
        // Pick a random empty cell
        const [row, col] = emptyCells[Math.floor(Math.random() * emptyCells.length)];
        const correctNumber = this.solution[row][col];
        
        this.board[row][col] = correctNumber;
        this.hintsUsed++;
        
        this.updateDisplay();
        
        const index = row * 9 + col;
        const cell = document.querySelector(`[data-index="${index}"]`);
        cell.classList.add('hint');
        setTimeout(() => cell.classList.remove('hint'), 2000);
        
        this.showMessage(`Hint used! (${this.hintsUsed}/${this.maxHints})`, 'info');
        
        // Check if game is complete
        if (this.isGameComplete()) {
            this.gameWon();
        }
    }

    checkSolution() {
        let errors = 0;
        const errorCells = [];
        
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (this.board[i][j] !== 0 && this.board[i][j] !== this.solution[i][j]) {
                    errors++;
                    errorCells.push(i * 9 + j);
                }
            }
        }
        
        if (errors === 0) {
            this.showMessage('Great! No errors found!', 'success');
        } else {
            this.showMessage(`Found ${errors} error(s)!`, 'error');
            
            // Highlight error cells
            errorCells.forEach(index => {
                const cell = document.querySelector(`[data-index="${index}"]`);
                cell.classList.add('error');
                setTimeout(() => cell.classList.remove('error'), 2000);
            });
        }
    }

    solveGame() {
        if (confirm('Are you sure you want to solve the entire puzzle?')) {
            for (let i = 0; i < 9; i++) {
                for (let j = 0; j < 9; j++) {
                    this.board[i][j] = this.solution[i][j];
                }
            }
            this.updateDisplay();
            this.stopTimer();
            this.showMessage('Puzzle solved!', 'info');
        }
    }

    isGameComplete() {
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (this.board[i][j] === 0) {
                    return false;
                }
            }
        }
        return true;
    }

    gameWon() {
        this.stopTimer();
        const timeElapsed = this.getTimeElapsed();
        this.showMessage(`🎉 Congratulations! You solved it in ${timeElapsed}!`, 'success');
        
        // Add confetti effect (simple version)
        this.createConfetti();
    }

    createConfetti() {
        const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
        
        for (let i = 0; i < 50; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.style.position = 'fixed';
                confetti.style.width = '10px';
                confetti.style.height = '10px';
                confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                confetti.style.left = Math.random() * 100 + 'vw';
                confetti.style.top = '-10px';
                confetti.style.borderRadius = '50%';
                confetti.style.pointerEvents = 'none';
                confetti.style.zIndex = '9999';
                confetti.style.animation = 'fall 3s linear forwards';
                
                document.body.appendChild(confetti);
                
                setTimeout(() => {
                    confetti.remove();
                }, 3000);
            }, i * 50);
        }
        
        // Add CSS animation for confetti
        if (!document.getElementById('confetti-style')) {
            const style = document.createElement('style');
            style.id = 'confetti-style';
            style.textContent = `
                @keyframes fall {
                    to {
                        transform: translateY(100vh) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    startTimer() {
        this.startTime = Date.now();
        this.timerInterval = setInterval(() => {
            const elapsed = this.getTimeElapsed();
            document.getElementById('timer').textContent = elapsed;
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    getTimeElapsed() {
        if (!this.startTime) return '00:00';
        
        const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    showMessage(text, type) {
        const messageElement = document.getElementById('message');
        messageElement.textContent = text;
        messageElement.className = `message ${type} show`;
        
        setTimeout(() => {
            messageElement.classList.remove('show');
        }, 3000);
    }

    // New UI Methods
    updateProgress() {
        let filledCells = 0;
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                if (this.board[i][j] !== 0) {
                    filledCells++;
                }
            }
        }
        const progress = Math.round((filledCells / 81) * 100);
        document.getElementById('progress-percent').textContent = `${progress}%`;
    }

    updateHintsDisplay() {
        document.getElementById('hints-count').textContent = `${this.hintsUsed}/${this.maxHints}`;
    }

    handleCellKeydown(e, index) {
        if (e.key >= '1' && e.key <= '9') {
            e.preventDefault();
            this.inputNumber(parseInt(e.key));
        } else if (e.key === '0' || e.key === 'Backspace' || e.key === 'Delete') {
            e.preventDefault();
            this.inputNumber(0);
        }
    }

    showBoardOverlay(show = true) {
        const overlay = document.getElementById('board-overlay');
        if (show) {
            overlay.style.display = 'flex';
        } else {
            overlay.style.display = 'none';
        }
    }

    // Statistics Management
    loadStats() {
        const defaultStats = {
            gamesPlayed: 0,
            gamesWon: 0,
            bestTime: null,
            totalTime: 0,
            hintsUsed: 0
        };
        
        try {
            const saved = localStorage.getItem('sudoku-stats');
            return saved ? { ...defaultStats, ...JSON.parse(saved) } : defaultStats;
        } catch (error) {
            console.warn('Failed to load stats:', error);
            return defaultStats;
        }
    }

    saveStats() {
        try {
            localStorage.setItem('sudoku-stats', JSON.stringify(this.gameStats));
        } catch (error) {
            console.warn('Failed to save stats:', error);
        }
    }

    updateStatsDisplay() {
        document.getElementById('games-played').textContent = this.gameStats.gamesPlayed;
        document.getElementById('best-time').textContent = this.gameStats.bestTime || '--:--';
        
        const avgTime = this.gameStats.gamesPlayed > 0 
            ? Math.round(this.gameStats.totalTime / this.gameStats.gamesPlayed)
            : 0;
        document.getElementById('avg-time').textContent = this.formatTime(avgTime);
        
        const winRate = this.gameStats.gamesPlayed > 0 
            ? Math.round((this.gameStats.gamesWon / this.gameStats.gamesPlayed) * 100)
            : 0;
        document.getElementById('win-rate').textContent = `${winRate}%`;
    }

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    // Settings Management
    loadSettings() {
        const defaultSettings = {
            autoCheck: true,
            showTimer: true,
            soundEffects: false,
            animations: true
        };
        
        try {
            const saved = localStorage.getItem('sudoku-settings');
            return saved ? { ...defaultSettings, ...JSON.parse(saved) } : defaultSettings;
        } catch (error) {
            console.warn('Failed to load settings:', error);
            return defaultSettings;
        }
    }

    saveSettings() {
        try {
            localStorage.setItem('sudoku-settings', JSON.stringify(this.settings));
        } catch (error) {
            console.warn('Failed to save settings:', error);
        }
    }

    applySettings() {
        // Apply settings to UI
        document.getElementById('auto-check').checked = this.settings.autoCheck;
        document.getElementById('show-timer').checked = this.settings.showTimer;
        document.getElementById('sound-effects').checked = this.settings.soundEffects;
        document.getElementById('animations').checked = this.settings.animations;
        
        // Apply timer visibility
        const timerCard = document.querySelector('.timer-card');
        timerCard.style.display = this.settings.showTimer ? 'flex' : 'none';
    }

    // Theme Management
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        const themeIcon = document.querySelector('.theme-icon');
        themeIcon.textContent = this.currentTheme === 'dark' ? '☀️' : '🌙';
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
    }

    // Move History (Undo/Redo)
    /**
     * Save move to history with size limit
     */
    saveMove(row, col, oldValue, newValue) {
        try {
            // Validate inputs
            if (!this.validateNumberInput(oldValue) && oldValue !== 0) return;
            if (!this.validateNumberInput(newValue) && newValue !== 0) return;
            if (row < 0 || row >= SUDOKU_CONFIG.BOARD_SIZE || col < 0 || col >= SUDOKU_CONFIG.BOARD_SIZE) return;
            
            // Remove any moves after current index
            this.moveHistory = this.moveHistory.slice(0, this.moveIndex + 1);
            
            // Add new move
            this.moveHistory.push({ row, col, oldValue, newValue, timestamp: Date.now() });
            this.moveIndex++;
            
            // Limit history size
            if (this.moveHistory.length > SUDOKU_CONFIG.MAX_MOVE_HISTORY) {
                this.moveHistory.shift();
                this.moveIndex--;
            }
        } catch (error) {
            this.handleError(error, 'saveMove');
        }
    }

    undo() {
        if (this.moveIndex >= 0) {
            const move = this.moveHistory[this.moveIndex];
            this.board[move.row][move.col] = move.oldValue;
            this.moveIndex--;
            this.updateDisplay();
            this.selectCell(move.row * 9 + move.col);
            this.showToast('Move undone', 'info');
        } else {
            this.showToast('No moves to undo', 'warning');
        }
    }

    redo() {
        if (this.moveIndex < this.moveHistory.length - 1) {
            this.moveIndex++;
            const move = this.moveHistory[this.moveIndex];
            this.board[move.row][move.col] = move.newValue;
            this.updateDisplay();
            this.selectCell(move.row * 9 + move.col);
            this.showToast('Move redone', 'info');
        } else {
            this.showToast('No moves to redo', 'warning');
        }
    }

    // Toast Notifications
    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        toastContainer.appendChild(toast);
        
        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove after delay
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Enhanced Game Methods
    newGame() {
        this.showBoardOverlay(true);
        
        setTimeout(() => {
            this.stopTimer();
            this.selectedCell = null;
            this.hintsUsed = 0;
            this.moveHistory = [];
            this.moveIndex = -1;
            this.generateNewGame();
            this.updateDisplay();
            this.startTimer();
            this.showBoardOverlay(false);
            this.showMessage('New game started!', 'info');
        }, 1000);
    }

    gameWon() {
        this.stopTimer();
        const timeElapsed = this.getTimeElapsed();
        const timeInSeconds = Math.floor((Date.now() - this.startTime) / 1000);
        
        // Update statistics
        this.gameStats.gamesPlayed++;
        this.gameStats.gamesWon++;
        this.gameStats.totalTime += timeInSeconds;
        this.gameStats.hintsUsed += this.hintsUsed;
        
        if (!this.gameStats.bestTime || timeInSeconds < this.gameStats.bestTime) {
            this.gameStats.bestTime = timeInSeconds;
        }
        
        this.saveStats();
        this.updateStatsDisplay();
        
        this.showMessage(`🎉 Congratulations! You solved it in ${timeElapsed}!`, 'success');
        this.createConfetti();
        this.showToast('Puzzle completed!', 'success');
    }

    // Modal Management
    openStatsPanel() {
        this.updateStatsDisplay();
        document.getElementById('stats-panel').classList.add('open');
    }

    closeStatsPanel() {
        document.getElementById('stats-panel').classList.remove('open');
    }

    openSettingsModal() {
        this.applySettings();
        document.getElementById('settings-modal').classList.add('open');
    }

    closeSettingsModal() {
        document.getElementById('settings-modal').classList.remove('open');
    }

    // Enhanced Event Listeners
    setupEventListeners() {
        // Number pad buttons
        document.querySelectorAll('.number-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const number = parseInt(btn.dataset.number);
                this.inputNumber(number);
            });
        });
        
        // Keyboard input
        document.addEventListener('keydown', (e) => {
            if (e.key >= '1' && e.key <= '9') {
                this.inputNumber(parseInt(e.key));
            } else if (e.key === '0' || e.key === 'Backspace' || e.key === 'Delete') {
                this.inputNumber(0);
            } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown' || 
                      e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                this.moveSelection(e.key);
            } else if (e.key === 'h' || e.key === 'H') {
                this.getHint();
            } else if (e.key === 'c' || e.key === 'C') {
                this.checkSolution();
            } else if (e.key === 'n' || e.key === 'N') {
                this.newGame();
            } else if (e.key === 'u' || e.key === 'U') {
                this.undo();
            } else if (e.key === 'r' || e.key === 'R') {
                this.redo();
            }
        });
        
        // Action buttons
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.newGame();
        });
        
        document.getElementById('hint-btn').addEventListener('click', () => {
            this.getHint();
        });
        
        document.getElementById('check-btn').addEventListener('click', () => {
            this.checkSolution();
        });
        
        document.getElementById('solve-btn').addEventListener('click', () => {
            this.solveGame();
        });
        
        document.getElementById('undo-btn').addEventListener('click', () => {
            this.undo();
        });
        
        document.getElementById('redo-btn').addEventListener('click', () => {
            this.redo();
        });
        
        // Difficulty change
        document.getElementById('difficulty-select').addEventListener('change', () => {
            this.newGame();
        });
        
        // Theme toggle
        document.getElementById('theme-toggle').addEventListener('click', () => {
            this.toggleTheme();
        });
        
        // Settings
        document.getElementById('settings-btn').addEventListener('click', () => {
            this.openSettingsModal();
        });
        
        document.getElementById('close-settings').addEventListener('click', () => {
            this.closeSettingsModal();
        });
        
        // Statistics
        document.getElementById('close-stats').addEventListener('click', () => {
            this.closeStatsPanel();
        });
        
        // Settings form
        document.getElementById('auto-check').addEventListener('change', (e) => {
            this.settings.autoCheck = e.target.checked;
            this.saveSettings();
        });
        
        document.getElementById('show-timer').addEventListener('change', (e) => {
            this.settings.showTimer = e.target.checked;
            this.saveSettings();
            this.applySettings();
        });
        
        document.getElementById('sound-effects').addEventListener('change', (e) => {
            this.settings.soundEffects = e.target.checked;
            this.saveSettings();
        });
        
        document.getElementById('animations').addEventListener('change', (e) => {
            this.settings.animations = e.target.checked;
            this.saveSettings();
        });
        
        // Modal backdrop clicks
        document.getElementById('settings-modal').addEventListener('click', (e) => {
            if (e.target.id === 'settings-modal') {
                this.closeSettingsModal();
            }
        });
        
        // Keyboard shortcuts for modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeSettingsModal();
                this.closeStatsPanel();
            }
        });
    }

    // Enhanced input method with move history
    inputNumber(number) {
        try {
            // Input validation
            if (!this.validateNumberInput(number)) {
                return;
            }
            
            if (!this.isGameActive) {
                this.showMessage('Game is not active', 'warning');
                return;
            }
            
            if (this.selectedCell === null) {
                this.showMessage('Please select a cell first!', 'error');
                return;
            }
            
            const row = Math.floor(this.selectedCell / SUDOKU_CONFIG.BOARD_SIZE);
            const col = this.selectedCell % SUDOKU_CONFIG.BOARD_SIZE;
            
            // Don't allow editing given numbers
            if (this.originalBoard[row][col] !== 0) {
                this.showMessage('Cannot edit given numbers!', 'error');
                return;
            }
            
            const oldValue = this.board[row][col];
            
            // Clear the cell
            if (number === 0) {
                this.board[row][col] = 0;
            } else {
                // Check if the move is valid
                if (this.isValidMove(row, col, number)) {
                    this.board[row][col] = number;
                } else {
                    this.showMessage('Invalid move!', 'error');
                    const cell = this.getCellElement(this.selectedCell);
                    if (cell) {
                        cell.classList.add('error');
                        setTimeout(() => cell.classList.remove('error'), SUDOKU_CONFIG.ANIMATION_TIMEOUT);
                    }
                    return;
                }
            }
            
            // Save move to history
            this.saveMove(row, col, oldValue, this.board[row][col]);
            
            this.updateDisplay();
            this.selectCell(this.selectedCell); // Re-select the cell
            
            // Auto-check if enabled
            if (this.settings.autoCheck && this.isGameComplete()) {
                this.gameWon();
            }
            
        } catch (error) {
            this.handleError(error, 'inputNumber');
            this.showMessage('Failed to input number', 'error');
        }
    }

    // Utility and Helper Methods
    
    /**
     * Safely get DOM element by ID with error handling
     */
    getElementById(id) {
        const element = document.getElementById(id);
        if (!element) {
            throw new Error(`Element with ID '${id}' not found`);
        }
        return element;
    }
    
    /**
     * Get cell element with bounds checking
     */
    getCellElement(index) {
        if (index < 0 || index >= SUDOKU_CONFIG.GRID_SIZE || !this.cellElements) {
            return null;
        }
        return this.cellElements[index];
    }
    
    /**
     * Validate number input
     */
    validateNumberInput(number) {
        if (!Number.isInteger(number) || number < 0 || number > SUDOKU_CONFIG.BOARD_SIZE) {
            console.warn('Invalid number input:', number);
            return false;
        }
        return true;
    }
    
    /**
     * Efficiently copy one board to another
     */
    copyBoard(destination, source) {
        for (let i = 0; i < SUDOKU_CONFIG.BOARD_SIZE; i++) {
            for (let j = 0; j < SUDOKU_CONFIG.BOARD_SIZE; j++) {
                destination[i][j] = source[i][j];
            }
        }
    }
    
    /**
     * Generate a simple fallback puzzle if generation fails
     */
    generateFallbackPuzzle() {
        console.warn('Using fallback puzzle generation');
        
        // Simple hardcoded puzzle as fallback
        const fallbackPuzzle = [
            [5,3,0,0,7,0,0,0,0],
            [6,0,0,1,9,5,0,0,0],
            [0,9,8,0,0,0,0,6,0],
            [8,0,0,0,6,0,0,0,3],
            [4,0,0,8,0,3,0,0,1],
            [7,0,0,0,2,0,0,0,6],
            [0,6,0,0,0,0,2,8,0],
            [0,0,0,4,1,9,0,0,5],
            [0,0,0,0,8,0,0,7,9]
        ];
        
        const fallbackSolution = [
            [5,3,4,6,7,8,9,1,2],
            [6,7,2,1,9,5,3,4,8],
            [1,9,8,3,4,2,5,6,7],
            [8,5,9,7,6,1,4,2,3],
            [4,2,6,8,5,3,7,9,1],
            [7,1,3,9,2,4,8,5,6],
            [9,6,1,5,3,7,2,8,4],
            [2,8,7,4,1,9,6,3,5],
            [3,4,5,2,8,6,1,7,9]
        ];
        
        this.copyBoard(this.board, fallbackPuzzle);
        this.copyBoard(this.solution, fallbackSolution);
    }
    
    /**
     * Handle errors with context and appropriate user feedback
     */
    handleError(error, context) {
        const errorMessage = `Error in ${context}: ${error.message}`;
        console.error(errorMessage, error);
        
        // Don't expose stack traces in production
        if (this.isDevelopment()) {
            console.error(error.stack);
        }
        
        // Track errors for debugging
        this.trackError(context, error.message);
    }
    
    /**
     * Check if running in development mode
     */
    isDevelopment() {
        return window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    }
    
    /**
     * Track errors for debugging (could be sent to analytics)
     */
    trackError(context, message) {
        try {
            const errorLog = JSON.parse(localStorage.getItem('sudoku-errors') || '[]');
            errorLog.push({
                context,
                message,
                timestamp: Date.now(),
                userAgent: navigator.userAgent
            });
            
            // Keep only last 10 errors
            if (errorLog.length > 10) {
                errorLog.splice(0, errorLog.length - 10);
            }
            
            localStorage.setItem('sudoku-errors', JSON.stringify(errorLog));
        } catch (e) {
            console.warn('Failed to track error:', e);
        }
    }
    
    /**
     * Show fallback error message when critical failure occurs
     */
    showFallbackError() {
        const fallbackMessage = document.createElement('div');
        fallbackMessage.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #f56565;
            color: white;
            padding: 20px;
            border-radius: 10px;
            font-family: Arial, sans-serif;
            text-align: center;
            z-index: 10000;
        `;
        fallbackMessage.innerHTML = `
            <h3>Game Error</h3>
            <p>The Sudoku game encountered an error and cannot continue.</p>
            <button onclick="location.reload()" style="margin-top: 10px; padding: 8px 16px; background: white; color: #f56565; border: none; border-radius: 5px; cursor: pointer;">
                Reload Game
            </button>
        `;
        document.body.appendChild(fallbackMessage);
    }
    
    /**
     * Clean up resources and event listeners
     */
    destroy() {
        try {
            this.stopTimer();
            this.isGameActive = false;
            
            // Remove all event listeners
            this.eventListeners.forEach(({ element, event, handler }) => {
                element.removeEventListener(event, handler);
            });
            this.eventListeners.clear();
            
            // Clear any pending timeouts
            // Note: In a real implementation, you'd track timeout IDs
            
            console.log('Sudoku game destroyed successfully');
        } catch (error) {
            console.error('Error during cleanup:', error);
        }
    }
    
    /**
     * Check if the game state is valid
     */
    isGameStateValid() {
        return (
            this.board && 
            this.solution && 
            this.originalBoard &&
            this.board.length === SUDOKU_CONFIG.BOARD_SIZE &&
            this.cellElements &&
            this.cellElements.length === SUDOKU_CONFIG.GRID_SIZE
        );
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SudokuGame();
});