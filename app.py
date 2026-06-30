import streamlit as st
import json
import streamlit.components.v1 as components

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    
    beat_duration = 60000 / bpm / 4
    
    time_map = {}
    for n in notes:
        import math
        beat_idx = math.floor(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    
    max_beat = max(time_map.keys()) if time_map else 0
    
    st.subheader(f"Nhạc phổ (BPM: {bpm}) - Nhịp 4/4")
    
    # CSS chung cho các khuông
    style = """
    <style>
        table { border-collapse: collapse; text-align: center; font-size: 16px; color: white; width: 100%; background-color: #0e1117; margin-bottom: 40px; }
        td { height: 60px; vertical-align: top; padding-top: 5px; font-weight: bold; width: 40px; }
    </style>
    """
    
    # Tạo danh sách các bảng HTML
    all_html = style
    for khuong in range(0, max_beat + 16, 16):
        html_content = "<table><tr>"
        for phach in range(khuong, khuong + 16):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            # Cấu hình vạch kẻ phải
            border_right = "1px solid #555"
            if (phach + 1) % 4 == 0: border_right = "2px solid #aaa" # Vạch nhịp
            if (phach + 1) % 16 == 0: border_right = "4px solid white" # Vạch khuông
            
            # Cấu hình vạch kẻ trái (thêm viền cho cột đầu tiên mỗi khuông)
            border_left = "2px solid #aaa" if phach == khuong else "none"
            
            # Xử lý nội dung hiển thị
            cell_content = ""
            if vals:
                cell_content = f"{vals[0]}"
                if len(vals) > 1:
                    cell_content += "<br>" + "<br>".join(map(str, vals[1:]))
            
            # Gộp border-left và border-right vào style của td
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        html_content += "</tr></table>"
        all_html += html_content
    
    # Hiển thị
    components.html(f"<html><body>{all_html}</body></html>", height=800, scrolling=True)
