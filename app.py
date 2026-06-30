import streamlit as st
import json

def draw_table(times, time_map):
    if not times: return
    
    html = "<table style='width:100%; border-collapse: collapse; text-align: center; margin-bottom: 20px; font-size: 12px; table-layout: fixed;'>"
    for row_idx in range(2):
        html += "<tr>"
        for t in times:
            vals = sorted(time_map.get(t, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            # Xử lý nội dung an toàn hơn
            if row_idx == 0:
                content = str(vals[0]) if len(vals) > 0 else ""
            else:
                content = "<br>".join(map(str, vals[1:])) if len(vals) > 1 else ""
                
            html += f"<td style='border: 1px solid #555; height: 35px; vertical-align: top; padding: 2px; word-wrap: break-word;'>{content}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    # Lấy dữ liệu an toàn
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    
    # Tính toán nhịp
    beat_duration = 60000 / bpm 
    row_duration = beat_duration * 8 # 2 khuông = 8 phách
    
    time_map = {}
    for n in notes:
        t = n['time']
        time_map.setdefault(t, []).append(get_number_from_key(n['key']))
    
    sorted_times = sorted(time_map.keys())
    
    st.subheader(f"Nhạc phổ (BPM: {bpm})")
    
    # Chia nhóm thời gian
    if sorted_times:
        row_times = []
        current_limit = sorted_times[0] + row_duration
        
        for t in sorted_times:
            if t >= current_limit:
                draw_table(row_times, time_map)
                row_times = []
                current_limit += row_duration
            row_times.append(t)
        
        if row_times: draw_table(row_times, time_map)
