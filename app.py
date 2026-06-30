import streamlit as st
import json

st.title("Trình diễn Nhạc phổ số")

uploaded_file = st.file_uploader("Tải lên file JSON bài nhạc", type=["json"])

def get_number_from_key(key_str):
    """Trích xuất con số từ chuỗi KeyX và đưa về khoảng 1-15"""
    try:
        parts = key_str.split('Key')
        if len(parts) > 1:
            number = int(parts[1])
            # Đảm bảo số nằm trong khoảng 1-15
            return (number % 15) + 1
        return "?"
    except:
        return "?"

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = data[0].get("songNotes", [])
    
    st.subheader(f"Nhạc phổ bài: {data[0].get('name')}")
    
    # Tạo container hiển thị dạng dòng giống ảnh
    display_container = st.container()
    
    with display_container:
        # Sắp xếp và nhóm nốt theo thời gian
    from itertools import groupby
    notes = sorted(notes, key=lambda x: x['time'])
    
    for time_val, group in groupby(notes, key=lambda x: x['time']):
        notes_at_same_time = list(group)
        
        # Tạo một hàng (row) cho mỗi thời điểm
        row = st.columns(len(notes_at_same_time))
        
        # Hiển thị từng nốt trong hợp âm đó vào các cột tương ứng
        for idx, n in enumerate(notes_at_same_time):
            number = get_number_from_key(n['key'])
            with row[idx]:
                st.markdown(f"<h3 style='text-align: center; border: 1px solid #555; padding: 5px;'>{number}</h3>", unsafe_allow_html=True)
