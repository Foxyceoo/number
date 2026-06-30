import streamlit as st
import json
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# Cấu hình tên trang
st.set_page_config(page_title='"Number" one Foxy')
st.title("Bộ chuyển đổi sheet số")

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

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
    
    # CSS và JS cho giao diện web (giữ nguyên của bạn)
    style = """
    <style>
        table { border-collapse: collapse; text-align: center; font-size: 16px; width: 100%; margin-bottom: 40px; color: inherit; }
        td { height: 60px; vertical-align: top; padding-top: 5px; font-weight: bold; width: 40px; 
             border-top: none; border-bottom: none; border-right: 1px solid #555; border-left: none; }
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
    
    # [Phần hiển thị web của bạn giữ nguyên ở đây...]
    # (Đảm bảo bạn vẫn để đoạn vòng lặp `for khuong...` và `components.html` tại đây)

    # Nút Tải về PDF (Bảng đẹp) - ĐÃ SỬA THỤT LỀ
    if st.button("Tải về PDF (Bảng đẹp)"):
        pdf_filename = f"{song_name}.pdf"
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        elements = []
        
        table_data = [["Phách", "Nốt"]]
        for phach, notes_list in time_map.items():
            table_data.append([str(phach), ", ".join(map(str, notes_list))])
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        
        with open(pdf_filename, "rb") as f:
            st.download_button("Click để tải file PDF", f, file_name=pdf_filename, mime="application/pdf")
