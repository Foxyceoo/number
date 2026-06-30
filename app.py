import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
st.title("Bộ chuyển đổi sheet số")
# Tùy chỉnh khoảng cách tên bài hát (thay số 40 theo ý bạn)
padding_top_px = 40
padding_bottom_px = 90

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải lên file JSON", type=["json"]):
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
    /* Chỉnh lề body để bảng không bị dính sát mép trình duyệt */
    body { 
        font-family: sans-serif; 
        padding: 40px 20px; /* Cách trên dưới 40px, trái phải 20px */
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
        height: 60px; 
        vertical-align: top; 
        /* Chỉnh lề trong ô để số cân đối hơn */
        padding-top: 10px; 
        font-weight: bold; 
        width: 40px; 
        border-top: 0px solid rgba(128, 128, 128, 0.3);
        border-bottom: 0px solid rgba(128, 128, 128, 0.3);
        border-right: 1px solid #555; 
        border-left: none;
        color: currentColor; 
    }
    
    /* Style cho in PDF */
    @media print {
        .page-break { page-break-after: always; }
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
    # Cập nhật đoạn này với f-string và các biến đã khai báo
    display_html = f"""
    <h1 style='text-align: center; margin-top: {padding_top_px}px; margin-bottom: {padding_bottom_px}px;'>
        {song_name}
    </h1>
    """ + "".join(all_khuong_html[0:8]) + "<div class='page-break'></div>"

    for i in range(8, len(all_khuong_html), 10):
        display_html += "".join(all_khuong_html[i:i+10]) + "<div class='page-break'></div>"

    # 1. Tính chiều cao động dựa trên tổng số dòng (all_khuong_html)
    # Mỗi dòng cao 60px (theo CSS của bạn) + một chút khoảng đệm
    total_height = (len(all_khuong_html) * 60) + 100 
    
    # 2. Sử dụng scrolling=False để ẩn thanh cuộn nội bộ
    # Thay vì components.html, hãy dùng st.markdown
    st.markdown(f"<html><head>{style}</head><body>{display_html}</body></html>", unsafe_allow_html=True)
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
