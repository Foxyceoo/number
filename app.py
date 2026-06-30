import streamlit as st
import json

st.title("🎵 Nhạc phổ chuẩn thời gian")
uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

# Hàm chuyển đổi key sang số hiển thị (1-15)
def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file is not None:
    data = json.load(uploaded_file)
    bpm = data[0].get("bpm", 320)
    st.subheader(f"Nhịp độ (BPM): {bpm}")
    
    notes = data[0].get("songNotes", [])
    
    # Gom nốt theo 'time' để xác định các cột
    time_map = {}
    for n in notes:
        t = n['time']
        if t not in time_map: time_map[t] = []
        time_map[t].append(get_number_from_key(n['key']))
    
    # Sắp xếp các mốc thời gian
    sorted_times = sorted(time_map.keys())
    
    # Định nghĩa độ dài 1 nhịp (ví dụ: khoảng thời gian 500ms là 1 nhịp)
    # Bạn có thể điều chỉnh con số này cho khớp với độ dài nhịp thực tế trong file
    BEAT_DURATION = 500 
    
    html = "<table style='width:100%; border-collapse: collapse; text-align: center;'>"
    for row_idx in range(2):
        html += "<tr>"
        for t in sorted_times:
            vals = sorted(time_map[t], reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            # Chia cột dựa trên thời gian
            content = str(vals[0]) if (row_idx == 0 and len(vals)>0) else (" ".join(map(str, vals[1:])) if (row_idx == 1 and len(vals)>1) else "")
            
            # Logic vạch nhịp: Nếu thời gian vượt qua bội số của BEAT_DURATION thì kẻ vạch đậm
            border_style = "1px solid #eee"
            if (t % BEAT_DURATION) < 50: # Sai số nhỏ để nhận diện mốc nhịp
                border_style = "3px solid black"
                
            html += f"<td style='border-right: {border_style}; border-bottom: 1px solid #ddd; height: 25px;'>{content}</td>"
        html += "</tr>"
    html += "</table>"
    
    st.markdown(html, unsafe_allow_html=True)
