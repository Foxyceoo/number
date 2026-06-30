import streamlit as st
import json

# Hàm chuyển đổi key sang số hiển thị (1-15)
def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    notes = data[0].get("songNotes", [])
    
    # Gom nốt theo thời gian
    time_map = {}
    for n in notes:
        t = n['time']
        if t not in time_map: time_map[t] = []
        time_map[t].append(get_number_from_key(n['key']))
    
    sorted_times = sorted(time_map.keys())
    
    # THIẾT LẬP NGẮT DÒNG: thay đổi số này để chỉnh độ dài mỗi dòng
    COLUMNS_PER_ROW = 16 
    
    st.subheader("Nhạc phổ (Đã ngắt dòng)")
    
    # Chia danh sách thời gian thành các đoạn nhỏ
    for i in range(0, len(sorted_times), COLUMNS_PER_ROW):
        row_times = sorted_times[i : i + COLUMNS_PER_ROW]
        
        html = "<table style='width:100%; border-collapse: collapse; text-align: center; margin-bottom: 20px;'>"
        for row_idx in range(2):
            html += "<tr>"
            for t in row_times:
                vals = sorted(time_map[t], reverse=True, key=lambda x: int(x) if x != "" else 0)
                content = str(vals[0]) if (row_idx == 0 and len(vals)>0) else (" ".join(map(str, vals[1:])) if (row_idx == 1 and len(vals)>1) else "")
                
                # Vẽ viền: 2 cột 1 nhịp, mỗi 16 cột 1 dòng
                border_style = "1px solid #555" 
                html += f"<td style='border: {border_style}; height: 30px; width: 6%;'>{content}</td>"
            html += "</tr>"
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
