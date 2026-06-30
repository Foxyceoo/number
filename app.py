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
    
    CHUNK_SIZE = 35
    for i in range(0, len(grouped_notes), CHUNK_SIZE):
        chunk = grouped_notes[i : i + CHUNK_SIZE]
        
        html = "<table style='width:100%; border-collapse: collapse; text-align: center; table-layout: fixed; margin-bottom: 30px;'>"
        
        for row_idx in range(2): 
            html += "<tr>"
            for col_idx, group in enumerate(chunk):
                # Lấy tất cả số trong nhóm và sắp xếp từ lớn đến bé
                vals = sorted([get_number_from_key(n['key']) for n in group], reverse=True, key=lambda x: int(x) if x != "" else 0)
                
                # Hàng 0: chỉ lấy số to nhất. Hàng 1: lấy các số còn lại.
                if row_idx == 0:
                    content = str(vals[0]) if len(vals) > 0 else ""
                else:
                    content = " ".join([str(v) for v in vals[1:]]) if len(vals) > 1 else ""
                
                # Vẽ vạch kẻ nhịp (mỗi 4 cột là 1 nhịp)
                border_right = "1px solid #eee"
                if (col_idx + 1) % 4 == 0:
                    border_right = "2px solid black"
                
                cell_style = (
                    f"border-right: {border_right}; "
                    f"border-bottom: 1px solid #ddd; "
                    f"height: 25px; width: 2.8%; "
                    f"font-size: 10px; padding: 1px; line-height: 1;"
                )
                html += f"<td style='{cell_style}'>{content}</td>"
            html += "</tr>"
        
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
