import streamlit as st
import json
from itertools import groupby

st.set_page_config(layout="wide") # Mở rộng màn hình để dải nhạc phổ hiển thị đẹp
st.title("🎵 Nhạc phổ trải dài")

uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Gom nốt theo nhịp (giả sử mỗi nhóm 4 nốt là 1 phân khu)
    # Tớ sẽ tạo một list các cột, mỗi cột là 1 danh sách các nốt tại thời điểm đó
    grouped_notes = [list(group) for time_val, group in groupby(notes, key=lambda x: x['time'])]
    
    # Tạo HTML cho dải nhạc phổ
    html = "<table style='width:100%; border-collapse: collapse; text-align: center; table-layout: fixed;'>"
    
    # Hàng 1: Hiển thị chỉ số nhịp (1), (2)...
    html += "<tr>"
    for i in range(len(grouped_notes)):
        label = f"({(i//4)+1})" if i % 4 == 0 else ""
        html += f"<td style='color: red; font-size: 10px; text-align: left;'>{label}</td>"
    html += "</tr>"
    
    # Hàng 2 & 3: Hiển thị nốt (Phân loại nốt cao/thấp)
    for row_idx in range(2): 
        html += "<tr>"
        for group in grouped_notes:
            # Lọc nốt: hàng 0 là nốt > 7, hàng 1 là nốt <= 7
            vals = [str(get_number_from_key(n['key'])) for n in group]
            filtered = [v for v in vals if (int(v) > 7 if row_idx == 0 else int(v) <= 7)]
            
            # Tạo vạch kẻ nhịp (vạch đen dọc) sau mỗi 4 nhóm nốt
            border_right = "1px solid #ccc"
            if (grouped_notes.index(group) + 1) % 4 == 0:
                border_right = "2px solid black"
                
            html += f"<td style='border-right: {border_right}; border-bottom: 1px solid #eee; height: 30px;'>{' '.join(filtered)}</td>"
        html += "</tr>"
    
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
