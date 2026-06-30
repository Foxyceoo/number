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
    
    # Thiết lập ngắt dòng
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
                
                # Logic phân chia nốt: hàng trên là nốt chính, hàng dưới là nốt phụ (xếp dọc)
                if row_idx == 0:
                    content = str(vals[0]) if len(vals) > 0 else ""
                else:
                    content = "<br>".join(map(str, vals[1:])) if len(vals) > 1 else ""
                
                # Vẽ viền: thêm vertical-align: top để số luôn sát mép trên
                border_style = "1px solid #555" 
                html += f"<td style='border: {border_style}; height: 40px; width: 6%; vertical-align: top; padding: 2px;'>{content}</td>"
            
            html += "</tr>"
        
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
