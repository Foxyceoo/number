import streamlit as st
import json

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    
    # Tính thời gian 1 nhịp (ms)
    beat_duration = 60000 / bpm 
    # Giả sử 1 khuông (measure) = 4 phách (4/4), hoặc tùy chỉnh theo ý bạn
    measure_duration = beat_duration * 4 
    
    # Gom nốt theo thời gian
    time_map = {}
    for n in notes:
        t = n['time']
        if t not in time_map: time_map[t] = []
        time_map[t].append(get_number_from_key(n['key']))
    
    sorted_times = sorted(time_map.keys())
    
    # Chia theo 2 khuông (measure) mỗi hàng
    row_duration = measure_duration * 2
    
    st.subheader(f"Nhạc phổ (BPM: {bpm})")
    
    # Gom các mốc thời gian vào từng hàng (2 khuông)
    current_row_end = row_duration
    row_times = []
    
    for t in sorted_times:
        if t >= current_row_end:
            # Vẽ hàng hiện tại
            draw_table(row_times, time_map)
            row_times = []
            current_row_end += row_duration
        row_times.append(t)
    
    if row_times: draw_table(row_times, time_map)

def draw_table(times, time_map):
    html = "<table style='width:100%; border-collapse: collapse; text-align: center; margin-bottom: 20px; font-size: 12px;'>"
    for row_idx in range(2):
        html += "<tr>"
        for t in times:
            vals = sorted(time_map[t], reverse=True, key=lambda x: int(x) if x != "" else 0)
            # Dùng <br> để xếp dọc các nốt
            if row_idx == 0:
                content = str(vals[0]) if len(vals) > 0 else ""
            else:
                content = "<br>".join(map(str, vals[1:])) if len(vals) > 1 else ""
                
            html += f"<td style='border: 1px solid #555; height: 40px; vertical-align: top; padding: 2px;'>{content}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
