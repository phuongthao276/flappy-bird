import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang web
st.set_page_config(page_title="Flappy Phone Bird", page_icon="🐦", layout="centered")

st.title("🐦 Flappy Phone Bird - Phiên Bản Điện Thoại")
st.write("Dùng phím **Cách (Space)** để điều khiển chú chim vỗ cánh bay qua các cột điện thoại nhé!")

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

        // Âm thanh Web Audio API
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

        // Cấu hình chim (chế độ siêu chậm, mượt)
        let bird = { 
            x: 50, y: 150, width: 32, height: 24, 
            gravity: 0.06, lift: -3.5, velocity: 0,
            rotation: 0 
        };
        
        let pipes = [];
        let pipeWidth = 50;
        let pipeGap = 160;
        let frameCount = 0;
        let score = 0;
        let highScore = localStorage.getItem("flappyHighScore") || 0;
        let isGameOver = false;
        let hitEffectTimer = 0; // Hiệu ứng chớp màn hình khi va chạm

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
            hitEffectTimer = 0;
            loop();
        }

        function update() {
            if (isGameOver) return;

            bird.velocity += bird.gravity;
            bird.y += bird.velocity;

            // Xoay góc con chim theo vận tốc rơi/nhảy
            bird.rotation = Math.min(Math.PI / 4, Math.max(-Math.PI / 4, bird.velocity * 0.1));

            // Kiểm tra chạm đất hoặc bay quá cao
            if (bird.y + bird.height >= canvas.height || bird.y <= 0) {
                isGameOver = true;
                hitEffectTimer = 20;
                playSound("die");
                checkHighScore();
            }

            // Tạo cột điện thoại
            if (frameCount % 180 === 0) {
                let minHeight = 60;
                let maxHeight = canvas.height - pipeGap - 60;
                let height = Math.floor(Math.random() * (maxHeight - minHeight + 1)) + minHeight;
                pipes.push({ x: canvas.width, top: height, bottom: canvas.height - height - pipeGap, passed: false });
            }

            for (let i = pipes.length - 1; i >= 0; i--) {
                pipes[i].x -= 0.9;

                // Va chạm với cột điện thoại
                if (
                    bird.x < pipes[i].x + pipeWidth &&
                    bird.x + bird.width > pipes[i].x &&
                    (bird.y < pipes[i].top || bird.y + bird.height > canvas.height - pipes[i].bottom)
                ) {
                    isGameOver = true;
                    hitEffectTimer = 20;
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

        // Vẽ cột dạng các chiếc điện thoại xếp chồng lên nhau
        function drawPhonePipes(x, y, width, height, isTop) {
            let phoneHeight = 70;
            let currentY = isTop ? 0 : y;
            let targetHeight = isTop ? height : canvas.height - y;
            let drawnHeight = 0;

            while (drawnHeight < targetHeight) {
                let h = Math.min(phoneHeight, targetHeight - drawnHeight);
                
                // Thân điện thoại
                ctx.fillStyle = "#333";
                ctx.fillRect(x, currentY, width, h);
                ctx.strokeStyle = "#777";
                ctx.lineWidth = 2;
                ctx.strokeRect(x, currentY, width, h);

                // Màn hình điện thoại phát sáng nhẹ
                if (h > 30) {
                    ctx.fillStyle = "#4a90e2";
                    ctx.fillRect(x + 5, currentY + 10, width - 10, h - 25);
                    
                    // Nút home giả lập
                    ctx.fillStyle = "#bbb";
                    ctx.beginPath();
                    ctx.arc(x + width / 2, currentY + h - 7, 3, 0, Math.PI * 2);
                    ctx.fill();
                }

                if (isTop) {
                    currentY += h;
                } else {
                    currentY += h; // Hoặc vẽ ngược lên nếu từ dưới lên
                }
                drawnHeight += h;
                if (isTop && currentY >= height) break;
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ background mây trời nhẹ nhàng
            ctx.fillStyle = "#70c5ce";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Vẽ các cột điện thoại
            for (let i = 0; i < pipes.length; i++) {
                // Cột trên
                drawPhonePipes(pipes[i].x, 0, pipeWidth, pipes[i].top, true);
                // Cột dưới
                drawPhonePipes(pipes[i].x, canvas.height - pipes[i].bottom, pipeWidth, pipes[i].bottom, false);
            }

            // Vẽ chú chim có hiệu ứng vỗ cánh (xoay theo góc bay)
            ctx.save();
            ctx.translate(bird.x + bird.width / 2, bird.y + bird.height / 2);
            ctx.rotate(bird.rotation);

            // Thân chim vàng
            ctx.fillStyle = "#f1c40f";
            ctx.beginPath();
            ctx.ellipse(0, 0, bird.width / 2, bird.height / 2, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = "#d35400";
            ctx.lineWidth = 2;
            ctx.stroke();

            // Mỏ chim
            ctx.fillStyle = "#e67e22";
            ctx.beginPath();
            ctx.moveTo(bird.width / 2 - 2, -4);
            ctx.lineTo(bird.width / 2 + 8, 0);
            ctx.lineTo(bird.width / 2 - 2, 4);
            ctx.fill();

            // Mắt chim
            ctx.fillStyle = "white";
            ctx.beginPath();
            ctx.arc(6, -4, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = "black";
            ctx.beginPath();
            ctx.arc(8, -4, 2, 0, Math.PI * 2);
            ctx.fill();

            // Cánh chim vỗ (đổi vị trí dựa theo frameCount để tạo hiệu ứng vỗ)
            ctx.fillStyle = "#f39c12";
            ctx.beginPath();
            let wingOffset = Math.floor(frameCount / 6) % 2 === 0 ? -6 : 4;
            ctx.ellipse(-4, wingOffset, 8, 5, Math.PI / 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();

            ctx.restore();

            // Hiệu ứng chớp đỏ khi va chạm
            if (hitEffectTimer > 0) {
                ctx.fillStyle = "rgba(255, 0, 0, 0.4)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                hitEffectTimer--;
            }

            // Hiển thị điểm số góc màn hình
            ctx.fillStyle = "white";
            ctx.font = "bold 18px Arial";
            ctx.fillText("Điểm: " + score, 15, 30);
            ctx.fillText("Cao nhất: " + highScore, 15, 55);

            // Màn hình Game Over kèm Bảng xếp hạng và hiệu ứng nứt màn hình
            if (isGameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.75)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Vẽ vết nứt giả lập trên màn hình game over
                ctx.strokeStyle = "rgba(255, 255, 255, 0.5)";
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(50, 50); ctx.lineTo(120, 150); ctx.lineTo(90, 200);
                ctx.moveTo(270, 80); ctx.lineTo(200, 180);
                ctx.stroke();

                ctx.fillStyle = "#f1c40f";
                ctx.font = "bold 26px Arial";
                ctx.fillText("GAME OVER", 80, 170);

                ctx.fillStyle = "white";
                ctx.font = "16px Arial";
                ctx.fillText("🏆 BẢNG XẾP HẠNG 🏆", 75, 220);
                ctx.fillText("Điểm của bạn: " + score, 100, 255);
                ctx.fillText("Kỷ lục cao nhất: " + highScore, 90, 285);

                ctx.fillStyle = "#2ecc71";
                ctx.font = "bold 16px Arial";
                ctx.fillText("Nhấn Space để chơi lại", 75, 345);
            }
        }

        function loop() {
            update();
            draw();
            if (!isGameOver) {
                requestAnimationFrame(loop);
            } else {
                draw(); // Vẽ lại khung cuối cùng để hiện bảng game over
            }
        }

        loop();
    </script>
</body>
</html>
"""

components.html(game_html, height=550)
