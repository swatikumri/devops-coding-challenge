class SudokuGame {
    constructor() {
        this.board = Array(9).fill().map(() => Array(9).fill(0));
        this.solution = Array(9).fill().map(() => Array(9).fill(0));
        this.originalBoard = Array(9).fill().map(() => Array(9).fill(0));
        this.selectedCell = null;
        this.startTime = null;
        this.timerInterval = null;
        this.hintsUsed = 0;
        this.maxHints = 3;
        this.cellElements = null;
        this.moveHistory = [];
        this.moveIndex = -1;
        this.gameStats = this.loadStats();
        this.settings = this.loadSettings();
        this.currentTheme = localStorage.getItem('theme') || 'light';
        
        this.initializeGame();
        this.setupEventListeners();
        this.applyTheme();
    }

    initializeGame() {
        this.createBoard();
        this.generateNewGame();
        this.updateDisplay();
        this.startTimer();
    }

    createBoard() {
        const boardElement = document.getElementById('sudoku-board');
        boardElement.innerHTML = '';
        
        for (let i = 0; i < 81; i++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            cell.dataset.index = i;
            cell.setAttribute('role', 'gridcell');
            cell.setAttribute('tabindex', '0');
            cell.addEventListener('click', () => this.selectCell(i));
            cell.addEventListener('keydown', (e) => this.handleCellKeydown(e, i));
            boardElement.appendChild(cell);
        }
        
        // Cache DOM elements for better performance
        this.cellElements = Array.from(document.querySelectorAll('.cell'));
    }

    generateNewGame() {
        // Generate a complete solution first
        this.generateSolution();
        
        // Copy solution to board
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                this.solution[i][j] = this.board[i][j];
            }
        }
        
        // Remove numbers based on difficulty
        this.removeNumbers();
        
        // Store original board (given numbers)
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                this.originalBoard[i][j] = this.board[i][j];
            }
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

    removeNumbers() {
        const difficulty = document.getElementById('difficulty-select').value;
        const difficultyConfig = {
            easy: { cellsToRemove: 40, maxHints: 5 },
            medium: { cellsToRemove: 50, maxHints: 3 },
            hard: { cellsToRemove: 60, maxHints: 2 },
            expert: { cellsToRemove: 70, maxHints: 1 }
        };
        
        const config = difficultyConfig[difficulty] || difficultyConfig.medium;
        this.maxHints = config.maxHints;
        
        const positions = [];
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                positions.push([i, j]);
            }
        }
        
        this.shuffleArray(positions);
        
        for (let i = 0; i < config.cellsToRemove; i++) {
            const [row, col] = positions[i];
            this.board[row][col] = 0;
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

    updateDisplay() {
        for (let i = 0; i < 9; i++) {
            for (let j = 0; j < 9; j++) {
                const index = i * 9 + j;
                const cell = this.cellElements[index];
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
    saveMove(row, col, oldValue, newValue) {
        // Remove any moves after current index
        this.moveHistory = this.moveHistory.slice(0, this.moveIndex + 1);
        
        // Add new move
        this.moveHistory.push({ row, col, oldValue, newValue });
        this.moveIndex++;
        
        // Limit history size
        if (this.moveHistory.length > 50) {
            this.moveHistory.shift();
            this.moveIndex--;
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
                const cell = this.cellElements[this.selectedCell];
                cell.classList.add('error');
                setTimeout(() => cell.classList.remove('error'), 1000);
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
    }
}

// Initialize the game when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new SudokuGame();
});