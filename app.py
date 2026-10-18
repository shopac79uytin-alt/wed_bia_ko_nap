import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pro 8 Ball Pool - Streamlit",
    page_icon="🎱",
    layout="centered",
)

st.title("🎱 Pro 8 Ball Pool (Streamlit Edition)")
st.write(
    "Trò chơi bida 8 bi mượt mà. Kéo chuột từ bi cái ngược hướng ngắm để lấy"
    " lực, sau đó thả ra để đánh!"
)

pool_game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>8 Ball Pool</title>
    <style>
        body {
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 10px;
        }
        #gameContainer {
            position: relative;
            display: inline-block;
            box-shadow: 0 8px 25px rgba(0,0,0,0.8);
            border-radius: 10px;
            overflow: hidden;
            border: 4px solid #3d2817;
        }
        canvas {
            background: #0b5c1e;
            display: block;
            cursor: crosshair;
        }
        #uiPanel {
            margin-top: 10px;
            background: #222222;
            padding: 10px 15px;
            border-radius: 6px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            font-size: 13px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .btn {
            background-color: #d9534f;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn:hover { background-color: #c9302c; }
    </style>
</head>
<body>

<div id="gameContainer">
    <canvas id="poolCanvas" width="800" height="400"></canvas>
</div>

<div id="uiPanel">
    <div><b>Lượt:</b> <span id="turnInfo">Người chơi 1</span></div>
    <div><b>Trạng thái:</b> <span id="statusInfo">Sẵn sàng</span></div>
    <button class="btn" onclick="resetGame()">Làm mới</button>
</div>

<script>
const canvas = document.getElementById('poolCanvas');
const ctx = canvas.getContext('2d');

const TABLE_X = 50;
const TABLE_Y = 50;
const TABLE_W = 700;
const TABLE_H = 300;
const BALL_RADIUS = 10;
const FRICTION = 0.985;
const ELASTICITY = 0.85;

const pockets = [
    {x: TABLE_X, y: TABLE_Y},
    {x: TABLE_X + TABLE_W / 2, y: TABLE_Y - 2},
    {x: TABLE_X + TABLE_W, y: TABLE_Y},
    {x: TABLE_X, y: TABLE_Y + TABLE_H},
    {x: TABLE_X + TABLE_W / 2, y: TABLE_Y + TABLE_H + 2},
    {x: TABLE_X + TABLE_W, y: TABLE_Y + TABLE_H}
];

let balls = [];
let gameState = 'AIMING'; 
let cueAngle = 0;
let cuePower = 0;
let isDragging = false;
let startX = 0, startY = 0;
let currentPlayer = 1;
let message = "Hãy kéo chuột để ngắm và đánh bi.";

function initBalls() {
    balls = [];
    balls.push({id: 0, x: 220, y: 200, vx: 0, vy: 0, color: '#ffffff', type: 'cue', number: 0, active: true});

    const startXPos = 550;
    const startYPos = 200;
    const spacing = BALL_RADIUS * 2 + 1;
    let numbers = [1, 2, 8, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 3];
    let numIdx = 0;

    for (let col = 0; col < 5; col++) {
        for (let row = 0; row <= col; row++) {
            let bx = startXPos + col * spacing * 0.866;
            let by = startYPos + (row - col / 2) * spacing;
            let num = numbers[numIdx++];
            let type = (num === 8) ? 'black' : (num < 8 ? 'solid' : 'stripe');
            let color = getColor(num);
            balls.push({id: num, x: bx, y: by, vx: 0, vy: 0, color: color, type: type, number: num, active: true});
        }
    }
}

function getColor(num) {
    const colors = {
        1: '#f1c40f', 2: '#2980b9', 3: '#e74c3c', 4: '#8e44ad',
        5: '#d35400', 6: '#27ae60', 7: '#7f8c8d', 8: '#111111',
        9: '#f1c40f', 10: '#2980b9', 11: '#e74c3c', 12: '#8e44ad',
        13: '#d35400', 14: '#27ae60', 15: '#7f8c8d'
    };
    return colors[num] || '#ffffff';
}

function resetGame() {
    initBalls();
    gameState = 'AIMING';
    currentPlayer = 1;
    message = "Đã làm mới bàn bida.";
    updateUI();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Thành băng
    ctx.fillStyle = '#3d2817';
    ctx.fillRect(TABLE_X - 16, TABLE_Y - 16, TABLE_W + 32, TABLE_H + 32);

    // Mặt bàn
    ctx.fillStyle = '#0b5c1e';
    ctx.fillRect(TABLE_X, TABLE_Y, TABLE_W, TABLE_H);

    // Lỗ
    ctx.fillStyle = '#050505';
    pockets.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 14, 0, Math.PI * 2);
        ctx.fill();
    });

    // Bi
    balls.forEach(b => {
        if (!b.active) return;
        ctx.save();
        ctx.beginPath();
        ctx.arc(b.x, b.y, BALL_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = b.color;
        ctx.shadowColor = 'rgba(0,0,0,0.5)';
        ctx.shadowBlur = 5;
        ctx.fill();
        ctx.restore();

        if (b.type === 'stripe') {
            ctx.beginPath();
            ctx.arc(b.x, b.y, BALL_RADIUS * 0.55, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
        }

        if (b.number > 0) {
            ctx.fillStyle = (b.number === 8 || b.type === 'stripe') ? '#000' : '#fff';
            ctx.font = 'bold 9px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(b.number, b.x, b.y);
        }
    });

    let cueBall = balls.find(b => b.type === 'cue');
    if (gameState === 'AIMING' && cueBall && cueBall.active) {
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(cueBall.x, cueBall.y);
        ctx.lineTo(cueBall.x + Math.cos(cueAngle) * 180, cueBall.y + Math.sin(cueAngle) * 180);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.save();
        ctx.translate(cueBall.x, cueBall.y);
        ctx.rotate(cueAngle + Math.PI);
        let offset = 15 + cuePower * 1.5;
        ctx.fillStyle = '#d2b48c';
        ctx.fillRect(offset, -3, 200, 6);
        ctx.restore();
    }
}

function updatePhysics() {
    if (gameState !== 'SHOOTING') return;

    let stopped = true;

    balls.forEach(b => {
        if (!b.active) return;
        b.x += b.vx;
        b.y += b.vy;
        b.vx *= FRICTION;
        b.vy *= FRICTION;

        if (Math.abs(b.vx) < 0.04) b.vx = 0;
        if (Math.abs(b.vy) < 0.04) b.vy = 0;

        if (b.vx !== 0 || b.vy !== 0) stopped = false;

        // Thành bàn
        if (b.x - BALL_RADIUS < TABLE_X) { b.x = TABLE_X + BALL_RADIUS; b.vx *= -ELASTICITY; }
        if (b.x + BALL_RADIUS > TABLE_X + TABLE_W) { b.x = TABLE_X + TABLE_W - BALL_RADIUS; b.vx *= -ELASTICITY; }
        if (b.y - BALL_RADIUS < TABLE_Y) { b.y = TABLE_Y + BALL_RADIUS; b.vy *= -ELASTICITY; }
        if (b.y + BALL_RADIUS > TABLE_Y + TABLE_H) { b.y = TABLE_Y + TABLE_H - BALL_RADIUS; b.vy *= -ELASTICITY; }

        // Lỗ
        pockets.forEach(p => {
            if (Math.hypot(b.x - p.x, b.y - p.y) < 15) {
                b.active = false;
                b.vx = 0; b.vy = 0;
                if (b.type === 'cue') {
                    message = "Bi cái rơi vào lỗ (Foul)!";
                } else if (b.type === 'black') {
                    message = `Người chơi ${currentPlayer} đưa bi số 8 vào lỗ! Kết thúc trận.`;
                    gameState = 'GAMEOVER';
                } else {
                    message = `Bi số ${b.number} đã vào lỗ!`;
                }
            }
        });
    });

    // Va chạm bi
    for (let i = 0; i < balls.length; i++) {
        for (let j = i + 1; j < balls.length; j++) {
            let b1 = balls[i], b2 = balls[j];
            if (!b1.active || !b2.active) continue;

            let dx = b2.x - b1.x, dy = b2.y - b1.y;
            let dist = Math.hypot(dx, dy);

            if (dist < BALL_RADIUS * 2) {
                let overlap = (BALL_RADIUS * 2 - dist) / 2;
                let nx = dx / dist, ny = dy / dist;
                b1.x -= nx * overlap; b1.y -= ny * overlap;
                b2.x += nx * overlap; b2.y += ny * overlap;

                let kx = b1.vx - b2.vx, ky = b1.vy - b2.vy;
                let p = (nx * kx + ny * ky);
                b1.vx -= p * nx; b1.vy -= p * ny;
                b2.vx += p * nx; b2.vy += p * ny;
            }
        }
    }

    if (stopped) {
        gameState = 'AIMING';
        let cue = balls.find(b => b.type === 'cue');
        if (!cue.active) {
            cue.x = 220; cue.y = 200; cue.vx = 0; cue.vy = 0; cue.active = true;
            currentPlayer = currentPlayer === 1 ? 2 : 1;
        }
        updateUI();
    }
}

function updateUI() {
    document.getElementById('turnInfo').innerText = `Người chơi ${currentPlayer}`;
    document.getElementById('statusInfo').innerText = message;
}

canvas.addEventListener('mousedown', (e) => {
    if (gameState !== 'AIMING') return;
    isDragging = true;
    let rect = canvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
});

canvas.addEventListener('mousemove', (e) => {
    if (gameState !== 'AIMING') return;
    let rect = canvas.getBoundingClientRect();
    let mx = e.clientX - rect.left, my = e.clientY - rect.top;
    let cueBall = balls.find(b => b.type === 'cue');
    if (cueBall) {
        cueAngle = Math.atan2(my - cueBall.y, mx - cueBall.x);
        if (isDragging) {
            let dist = Math.hypot(mx - startX, my - startY);
            cuePower = Math.min(Math.max(dist, 0), 50);
        }
    }
});

canvas.addEventListener('mouseup', () => {
    if (!isDragging || gameState !== 'AIMING') return;
    isDragging = false;
    if (cuePower > 2) {
        let cueBall = balls.find(b => b.type === 'cue');
        cueBall.vx = -Math.cos(cueAngle) * (cuePower * 0.45);
        cueBall.vy = -Math.sin(cueAngle) * (cuePower * 0.45);
        gameState = 'SHOOTING';
        message = "Đang đánh...";
    }
    cuePower = 0;
    updateUI();
});

function loop() {
    updatePhysics();
    draw();
    requestAnimationFrame(loop);
}

initBalls();
loop();
</script>

</body>
</html>
"""

components.html(pool_game_html, height=520, scrolling=False)
