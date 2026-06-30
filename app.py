import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
padding_top_px = 40
padding_bottom_px = 90
margin_side = "1000px"

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---")  # Kẻ vạch ngăn cách cho đẹp
    uploaded_file = st.file_uploader("**Sheet 123**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")

if uploaded_file:
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
    # Nhân đôi {{ }} cho những đoạn CSS không phải biến Python
    # Sửa lại đoạn style, xóa các dòng chú thích /*...*/ bên trong f-string
    style = f"""
    <style>
    ::-webkit-scrollbar {{ display: none !important; }}
    
    html, body {{ width: 100%; margin: 0; padding: 0; overflow-y: hidden !important; }}

    table {{ 
        border-collapse: collapse; 
        text-align: center; 
        table-layout: fixed !important; 
        width: {margin_side}; 
        margin: 0 auto 30px auto; 
        height: 50px !important; 
    }}

    td {{ 
        padding: 0 !important; 
        height: 50px !important; 
        width: 20px !important; 
        vertical-align: top !important; 
        border-right: 1px solid #555; 
        border-left: none; 
        overflow: hidden;
    }}

    /* Đưa các class này ra ngoài table để chúng có hiệu lực */
    .top-row {{ 
        font-size: 16px !important; 
        font-weight: bold !important; 
        line-height: 1 !important; 
    }}

    .bottom-row {{ 
        font-size: 16px !important; 
        line-height: 1 !important; 
        margin-top: 2px !important;
    }}

    @media print {{
        .sidebar, header, .stAppDeployButton, footer {{ display: none !important; }}
        table {{ page-break-inside: avoid !important; margin-bottom: 20px !important; }}
    }}
    </style>
    """
    # Tạo danh sách các dòng nhạc
    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        # Sửa đoạn này trong vòng lặp tạo khuông nhạc:
        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle; font-size: 10px;'>{line_number}</td>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True)

            # --- CẤU HÌNH VẠCH KẺ ---
            # Vạch mặc định cho mỗi phách
            border_right = "0.1px solid #d8d8d8"

            # Vạch đậm hơn mỗi 4 phách
            if (phach + 1) % 4 == 0:
                border_right = "1px solid #00008c"

            # Vạch đậm nhất mỗi 16 phách
            if (phach + 1) % 16 == 0:
                border_right = "2px solid #00008c"

            # Vạch bên trái khuông nhạc
            border_left = "2px solid #00008c" if phach == khuong else "none"
            # ------------------------

            # Sửa lại phần này để bỏ min-height động
            if vals:
                top_num = vals[0]
                bottom_nums = "<br>".join(map(str, vals[1:]))
                # Dùng height: 100% để ép div nằm gọn trong td 50px
                cell_content = f"""
                <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 50px;'>
                    <div class='top-row'>{top_num}</div>
                    <div class='bottom-row'>{bottom_nums}</div>
                </div>
                """
            else:
                cell_content = ""

            # Cập nhật style cho thẻ td với các biến trên
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        all_khuong_html.append(html_content)
        line_number += 2

    # GHÉP HTML VÀ CHÈN DẤU NGẮT TRANG
    display_html = f"<h1 style='text-align: center; margin-top: {padding_top_px}px; margin-bottom: {padding_bottom_px}px;'>{song_name}</h1>"

    # Định nghĩa chiều cao tối đa của một trang in (ví dụ: 800px)
    PAGE_HEIGHT_LIMIT = 800
    current_page_height = 0
    # Sửa lại phần này, giảm margin-bottom xuống (ví dụ 10px hoặc 5px)
    display_html = f"<h1 style='text-align: center; font-size: 40px; margin-top: 20px; margin-bottom: 70px;'>{song_name}</h1>"

    for khuong_html in all_khuong_html:
        # Giả định mỗi khuông nhạc có chiều cao khoảng 110px (cần khớp với tính toán của bạn)
        khuong_height = 110 
        
        if current_page_height + khuong_height > PAGE_HEIGHT_LIMIT:
            # Nếu khuông này làm vượt quá chiều cao trang, ngắt trang và reset chiều cao
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div><div class='page-break'></div>"
            current_page_height = khuong_height
        else:
            # Nếu vẫn đủ chỗ, thêm khuông vào trang hiện tại
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"
            current_page_height += khuong_height

    # --- ĐÂY LÀ ĐOẠN ĐÃ SỬA ---
    # Kết hợp style và nội dung vào biến html_to_render
    html_to_render = style + display_html

    # Sửa lại công thức tính toán chiều cao cho khớp với 50px
    # Nếu mỗi khuông là 50px và margin-bottom là 30px như trong CSS:
    row_height = 50 + 30 
    total_height = (len(all_khuong_html) * row_height) + 150

    # Và trong vòng lặp tính current_page_height, cũng phải sửa:
    khuong_height = 80 # (50px table + 30px margin)

    # Gọi component với chiều cao đã tính, scrolling=False như bạn muốn
    components.html(html_to_render, height=total_height, scrolling=False)
    # --------------------------

    # NÚT IN PDF
    # Bỏ đoạn code cũ và thay bằng đoạn này ngay dưới dòng components.html
    
    # Nút in dùng chính chức năng của Streamlit
    if st.button("to PDF"):
        # Sử dụng Javascript để kích hoạt in từ cửa sổ chính (không phải từ iframe)
        js_code = """
        <script>
            window.parent.window.print();
        </script>
        """
        components.html(js_code, height=0)
