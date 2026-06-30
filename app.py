import streamlit as st
import json
from itertools import groupby  # Đã chuyển lên đầu file

st.title("🎵 Trình diễn Nhạc phổ số (1-15)")

uploaded_file = st.file_uploader("Tải lên file JSON bài nhạc", type=["json"])

def get_number_from_key(key_str):
    try:
        parts = key_str.split('Key')
        if len(parts) > 1:
            return (int(parts[1]) % 15) + 1
        return "?"
    except:
        return "?"

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = data[0].get("songNotes", [])
    st.subheader(f"Nhạc phổ bài: {data[0].get('name')}")
    
    # Sắp xếp theo thời gian và nhóm lại
    notes = sorted(notes, key=lambda x: x['time'])
    
    # Hiển thị
    for time_val, group in groupby(notes, key=lambda x: x['time']):
        notes_at_same_time = list(group)
        
        # Tạo cột dựa trên số lượng nốt cùng thời điểm
        row = st.columns(len(notes_at_same_time))
        for idx, n in enumerate(notes_at_same_time):
            number = get_number_from_key(n['key'])
            with row[idx]:
                st.markdown(f"<h3 style='text-align: center; border: 1px solid #555; padding: 5px;'>{number}</h3>", unsafe_allow_html=True)
