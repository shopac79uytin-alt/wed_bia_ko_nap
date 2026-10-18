import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Pro 8 Ball Pool - Full Engine Edition",
    page_icon="🎱",
    layout="centered",
)

st.title("🎱 Pro 8 Ball Pool (Phiên bản Đầy đủ Cơ chế & Luật chơi)")
st.write(
    "Trò chơi bida 8 bi chuẩn xác. Click và kéo chuột quanh bi cái để ngắm, kéo ngược lại để lấy lực, thả ra để đánh!"
)

pool_game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>8 Ball Pool Full Engine</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 10px;
            user-select: none;
        }
        #gameContainer {
            position: relative;
            display: inline-block;
            box-shadow: 0 10px 30px rgba(0,0,0,0.9);
            border-radius: 12px;
            overflow: hidden;
            border: 6px solid #3d2817;
        }
        canvas {
            background: #0b5c1e;
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
            max-width: 820px;
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
    <canvas id="poolCanvas" width="840" height="420"></canvas>
</div>

<div id="uiPanel">
    <div><b>Lượt:</b> <span id="turnInfo" style="color: #f1c40f;">Người chơi 1</span></div>
    <div><b>Nhóm:</b> <span id="groupInfo">Chưa phân nhóm</span></div>
    <div><b>Trạng thái:</b> <span id="statusInfo">Sẵn sàng đánh</span></div>
    <button class="btn" onclick="resetGame()">Làm mới bàn</button>
</div>

<script>
const canvas = document.getElementById('poolCanvas');
const ctx = canvas.getContext('2d');

const TABLE_X = 60;
const TABLE_Y = 60;
const TABLE_W = 720;
const TABLE_H = 300;
const BALL_RADIUS = 11;
const POCKET_RADIUS = 18;
const FRICTION = 0.985;
const ELASTICITY = 0.85;

// 6 Lỗ bida chuẩn (4 góc + 2 giữa cạnh dài)
const pockets = [
    {x: TABLE_X, y: TABLE_Y},
    {x: TABLE_X + TABLE_W / 2, y: TABLE_Y - 4},
    {x: TABLE_X + TABLE_W, y: TABLE_Y},
    {x: TABLE_X, y: TABLE_Y + TABLE_H},
    {x: TABLE_X + TABLE_W / 2, y: TABLE_Y + TABLE_H + 4},
    {x: TABLE_X + TABLE_W, y: TABLE_Y + TABLE_H}
];

let balls = [];
let gameState = 'AIMING'; // AIMING, SHOOTING, BALL_IN_HAND, GAMEOVER
let cueAngle = 0;
let cuePower = 0;
let isDragging = false;
let dragStartX = 0, dragStartY = 0;

let currentPlayer = 1; // 1 hoặc 2
let playerGroups = { 1: null, 2: null }; // 'solid' hoặc 'stripe'
let gameMessage = "Kéo chuột từ bi cái ngược hướng ngắm để lấy lực.";
let firstContactBall = null;
let pocketedThisTurn = [];

function initBalls() {
    balls = [];
    // Bi cái (Cue Ball)
    balls.push({id: 0, x: 220, y: 210, vx: 0, vy: 0, color: '#ffffff', type: 'cue', number: 0, active: true});

    // Tam giác 15 bi mục tiêu
    const startX = 580;
    const startY = 210;
    const spacing = BALL_RADIUS * 2 + 1.5;
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
    currentPlayer = 1;
    playerGroups = { 1: null, 2: null };
    gameMessage = "Đã làm mới bàn bida. Lượt Người chơi 1.";
    firstContactBall = null;
    pocketedThisTurn = [];
    updateUI();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Thành băng gỗ bàn bida
    ctx.fillStyle = '#3d2817';
    ctx.fillRect(TABLE_X - 22, TABLE_Y - 22, TABLE_W + 44, TABLE_H + 44);

    // Mặt vải bàn bida
    ctx.fillStyle = '#0b5c1e';
    ctx.fillRect(TABLE_X, TABLE_Y, TABLE_W, TABLE_H);

    // 6 Lỗ bida
    ctx.fillStyle = '#050505';
    pockets.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x, p.y, POCKET_RADIUS, 0, Math.PI * 2);
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
        // Đường ngắm (dừng tại vật cản đầu tiên)
        let rayLength = 300;
        let endX = cueBall.x + Math.cos(cueAngle) * rayLength;
        let endY = cueBall.y + Math.sin(cueAngle) * rayLength;

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(cueBall.x, cueBall.y);
        ctx.lineTo(endX, endY);
        ctx.stroke();
        ctx.setLineDash([]);

        // Vẽ gậy bida
        ctx.save();
        ctx.translate(cueBall.x, cueBall.y);
        ctx.rotate(cueAngle + Math.PI);
        let stickOffset = 25 + cuePower * 1.5;
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

        // Va chạm thành băng (giữ bi trong bàn)
        if (b.x - BALL_RADIUS < TABLE_X) { b.x = TABLE_X + BALL_RADIUS; b.vx *= -ELASTICITY; }
        if (b.x + BALL_RADIUS > TABLE_X + TABLE_W) { b.x = TABLE_X + TABLE_W - BALL_RADIUS; b.vx *= -ELASTICITY; }
        if (b.y - BALL_RADIUS < TABLE_Y) { b.y = TABLE_Y + BALL_RADIUS; b.vy *= -ELASTICITY; }
        if (b.y + BALL_RADIUS > TABLE_Y + TABLE_H) { b.y = TABLE_Y + TABLE_H - BALL_RADIUS; b.vy *= -ELASTICITY; }

        // Kiểm tra rơi vào lỗ (bi chỉ rơi khi thực sự đi vào tâm lỗ, không bị hút sai)
        pockets.forEach(p => {
            let dist = Math.hypot(b.x - p.x, b.y - p.y);
            if (dist < POCKET_RADIUS - 3) {
                b.active = false;
                b.vx = 0;
                b.vy = 0;
                pocketedThisTurn.push(b);
            }
        });
    });

    // Va chạm giữa các bi (Ball-to-Ball Collision)
    for (let i = 0; i < balls.length; i++) {
        for (let j = i + 1; j < balls.length; j++) {
            let b1 = balls[i];
            let b2 = balls[j];
            if (!b1.active || !b2.active) continue;

            let dx = b2.x - b1.x;
            let dy = b2.y - b1.y;
            let dist = Math.hypot(dx, dy);

            if (dist < BALL_RADIUS * 2) {
                // Ghi nhận va chạm đầu tiên của bi cái phục vụ xét luật
                if ((b1.type === 'cue' || b2.type === 'cue') && firstContactBall === null) {
                    firstContactBall = (b1.type === 'cue') ? b2 : b1;
                }

                let overlap = (BALL_RADIUS * 2 - dist) / 2;
                let nx = dx / dist;
                let ny = dy / dist;

                b1.x -= nx * overlap;
                b1.y -= ny * overlap;
                b2.x += nx * overlap;
                b2.y += ny * overlap;

                let kx = b1.vx - b2.vx;
                let ky = b1.vy - b2.vy;
                let p = (nx * kx + ny * ky);

                b1.vx -= p * nx;
                b1.vy -= p * ny;
                b2.vx += p * nx;
                b2.vy += p * ny;
            }
        }
    }

    if (allStopped) {
        resolveTurnRules();
    }
}

