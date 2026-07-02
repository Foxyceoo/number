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
                    
        if st.button("Đăng logout"):
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

# ==========================================
# GOM TOÀN BỘ SIDEBAR VÀO ĐÂY ĐỂ TRÁNH LỖI NHẢY ELEMENT
# ==========================================
with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    uploaded_files = st.file_uploader(
        "Nhập file của bạn", 
        type=["json"], 
        accept_multiple_files=True
    )
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")
    
    # Nút chọn chế độ
    display_mode = st.radio("Chế độ hiển thị:", ["1-15", "1. 1.. 1...", "abc"])
    st.markdown("---")

    # HIỂN THỊ DANH SÁCH BÀI HÁT NGAY TRONG BLOCK SIDEBAR CHÍNH
    if uploaded_files:
        if "selected_song_index" not in st.session_state:
            st.session_state.selected_song_index = 0
            
        st.write("**Danh sách bài hát:**")
        for index, file in enumerate(uploaded_files):
            display_name = file.name.replace(".json", "")
            
            is_selected = st.session_state.selected_song_index == index
            btn_type = "primary" if is_selected else "secondary"
            
            if st.button(display_name, key=f"btn_song_{index}", type=btn_type, use_container_width=True):
                st.session_state.selected_song_index = index
                st.rerun()

