import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang web
st.set_page_config(page_title="Flappy Bird Online", page_icon="🐦", layout="centered")

st.title("🐦 Flappy Bird Siêu Mượt")
st.write("Dùng phím **Cách (Space)** để điều khiển chú chim bay qua các ống nước nhé!")

# Đoạn mã HTML/JS mới: Chim rơi mượt hơn và có hình chú chim 🐦
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

        // Đã giảm trọng lực (gravity: 0.35) và lực nhảy (lift: -7) để chim rơi từ từ, dễ điều khiển hơn
        let bird = { x: 50, y: 150, width: 28, height: 28, gravity: 0.35, lift: -7, velocity: 0 };
        let pipes = [];
        let pipeWidth = 45;
        let pipeGap = 130; // Nới rộng khoảng cách giữa 2 ống một chút cho dễ qua
        let frameCount = 0;
        let score = 0;
        let isGameOver = false;

        document.addEventListener("keydown", function(e) {
            if (e.code === "Space") {
                e.preventDefault(); 
                if (isGameOver) {
                    resetGame();
                } else {
                    bird.velocity = bird.lift;
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
            }

            // Tạo cột mới chậm hơn một chút (100 khung hình)
            if (frameCount % 100 === 0) {
                let minHeight = 50;
                let maxHeight = canvas.height - pipeGap - 50;
                let height = Math.floor(Math.random() * (maxHeight - minHeight + 1)) + minHeight;
                pipes.push({ x: canvas.width, top: height, bottom: canvas.height - height - pipeGap, passed: false });
            }

            for (let i = pipes.length - 1; i >= 0; i--) {
                pipes[i].x -= 2; // Tốc độ di chuyển của ống

                // Va chạm với cột
                if (
                    bird.x < pipes[i].x + pipeWidth &&
                    bird.x + bird.width > pipes[i].x &&
                    (bird.y < pipes[i].top || bird.y + bird.height > canvas.height - pipes[i].bottom)
                ) {
                    isGameOver = true;
                }

                // Cộng điểm
                if (!pipes[i].passed && pipes[i].x + pipeWidth < bird.x) {
                    score++;
                    pipes[i].passed = true;
                }

                if (pipes[i].x + pipeWidth < 0) {
                    pipes.splice(i, 1);
                }
            }
            frameCount++;
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // THAY ĐỔI: Thay khối vuông thành Emoji chú chim 🐦 sinh động
            ctx.font = "28px Arial";
            ctx.fillText("🐦", bird.x - 2, bird.y + 22);

            // Vẽ ống nước màu xanh lá
            ctx.fillStyle = "#2ecc71";
            for (let i = 0; i < pipes.length; i++) {
                ctx.fillRect(pipes[i].x, 0, pipeWidth, pipes[i].top);
                ctx.fillRect(pipes[i].x, canvas.height - pipes[i].bottom, pipeWidth, pipes[i].bottom);
            }

            // Hiển thị điểm số
            ctx.fillStyle = "white";
            ctx.font = "20px Arial";
            ctx.fillText("Điểm: " + score, 15, 35);

            if (isGameOver) {
                ctx.fillStyle = "rgba(0, 0, 0, 0.6)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = "white";
                ctx.font = "25px Arial";
                ctx.fillText("GAME OVER", 80, 220);
                ctx.font = "16px Arial";
                ctx.fillText("Nhấn Space để chơi lại", 75, 260);
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
