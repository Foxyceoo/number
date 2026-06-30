import streamlit as st
import json
from itertools import groupby

st.title("🎵 Nhạc phổ chuẩn 2 Khuông/Hàng")

uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

def get_number_from_key(key_str):
    try:
        return (int(key_str.split('Key')[1]) % 15) + 1
    except:
        return "?"

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Cấu hình thời gian
    BPM = 100
    MS_PER_BEAT = 60000 / BPM
    MS_PER_MEASURE = MS_PER_BEAT * 4
    MS_PER_KHUONG = MS_PER_MEASURE * 4 # 1 khuông = 4 nhịp
    
    # Phân loại nốt vào các khuông và nhịp
    khuong_map = {}
    for n in notes:
        k_idx = int(n['time'] / MS_PER_KHUONG)
        m_idx = int((n['time'] % MS_PER_KHUONG) / MS_PER_MEASURE)
        if k_idx not in khuong_map: khuong_map[k_idx] = {}
        if m_idx not in khuong_map[k_idx]: khuong_map[k_idx][m_idx] = []
        khuong_map[k_idx][m_idx].append(n)

    # Hiển thị
    for k_idx in sorted(khuong_map.keys()):
        # Cứ 2 khuông thì xuống dòng (để tạo 2 khuông mỗi hàng)
        if k_idx % 2 == 0:
            row = st.columns(2)
        
        with row[k_idx % 2]:
            st.markdown(f"**Khuông {k_idx + 1}**")
            # Vẽ 4 nhịp cho khuông
            cols = st.columns(4)
            for m_idx in range(4):
                with cols[m_idx]:
                    st.markdown("<div style='border-left: 2px solid #000; padding-left: 5px;'>", unsafe_allow_html=True)
                    if m_idx in khuong_map[k_idx]:
                        # Hiển thị các nốt trong nhịp này
                        for time_val, group in groupby(khuong_map[k_idx][m_idx], key=lambda x: x['time']):
                            for n in group:
                                st.markdown(f"<span>{get_number_from_key(n['key'])}</span>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
