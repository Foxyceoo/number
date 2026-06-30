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

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Chia nốt theo nhịp (Measure)
    measures = {}
    for n in notes:
        m_idx = int(n['time'] / MS_PER_MEASURE)
        if m_idx not in measures: measures[m_idx] = []
        measures[m_idx].append(n)

    # Thay đoạn hiển thị trong vòng lặp nhịp bằng đoạn này:

    # Giả sử trong một nhịp, các nốt được chia thành 2 dòng (dòng 1: nốt cao, dòng 2: nốt thấp)
    # Bạn cần một logic phân loại nốt vào dòng 1 hoặc dòng 2 dựa trên cao độ (ví dụ nốt > 7 là dòng 1)
    
    st.markdown("<div style='display: flex; gap: 20px; border-left: 2px solid #555; padding-left: 10px;'>", unsafe_allow_html=True)
    
    row1 = [str(get_number_from_key(n['key'])) for n in group if get_number_from_key(n['key']) > 7]
    row2 = [str(get_number_from_key(n['key'])) for n in group if get_number_from_key(n['key']) <= 7]
    
    st.markdown(f"<div>{' '.join(row1)}</div>", unsafe_allow_html=True)
    st.markdown(f"<div>{' '.join(row2)}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
