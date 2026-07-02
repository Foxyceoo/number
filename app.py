import streamlit as st
import pandas as pd
import json
import math
import time
import pyrebase
import requests
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
    # Dùng key để quản lý giá trị ô nhập liệu rõ ràng hơn
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Mật khẩu", type="password", key="pass_input")
    
    if st.button("Đăng nhập"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.user_name = email.split('@')[0]
            # Xóa sạch dữ liệu cũ trong bộ nhớ sau khi đăng nhập thành công
            st.rerun() 
        except Exception as e:
            # Thông báo lỗi chi tiết hơn nếu cần
            st.error("Email hoặc mật khẩu không chính xác. Vui lòng thử lại!")
            
# Luồng kiểm tra đăng nhập
if st.session_state.user is None:
    login_form()
    st.stop() # Dừng ứng dụng nếu chưa đăng nhập
else:
    # 1. Kiểm tra trạng thái đã tải xong chưa trong session_state
    if 'is_loaded' not in st.session_state:
        st.session_state.is_loaded = False
    
    # 2. Nếu chưa tải, hiển thị spinner và đặt lại cờ
    if not st.session_state.is_loaded:
        with st.spinner('Đang tải dữ liệu...'):
            time.sleep(2) # Giả lập thời gian tải
        st.session_state.is_loaded = True
        st.rerun() # Chỉ rerun duy nhất 1 lần sau khi đặt flag
    
    # 3. Sau khi đã tải xong (is_loaded là True), hiển thị nội dung chính
    st.success(f"hello, {st.session_state.user_name}!")
    # ... (code hiển thị sheet nhạc của bạn nằm ở đây)

# Kiểm tra nếu người dùng đã đăng nhập thành công
if st.session_state.user is not None:
    with st.sidebar:
        st.markdown("---")
        st.write(f"**Người dùng:** {st.session_state.user_name}")
        
        # Nút đổi mật khẩu
        if st.button("Đổi mật khẩu"):
            st.session_state.show_change_password = True
            
        # Logic đổi mật khẩu
        if st.session_state.get("show_change_password", False):
            new_password = st.text_input("Nhập mật khẩu mới", type="password")
            if st.button("Xác nhận đổi"):
                try:
                    id_token = st.session_state.user['idToken']
                    api_key = st.secrets["FIREBASE_API_KEY"]
                    api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
                    payload = {"idToken": id_token, "password": new_password, "returnSecureToken": True}
                    
                    response = requests.post(api_url, json=payload)
                    
                    if response.status_code == 200:
                        st.success("Đổi mật khẩu thành công!")
                        st.session_state.show_change_password = False
                        st.rerun()
                    else:
                        error_data = response.json()
                        st.error(f"Lỗi Firebase: {error_data.get('error', {}).get('message', 'Có lỗi xảy ra')}")
                        
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
                    
        if st.button("Đăng xuất"):
            st.session_state.user = None
            st.rerun()
            
# Hàm chuyển đổi Key thành số 1-15
def get_number_from_key(note_data):
    # note_data là list [pitch, layer], ví dụ: [7, "2"]
    # Pitch (note_data[0]) chính là vị trí phím 0-14
    pitch = int(note_data[0])
    return pitch + 1  # Vì index bắt đầu từ 0 nên cộng 1 để ra số 1-15

#Hiển thị
def get_symbol(value, mode):
    if mode == "1. 1.. 1...":
        mapping = {
            1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 
            6: "6", 7: "7", 8: "1.", 9: "2.", 10: "3.", 
            11: "4.", 12: "5.", 13: "6.", 14: "7.", 15: "1.."
        }
    elif mode == "abc":
        mapping = {
            1: "a1", 2: "a2", 3: "a3", 4: "a4", 5: "a5",
            6: "b1", 7: "b2", 8: "b3", 9: "b4", 10: "b5",
            11: "c1", 12: "c2", 13: "c3", 14: "c4", 15: "c5"
        }
    else: # Chế độ "1 - 15" mặc định
        return str(value)
        
    return mapping.get(value, str(value))

# 2. Thêm nút chọn chế độ vào Sidebar

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    uploaded_file = st.file_uploader("**Nhập file của bạn**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")
    # Nút chọn chế độ
    display_mode = st.radio("Chế độ hiển thị:", ["1-15", "1. 1.. 1...", "abc"])
    st.markdown("---")

if uploaded_file:
    data = json.load(uploaded_file)
    song_data = data[0]
    song_name = uploaded_file.name.replace(".json", "")
    columns = song_data.get("columns", [])
    bits_per_page = 32
    
    # Hàm lấy số thuần (cũ)
    def get_number_from_key(note_data):
        pitch = int(note_data[0])
        return pitch + 1
    
    # Lấy danh sách các cột và số bit mỗi trang từ file
    columns = song_data.get("columns", [])
    bits_per_page = 32
    
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
        @page {{ size: A4; margin: 1cm 2cm 1cm 0.8cm; }}
        
        /* Ẩn các thứ không cần thiết */
        .sidebar, header, .stAppDeployButton, footer {{ display: none !important; }}
        
        .note-number {{ font-size: 11px !important; }}
        table {{ page-break-inside: avoid !important; break-inside: avoid !important; margin-bottom: 56px !important; width: 100% !important; }}
        td {{ width: 14px !important; min-width: 14px !important; max-width: 14px !important; padding: 0 !important; overflow: hidden !important; white-space: nowrap !important; }}
        
        /* Đảm bảo mỗi dòng nhạc không bị cắt ngang */
        .khuong-wrapper {{
            margin-top: 50px !important;
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
    
    for i in range(0, len(columns), bits_per_page):
        khuong_columns = columns[i : i + bits_per_page]
        
        # Kiểm tra đệm nhịp (đã có trong code cũ của bạn)
        if len(khuong_columns) < bits_per_page:
            needed = bits_per_page - len(khuong_columns)
            for _ in range(needed):
                khuong_columns.append([0, []])

        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle; font-size: 10px;'>{line_number}</td>"
        
        for col_idx, col in enumerate(khuong_columns):
            notes_in_col = col[1]
            # Lấy danh sách số
            raw_vals = sorted([get_number_from_key(n) for n in notes_in_col], reverse=True)
            
            # --- TÍCH HỢP CHUYỂN ĐỔI ---
            if display_mode == "1. 1.. 1..." or display_mode == "abc":
                vals = [get_symbol(v, display_mode) for v in raw_vals]
            else:
                vals = raw_vals
            
            # ... (Phần logic kẻ bảng giữ nguyên)
            is_new_line = (col_idx == 0)
            is_beat_4 = ((col_idx + 1) % 8 == 0)
            border_right = "0.5px solid #00008c" if (is_beat_4 or (col_idx + 1) == bits_per_page) else "0px solid #ff0000"
            border_left = "0.5px solid #00008c" if is_new_line else "none"

            if vals:
                # Dùng join để nối các số/ký hiệu
                all_nums = "<br>".join(map(str, vals))
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
        line_number += 2

    # Tạo khoảng trắng 50px phía trên tên bài hát
    st.markdown("---")
    st.write('<div style="height: 50px;"></div>', unsafe_allow_html=True)
        
    display_html = f"<h1 style='text-align: center; font-size: 40px; margin-top: 20px; margin-bottom: 70px;'>{song_name}</h1>"
    
    # Render HTML
    for khuong_html in all_khuong_html:
        display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"

    html_to_render = style + display_html
    
    total_height = (len(all_khuong_html) * 110) + 200
    components.html(html_to_render, height=total_height, scrolling=False)

    
    # Tạo khoảng cách cố định 50px
    st.write('<div style="height: 1000px;"></div>', unsafe_allow_html=True)    
    if st.button("to PDF"):
        js_code = "<script>window.parent.window.print();</script>"
        components.html(js_code, height=0)
