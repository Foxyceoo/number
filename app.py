import streamlit as st
import json
import streamlit.components.v1 as components
# Thư viện để vẽ bảng chuyên nghiệp trong PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.platypus import PageBreak

# Cấu hình tên trang
st.set_page_config(page_title='"Number" one Foxy')
st.title("Bộ chuyển đổi sheet số")

# Hàm lấy số từ key (giữ nguyên logic của bạn)
def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

# 1. KHU VỰC TẢI FILE VÀ XỬ LÝ DỮ LIỆU
if uploaded_file := st.file_uploader("Sheet số (123)", type=["json"]):
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
    
    st.markdown(f"<h2 style='text-align: center;'>{song_name}</h2>", unsafe_allow_html=True)
    
    # 2. KHU VỰC HIỂN THỊ BẢNG TRÊN WEB (CSS & HTML)
    style = """
    <style>
        table { 
            border-collapse: collapse; 
            text-align: center; 
            font-size: 16px; 
            width: 100%; 
            margin-bottom: 40px; 
            color: inherit; 
        }
        td { 
            height: 60px; 
            vertical-align: top; 
            padding-top: 5px; 
            font-weight: bold; 
            width: 40px; 
            /* Kẻ ngang: Dùng màu xám nhạt (cùng tông theme) */
            border-top: 0px solid rgba(128, 128, 128, 0.3);
            border-bottom: 0px solid rgba(128, 128, 128, 0.3);
            /* Kẻ dọc: Giữ nguyên màu đậm để phân chia phách */
            border-right: 1px solid #555; 
            border-left: none;
        }
    </style>
    <script>
        function adjustTheme() {
            const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.style.color = isDarkMode ? '#FFFFFF' : '#000000';
            document.body.style.backgroundColor = 'transparent';
        }
        window.onload = adjustTheme;
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', adjustTheme);
    </script>
    """
    
    all_html = style
    for khuong in range(0, max_beat + 32, 32):
        # Thêm class 'khuong-nhac' để PDF biết chỗ ngắt trang
        html_content = "<div class='khuong-nhac'><table><tr>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            border_right = "1px solid #555"
            if (phach + 1) % 4 == 0: border_right = "2px solid #aaa"
            if (phach + 1) % 16 == 0: border_right = "4px solid #00008c"
            
            border_left = "4px solid #00008c" if phach == khuong else "none"
            
            cell_content = "<br>".join(map(str, vals)) if vals else ""
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        html_content += "</tr></table></div>"
        all_html += html_content
    
    components.html(f"<html><body>{all_html}</body></html>", height=800, scrolling=True)

    # 3. KHU VỰC XUẤT FILE PDF
    # Trong hàm xử lý nút tải PDF, thay thế phần tạo Table bằng đoạn này:
    if st.button("Tải về PDF (Bố cục Lưới)"):
        pdf_filename = f"{song_name}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
    
        # Thiết lập kích thước ô
        cell_w, cell_h = 20, 40
        start_x, start_y = 50, 700
    
        # Tạo một trang vẽ mới
        d = Drawing(500, 800)
    
        # Vẽ lưới và điền số (mô phỏng theo image_709bc4.png)
        for phach in range(max_beat + 1):
            x = start_x + (phach % 16) * cell_w
            y = start_y - (phach // 16) * cell_h
           
            # Vẽ ô
            d.add(Rect(x, y, cell_w, cell_h, strokeColor=colors.grey, fillColor=None))
        
            # Điền nốt
            vals = time_map.get(phach, [])
            if vals:
                # Sắp xếp để nốt cao nằm trên, nốt thấp nằm dưới
                vals_sorted = sorted(vals, reverse=True)
                for idx, val in enumerate(vals_sorted):
                    d.add(String(x + 5, y + 25 - (idx * 15), str(val), fontSize=10))
    
        elements.append(d)
        doc.build(elements)
    
        with open(pdf_filename, "rb") as f:
            st.download_button("Tải PDF (Chuẩn Lưới)", f, file_name=pdf_filename, mime="application/pdf")
