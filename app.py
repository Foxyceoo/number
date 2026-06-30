import streamlit as st
import json
from itertools import groupby

st.title("🎵 Nhạc phổ chuẩn 2 Khuông/Hàng")
uploaded_file = st.file_uploader("Tải file JSON", type=["json"])

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return "?"

if uploaded_file is not None:
    data = json.load(uploaded_file)
    notes = sorted(data[0].get("songNotes", []), key=lambda x: x['time'])
    
    # Cấu hình: 1 khuông = 4 nhịp
    MS_PER_MEASURE = 2000 # Điều chỉnh số này để khớp nhịp bài của bạn
    
    # Gom nhóm theo khuông (mỗi khuông 4 nhịp = 8000ms)
    MS_PER_KHUONG = MS_PER_MEASURE * 4
    
    # Chia khuông
    khuong_map = {}
    for n in notes:
        k_idx = int(n['time'] / MS_PER_KHUONG)
        if k_idx not in khuong_map: khuong_map[k_idx] = []
        khuong_map[k_idx].append(n)

    # Hiển thị 2 khuông trên 1 hàng
    sorted_k_indices = sorted(khuong_map.keys())
    for i in range(0, len(sorted_k_indices), 2):
        row = st.columns(2)
        for col_idx in range(2):
            if i + col_idx < len(sorted_k_indices):
                k_idx = sorted_k_indices[i + col_idx]
                with row[col_idx]:
                    st.markdown(f"### Khuông {k_idx + 1}")
                    # Hiển thị nốt theo dạng bảng hoặc lưới nhịp
                    notes_in_khuong = khuong_map[k_idx]
                    # Sử dụng code hiển thị nốt gọn gàng hơn
                    for time_val, group in groupby(notes_in_khuong, key=lambda x: x['time']):
                        # Hiển thị các nốt cùng lúc thành 1 hàng ngang
                        n_list = [str(get_number_from_key(n['key'])) for n in group]
                        st.markdown(f"**{' | '.join(n_list)}**")
