import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang web
st.set_page_config(page_title="Flappy Bird Đỉnh Cao", page_icon="🐦", layout="centered")

st.title("🐦 Flappy Bird - Có Bảng Xếp Hạng & Âm Thanh")
st.write("Dùng phím **Cách (Space)** để điều khiển chú chim bay qua các ống nước nhé!")

game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Flappy Bird Mini</title>
    <style>
        body {
            text-align: center;
            background-color: #111;
            color: white;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }
        canvas {
            border: 2px solid #fff;
            background-color: #70c5ce;
            box-shadow: 0 0 15px rgba(0,0,0,0.7);
        }
    </style>
</head>
<body>
    <canvas id="gameCanvas" width="320" height="480"></canvas>
    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");

        // Tạo âm thanh bằng Web Audio API (không cần file nhạc ngoài)
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            let now = audioCtx.currentTime;
            if (type === "jump") {
                osc.type = "sine";
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.exponentialRampToValueAtTime(600, now + 0.1);
                gain.gain.setValueAtTime(0.1, now);
                gain.gain.linearRampToValueAtTime(0, now + 0.1);
                osc.start(now);
                osc.stop(now + 0.1);
            } else if (type === "score") {
                osc.type = "triangle";
                osc.frequency.setValueAtTime(500, now);
                osc.frequency.setValueAtTime(800, now + 0.08);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.linearRampToValueAtTime(0, now + 0.2);
                osc.start(now);
                osc.stop(now + 0.2);
            } else if (type === "die") {
                osc.type = "sawtooth";
                osc.frequency.setValueAtTime(200, now);
                osc.frequency.linearRampToValueAtTime(80, now + 0.3);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.linearRampToValueAtTime(0, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            }
        }

        // Cấu hình chim và độ chậm
        let bird = { x: 50, y: 150, width: 28, height: 28, gravity: 0.06, lift: -3.5, velocity: 0 };
        let pipes = [];
        let pipeWidth = 45;
        let pipeGap = 160;
        let frameCount = 0;
        let score = 0;
        
        // Lấy Điểm cao nhất từ bộ nhớ trình duyệt (localStorage)
        let highScore = localStorage.getItem("flappyHighScore") || 0;
        let isGameOver = false;

        document.addEventListener("keydown", function(e) {
            if (e.code === "Space") {
                e.preventDefault(); 
                if (isGameOver) {
                    resetGame();
                } else {
                    bird.velocity = bird.lift;
                    playSound("jump");
                }
            }
        });

        function resetGame() {
            bird.y = 150;
            bird.velocity = 0;
            pipes = [];
            score = 0;
            frameCount = 0;
            isGameOver = false;
            loop();
        }

        function update() {
            if (isGameOver) return;

            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            // Kiểm tra chạm đất hoặc bay quá cao
            if (bird.y + bird.height >= canvas.height || bird.y <= 0) {
                isGameOver = true;
                playSound("die");
                checkHighScore();
            }

            // Tạo cột
            if (frameCount % 180 === 0) {
                let minHeight = 50;
                let maxHeight = canvas.height - pipeGap - 50;
                let height = Math.floor(Math.random() * (maxHeight - minHeight + 1)) + minHeight;
                pipes.push({ x: canvas.width, top: height, bottom: canvas.height - height - pipeGap, passed: false });
            }

            for (let i = pipes.length - 1; i >= 0; i--) {
                pipes[i].x -= 0.9;

                // Va chạm với cột
                if (
                    bird.x < pipes[i].x + pipeWidth &&
                    bird.x + bird.width > pipes[i].x &&
                    (bird.y < pipes[i].top || bird.y + bird.height > canvas.height - pipes[i].bottom)
                ) {
                    isGameOver = true;
                    playSound("die");
                    checkHighScore();
                }

                // Cộng điểm
                if (!pipes[i].passed && pipes[i].x + pipeWidth < bird.x) {
                    score++;
                    playSound("score");
                    pipes[i].passed = true;
                }

                if (pipes[i].x + pipeWidth < 0) {
                    pipes.splice(i, 1);
                }
            }
            frameCount++;
        }

        function checkHighScore() {
            if (score > highScore) {
                highScore = score;
                localStorage.setItem("flappyHighScore", highScore);
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ chú chim 🐦
            ctx.font = "28px Arial";
            ctx.fillText("🐦", bird.x - 2, bird.y + 22);

            // Vẽ ống nước màu xanh lá
            ctx.fillStyle = "#2ecc71";
            for (let i = 0; i < pipes.length; i++) {
                ctx.fillRect(pipes[i].x, 0, pipeWidth, pipes[i].top);
                ctx.fillRect(pipes[i].x, canvas.height - pipes[i].bottom, pipeWidth, pipes[i].bottom);
            }

            // Hiển thị điểm số và điểm cao nhất hiện tại trên góc màn hình
            ctx.fillStyle = "white";
            ctx.font = "18px Arial";
            ctx.fillText("Điểm: " + score, 15, 30);
            ctx.fillText("Cao nhất: " + highScore, 15, 55);

            // Màn hình Game Over kèm Bảng xếp hạng nhỏ
            if (isGameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "#f1c40f";
                ctx.font = "bold 26px Arial";
                ctx.fillText("GAME OVER", 80, 180);

                ctx.fillStyle = "white";
                ctx.font = "18px Arial";
                ctx.fillText("🏆 BẢNG XẾP HẠNG 🏆", 65, 230);
                ctx.fillText("Điểm của bạn: " + score, 90, 270);
                ctx.fillText("Kỷ lục cao nhất: " + highScore, 80, 300);

                ctx.fillStyle = "#2ecc71";
                ctx.font = "bold 16px Arial";
                ctx.fillText("Nhấn Space để chơi lại", 75, 360);
            }
        }

        function loop() {
            update();
            draw();
            if (!isGameOver) {
                requestAnimationFrame(loop);
            }
        }

        loop();
    </script>
</body>
</html>
"""

components.html(game_html, height=550)
