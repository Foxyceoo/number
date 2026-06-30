import streamlit as st
import json
import pandas as pd
from itertools import groupby

st.title("🎵 Nhạc phổ chuẩn 16 Cột")
uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

# Hàm hiển thị bảng với CSS tùy chỉnh
def display_custom_table(data_chunk):
    # Tạo bảng với màu nền #ffe4e1 (hồng nhạt)
    html = "<table style='width:100%; border-collapse: collapse; background-color: #ffe4e1; text-align: center;'>"
    for row in data_chunk:
        html += "<tr>"
        for i, val in enumerate(row):
            # Đường kẻ dọc đậm hơn ở mỗi cột thứ 4 (4, 8, 12)
            border_style = "1px solid #999"
            if (i + 1) % 4 == 0 and i != 15:
                border_style = "2px solid #555" # Đường kẻ đậm
            
            html += f"<td style='border: {border_style}; padding: 8px; width: 6.25%;'>{val}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    grouped = groupby(notes, key=lambda x: x['time'])
    
    table_data = []
    for time_val, group in grouped:
        row = [""] * 16
        for i, n in enumerate(group):
            if i < 16:
                row[i] = get_number_from_key(n['key'])
        table_data.append(row)
    
    chunk_size = 20
    chunks = [table_data[i:i + chunk_size] for i in range(0, len(table_data), chunk_size)]
    
    for i in range(0, len(chunks), 2):
        row = st.columns(2)
        for col_idx in range(2):
            if i + col_idx < len(chunks):
                with row[col_idx]:
                    display_custom_table(chunks[i + col_idx])
