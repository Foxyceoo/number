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
    
    # Sử dụng * 4 như bạn đã xác nhận là chạy đúng với nhạc phổ của bạn
    beat_duration = 60000 / bpm /2
    
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    
    # Phải tính max_beat TRƯỚC khi dùng nó trong vòng lặp
    max_beat = max(time_map.keys()) if time_map else 0
    
    st.subheader(f"Nhạc phổ (BPM: {bpm}) - Nhịp 4/4")
    
    style = """
    <style>
        table { border-collapse: collapse; text-align: center; font-size: 16px; color: white; width: 100%; background-color: #0e1117; margin-bottom: 40px; }
        td { height: 60px; vertical-align: top; padding-top: 5px; font-weight: bold; width: 40px; }
    </style>
    """
    
    all_html = style
    # Vòng lặp khuông chuẩn (mỗi khuông 16 phách)
    for khuong in range(0, max_beat + 16, 16):
        html_content = "<table><tr>"
        for phach in range(khuong, khuong + 16):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            border_right = "1px solid #555"
            if (phach + 1) % 4 == 0: border_right = "2px solid #aaa"
            if (phach + 1) % 16 == 0: border_right = "4px solid white"
            
            border_left = "2px solid #aaa" if phach == khuong else "none"
            
            cell_content = ""
            if vals:
                cell_content = f"{vals[0]}"
                if len(vals) > 1:
                    cell_content += "<br>" + "<br>".join(map(str, vals[1:]))
            
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        html_content += "</tr></table>"
        all_html += html_content
    
    components.html(f"<html><body>{all_html}</body></html>", height=800, scrolling=True)
