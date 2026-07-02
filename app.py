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
    style = """
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/turn.js/3/turn.min.js"></script>
    <style>
    ::-webkit-scrollbar { display: none !important; }
    body { 
        background-color: #f0f2f6; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin: 0; 
        padding: 20px;
        font-family: sans-serif;
    }
    
    /* Khung cuốn sách */
    #flipbook {
        width: 800px;
        height: 550px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Định hình từng trang sách */
    .page {
        background-color: #ffffff;
        box-sizing: border-box;
        padding: 25px 35px;
        border-right: 1px solid #ddd;
        overflow: hidden;
    }
    
    /* Trang bìa */
    .cover-page {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }

    table { 
        border-collapse: collapse; 
        text-align: center; 
        table-layout: fixed !important; 
        width: 100%; 
        margin: 0 auto 15px auto; 
    }

    td { 
        padding: 2px !important;  
        width: 20px !important; 
        vertical-align: top !important; 
        border-right: 1px solid #ccc; 
    }
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
        
    # === THAY THẾ TỪ ĐÂY ĐỂ CHUYỂN SANG DẠNG LẬT TRANG ===
    
    # 1. Tạo cấu trúc lật trang và trang bìa đầu tiên
    display_html = f"""
    <div id="flipbook">
        <div class="page cover-page">
            <h1 style="font-size: 32px; margin-bottom: 10px; font-weight: bold;">{song_name}</h1>
            <p style="font-size: 14px; opacity: 0.8; font-style: italic;">Nhấp vào mép giấy bên phải để mở sách</p>
        </div>
    """
    
    # 2. Chia các khuông nhạc vào từng trang (mỗi trang chứa đúng 3 dòng nhạc để vừa khung)
    lines_per_page = 3
    for idx in range(0, len(all_khuong_html), lines_per_page):
        chunk = all_khuong_html[idx : idx + lines_per_page]
        
        display_html += "<div class='page'>"
        for khuong_html in chunk:
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"
        display_html += "</div>"
        
    # 3. Thêm mã JavaScript kích hoạt hiệu ứng lật sách 3D của Turn.js
    # === THAY THẾ TOÀN BỘ ĐOẠN CUỐI TỪ ĐÂY ĐẾN HẾT FILE ===
    
    # 1. Tạo cấu trúc lật trang và trang bìa đầu tiên
    display_html = f"""
    <div id="flipbook">
        <div class="page cover-page">
            <h1 style="font-size: 32px; margin-bottom: 10px; font-weight: bold;">{song_name}</h1>
            <p style="font-size: 14px; opacity: 0.8; font-style: italic;">Nhấp vào mép giấy bên phải để mở sách</p>
        </div>
    """
    
    # 2. Chia các khuông nhạc vào từng trang (mỗi trang chứa đúng 3 dòng nhạc để vừa khung)
    lines_per_page = 3
    for idx in range(0, len(all_khuong_html), lines_per_page):
        chunk = all_khuong_html[idx : idx + lines_per_page]
        
        display_html += "<div class='page'>"
        for khuong_html in chunk:
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"
        display_html += "</div>"
        
    # === THAY THẾ TOÀN BỘ ĐOẠN CUỐI TỪ ĐÂY ĐẾN HẾT FILE ===
    
    # 1. Định nghĩa lại Style để hiển thị dạng trang giấy trải dài (A4-like style)
    # Bỏ thư viện turn.js cũ, chỉ giữ lại CSS tạo khung trang giấy đẹp mắt
    page_style = """
    <style>
    ::-webkit-scrollbar { display: none !important; }
    body { 
        background-color: #f0f2f6; 
        margin: 0; 
        padding: 20px;
        font-family: sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 25px; /* Khoảng cách giữa các trang giấy */
    }
    
    /* Định hình từng trang giấy trắng riêng biệt */
    .sheet-page {
        background-color: #ffffff;
        box-sizing: border-box;
        width: 800px;
        min-height: 850px; /* Chiều cao vừa vặn cho 5 dòng nhạc */
        padding: 40px 35px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-radius: 4px;
        page-break-after: always; /* Lệnh cài đặt giúp trình duyệt tự cắt trang chuẩn khi in PDF */
    }
    
    /* Thiết kế tiêu đề trang bìa / đầu trang */
    .sheet-header {
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #333;
        padding-bottom: 10px;
    }

    table { 
        border-collapse: collapse; 
        text-align: center; 
        table-layout: fixed !important; 
        width: 100%; 
        margin: 0 auto 25px auto; 
    }

    td { 
        padding: 2px !important;  
        width: 20px !important; 
        vertical-align: top !important; 
        border-right: 1px solid #ccc; 
    }
    
    /* Khi bấm In/Xuất PDF, ẩn bớt bóng đổ nền để trang in sạch đẹp */
    @media print {
        body { background-color: #ffffff; padding: 0; }
        .sheet-page { box-shadow: none; padding: 0; width: 100%; }
    }
    </style>
    """
    
    # 2. Bắt đầu xây dựng chuỗi HTML hiển thị tất cả các trang
    display_html = ""
    
    # Thiết lập số dòng nhạc trên mỗi trang là 5
    lines_per_page = 5
    page_count = 1
    
    # Vòng lặp chia cụm all_khuong_html, mỗi cụm lấy đúng 5 dòng
    for idx in range(0, len(all_khuong_html), lines_per_page):
        chunk = all_khuong_html[idx : idx + lines_per_page]
        
        # Mở một trang giấy mới
        display_html += "<div class='sheet-page'>"
        
        # Nếu là trang đầu tiên (Trang 1), chèn thêm Tiêu đề bài hát làm trang bìa đầu sheet
        if page_count == 1:
            display_html += f"""
            <div class='sheet-header'>
                <h1 style="font-size: 32px; margin: 0 0 5px 0; color: #1a2a4a; font-weight: bold;">{song_name}</h1>
                <p style="font-size: 13px; color: #666; font-style: italic; margin: 0;">Bộ chuyển đổi sheet số điện tử</p>
            </div>
            """
        else:
            # Từ trang 2 trở đi, chèn một tiêu đề nhỏ (Header) ở góc trên cho chuyên nghiệp
            display_html += f"""
            <div style="display: flex; justify-content: space-between; font-size: 11px; color: #888; margin-bottom: 20px; border-bottom: 1px dashed #ccc; padding-bottom: 5px;">
                <span>{song_name}</span>
                <span>Trang {page_count}</span>
            </div>
            """
            
        # Thêm lần lượt 5 khuông nhạc thuộc trang này vào
        for khuong_html in chunk:
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"
            
        # Đóng trang giấy
        display_html += "</div>"
        page_count += 1
        
    # 3. Gom style và toàn bộ các trang giấy để render lên Streamlit
    html_to_render = page_style + display_html
    
    # Tính toán chiều cao tổng thể để khung components mở rộng tối đa theo số lượng trang, không bị xuất hiện thanh cuộn bên trong khung
    # Trung bình mỗi trang giấy kèm khoảng cách rộng tầm 900px
    total_pages = math.ceil(len(all_khuong_html) / lines_per_page)
    calculated_height = total_pages * 900 + 100
    
    # Render toàn bộ các trang nhạc ra màn hình
    components.html(html_to_render, height=calculated_height, scrolling=False)
    
    # 4. Nút bấm xuất sang PDF của Streamlit đặt ở cuối cùng
    st.write('<div style="height: 20px;"></div>', unsafe_allow_html=True)    
    if st.button("Xuất PDF / In Sheet nhạc 🖨️", key="btn_to_pdf_layout"):
        js_code_print = "<script>window.parent.window.print();</script>"
        components.html(js_code_print, height=0)
