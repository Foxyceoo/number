import streamlit as st
import json
from itertools import groupby

# Giả sử bài nhạc có BPM là 100 (bạn có thể để người dùng nhập BPM)
BPM = 100
MS_PER_BEAT = 60000 / BPM
MS_PER_MEASURE = MS_PER_BEAT * 4  # Giả sử nhịp 4/4

def get_number_from_key(key_str):
    try:
        parts = key_str.split('Key')
        return (int(parts[1]) % 15) + 1 if len(parts) > 1 else "?"
    except:
        return "?"

# ... (đoạn load file giữ nguyên)

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Chia các nốt vào từng ô nhịp dựa trên thời gian
    current_measure = 0
    measures = {}
    for n in notes:
        measure_idx = int(n['time'] / MS_PER_MEASURE)
        if measure_idx not in measures: measures[measure_idx] = []
        measures[measure_idx].append(n)
        
    # Hiển thị
    for m_idx in sorted(measures.keys()):
        st.markdown(f"**Ô nhịp {m_idx + 1}**")
        # Nhóm theo thời điểm trong ô nhịp
        measure_notes = sorted(measures[m_idx], key=lambda x: x['time'])
        for time_val, group in groupby(measure_notes, key=lambda x: x['time']):
            notes_at_time = list(group)
            
            # Nếu có 3 nốt trở lên, hiển thị 3 hàng ngang
            cols = st.columns(len(notes_at_time))
            for i, n in enumerate(notes_at_time):
                with cols[i]:
                    st.markdown(f"<h3 style='text-align: center; border: 1px solid #ccc;'>{get_number_from_key(n['key'])}</h3>", unsafe_allow_html=True)
