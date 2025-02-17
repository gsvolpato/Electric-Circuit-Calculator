class Terminal {
    constructor() {
        this.input = document.getElementById('terminal-input');
        this.history = document.getElementById('terminal-history');
        this.setupEventListeners();
        this.commandHistory = [];
        this.historyIndex = -1;
    }

    setupEventListeners() {
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                this.handleCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateHistory('up');
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.navigateHistory('down');
            }
        });
    }

    handleCommand() {
        const command = this.input.value.trim();
        if (command) {
            // Add command to history
            this.addToHistory(command);
            
            // Process command
            this.processCommand(command);
            
            // Clear input
            this.input.value = '';
            
            // Add to command history
            this.commandHistory.push(command);
            this.historyIndex = this.commandHistory.length;
        }
    }

    addToHistory(text) {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerHTML = `<span class="terminal-prompt">>> </span><span class="terminal-text">${text}</span>`;
        this.history.appendChild(line);
        this.history.scrollTop = this.history.scrollHeight;
    }

    processCommand(command) {
        // Add your command processing logic here
        // For example:
        const parts = command.toUpperCase().split(' ');
        switch(parts[0]) {
            case 'ADD':
                // Handle ADD command
                break;
            case 'REMOVE':
                // Handle REMOVE command
                break;
            case 'HELP':
                this.addToHistory('Available commands: ADD, REMOVE, HELP');
                break;
            default:
                this.addToHistory('Unknown command. Type HELP for available commands.');
        }
    }

    navigateHistory(direction) {
        if (direction === 'up' && this.historyIndex > 0) {
            this.historyIndex--;
            this.input.value = this.commandHistory[this.historyIndex];
        } else if (direction === 'down' && this.historyIndex < this.commandHistory.length) {
            this.historyIndex++;
            this.input.value = this.commandHistory[this.historyIndex] || '';
        }
    }
}

// Initialize terminal when page loads
document.addEventListener('DOMContentLoaded', () => {
    const terminal = new Terminal();
}); 