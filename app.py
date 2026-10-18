import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pro 8 Ball Pool - Streamlit Edition",
    page_icon="🎱",
    layout="centered",
)

st.title("🎱 Pro 8 Ball Pool (Phiên bản Nâng cấp)")
st.write(
    "Trải nghiệm game bida chuẩn xác: Click và kéo chuột từ bi cái ngược lại để lấy lực, "
    "sau đó thả ra để đánh!"
)

pool_game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>8 Ball Pool Game</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 10px;
        }
        #gameContainer {
            position: relative;
            display: inline-block;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8);
            border-radius: 12px;
            overflow: hidden;
            border: 5px solid #3d2817;
        }
        canvas {
            background: #0d5c22;
            display: block;
            cursor: crosshair;
        }
        #uiPanel {
            margin-top: 12px;
            background: #1e1e1e;
            padding: 12px 20px;
            border-radius: 8px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            font-size: 14px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
        }
        .btn {
            background-color: #d9534f;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
            transition: background 0.2s;
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
    <div><b>Nhóm:</b> <span id="groupInfo">Chưa phân nhóm</span></div>
    <div><b>Trạng thái:</b> <span id="statusInfo">Sẵn sàng ngắm & đánh</span></div>
    <button class="btn" onclick="resetGame()">Làm mới bàn</button>
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
const TABLE_ELASTICITY = 0.85;

// 6 Lỗ bida chuẩn
const pockets = [
    {x: TABLE_X, y: TABLE_Y},
    {x: TABLE_X + TABLE_W / 2, y: TABLE_Y - 2},
    {x: TABLE_X + TABLE_W, y: TABLE_Y},
    {x: TABLE_X, y: TABLE_Y + TABLE_H},
    {x: TABLE_X + TABLE_W / 2, y: TABLE_Y + TABLE_H + 2},
    {x: TABLE_X + TABLE_W, y: TABLE_Y + TABLE_H}
];

let balls = [];
let gameState = 'AIMING'; // AIMING, SHOOTING, GAMEOVER
let cueAngle = 0;
let cuePower = 0;
let isDragging = false;
let dragStartX = 0, dragStartY = 0;

let playerGroup = null; 
let currentTurnPlayer = 1; 
let gameMessage = "Kéo chuột ngược hướng đánh để lấy lực.";

function initBalls() {
    balls = [];
    // Bi cái
    balls.push({id: 0, x: 220, y: 200, vx: 0, vy: 0, color: '#ffffff', type: 'cue', number: 0, active: true});

    // Tam giác 15 bi
    const startX = 550;
    const startY = 200;
    const spacing = BALL_RADIUS * 2 + 1;
    let numbers = [1, 2, 8, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 3];
    let numIdx = 0;

    for (let col = 0; col < 5; col++) {
        for (let row = 0; row <= col; row++) {
            let bx = startX + col * spacing * 0.866;
            let by = startY + (row - col / 2) * spacing;
            let num = numbers[numIdx++];
            let type = (num === 8) ? 'black' : (num < 8 ? 'solid' : 'stripe');
            let color = getBallColor(num);

            balls.push({id: num, x: bx, y: by, vx: 0, vy: 0, color: color, type: type, number: num, active: true});
        }
    }
}

function getBallColor(num) {
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
    playerGroup = null;
    currentTurnPlayer = 1;
    gameMessage = "Đã làm mới bàn bida. Lượt Người chơi 1.";
    updateUI();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Thành băng gỗ
    ctx.fillStyle = '#3d2817';
    ctx.fillRect(TABLE_X - 18, TABLE_Y - 18, TABLE_W + 36, TABLE_H + 36);

    // Mặt vải bàn
    ctx.fillStyle = '#0d5c22';
    ctx.fillRect(TABLE_X, TABLE_Y, TABLE_W, TABLE_H);

    // Lỗ bida
    ctx.fillStyle = '#050505';
    pockets.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 15, 0, Math.PI * 2);
        ctx.fill();
    });

    // Vẽ các bi
    balls.forEach(b => {
        if (!b.active) return;
        
        ctx.save();
        ctx.beginPath();
        ctx.arc(b.x, b.y, BALL_RADIUS, 0, Math.PI * 2);
        ctx.fillStyle = b.color;
        ctx.shadowColor = 'rgba(0,0,0,0.6)';
        ctx.shadowBlur = 6;
        ctx.fill();
        ctx.restore();

        // Bi sọc
        if (b.type === 'stripe') {
            ctx.beginPath();
            ctx.arc(b.x, b.y, BALL_RADIUS * 0.55, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
        }

        // Số trên bi
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
        // Đường ngắm
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(cueBall.x, cueBall.y);
        ctx.lineTo(cueBall.x + Math.cos(cueAngle) * 200, cueBall.y + Math.sin(cueAngle) * 200);
        ctx.stroke();
        ctx.setLineDash([]);

        // Gậy bida và hiệu ứng kéo lực
        ctx.save();
        ctx.translate(cueBall.x, cueBall.y);
        ctx.rotate(cueAngle + Math.PI);
        let stickOffset = 20 + cuePower * 1.5;
        ctx.fillStyle = '#d2b48c';
        ctx.fillRect(stickOffset, -3.5, 220, 7);
        ctx.restore();
    }
}

function updatePhysics() {
    if (gameState !== 'SHOOTING') return;

    let allStopped = true;

    balls.forEach(b => {
        if (!b.active) return;

        b.x += b.vx;
        b.y += b.vy;

        b.vx *= FRICTION;
        b.vy *= FRICTION;

        if (Math.abs(b.vx) < 0.04) b.vx = 0;
        if (Math.abs(b.vy) < 0.04) b.vy = 0;

        if (b.vx !== 0 || b.vy !== 0) {
            allStopped = false;
        }

        // Va chạm thành băng
        if (b.x - BALL_RADIUS < TABLE_X) { b.x = TABLE_X + BALL_RADIUS; b.vx *= -TABLE_ELASTICITY; }
        if (b.x + BALL_RADIUS > TABLE_X + TABLE_W) { b.x = TABLE_X + TABLE_W - BALL_RADIUS; b.vx *= -TABLE_ELASTICITY; }
        if (b.y - BALL_RADIUS < TABLE_Y) { b.y = TABLE_Y + BALL_RADIUS; b.vy *= -TABLE_ELASTICITY; }
        if (b.y + BALL_RADIUS > TABLE_Y + TABLE_H) { b.y = TABLE_Y + TABLE_H - BALL_RADIUS; b.vy *= -TABLE_ELASTICITY; }

        // Rơi vào lỗ
        pockets.forEach(p => {
            let dist = Math.hypot(b.x - p.x, b.y - p.y);
            if (dist < 16) {
                b.active = false;
                b.vx = 0;
                b.vy = 0;
                handlePocket(b);
            }
        });
    });

    // Va chạm giữa các bi
    for (let i = 0; i < balls.length; i++) {
        for (let j = i + 1; j < balls.length; j++) {
            let b1 = balls[i];
            let b2 = balls[j];
            if (!b1.active || !b2.active) continue;

            let dx = b2.x - b1.x;
            let dy = b2.y - b1.y;
            let dist = Math.hypot(dx, dy);

            if (dist < BALL_RADIUS * 2) {
                let overlap = (BALL_RADIUS * 2 - dist) / 2;
                let nx = dx / dist;
                let ny = dy / dist;

                b1.x -= nx * overlap;
                b1.y -= ny * overlap;
                b2.x += nx * overlap;
                b2.y += ny * overlap;

                let kx = b1.vx - b2.vx;
                let ky = b1.vy - b2.vy;
                let p = 2 * (nx * kx + ny * ky) / 2;

                b1.vx -= p * nx;
                b1.vy -= p * ny;
                b2.vx += p * nx;
                b2.vy += p * ny;
            }
        }
    }

    if (allStopped) {
        gameState = 'AIMING';
        let cue = balls.find(b => b.type === 'cue');
        if (!cue.active) {
            gameMessage = "Phạm lỗi! Bi cái vào lỗ. Đặt lại bi cái.";
            cue.x = 220;
            cue.y = 200;
            cue.vx =
