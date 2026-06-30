import streamlit as st
import json
from itertools import groupby

# Thiết lập BPM để chia nhịp
BPM = 100
MS_PER_BEAT = 60000 / BPM
MS_PER_MEASURE = MS_PER_BEAT * 4

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return "?"

st.title("🎵 Nhạc phổ chuẩn")
uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Gom nốt theo nhịp (Measure)
    measures = {}
    for n in notes:
        m_idx = int(n['time'] / MS_PER_MEASURE)
        if m_idx not in measures: measures[m_idx] = []
        measures[m_idx].append(n)

    # Hiển thị các nhịp
    for m_idx in sorted(measures.keys()):
        st.markdown(f"**Nhịp {m_idx + 1}**")
        
        # Nhóm theo thời điểm (time) bên trong nhịp
        measure_notes = sorted(measures[m_idx], key=lambda x: x['time'])
        
        # Bắt đầu container cho nhịp
        st.markdown("<div style='border-left: 2px solid #555; padding-left: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
        
        for time_val, group in groupby(measure_notes, key=lambda x: x['time']):
            notes_at_time = list(group)
            
            # Phân loại nốt vào row1 (nốt > 7) và row2 (nốt <= 7)
            row1 = [str(get_number_from_key(n['key'])) for n in notes_at_time if get_number_from_key(n['key']) > 7]
            row2 = [str(get_number_from_key(n['key'])) for n in notes_at_time if get_number_from_key(n['key']) <= 7]
            
            # Hiển thị 2 dòng số
            if row1: st.write(" ".join(row1))
            if row2: st.write(" ".join(row2))
            st.write("---") # Dòng kẻ nhẹ giữa các thời điểm
            
        st.markdown("</div>", unsafe_allow_html=True)
