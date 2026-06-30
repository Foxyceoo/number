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
    st.markdown("---")  # Kẻ vạch ngăn cách cho đẹp
    uploaded_file = st.file_uploader("**Sheet 123**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")

    # --- THÊM PHẦN GHÉP PDF VÀO ĐÂY ---
    st.subheader("Ghép PDF")
    pdf_files = st.file_uploader("Chọn các file PDF cần ghép", type=["pdf"], accept_multiple_files=True)

    if pdf_files:
        if st.button("Ghép PDF"):
            from pypdf import PdfWriter
            import io

            merger = PdfWriter()
            for file in pdf_files:
                merger.append(file)

            pdf_stream = io.BytesIO()
            merger.write(pdf_stream)
            pdf_stream.seek(0)

            st.download_button(
                label="Tải xuống file đã ghép",
                data=pdf_stream,
                file_name="Sheet_Music_Combined.pdf",
                mime="application/pdf"
            )
            st.success("Ghép thành công!")
    # -----------------------------------

    st.caption("Hãy chọn file JSON hoặc PDF để bắt đầu!")

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
    style = """
    <style>
    /* BẮT BUỘC: Cho phép body cuộn */
    html, body {
        width: 100%;
        height: 100%;
        margin: 0;
        padding: 0;
        overflow-y: auto !important; /* Luôn hiện thanh cuộn dọc */
        overflow-x: auto !important;
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
        height: 50px !important;    /* Ép cứng chiều cao, không phụ thuộc nội dung */
        min-height: 50px !important;
        max-height: 50px !important;

        vertical-align: top !important;   /* Luôn giữ nội dung ở đỉnh ô */
        padding: 0;                   /* Bỏ padding để không làm đẩy ô */

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
        /* Ẩn hoàn toàn thanh cuộn và các phần thừa của iframe */
        body, html {
            overflow: hidden !important; 
        }

        /* Ẩn các nút bấm, header, sidebar và cả iframe container nếu cần */
        .print-btn, .sidebar, header, .stAppDeployButton, footer { 
            display: none !important; 
        }

        /* Đảm bảo bảng không bị cắt ngang dòng khi sang trang */
        table {
            page-break-inside: avoid;
        }
        /* Đưa dòng này vào trong khối style này */
        #root footer, .stAppDeployButton, .viewerBadge_container__1QSob, 
        .styles_viewerBadge__1yB5_ { 
            display: none !important; 
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

            # Trong vòng lặp tạo cell_content:
            if vals:
                top_num = vals[0]  # Số lớn nhất (đã được sắp xếp bởi reverse=True)
                # Các số còn lại nối lại với nhau bằng <br> để chúng nằm cùng một hàng dưới
                bottom_nums = "<br>".join(map(str, vals[1:])) if len(vals) > 1 else ""
                # Ép vào cấu trúc 2 tầng cố định
                cell_content = f"""
                <div class='grid-cell'>
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

    # Định nghĩa số khuông mỗi trang (ví dụ: mỗi trang 8 khuông)
    khuong_moi_trang = 8

    for i in range(0, len(all_khuong_html), khuong_moi_trang):
        # Lấy một cụm khuông nhạc
        cum_khuong = all_khuong_html[i : i + khuong_moi_trang]
        # Nối các bảng lại và thêm thẻ ngắt trang
        display_html += "".join(cum_khuong) + "<div class='page-break'></div>"

    # HIỂN THỊ VỚI THANH CUỘN
    html_to_render = f"""
    <html>
        <head>
            {style}
            <style>
                /* Ẩn các thành phần giao diện của Streamlit khi nằm trong iframe */
                #root footer, .stAppDeployButton, .viewerBadge_container__1QSob, 
                .styles_viewerBadge__1yB5_, div[data-testid="stDecoration"] { 
                    display: none !important; 
                }
            </style>
        </head>
        <body>{display_html}</body>
    </html>
    """

    components.html(html_to_render, height=1123, scrolling=True)

    # NÚT IN PDF
    st.markdown("""
    <style>
        @media print {
            .print-btn { display: none !important; }
        }
        .print-btn {
            display: inline-block;
            padding: 0.5em 1em;
            background-color: #ffcbcc; /* Màu nền mới */
            color: #00008c;            /* Màu chữ mới */
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