function resolveTurnRules() {
    gameState = 'AIMING';
    let cue = balls.find(b => b.type === 'cue');
    let foul = false;

    // 1. Kiểm tra bi cái vào lỗ
    let cuePocketed = pocketedThisTurn.some(b => b.type === 'cue');
    if (cuePocketed) {
        foul = true;
        gameMessage = `Phạm lỗi (Scratch)! Bi cái vào lỗ.`;
        cue.x = 220;
        cue.y = 210;
        cue.vx = 0;
        cue.vy = 0;
        cue.active = true;
    }

    // 2. Kiểm tra bi chạm đầu tiên hợp lệ
    if (!cuePocketed && firstContactBall) {
        let myGroup = playerGroups[currentPlayer];
        if (myGroup) {
            if (firstContactBall.type !== 'black' && firstContactBall.type !== myGroup) {
                // Kiểm tra xem người chơi đã ăn hết nhóm của mình chưa
                let remainingMyBalls = balls.filter(b => b.active && b.type === myGroup);
                if (remainingMyBalls.length > 0) {
                    foul = true;
                    gameMessage = `Phạm lỗi! Chạm nhầm bi của đối phương trước.`;
                }
            }
        }
    } else if (!cuePocketed && !firstContactBall) {
        foul = true;
        gameMessage = `Phạm lỗi! Bi cái không chạm bất kỳ bi nào.`;
    }

    // 3. Xử lý bi số 8
    let eightBallPocketed = pocketedThisTurn.some(b => b.type === 'black');
    if (eightBallPocketed) {
        let myGroup = playerGroups[currentPlayer];
        let remainingMyBalls = myGroup ? balls.filter(b => b.active && b.type === myGroup).length : 1;
        
        if (remainingMyBalls === 0 && !foul) {
            gameMessage = `🎉 Người chơi ${currentPlayer} đã đưa bi số 8 vào lỗ hợp lệ và CHIẾN THẮNG!`;
            gameState = 'GAMEOVER';
            updateUI();
            return;
        } else {
            gameMessage = `❌ Người chơi ${currentPlayer} đánh bi số 8 khi chưa đủ điều kiện hoặc phạm lỗi -> THUA CUỘC!`;
            gameState = 'GAMEOVER';
            updateUI();
            return;
        }
    }

    // 4. Phân nhóm bi nếu chưa có
    if (!playerGroups[1] && !playerGroups[2]) {
        let objectivePocketed = pocketedThisTurn.filter(b => b.type === 'solid' || b.type === 'stripe');
        if (objectivePocketed.length > 0) {
            let firstP = objectivePocketed[0];
            playerGroups[currentPlayer] = firstP.type;
            playerGroups[currentPlayer === 1 ? 2 : 1] = (firstP.type === 'solid') ? 'stripe' : 'solid';
            gameMessage = `Người chơi ${currentPlayer} thuộc nhóm bi [${firstP.type.toUpperCase()}].`;
        }
    }

    // 5. Chuyển lượt nếu đánh hụt hoặc phạm lỗi
    let validPocketed = pocketedThisTurn.some(b => {
        let myGroup = playerGroups[currentPlayer];
        if (!myGroup) return b.type === 'solid' || b.type === 'stripe';
        return b.type === myGroup;
    });

    if (foul || !validPocketed) {
        currentPlayer = currentPlayer === 1 ? 2 : 1;
        if (!foul) gameMessage = `Không ăn được bi, chuyển lượt cho Người chơi ${currentPlayer}.`;
    } else {
        gameMessage = `Tuyệt vời! Người chơi ${currentPlayer} được tiếp tục đánh.`;
    }

    firstContactBall = null;
    pocketedThisTurn = [];
    updateUI();
}

