import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components
from pypdf import PdfWriter
import io

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
padding_top_px = 40
padding_bottom_px = 90

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---")
    uploaded_file = st.file_uploader("**Sheet 123**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")

    st.subheader("Ghép PDF")
    pdf_files = st.file_uploader("Chọn các file PDF cần ghép", type=["pdf"], accept_multiple_files=True)
    
    if pdf_files:
        if st.button("Ghép PDF"):
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

# Gom CSS vào 1 khối duy nhất để không bị lỗi NameError
style = """
<style>
    html, body { width: 100%; height: 100%; margin: 0; padding: 0; overflow-y: auto !important; }
    table { border-collapse: collapse; text-align: center; font-size: 16px; width: 100%; margin-bottom: 50px; }
    td { height: 50px !important; vertical-align: top !important; padding: 0; font-weight: bold; width: 40px; border-right: 1px solid #555; }
    
    /* Ẩn các thành phần giao diện Streamlit */
    #root footer, .stAppDeployButton, .viewerBadge_container__1QSob, 
    .styles_viewerBadge__1yB5_, div[data-testid="stDecoration"] { 
        display: none !important; 
    }

    @media print {
        body, html { overflow: hidden !important; }
        .print-btn, .sidebar, header, .stAppDeployButton, footer { display: none !important; }
        table { page-break-inside: avoid; }
    }
</style>
"""

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

    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle;'>{line_number}</td>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True)
            border_right = "1px solid #555"
            if (phach + 1) % 4 == 0: border_right = "2px solid #ff0000"
            if (phach + 1) % 16 == 0: border_right = "3px solid #00008c"
            border_left = "3px solid #00008c" if phach == khuong else "none"
            
            cell_content = f"<div class='grid-cell'><div class='top-row'>{vals[0]}</div><div class='bottom-row'>{'<br>'.join(map(str, vals[1:]))}</div></div>" if vals else ""
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        all_khuong_html.append(html_content)
        line_number += 2

    display_html = f"<h1 style='text-align: center; margin-top: {padding_top_px}px; margin-bottom: {padding_bottom_px}px;'>{song_name}</h1>"
    for i in range(0, len(all_khuong_html), 8):
        display_html += "".join(all_khuong_html[i : i + 8]) + "<div class='page-break'></div>"

    html_to_render = f"<html><head>{style}</head><body>{display_html}</body></html>"
    components.html(html_to_render, height=1123, scrolling=True)

    st.markdown("""
    <a href="#" class="print-btn" onclick="window.print(); return false;" 
    style="display: inline-block; padding: 0.5em 1em; background-color: #ffcbcc; color: #00008c; text-decoration: none; border-radius: 5px; font-weight: bold;">
    Mở bảng in</a>
    """, unsafe_allow_html=True)
