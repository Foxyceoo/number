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
                # Thay đoạn xử lý nốt trong vòng lặp bằng đoạn này:
            
            vals = sorted([get_number_from_key(n['key']) for n in group], reverse=True)
            
            # Gán nốt đầu tiên (số to nhất) vào hàng 0, các nốt còn lại vào hàng 1
            row1_val = str(vals[0]) if len(vals) > 0 else ""
            row2_val = " ".join([str(v) for v in vals[1:]]) if len(vals) > 1 else ""
            
            # Nếu là row_idx 0 thì hiển thị row1_val, row_idx 1 hiển thị row2_val
            content = row1_val if row_idx == 0 else row2_val
            
            # Vẽ vạch kẻ nhịp (giữ nguyên logic của bạn)
            border_right = "1px solid #eee"
            if (col_idx + 1) % 4 == 0:
                border_right = "2px solid black"
                
            cell_style = "border-right: {border_right}; border-bottom: 1px solid #ddd; height: 25px; width: 2.8%; font-size: 10px; padding: 1px; line-height: 1;"
            html += f"<td style='{cell_style}'>{content}</td>"
