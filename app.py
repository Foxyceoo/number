import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
padding_top_px = 40
padding_bottom_px = 90

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---") # Kẻ vạch ngăn cách cho đẹp
    uploaded_file = st.file_uploader("Sheet 123", type=["json"])
    st.markdown("---")
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")

if uploaded_file :
    data = json.load(uploaded_file)
    song_name = uploaded_file.name.replace(".json", "")
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    beat_duration = 60000 / bpm 
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    max_beat = max(time_map.keys()) if time_map else 0

    # CSS của bạn được giữ nguyên
    style = """
    <style>
    /* Cho phép thanh cuộn hiện ra khi nội dung dài */
    body {
        overflow-x: auto !important; 
        overflow-y: auto !important; 
    }
    
    table { 
        border-collapse: collapse; 
        text-align: center; 
        font-size: 16px; 
        width: 100%; 
        margin-bottom: 50px; /* Tăng khoảng cách giữa các bảng nhạc */
        color: inherit; 
    }
    
    td { 
        height: 60px !important;    /* Ép cứng chiều cao, không phụ thuộc nội dung */
        min-height: 50px !important;
        max-height: 50px !important;
        
        vertical-align: middle;     /* Căn giữa số theo chiều dọc để cân đối */
        padding: 0;                 /* Bỏ padding để không làm đẩy ô */
        
        font-weight: bold; 
        width: 40px; 
        border-right: 1px solid #555; 
        border-left: none;
        
        /* Đảm bảo số nằm gọn và không đẩy ô */
        overflow: hidden; 
        line-height: 1.2;
    }
    
    /* Style cho in PDF */
    @media print {
            .page-break { 
                page-break-after: always !important; 
                break-after: page !important;
                display: block;
                height: 0;
            }
            .print-btn, .sidebar, header { display: none !important; }
        }
</style>
    """

    # Tạo danh sách các dòng nhạc
    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle;'>{line_number}</td>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True)
            
            # --- CẤU HÌNH VẠCH KẺ ---
            # Vạch mặc định cho mỗi phách
            border_right = "1px solid #555" 
            
            # Vạch đậm hơn mỗi 4 phách
            if (phach + 1) % 4 == 0: 
                border_right = "2px solid #ff0000"
            
            # Vạch đậm nhất mỗi 16 phách
            if (phach + 1) % 16 == 0: 
                border_right = "3px solid #00008c"
            
            # Vạch bên trái khuông nhạc
            border_left = "3px solid #00008c" if phach == khuong else "none"
            # ------------------------
            
            cell_content = "<br>".join(map(str, vals)) if vals else ""
            
            # Cập nhật style cho thẻ td với các biến trên
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        all_khuong_html.append(html_content)
        line_number += 2

    # Thay bằng dòng này:
    # 2. GHÉP HTML VÀ CHÈN DẤU NGẮT TRANG (Thay thế đoạn display_html cũ)
    display_html = f"<h1 style='text-align: center; margin-top: {padding_top_px}px; margin-bottom: {padding_bottom_px}px;'>{song_name}</h1>"
    
    # Định nghĩa số khuông mỗi trang (ví dụ: mỗi trang 8 khuông)
    khuong_moi_trang = 8
    
    for i in range(0, len(all_khuong_html), khuong_moi_trang):
        # Lấy một cụm khuông nhạc
        cum_khuong = all_khuong_html[i : i + khuong_moi_trang]
        # Nối các bảng lại và thêm thẻ ngắt trang
        display_html += "".join(cum_khuong) + "<div class='page-break'></div>"

    # 1. Tính chiều cao động dựa trên tổng số dòng (all_khuong_html)
    # Mỗi dòng cao 60px (theo CSS của bạn) + một chút khoảng đệm
    total_height = (len(all_khuong_html) * 60) + 100 
    
    # 2. Sử dụng scrolling=False để ẩn thanh cuộn nội bộ
    # 1. Tính chiều cao động dựa trên tổng số dòng (all_khuong_html)
    # 60px là height của td, 50px là margin-bottom của table, 100px là khoảng đệm an toàn
    total_height = (len(all_khuong_html) * (60 + 50)) + 200 
    
    # 2. Sử dụng scrolling=True để nội dung cuộn bên trong iframe
    # 1. TÍNH CHIỀU CAO ĐỘNG (Dựa trên số lượng khuông nhạc)
    # 60px là chiều cao mỗi khuông, 50px là margin, + 300px khoảng đệm an toàn
    total_height = (len(all_khuong_html) * 110) + 300 
    
    # 2. HIỂN THỊ VỚI THANH CUỘN
    # scrolling=True sẽ giúp bạn cuộn xem bản nhạc dài, 
    # và khi bạn cuộn đến đâu, in đến đó sẽ rất tiện!
    components.html(
        f"<html><head>{style}</head><body>{display_html}</body></html>", 
        height=total_height, 
        scrolling=True
    )

    # NÚT IN PDF
    # 3. NÚT IN PDF (Dùng HTML để gọi lệnh in)
    st.markdown("""
    <style>
        @media print {
            .print-btn { display: none !important; }
        }
        .print-btn {
            display: inline-block;
            padding: 0.5em 1em;
            /* CHỈNH 2 DÒNG DƯỚI ĐÂY LÀ ĐƯỢC */
            background-color: #ffcbcc; /* Màu nền mới */
            color: #00008c;             /* Màu chữ mới */
            /* ----------------------------- */
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
            border: none;
            margin-top: 20px;
        }
    </style>
    <a href="#" class="print-btn" onclick="window.print(); return false;">Mở bảng in</a>
    """, unsafe_allow_html=True)
