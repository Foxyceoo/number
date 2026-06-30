import streamlit as st
import json
import streamlit.components.v1 as components
from fpdf import FPDF

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
    
    # CSS với quy định kích thước A4 cho PDF
    style = """
    <style>
        /* Dùng biến của Streamlit để màu tự đảo ngược theo nền */
        table { 
            border-collapse: collapse; 
            text-align: center; 
            font-size: 16px; 
            width: 100%; 
            margin-bottom: 40px; 
            /* Biến màu chữ tự động của Streamlit */
            color: var(--text-color); 
        }
        td { 
            height: 60px; 
            vertical-align: top; 
            padding-top: 5px; 
            font-weight: bold; 
            width: 40px; 
            border: 1px solid var(--text-color); 
        }
    </style>
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

    # Nút Tải về PDF dùng FPDF
    if st.button("Tải về PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=song_name, ln=True, align='C')
        
        pdf.set_font("Courier", '', 12)
        pdf.ln(10) # Khoảng cách dòng
        
        # In dữ liệu ra PDF (đơn giản hóa)
        for phach, notes in time_map.items():
            line = f"Phach {phach}: {', '.join(map(str, notes))}"
            pdf.cell(200, 10, txt=line, ln=True)
            
        # Xuất PDF dưới dạng byte
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        st.download_button(
            label="Tải file PDF (FPDF)",
            data=pdf_output,
            file_name=f"{song_name}.pdf",
            mime="application/pdf"
        )
