import streamlit as st
import json
import streamlit.components.v1 as components
import streamlit as st

st.set_page_config(page_title='"Number" one Foxy')

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

st.title("Bộ chuyển đổi sheet số")

# Bạn để trống label hoặc đặt tên mới, sau đó dùng help để hiển thị "- 123 -"
if uploaded_file := st.file_uploader("Sheet số (123)", type=["json"]):
    data = json.load(uploaded_file)
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    
    # Sử dụng logic mới: beat_duration không chia 4, kết hợp với hiển thị 32 phách
    beat_duration = 60000 / bpm 
    
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    
    max_beat = max(time_map.keys()) if time_map else 0
    
    st.subheader(f"Nhạc phổ (BPM: {bpm}) - Nhịp 4/4")
    
    style = """
    <style>
        table { border-collapse: collapse; text-align: center; font-size: 16px; color: white; width: 100%; background-color: #0e1117; margin-bottom: 40px; }
        td { height: 60px; vertical-align: top; padding-top: 5px; font-weight: bold; width: 40px; }
    </style>
    """
    
    all_html = style
    # Hiển thị 32 phách mỗi khuông để nốt không bị nhảy dòng
    for khuong in range(0, max_beat + 32, 32):
        html_content = "<table><tr>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            # Cấu hình vạch kẻ
            border_right = "1px solid #555"
            if (phach + 1) % 4 == 0: border_right = "2px solid #aaa" # Vạch nhịp
            if (phach + 1) % 16 == 0: border_right = "4px solid #00008c" # Vạch kết khuông màu vàng
            
            # Vạch đầu khuông màu vàng
            border_left = "2px solid #00008c" if phach == khuong else "none"
            
            cell_content = ""
            if vals:
                cell_content = f"{vals[0]}"
                if len(vals) > 1:
                    cell_content += "<br>" + "<br>".join(map(str, vals[1:]))
            
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        html_content += "</tr></table>"
        all_html += html_content
    
    components.html(f"<html><body>{all_html}</body></html>", height=800, scrolling=True)
