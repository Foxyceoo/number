import streamlit as st
import json
import pandas as pd

st.title("🎵 Nhạc phổ chuẩn 16 Cột")
uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Gom nhóm theo thời điểm
    from itertools import groupby
    grouped = groupby(notes, key=lambda x: x['time'])
    
    # Tạo danh sách các dòng cho bảng
    table_data = []
    for time_val, group in grouped:
        row = [""] * 16  # Bảng 16 cột
        # Điền nốt vào cột dựa trên thứ tự xuất hiện
        for i, n in enumerate(group):
            if i < 16:
                row[i] = get_number_from_key(n['key'])
        table_data.append(row)
    
    # Hiển thị 2 bảng trên 1 hàng
    # Chia dữ liệu thành các phần (mỗi phần 20 dòng để bảng không quá dài)
    chunk_size = 20
    chunks = [table_data[i:i + chunk_size] for i in range(0, len(table_data), chunk_size)]
    
    for i in range(0, len(chunks), 2):
        row = st.columns(2)
        for col_idx in range(2):
            if i + col_idx < len(chunks):
                with row[col_idx]:
                    df = pd.DataFrame(chunks[i + col_idx], columns=[f"C{i+1}" for i in range(16)])
                    # Hiển thị bảng không có index để trông giống nhạc phổ
                    st.table(df.astype(str).replace('nan', '').replace('0', ''))
