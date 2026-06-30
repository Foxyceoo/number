import streamlit as st
import json

# 1. Đưa hàm lên trước để tránh lỗi NameError
def draw_table(times, time_map):
    html = "<table style='width:100%; border-collapse: collapse; text-align: center; margin-bottom: 20px; font-size: 12px;'>"
    for row_idx in range(2):
        html += "<tr>"
        for t in times:
            vals = sorted(time_map.get(t, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            if row_idx == 0:
                content = str(vals[0]) if len(vals) > 0 else ""
            else:
                content = "<br>".join(map(str, vals[1:])) if len(vals) > 1 else ""
            html += f"<td style='border: 1px solid #555; height: 40px; vertical-align: top; padding: 2px;'>{content}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_html=True)

# 2. Đoạn code chính
def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    
    beat_duration = 60000 / bpm 
    measure_duration = beat_duration * 4 
    row_duration = measure_duration * 2
    
    time_map = {}
    for n in notes:
        t = n['time']
        if t not in time_map: time_map[t] = []
        time_map[t].append(get_number_from_key(n['key']))
    
    sorted_times = sorted(time_map.keys())
    
    st.subheader(f"Nhạc phổ (BPM: {bpm})")
    
    # Chia theo 2 khuông (measure) mỗi hàng
    current_row_end = row_duration
    row_times = []
    
    for t in sorted_times:
        if t >= current_row_end:
            if row_times: draw_table(row_times, time_map)
            row_times = []
            current_row_end += row_duration
        row_times.append(t)
    
    if row_times: draw_table(row_times, time_map)
