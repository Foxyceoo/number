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
            # Dùng enumerate(chunk) để lấy index chính xác cho vạch kẻ nhịp
            for col_idx, group in enumerate(chunk):
                vals = [str(get_number_from_key(n['key'])) for n in group]
                filtered = [v for v in vals if (int(v) > 7 if row_idx == 0 else int(v) <= 7)]
                
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
                html += f"<td style='{cell_style}'>{ ' '.join(filtered) }</td>"
            html += "</tr>"
        
        html += "</table>"
        st.markdown(html, unsafe_allow_html=True)
