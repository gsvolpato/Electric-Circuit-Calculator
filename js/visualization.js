const canvas = document.getElementById('circuit-canvas');
const ctx = canvas.getContext('2d');

// Set canvas size with high DPI support
function setupCanvas() {
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    
    ctx.scale(dpr, dpr);
    ctx.strokeStyle = '#e6e600';
    ctx.fillStyle = '#e6e600';
    ctx.lineWidth = 2;
    ctx.font = '14px Courier New';
}

function drawCircuit() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const centerX = canvas.width / 3;
    const centerY = canvas.height / 3;
    
    // Draw CS1 (5A source)
    drawCurrentSource(centerX, centerY - 80, 'CS1', '5A', true);
    
    // Draw main circuit structure
    ctx.beginPath();
    ctx.moveTo(centerX, centerY - 60);
    ctx.lineTo(centerX, centerY);
    ctx.lineTo(centerX - 80, centerY);
    ctx.lineTo(centerX - 80, centerY + 120);
    ctx.lineTo(centerX + 80, centerY + 120);
    ctx.lineTo(centerX + 80, centerY);
    ctx.lineTo(centerX, centerY);
    ctx.stroke();
    
    // Draw R1 (2Ω)
    drawResistor(centerX - 80, centerY + 40, 'R1', '2Ω', true);
    
    // Draw R2 (4Ω)
    drawResistor(centerX, centerY - 30, 'R2', '4Ω', false);
    
    // Draw R3 (6Ω)
    drawResistor(centerX + 80, centerY + 40, 'R3', '6Ω', true);
    
    // Draw CS2 (10A source)
    drawCurrentSource(centerX + 80, centerY + 80, 'CS2', '10A', false);
    
    // Draw node numbers
    ctx.fillText('1', centerX - 15, centerY - 5);
    ctx.fillText('2', centerX + 65, centerY - 5);
}

function drawCurrentSource(x, y, label, value, down) {
    ctx.beginPath();
    ctx.arc(x, y, 15, 0, 2 * Math.PI);
    ctx.stroke();
    
    // Draw arrow
    ctx.beginPath();
    if (down) {
        ctx.moveTo(x, y - 10);
        ctx.lineTo(x, y + 10);
        ctx.moveTo(x - 5, y + 5);
        ctx.lineTo(x, y + 10);
        ctx.lineTo(x + 5, y + 5);
    } else {
        ctx.moveTo(x, y + 10);
        ctx.lineTo(x, y - 10);
        ctx.moveTo(x - 5, y - 5);
        ctx.lineTo(x, y - 10);
        ctx.lineTo(x + 5, y - 5);
    }
    ctx.stroke();
    
    ctx.fillText(label, x - 15, y - 25);
    ctx.fillText(value, x - 10, y + 30);
}

function drawResistor(x, y, label, value, vertical) {
    if (vertical) {
        ctx.beginPath();
        ctx.moveTo(x, y - 20);
        ctx.lineTo(x - 10, y - 15);
        ctx.lineTo(x + 10, y - 5);
        ctx.lineTo(x - 10, y + 5);
        ctx.lineTo(x + 10, y + 15);
        ctx.lineTo(x, y + 20);
        ctx.stroke();
        
        ctx.fillText(label, x - 30, y);
        ctx.fillText(value, x + 15, y);
    } else {
        ctx.beginPath();
        ctx.moveTo(x - 20, y);
        ctx.lineTo(x - 15, y - 10);
        ctx.lineTo(x - 5, y + 10);
        ctx.lineTo(x + 5, y - 10);
        ctx.lineTo(x + 15, y + 10);
        ctx.lineTo(x + 20, y);
        ctx.stroke();
        
        ctx.fillText(label, x - 5, y - 15);
        ctx.fillText(value, x - 5, y + 25);
    }
}

window.addEventListener('load', () => {
    setupCanvas();
    drawCircuit();
});

window.addEventListener('resize', () => {
    setupCanvas();
    drawCircuit();
}); 