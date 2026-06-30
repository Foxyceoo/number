import streamlit as st
import pandas as pd
import json
import io
import streamlit.components.v1 as components
from weasyprint import HTML

st.set_page_config(page_title='Sheet Music Converter', layout="wide")
st.title("Bộ chuyển đổi sheet số")

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

    # CSS chung
    style = """
    <style>
        body { font-family: sans-serif; }
        table { border-collapse: collapse; text-align: center; font-size: 14px; width: 100%; margin-bottom: 20px; }
        td { height: 50px; vertical-align: middle; font-weight: bold; width: 30px; border-right: 1px solid #ccc; }
    </style>
    """

    # Tạo danh sách các dòng nhạc (khuông)
    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        html_content = f"<table><tr><td style='color: red; border: none;'>{line_number}</td>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True)
            cell_content = "<br>".join(map(str, vals)) if vals else ""
            html_content += f"<td>{cell_content}</td>"
        html_content += "</tr></table>"
        all_khuong_html.append(html_content)
        line_number += 2

    # HIỂN THỊ TRÊN WEB
    st.subheader(song_name)
    components.html(f"<html><body>{style}{''.join(all_khuong_html)}</body></html>", height=600, scrolling=True)

    # XUẤT PDF (Chia trang 8 - 10)
    if st.button("📥 Xuất file PDF (Chia trang 8-10)"):
        pages = []
        # Trang đầu: 8 dòng
        pages.append(f"<html><head>{style}</head><body><h1>{song_name}</h1>{''.join(all_khuong_html[0:8])}</body></html>")
        # Các trang sau: 10 dòng
        for i in range(8, len(all_khuong_html), 10):
            pages.append(f"<html><head>{style}</head><body>{''.join(all_khuong_html[i:i+10])}</body></html>")
        
        pdf_buffer = io.BytesIO()
        HTML(string="".join(pages)).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        
        st.download_button("Tải PDF ngay", data=pdf_buffer, file_name=f"{song_name}.pdf", mime="application/pdf")
