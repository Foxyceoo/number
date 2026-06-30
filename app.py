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
        # Tạm thời nhóm mỗi 8 nốt thành một ô nhịp (có thể điều chỉnh)
        cols = st.columns(8)
        for i, note in enumerate(notes[:40]):  # Demo 40 nốt đầu
            number = get_number_from_key(note['key'])
            with cols[i % 8]:
                st.markdown(f"<h2 style='text-align: center;'>{number}</h2>", unsafe_allow_html=True)
                # Dấu gạch đứng phân cách nhịp
                # Dấu gạch đứng phân cách nhịp
                if (i + 1) % 8 == 0:
                    st.markdown("<hr>", unsafe_allow_html=True) # Dòng này sẽ tạo đường kẻ ngang phân cách nhịp
