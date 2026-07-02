import streamlit as st
import pandas as pd
import json
import math
import time
import pyrebase
import requests
import streamlit.components.v1 as components

# Khởi tạo URL dữ liệu và cấu hình Firebase
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT4HTreKOHkHRXq2zdolvnEt2o5HyDN6JAWBy3DSI8kRgftC3_pAHJZKztQCXfBrLzvVbw0ohY6vfNG/pub?gid=0&single=true&output=csv"

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
@st.cache_resource
def init_firebase():
    firebase = pyrebase.initialize_app(config)
    return firebase.auth()

auth = init_firebase()

# Quản lý trạng thái đăng nhập
if 'user' not in st.session_state:
    st.session_state.user = None
if 'is_loaded' not in st.session_state:
    st.session_state.is_loaded = False

# Giao diện đăng nhập đơn giản
def login_form():
    st.title("Đăng nhập")
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Mật khẩu", type="password", key="pass_input")
    
    if st.button("Đăng nhập", use_container_width=True):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.user_name = email.split('@')[0]
            st.session_state.is_loaded = False 
            st.rerun() 
        except Exception as e:
            st.error("Email hoặc mật khẩu không chính xác. Vui lòng thử lại!")
            
# Luồng kiểm tra đăng nhập
if st.session_state.user is None:
    login_form()
    st.stop() 

# Hiển thị spinner nạp dữ liệu 1 lần duy nhất sau login
if not st.session_state.is_loaded:
    with st.spinner('Đang tải dữ liệu...'):
        time.sleep(1.5)
    st.session_state.is_loaded = True
    st.rerun()

# Hiển thị lời chào sau khi tải xong
st.success(f"Hello, {st.session_state.user_name}!")

# Chức năng bổ trợ hiển thị ký tự nốt nhạc
def get_number_from_key(note_data):
    pitch = int(note_data[0])
    return pitch + 1 

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
    else: 
        return str(value)
    return mapping.get(value, str(value))

# --- THIẾT KẾ SIDEBAR ---
with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    uploaded_files = st.file_uploader(
        "Nhập file của bạn", 
        type=["json"], 
        accept_multiple_files=True 
    )
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    
    # Render danh sách nút chọn bài hát ngay trong sidebar cho gọn gàng
    if uploaded_files:
        st.markdown("---")
        st.write("**Danh sách bài hát:**")
        if "selected_song_index" not in st.session_state:
            st.session_state.selected_song_index = 0
            
        if st.session_state.selected_song_index >= len(uploaded_files):
            st.session_state.selected_song_index = 0
            
        for index, file in enumerate(uploaded_files):
            display_name = file.name.replace(".json", "")
            is_selected = st.session_state.selected_song_index == index
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(display_name, key=f"btn_song_{index}", type=btn_type, use_container_width=True):
                st.session_state.selected_song_index = index
                st.rerun()

    st.markdown("---")
    display_mode = st.sidebar.radio("Chế độ hiển thị:", ["1-15", "1. 1.. 1...", "abc"])
    st.markdown("---")
    
    # Tiện ích tài khoản
    st.write(f"**Người dùng:** {st.session_state.user_name}")
    if st.button("Đổi mật khẩu", use_container_width=True):
        st.session_state.show_change_password = not st.session_state.get("show_change_password", False)
        
    if st.session_state.get("show_change_password", False):
        with st.form("change_password_inner"):
            new_password = st.text_input("Nhập mật khẩu mới", type="password")
            if st.form_submit_button("Xác nhận đổi"):
                try:
                    id_token = st.session_state.user['idToken']
                    api_key = st.secrets["FIREBASE_API_KEY"]
                    api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
                    payload = {"idToken": id_token, "password": new_password, "returnSecureToken": True}
                    response = requests.post(api_url, json=payload)
                    
                    if response.status_code == 200:
                        st.success("Đổi mật khẩu thành công!")
                        st.session_state.show_change_password = False
                    else:
                        st.error("Có lỗi xảy ra khi đổi mật khẩu.")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
                    
    if st.button("Đăng xuất", use_container_width=True):
        st.session_state.user = None
        st.session_state.is_loaded = False
        st.rerun()