# Xử lý logic đọc dữ liệu sau khi Sidebar đã dựng xong ổn định
if uploaded_files:
    if st.session_state.selected_song_index >= len(uploaded_files):
        st.session_state.selected_song_index = 0
        
    current_selected_file = uploaded_files[st.session_state.selected_song_index]
    
    # Tiếp tục luồng xử lý JSON của cậu
    data = json.load(current_selected_file)
    song_data = data[0]
    song_name = current_selected_file.name.replace(".json", "")
    
    # =========================================================================
    # CÁC THUẬT TOÁN ĐẰNG SAU GIỮ NGUYÊN HOÀN TOÀN...
    # =========================================================================
    
    # =========================================================================
    # 1. THUẬT TOÁN KHÔI PHỤC KHOẢNG LẶNG (Điền đầy đủ các phách trống bị thiếu)
    # =========================================================================
    raw_columns = song_data.get("columns", [])
    bits_per_page = 32  # Nếu muốn đổi thành 64 phách, bạn cứ sửa số này nhé!
    
    if raw_columns:
        max_bit_index = max([col[0] for col in raw_columns])
        columns = [[i, []] for i in range(max_bit_index + 1)]
        for col in raw_columns:
            bit_pos = col[0]
            columns[bit_pos] = col
    else:
        columns = []
  

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

    st.markdown(
        """
        <style>
        /* Mở rộng tối đa container chính của Streamlit */
        .block-container {
            max-width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 2rem !important;
        }
        /* Căn giữa thành phần iframe */
        iframe {
            display: block;
            margin: 0 auto !important;
            width: 90% !important;
        }
        
        /* ========================================================================= */
        /* MỚI: Tác động trực tiếp lên Sidebar để thu ngắn ô nhập và ẩn danh sách file */
        /* ========================================================================= */
        /* 1. Ép chiều cao ô nhập file ngắn lại */
        [data-testid="stSidebar"] [data-testid="stFileUploader"] section {
            padding: 10px !important;
            min-height: 60px !important;
            height: 60px !important;
        }
        
        /* 2. Thu nhỏ icon và chữ hướng dẫn cho gọn */
        [data-testid="stSidebar"] [data-testid="stFileUploader"] section svg {
            transform: scale(0.7) !important;
            margin-bottom: 0px !important;
        }
        [data-testid="stSidebar"] [data-testid="stFileUploader"] section small {
            font-size: 11px !important;
        }

        /* 3. Ẩn danh sách file lặp mặc định xuất hiện ở Sidebar */
        [data-testid="stSidebar"] [data-testid="stFileUploaderFilesContainer"],
        [data-testid="stSidebar"] [data-testid="stFileUploader"] + div,
        [data-testid="stSidebar"] .uploadedFiles,
        [data-testid="stSidebar"] .uploadedFile {
            display: none !important;
            height: 0px !important;
            padding: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

        
    #CSS
    # =========================================================================
    # 2. ĐỊNH NGHĨA CSS TRANG GIẤY A4 (Đã thêm lề trang trái/phải 20px)
    # =========================================================================
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
    
    /* Trang A4 chuẩn Web - Đã thêm căn giữa trên/dưới */
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

        /* ========================================================================= */
        /* MỚI: Biến trang giấy thành Flexbox để căn giữa nội dung theo chiều dọc */
        /* ========================================================================= */
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important; /* Căn giữa tất cả các dòng nhạc theo chiều dọc */
    }

    /* Bảng nhạc co giãn ăn trọn 100% không gian còn lại sau khi đã trừ lề */
    table { 
        border-collapse: collapse !important; 
        text-align: center; 
        table-layout: fixed !important; 
        width: 94% !important; /* Đồng bộ độ rộng co vào tại đây */
        margin: 0 auto !important; /* Luôn luôn nằm chính giữa trang giấy */
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
        /* 1. Ẩn toàn bộ giao diện thừa của Streamlit */
        header, footer, .sidebar, [data-testid="stSidebar"], .stAppDeployButton, button {
            display: none !important;
        }
        
        /* 2. Đưa body về trạng thái in chuẩn, xóa sạch nền xám và khoảng cách thừa */
        html, body {
            background-color: #ffffff !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
        }

        /* 3. Ép các trang giấy A4 hiển thị chuẩn xác khi xuất file */
        .sheet-page {
            width: 100% !important;
            max-width: 794px !important;
            box-shadow: none !important;
            border: none !important;
            margin: 0 auto !important;
            padding: 50px 0px !important; /* Giữ nguyên lề trên dưới bạn vừa chỉnh */
            
            /* Ép trình duyệt BẮT BUỘC phải ngắt trang sau khi hết 1 khối .sheet-page */
            page-break-after: always !important;
            break-after: page !important;
        }

        /* 4. Cấu hình cài đặt trang in của trình duyệt */
        @page {
            size: A4 portrait;
            margin: 0; /* Xóa lề mặc định của trình duyệt để không bị lệch */
        }
    }
    </style>
    """
    
    # =========================================================================
    # 4. VÒNG LẶP DỰNG BẢNG KHUÔNG NHẠC CHIA ĐỀU TỶ LỆ %
    # =========================================================================
    all_khuong_html = []
    
    for i in range(0, len(columns), bits_per_page):
        khuong_columns = columns[i : i + bits_per_page]
        
        if len(khuong_columns) < bits_per_page:
            needed = bits_per_page - len(khuong_columns)
            for _ in range(needed):
                khuong_columns.append([0, []])

        # MỚI: Ép chiều rộng bảng nhạc co lại còn 94% và căn giữa để tự tạo lề trái/phải đều nhau
        html_content = "<table style='table-layout: fixed; width: 90% !important; border-collapse: collapse; margin: 0 auto !important; padding: 0;'><tr>"
        cell_width_pct = 100.0 / bits_per_page

        for col_idx, col in enumerate(khuong_columns):
            notes_in_col = col[1] if len(col) > 1 else []
            raw_vals = sorted([get_number_from_key(n) for n in notes_in_col], reverse=True)
            
            if display_mode == "1. 1.. 1..." or display_mode == "abc":
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
                    <!-- Yaoyao đã tăng font-size từ 10px lên 15px và chỉnh lại line-height cho thoáng -->
                    <div style='font-size: 15px; font-weight: bold; line-height: 1.3; text-align: center; font-family: monospace, sans-serif;'>{all_nums}</div>
                </div>
                """
            else:
                # Đồng bộ min-height cho các ô trống để hàng nhạc thẳng tắp
                cell_content = "<div style='min-height: 60px;'></div>"

            html_content += f"<td style='width: {cell_width_pct}%; border-right: {border_right}; border-left: {border_left}; padding: 2px 0 !important; vertical-align: top; box-sizing: border-box;'>{cell_content}</td>"
        
        html_content += "</tr></table>"
        all_khuong_html.append(html_content)
        
    # =========================================================================
    # 5. XẾP DÒNG NHẠC VÀO TRANG GIẤY CHUẨN & TỰ ĐỘNG BÙ KHUÔNG ẨN (8 DÒNG/TRANG)
    # =========================================================================
    display_html = ""
    lines_per_page = 8  # Đã đổi thành 8 dòng theo ý bạn nè!
    
    # Danh sách chứa HTML của từng trang sau khi gom đủ 8 dòng
    pages_list = []
    
    for idx in range(0, len(all_khuong_html), lines_per_page):
        chunk = all_khuong_html[idx : idx + lines_per_page]
        
        page_content = "<div class='sheet-page'>"
        
        # 1. Chèn các khuông nhạc có dữ liệu thực tế vào trước
        for khuong_html in chunk:
            page_content += f"<div class='khuong-wrapper'>{khuong_html}</div>"
        
        # 2. TRƯỜNG HỢP TRANG CUỐI THIẾU DÒNG: Tự động bù các khuông nhạc ẩn cho đủ 8 dòng
        if len(chunk) < lines_per_page:
            needed_lines = lines_per_page - len(chunk)
            
            # Tạo một khung bảng trống có kích thước y hệt khuông thật để giữ dáng hàng
            cell_width_pct = 100.0 / bits_per_page
            empty_table = "<table style='table-layout: fixed; width: 94% !important; border-collapse: collapse; margin: 0 auto !important; padding: 0;'><tr>"
            for _ in range(bits_per_page):
                empty_table += f"<td style='width: {cell_width_pct}%; padding: 2px 0 !important; vertical-align: top; box-sizing: border-box;'><div style='min-height: 60px;'></div></td>"
            empty_table += "</tr></table>"
            
            # Bù thêm số dòng ẩn cần thiết
            for _ in range(needed_lines):
                page_content += f"<div class='khuong-wrapper' style='visibility: hidden;'>{empty_table}</div>"
        
        page_content += "</div>"
        pages_list.append(page_content)
        
    # Chuỗi HTML đầy đủ để hiển thị trên Web xem trước
    html_to_render = page_style + "".join(pages_list)
    
    # Tính chiều cao hiển thị trên web (8 dòng thì trang sẽ cao hơn một chút)
    total_pages = len(pages_list)
    calculated_height = total_pages * 1200 + 100
    
    # Render nội dung chính lên màn hình Web hiển thị
    components.html(html_to_render, height=calculated_height, scrolling=False)
    
    # =========================================================================
    # 6. XỬ LÝ TRUYỀN TOÀN BỘ TRANG IN BẰNG PYTHON & MÃ HÓA JSON AN TOÀN
    # =========================================================================
    st.write('<div style="height: 20px;"></div>', unsafe_allow_html=True)    
    
    # 1. Khởi tạo trạng thái kích hoạt in nếu chưa tồn tại
    if "trigger_print" not in st.session_state:
        st.session_state.trigger_print = False

    # 2. Khi bấm nút, bật cờ trigger
    if st.button("Xuất PDF", key="btn_to_pdf_layout"):
        if not pages_list:
            st.error("Không có dữ liệu trang để in!")
        else:
            st.session_state.trigger_print = True

    # 3. Khi cờ trigger được bật, tiến hành sinh JS
    if st.session_state.get("trigger_print", False):
        html_for_print = page_style + "".join(pages_list)
        
        import json
        safe_html_json = json.dumps(html_for_print)
        
        # Tạo mã số duy nhất dựa trên thời gian
        print_id = int(time.time())
        
        # Chèn thẳng print_id vào comment của JS để thay đổi nội dung chuỗi, ép Streamlit reload lại component này
        js_code_print = f"""
        <script>
        (function() {{
            // ID lượt in: {print_id}
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
            }}, 500);
        }})();
        </script>
        """
        # Bỏ tham số key lỗi đi, chỉ giữ lại nội dung và chiều cao
        components.html(js_code_print, height=0)
        
        # 4. Tắt cờ trigger để sẵn sàng cho lần bấm tiếp theo
        st.session_state.trigger_print = False
