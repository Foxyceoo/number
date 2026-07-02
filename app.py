import streamlit as st
import pandas as pd
import json
import math
import time
import pyrebase
import streamlit.components.v1 as components

# Sát lề trái, không thụt đầu dòng
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4HTreKOHkHRXq2zdolvnEt2o5HyDN6JAWBy3DSI8kRgftC3_pAHJZKztQCXfBrLzvVbw0ohY6vfNG/pub?gid=0&single=true&output=csv"

# Sát lề trái
config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "databaseURL": "https://email-8c050-default-rtdb.firebaseio.com/"
}

# Khởi tạo Auth
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# 2. Quản lý trạng thái đăng nhập
if 'user' not in st.session_state:
    st.session_state.user = None

# Giao diện đăng nhập đơn giản
def login_form():
    st.title("Đăng nhập")
    email = st.text_input("Email")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("Đăng nhập"):
        try:
            # Sử dụng thư viện pyrebase để đăng nhập
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.user_name = email.split('@')[0]
            st.rerun() # Tải lại trang để vào ứng dụng
        except:
            st.error("Email hoặc mật khẩu không đúng!")

# Luồng kiểm tra đăng nhập
if st.session_state.user is None:
    login_form()
    st.stop() # Dừng ứng dụng nếu chưa đăng nhập
else:
    st.success(f"Chào {st.session_state.user_name}!")
    
    # Thay vì dùng placeholder.markdown(...), hãy dùng st.empty() nếu muốn xóa
    # Hoặc đơn giản là hiển thị lời chào và đợi 3 giây rồi dùng st.empty()
    hello_msg = st.empty()
    hello_msg.markdown(f"<h2 style='text-align: center;'>Hello {st.session_state.user_name}!</h2>", unsafe_allow_html=True)
    
    time.sleep(3)
    hello_msg.empty() # Xóa lời chào sau 3 giây

# Hàm chuyển đổi Key thành số 1-15
def get_number_from_key(note_data):
    # note_data là list [pitch, layer], ví dụ: [7, "2"]
    # Pitch (note_data[0]) chính là vị trí phím 0-14
    pitch = int(note_data[0])
    return pitch + 1  # Vì index bắt đầu từ 0 nên cộng 1 để ra số 1-15

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---")
    uploaded_file = st.file_uploader("**Sheet 123**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")

if uploaded_file:
    data = json.load(uploaded_file)
    song_data = data[0]
    song_name = uploaded_file.name.replace(".json", "")
    
    # Lấy danh sách các cột và số bit mỗi trang từ file
    columns = song_data.get("columns", [])
    bits_per_page = song_data.get("bitsPerPage", 36)
    
    def get_number_from_data(note_data):
        # note_data là list [pitch, key]
        return int(note_data[1])
        
    #CSS
    style = f"""
    <style>
    ::-webkit-scrollbar {{ display: none !important; }}
    html, body {{ width: 100%; margin: 0; padding: 0; overflow-y: hidden !important; }}

    table {{ 
        border-collapse: collapse; 
        text-align: center; 
        table-layout: fixed !important; 
        width: {{margin_side}}; 
        margin: 0 auto 30px auto; 
        height: 60px !important; 
    }}

    td {{ 
        padding: 2px !important;  
        width: 20px !important; 
        vertical-align: top !important; 
        border-right: 1px solid #555; 
        border-left: none; 
        overflow: hidden;
    }}

    .note-number {{ 
        font-size: 15px !important; 
        font-weight: bold !important; 
        line-height: 2 !important; 
        display: block;
    }}

    @media print {{
        .sidebar, header, .stAppDeployButton, footer {{ display: none !important; }}
        @page {{ size: A4; margin: 1cm 1.2cm 1cm 0.8cm; }}
        
        /* Ẩn các thứ không cần thiết */
        .sidebar, header, .stAppDeployButton, footer {{ display: none !important; }}
        
        .note-number {{ font-size: 11px !important; }}
        table {{ page-break-inside: avoid !important; break-inside: avoid !important; margin-bottom: 56px !important; width: 100% !important; }}
        td {{ width: 14px !important; min-width: 14px !important; max-width: 14px !important; padding: 0 !important; overflow: hidden !important; white-space: nowrap !important; }}
        
        /* Đảm bảo mỗi dòng nhạc không bị cắt ngang */
        .khuong-wrapper {{
            page-break-inside: avoid !important; 
            break-inside: avoid !important; 
            margin-bottom: 20px !important;
         }}
         
        /* Ép bảng luôn nằm trọn vẹn */
        table {{ 
            width: 100% !important; 
            table-layout: fixed !important; 
        }}

        /* Giữ số ở cỡ nhỏ vừa đọc */
        .note-number {{ font-size: 10px !important; }}
         
       }}
    </style>
    """
    
    all_khuong_html = []
    line_number = 1
    
    # Duyệt theo từng trang (bits_per_page)
    for i in range(0, len(columns), bits_per_page):
        khuong_columns = columns[i : i + bits_per_page]
        
        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle; font-size: 10px;'>{line_number}</td>"
        
        for col_idx, col in enumerate(khuong_columns):
            # col là [time, [[pitch, key], ...]]
            notes_in_col = col[1]
            vals = sorted([get_number_from_key(n) for n in notes_in_col], reverse=True)

            # Logic kẻ bảng
            is_new_line = (col_idx == 0)
            is_beat_4 = ((col_idx + 1) % 4 == 0)
            border_right = "0.5px solid #00008c" if (is_beat_4 or (col_idx + 1) == bits_per_page) else "0px solid #d8d8d8"
            border_left = "0.5px solid #00008c" if is_new_line else "none"

            # --- BỔ SUNG ĐOẠN NÀY ĐỂ ĐỆM CHO ĐỦ NHỊP ---
            # Kiểm tra xem khuông cuối cùng có thiếu nhịp không
            if len(khuong_columns) < bits_per_page:
                needed = bits_per_page - len(khuong_columns)
                for _ in range(needed):
                    khuong_columns.append([0, []]) # Thêm cột rỗng

            if vals:
                # Dùng join để nối các số bằng thẻ <br>
                all_nums = "<br>".join(map(str, vals))
                
                # Sửa lại: Dùng display: flex và bỏ dynamic_padding dựa trên giá trị nốt
                # Chỉ để padding-top cố định một chút để tránh dính sát mép trên
                cell_content = f"""
                <div style='display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding-top: 2px;'>
                    <div style='font-size: 12px; font-weight: bold; line-height: 1.4;'>{all_nums}</div>
                </div>
                """
            else:
                cell_content = ""

            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        
        html_content += "</tr></table>"
        all_khuong_html.append(html_content)
        line_number += 1
        
    display_html = f"<h1 style='text-align: center; font-size: 40px; margin-top: 20px; margin-bottom: 70px;'>{song_name}</h1>"
    
    # Render HTML
    for khuong_html in all_khuong_html:
        display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"

    html_to_render = style + display_html
    
    total_height = (len(all_khuong_html) * 110) + 200
    components.html(html_to_render, height=total_height, scrolling=False)

    if st.button("to PDF"):
        js_code = "<script>window.parent.window.print();</script>"
        components.html(js_code, height=0)