function updateUI() {
    document.getElementById('turnInfo').innerText = `Người chơi ${currentPlayer}`;
    let g1 = playerGroups[1] ? playerGroups[1].toUpperCase() : 'Chưa chọn';
    let g2 = playerGroups[2] ? playerGroups[2].toUpperCase() : 'Chưa chọn';
    document.getElementById('groupInfo').innerText = `P1: ${g1} | P2: ${g2}`;
    document.getElementById('statusInfo').innerText = gameMessage;
}

canvas.addEventListener('mousedown', (e) => {
    if (gameState !== 'AIMING') return;
    isDragging = true;
    let rect = canvas.getBoundingClientRect();
    dragStartX = e.clientX - rect.left;
    dragStartY = e.clientY - rect.top;
});

canvas.addEventListener('mousemove', (e) => {
    if (gameState !== 'AIMING') return;
    let rect = canvas.getBoundingClientRect();
    let mx = e.clientX - rect.left;
    let my = e.clientY - rect.top;

    let cueBall = balls.find(b => b.type === 'cue');
    if (cueBall) {
        cueAngle = Math.atan2(my - cueBall.y, mx - cueBall.x);
        if (isDragging) {
            let dist = Math.hypot(mx - dragStartX, my - dragStartY);
            cuePower = Math.min(Math.max(dist, 0), 65);
        }
    }
});

canvas.addEventListener('mouseup', () => {
    if (!isDragging || gameState !== 'AIMING') return;
    isDragging = false;

    if (cuePower > 3) {
        let cueBall = balls.find(b => b.type === 'cue');
        cueBall.vx = -Math.cos(cueAngle) * (cuePower * 0.45);
        cueBall.vy = -Math.sin(cueAngle) * (cuePower * 0.45);
        gameState = 'SHOOTING';
        gameMessage = "Bi đang chuyển động...";
        firstContactBall = null;
        pocketedThisTurn = [];
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

components.html(pool_game_html, height=540, scrolling=False)
