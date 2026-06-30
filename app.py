import streamlit as st
import json

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
        beat_idx = round(n['time'] / beat_duration)
        if beat_idx not in time_map: time_map[beat_idx] = []
        time_map[beat_idx].append(get_number_from_key(n['key']))
    
    max_beat = max(time_map.keys()) if time_map else 0
    
    st.subheader(f"Nhạc phổ (BPM: {bpm}) - Nhịp 4/4")
    
    html = "<table style='border-collapse: collapse; text-align: center; font-size: 10px;'>"
    
    for khuong in range(0, max_beat + 16, 16):
        html += "<tr>"
        for phach in range(khuong, khuong + 16):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            border_right = "1px solid #ccc"
            if (phach + 1) % 4 == 0: border_right = "2px solid #555"
            if (phach + 1) % 16 == 0: border_right = "4px solid black"
            
            # SỬA LỖI Ở ĐÂY: Kiểm tra kỹ vals trước khi truy cập chỉ số
            if vals:
                nots_str = f"{vals[0]}"
                if len(vals) > 1:
                    nots_str += "<br>" + "<br>".join(map(str, vals[1:]))
                content = nots_str
            else:
                content = ""
            
            html += f"<td style='border-right: {border_right}; border-bottom: 1px solid #ccc; width: 30px; height: 50px; vertical-align: top;'>{content}</td>"
        html += "</tr>"
        
    html += "</table>"
    st.markdown(html, unsafe_html=True)
