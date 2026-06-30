import streamlit as st
import json
import streamlit.components.v1 as components
# Thư viện để vẽ bảng chuyên nghiệp trong PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

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
    # Tự động tạo file và hiển thị nút tải về ngay khi có dữ liệu
    if st.button("Tải về PDF (Bản chuẩn lưới)"):
        pdf_filename = f"{song_name}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    
        # Tạo dữ liệu: Chia theo từng khuông 32 phách giống web
        # Ta sẽ tạo một list các dòng, mỗi dòng là một phách
        table_data = [["Phách", "Nốt"]]
        for phach, notes_list in time_map.items():
            table_data.append([str(phach), ", ".join(map(str, notes_list))])
    
        # Thiết lập bảng với đường kẻ dọc (giống lưới web)
        t = Table(table_data, colWidths=[50, 300]) # Cột phách 50, cột nốt 300
    
        style_list = [
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey), # Kẻ lưới toàn bộ
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey), # Kẻ dọc mờ
            ('BOX', (0,0), (-1,-1), 2, colors.black), # Khung ngoài đậm
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]
    
        # Thêm logic kẻ dọc đậm mỗi 4 phách hoặc 16 phách nếu muốn (giống web)
        # Ví dụ: Kẻ đậm cột mỗi 4 phách
        for i in range(len(table_data)):
            if i % 4 == 0: 
                style_list.append(('LINEBELOW', (0,i), (-1,i), 1, colors.black))
            
        t.setStyle(TableStyle(style_list))

        doc.build([t])
    
        with open(pdf_filename, "rb") as f:
            st.download_button("Tải PDF", f, file_name=pdf_filename, mime="application/pdf")
