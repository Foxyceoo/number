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
        
        st.markdown("<div style='border-left: 2px solid #555; padding-left: 10px; margin-bottom: 20px;'>", unsafe_allow_html=True)
        
        for time_val, group in groupby(measure_notes, key=lambda x: x['time']):
            notes_at_time = list(group)
            
            # Phân loại nốt
            row1_vals = [str(get_number_from_key(n['key'])) for n in notes_at_time if get_number_from_key(n['key']) > 7]
            row2_vals = [str(get_number_from_key(n['key'])) for n in notes_at_time if get_number_from_key(n['key']) <= 7]
            
            # Gộp các nốt lại thành một chuỗi duy nhất để hiển thị trên cùng một dòng
            if row1_vals:
                st.markdown(f"**{' '.join(row1_vals)}**")
            if row2_vals:
                st.markdown(f"**{' '.join(row2_vals)}**")
            
            st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)
