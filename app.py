import math
import random
import streamlit as st

st.set_page_config(
    page_title="Bida 8 Ball Pool - Streamlit Edition",
    page_icon="🎱",
    layout="centered",
)

st.title("🎱 Bida 8 Ball Pool (Phiên bản Streamlit)")
st.write(
    "Kéo thanh điều chỉnh góc và lực đánh, sau đó nhấn **Đánh Bi** để đưa bi"
    " vào lỗ!"
)

# Khởi tạo trạng thái bàn bida trong Session State
if "ball_x" not in st.session_state:
  st.session_state.ball_x = 200.0  # Tọa độ X bi cái
  st.session_state.ball_y = 200.0  # Tọa độ Y bi cái
  st.session_state.target_x = 400.0  # Tọa độ X bi mục tiêu
  st.session_state.target_y = 200.0  # Tọa độ Y bi mục tiêu
  st.session_state.score = 0
  st.session_state.message = "Trận đấu bắt đầu! Hãy nhắm chuẩn xác."

# Khu vực điều khiển cú đánh
col1, col2 = st.columns(2)
with col1:
  angle = st.slider("Góc đánh (Độ)", min_value=0, max_value=360, value=0, step=1)
with col2:
  power = st.slider(
      "Lực đánh (Power)", min_value=1, max_value=100, value=50, step=1
  )

# Hiển thị trực quan bàn bida dạng văn bản/HTML/Markdown hoặc vẽ tọa độ
st.markdown("---")
st.subheader("🟢 Bàn Bida (Mô phỏng 2D)")

# Vẽ bàn bida dạng bảng thông tin trực quan
st.info(f"📍 Trạng thái: {st.session_state.message}")
st.write(
    f"⚪ **Bi cái (Cue Ball):** X = {st.session_state.ball_x:.1f}, Y ="
    f" {st.session_state.ball_y:.1f}"
)
st.write(
    f"🔴 **Bi mục tiêu:** X = {st.session_state.target_x:.1f}, Y ="
    f" {st.session_state.target_y:.1f}"
)
st.write(f"🏆 **Điểm số / Số bi đã ăn:** {st.session_state.score}")


# Xử lý logic khi bấm nút đánh
if st.button("🎯 Đánh Bi (Shoot!)", type="primary"):
  # Tính toán đường đi dựa trên góc và lực
  rad = math.radians(angle)
  distance = power * 2.5

  # Dịch chuyển bi cái theo hướng góc đánh
  st.session_state.ball_x += distance * math.cos(rad)
  st.session_state.ball_y += distance * math.sin(rad)

  # Kiểm tra xem bi cái có va chạm với bi mục tiêu hoặc vào lỗ không
  # Giả lập lỗ ở góc bàn (Tọa độ 500, 300)
  distance_to_target = math.hypot(
      st.session_state.ball_x - st.session_state.target_x,
      st.session_state.ball_y - st.session_state.target_y,
  )

  if distance_to_target < 30:
    st.session_state.score += 1
    st.session_state.message = (
        "🎉 Tuyệt vời! Bạn đã đánh trúng bi mục tiêu và ghi điểm!"
    )
    # Reset lại vị trí bi mục tiêu ngẫu nhiên
    st.session_state.target_x = random.randint(150, 450)
    st.session_state.target_y = random.randint(100, 300)
  else:
    st.session_state.message = (
        "💨 Hụt rồi! Bi đi lệch hướng hoặc lực chưa đủ."
    )

  st.rerun()

# Nút chơi lại từ đầu
if st.button("🔄 Đặt lại bàn (Reset Game)"):
  st.session_state.ball_x = 200.0
  st.session_state.ball_y = 200.0
  st.session_state.target_x = 400.0
  st.session_state.target_y = 200.0
  st.session_state.score = 0
  st.session_state.message = "Đã reset bàn bida."
  st.rerun()
