import streamlit as st
import json
import streamlit.components.v1 as components
# Thư viện để vẽ bảng chuyên nghiệp trong PDF
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Cấu hình tiêu đề trang
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
    # Tớ đã để border-top/bottom mờ và border-right đậm theo ý bạn
    style = """
    <style>
        table { border-collapse: collapse; text-align: center; font-size: 16px; width: 100%; color: inherit; }
        td { height: 60px; vertical-align: top; font-weight: bold; width: 40px; 
             border-top: 1px solid rgba(128, 128, 128, 0.3); 
             border-bottom: 1px solid rgba(128, 128, 128, 0.3);
             border-right: 1px solid #555; border-left: none; }
    </style>
    """
    
    all_html = style + "<table><tr>"
    for phach in range(max_beat + 1):
        vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
        html_cell = "<br>".join(map(str, vals)) if vals else ""
        all_html += f"<td>{html_cell}</td>"
    all_html += "</tr></table>"
    components.html(f"<html><body>{all_html}</body></html>", height=500, scrolling=True)

    # 3. KHU VỰC XUẤT FILE PDF (BẢNG ĐẸP)
    # Tự động tạo file và hiển thị nút tải về ngay khi có dữ liệu
    pdf_filename = f"{song_name}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    
    # Chuẩn bị dữ liệu dạng bảng cho ReportLab
    table_data = [["Phách", "Nốt"]]
    for phach, notes_list in time_map.items():
        table_data.append([str(phach), ", ".join(map(str, notes_list))])
    
    # Thiết lập giao diện bảng PDF
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey), # Kẻ lưới mờ hơn cho sang
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), # In đậm tiêu đề
    ]))
    
    doc.build([t])
    
    # Nút tải file
    with open(pdf_filename, "rb") as f:
        st.download_button(
            label="📥 Tải file PDF (Bảng đẹp)", 
            data=f, 
            file_name=pdf_filename, 
            mime="application/pdf"
        )