# --- XỬ LÝ DỮ LIỆU CHÍNH & HIỂN THỊ SHEET ---
if uploaded_files:
    current_selected_file = uploaded_files[st.session_state.selected_song_index]
    
    # Đảm bảo con trỏ file quay về đầu để không bị lỗi trống dữ liệu khi rerun
    current_selected_file.seek(0)
    data = json.load(current_selected_file)
    song_data = data[0]
    
    # 1. THUẬT TOÁN KHÔI PHỤC KHOẢNG LẶNG
    raw_columns = song_data.get("columns", [])
    bits_per_page = 32  
    
    if raw_columns:
        max_bit_index = max([col[0] for col in raw_columns])
        columns = [[i, []] for i in range(max_bit_index + 1)]
        for col in raw_columns:
            bit_pos = col[0]
            columns[bit_pos] = col
    else:
        columns = []

    # Inject CSS làm rộng container hiển thị nội dung chính
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
        }
        iframe {
            display: block;
            margin: 0 auto !important;
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Cấu hình Style CSS cho trang giấy A4
    page_style = """
    <style>
    ::-webkit-scrollbar { display: none !important; }
    body { 
        background-color: #f0f2f6; 
        margin: 0; 
        padding: 20px 0;
        font-family: sans-serif;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
    }
    .sheet-page {
        background-color: #ffffff;
        box-sizing: border-box;
        width: 794px;
        min-height: 1123px;
        padding: 60px 0px !important; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-radius: 4px;
        page-break-after: always;
        margin-bottom: 25px;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important; 
    }
    table { 
        border-collapse: collapse !important; 
        text-align: center; 
        table-layout: fixed !important; 
        width: 94% !important; 
        margin: 0 auto !important; 
        padding: 0 !important;
    }
    td { 
        padding: 2px 0 !important;  
        vertical-align: top !important; 
        overflow: hidden;
        box-sizing: border-box !important;
    }
    .khuong-wrapper {
        width: 100% !important;
        padding: 0 !important;
        margin-bottom: 35px !important;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    @media print {
        header, footer, .sidebar, [data-testid="stSidebar"], .stAppDeployButton, button {
            display: none !important;
        }
        html, body {
            background-color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }
        .sheet-page {
            width: 100% !important;
            max-width: 794px !important;
            box-shadow: none !important;
            border: none !important;
            margin: 0 auto !important;
            padding: 50px 0px !important; 
            page-break-after: always !important;
            break-after: page !important;
        }
        @page {
            size: A4 portrait;
            margin: 0; 
        }
    }
    </style>
    """
    
    # 2. VÒNG LẶP DỰNG BẢNG KHUÔNG NHẠC CHIA ĐỀU TỶ LỆ
    all_khuong_html = []
    for i in range(0, len(columns), bits_per_page):
        khuong_columns = columns[i : i + bits_per_page]
        
        if len(khuong_columns) < bits_per_page:
            needed = bits_per_page - len(khuong_columns)
            for _ in range(needed):
                khuong_columns.append([0, []])

        html_content = "<table style='table-layout: fixed; width: 90% !important; border-collapse: collapse; margin: 0 auto !important; padding: 0;'><tr>"
        cell_width_pct = 100.0 / bits_per_page

        for col_idx, col in enumerate(khuong_columns):
            notes_in_col = col[1] if len(col) > 1 else []
            raw_vals = sorted([get_number_from_key(n) for n in notes_in_col], reverse=True)
            
            if display_mode in ["1. 1.. 1...", "abc"]:
                vals = [get_symbol(v, display_mode) for v in raw_vals]
            else:
                vals = raw_vals
            
            is_new_line = (col_idx == 0)
            is_beat_4 = ((col_idx + 1) % 8 == 0)
            
            border_right = "1.5px solid #00008c" if (is_beat_4 or (col_idx + 1) == bits_per_page) else "none"
            border_left = "1.5px solid #00008c" if is_new_line else "none"

            if vals:
                all_nums = "<br>".join(map(str, vals))
                cell_content = f"""
                <div style='display: flex; flex-direction: column; align-items: center; justify-content: flex-start; min-height: 60px;'>
                    <div style='font-size: 15px; font-weight: bold; line-height: 1.3; text-align: center; font-family: monospace, sans-serif;'>{all_nums}</div>
                </div>
                """
            else:
                cell_content = "<div style='min-height: 60px;'></div>"

            html_content += f"<td style='width: {cell_width_pct}%; border-right: {border_right}; border-left: {border_left}; padding: 2px 0 !important; vertical-align: top; box-sizing: border-box;'>{cell_content}</td>"
        
        html_content += "</tr></table>"
        all_khuong_html.append(html_content)
        
    # 3. PHÂN TRANG VÀ TỰ ĐỘNG BÙ KHUÔNG ẨN (8 DÒNG/TRANG)
    lines_per_page = 8  
    pages_list = []
    
    for idx in range(0, len(all_khuong_html), lines_per_page):
        chunk = all_khuong_html[idx : idx + lines_per_page]
        page_content = "<div class='sheet-page'>"
        
        for khuong_html in chunk:
            page_content += f"<div class='khuong-wrapper'>{khuong_html}</div>"
        
        if len(chunk) < lines_per_page:
            needed_lines = lines_per_page - len(chunk)
            cell_width_pct = 100.0 / bits_per_page
            empty_table = "<table style='table-layout: fixed; width: 94% !important; border-collapse: collapse; margin: 0 auto !important; padding: 0;'><tr>"
            for _ in range(bits_per_page):
                empty_table += f"<td style='width: {cell_width_pct}%; padding: 2px 0 !important; vertical-align: top; box-sizing: border-box;'><div style='min-height: 60px;'></div></td>"
            empty_table += "</tr></table>"
            
            for _ in range(needed_lines):
                page_content += f"<div class='khuong-wrapper' style='visibility: hidden;'>{empty_table}</div>"
        
        page_content += "</div>"
        pages_list.append(page_content)
        
    html_to_render = page_style + "".join(pages_list)
    
    # Tính toán chiều cao hiển thị tương thích số trang để tránh cuộn đôi
    total_pages = len(pages_list)
    calculated_height = total_pages * 1180 + 50
    
    # Kết xuất giao diện xem trước bài hát hoàn chỉnh
    components.html(html_to_render, height=calculated_height, scrolling=True)
    
    # NÚT XUẤT FILE PDF TRỰC TIẾP KHÔNG DÙNG STATE TRIGGER (TRÁNH LỖI PHÁT SINH KHI RE-RENDER)
    st.write('<div style="height: 10px;"></div>', unsafe_allow_html=True)    
    
    if st.button("Xuất PDF Toàn Bộ Bản Nhạc", key="btn_to_pdf_layout", type="primary", use_container_width=True):
        if not pages_list:
            st.error("Không có dữ liệu trang để in!")
        else:
            safe_html_json = json.dumps(html_to_render)
            js_code_print = f"""
            <script>
            (function() {{
                var htmlContent = {safe_html_json};
                var printWindow = window.open('', '_blank');
                if (!printWindow) {{
                    alert('Trình duyệt đã chặn cửa sổ bật lên (Popup). Bạn hãy cho phép hiện popup để in nhé!');
                    return;
                }}
                printWindow.document.write('<html><head><title>In Toàn Bộ Sheet Nhạc</title></head><body>' + htmlContent + '</body></html>');
                printWindow.document.close();
                printWindow.focus();
                setTimeout(function() {{
                    printWindow.print();
                    printWindow.close();
                }}, 600);
            }})();
            </script>
            """
            components.html(js_code_print, height=0)
else:
    st.info("Cậu hãy thả hoặc chọn các file JSON ở thanh Sidebar bên trái để hiển thị sheet nhạc nhé!")
