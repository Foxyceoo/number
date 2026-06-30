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

    # Hiển thị 2 Khuông trên 1 hàng (mỗi khuông 4 nhịp)
    sorted_m = sorted(measures.keys())
    for i in range(0, len(sorted_m), 8): # Mỗi hàng 8 nhịp (2 khuông x 4 nhịp)
        # Tạo hàng chứa 2 khuông
        row = st.columns(2)
        for col_idx in range(2):
            with row[col_idx]:
                st.subheader(f"Khuông {(i // 8) * 2 + col_idx + 1}")
                # Hiển thị 4 nhịp của khuông này
                cols_measure = st.columns(4)
                for m_offset in range(4):
                    m_idx = i + col_idx * 4 + m_offset
                    if m_idx in measures:
                        with cols_measure[m_offset]:
                            # Hiển thị các nốt trong nhịp theo hàng dọc
                            st.markdown("<div style='border-left: 1px solid #555; padding-left: 5px;'>", unsafe_allow_html=True)
                            for time_val, group in groupby(measures[m_idx], key=lambda x: x['time']):
                                n_vals = " ".join([str(get_number_from_key(n['key'])) for n in group])
                                st.markdown(f"**{n_vals}**")
                            st.markdown("</div>", unsafe_allow_html=True)
