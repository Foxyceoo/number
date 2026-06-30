import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

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

    # CSS cải tiến để in đẹp hơn (tỉ lệ 9:16)
    style = """
    <style>
        body { font-family: sans-serif; padding: 20px; }
        table { border-collapse: collapse; text-align: center; font-size: 14px; width: 100%; margin-bottom: 20px; }
        td { height: 50px; vertical-align: middle; font-weight: bold; width: 30px; border-right: 1px solid #ccc; }
        /* Tự động ngắt trang khi in */
        @media print {
            .page-break { page-break-after: always; }
        }
    </style>
    """

    # Tạo danh sách các dòng nhạc
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

    # Gộp theo yêu cầu chia trang: Trang 1 (8 dòng), các trang sau (10 dòng)
    # Tớ thêm class 'page-break' vào sau mỗi nhóm để khi bạn bấm Ctrl+P nó tự ngắt trang
    display_html = f"<h1>{song_name}</h1>" + "".join(all_khuong_html[0:8]) + "<div class='page-break'></div>"
    
    for i in range(8, len(all_khuong_html), 10):
        display_html += "".join(all_khuong_html[i:i+10]) + "<div class='page-break'></div>"

    # HIỂN THỊ
    components.html(f"<html><head>{style}</head><body>{display_html}</body></html>", height=1000, scrolling=True)

    # NÚT IN PDF
    if st.button("🖨️ Mở bảng in (Để lưu PDF)"):
        st.write("### Hướng dẫn:")
        st.write("1. Một cửa sổ mới sẽ hiện ra (hoặc trang hiện tại sẽ tự mở bảng in).")
        st.write("2. Nếu trình duyệt hỏi, chọn **'Lưu dưới dạng PDF' (Save as PDF)**.")
        st.write("3. Nhấn **In/Lưu** là xong!")
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
