import os
import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="8 Ball Pool Pro",
    page_icon="🎱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ẩn thanh header và footer mặc định của Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding: 0rem;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Đọc file game.html an toàn tuyệt đối
html_file_path = os.path.join(os.path.dirname(__file__), "game.html")
if os.path.exists(html_file_path):
    with open(html_file_path, "r", encoding="utf-8") as f:
        game_html = f.read()
    components.html(game_html, height=750, scrolling=False)
else:
    st.error("Không tìm thấy file `game.html`. Vui lòng tạo file `game.html` đặt cùng thư mục với `app.py` trên GitHub!")
