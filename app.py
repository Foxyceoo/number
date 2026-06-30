import streamlit as st
import json
from itertools import groupby

# 1. Cấu hình ban đầu
st.title("🎵 Trình diễn Nhạc phổ số (1-15)")

# 2. Khai báo biến này ở ngoài cùng, không nằm trong khối lệnh nào
uploaded_file = st.file_uploader("Tải lên file JSON bài nhạc", type=["json"])

def get_number_from_key(key_str):
    try:
        parts = key_str.split('Key')
        return (int(parts[1]) % 15) + 1 if len(parts) > 1 else "?"
    except:
        return "?"

# 3. Chỉ kiểm tra khi biến đã được định nghĩa
if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    st.subheader(f"Nhạc phổ bài: {data[0].get('name')}")
    
    # Tính toán BPM và chia nhịp
    BPM = 100
    MS_PER_MEASURE = (60000 / BPM) * 4
    
    # Gom nhóm theo ô nhịp
    measures = {}
    for n in notes:
        m_idx = int(n['time'] / MS_PER_MEASURE)
        if m_idx not in measures: measures[m_idx] = []
        measures[m_idx].append(n)
        
    # Hiển thị
    for m_idx in sorted(measures.keys()):
        st.markdown(f"**Ô nhịp {m_idx + 1}**")
        # Nhóm theo thời điểm
        measure_notes = sorted(measures[m_idx], key=lambda x: x['time'])
        for time_val, group in groupby(measure_notes, key=lambda x: x['time']):
            notes_at_time = list(group)
            cols = st.columns(len(notes_at_time))
            for i, n in enumerate(notes_at_time):
                with cols[i]:
                    st.markdown(f"<h3 style='text-align: center; border: 1px solid #ccc; padding: 5px;'>{get_number_from_key(n['key'])}</h3>", unsafe_allow_html=True)
