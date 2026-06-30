import streamlit as st
import json
from itertools import groupby

st.title("🎵 Nhạc phổ trải dài (Ngắt dòng 35 cột)")
uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    grouped_notes = [list(group) for time_val, group in groupby(notes, key=lambda x: x['time'])]
    
    # Chia danh sách nốt thành các nhóm, mỗi nhóm 35 cột
    CHUNK_SIZE = 35
    for i in range(0, len(grouped_notes), CHUNK_SIZE):
        chunk = grouped_notes[i : i + CHUNK_SIZE]
        
        # Vẽ bảng cho đoạn 35 cột này
        html = "<table style='width:100%; border-collapse: collapse; text-align: center; table-layout: fixed; margin-bottom: 30px;'>"
        
        # Hàng hiển thị nốt (chia làm 2 dòng: trên > 7, dưới <= 7)
        for row_idx in range(2): 
            html += "<tr>"
            for group in chunk:
                vals = [str(get_number_from_key(n['key'])) for n in group]
                filtered = [v for v in vals if (int(v) > 7 if row_idx == 0 else int(v) <= 7)]
                
                # Vẽ vạch kẻ nhịp (giả sử mỗi 4 cột là 1 nhịp)
                border_right = "1px solid #eee"
                if (chunk.index(group) + 1) % 4 == 0:
                    border_right = "2px solid black"
                    
                html += f"<td style='border-right: {border_right}; border-bottom: 1px solid #ddd; height: 35px; width: 2.8%;'>{ ' '.join(filtered) }</td>"
            html += "</tr>"
        
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
