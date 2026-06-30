import streamlit as st
import json
import streamlit.components.v1 as components

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải file JSON", type=["json"]):
    data = json.load(uploaded_file)
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    
    # Sử dụng logic mới: beat_duration không chia 4, kết hợp với hiển thị 32 phách
    beat_duration = 60000 / bpm 
    
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    
    max_beat = max(time_map.keys()) if time_map else 0
    
    st.subheader(f"Nhạc phổ (BPM: {bpm}) - Nhịp 4/4")
    
    style = """
    <style>
        table { border-collapse: collapse; text-align: center; font-size: 16px; color: white; width: 100%; background-color: #0e1117; margin-bottom: 40px; }
        td { height: 60px; vertical-align: top; padding-top: 5px; font-weight: bold; width: 40px; }
    </style>
    """
    
    all_html = style
    # Hiển thị 32 phách mỗi khuông để nốt không bị nhảy dòng
    for khuong in range(0, max_beat + 32, 32):
        html_content = "<table><tr>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            # Cấu hình vạch kẻ
            border_right = "1px solid #555"
            
            # Vạch nhịp bình thường
            if (phach + 1) % 4 == 0: 
                border_right = "2px solid #aaa" 
            
            # Vạch ngăn cách khuông (vạch cuối) - Đổi màu tại đây
            if (phach + 1) % 32 == 0: 
                border_right = "4px solid #f1c40f" # Màu vàng cho vạch cuối
            
            # Vạch bắt đầu khuông (vạch đầu) - Đổi màu tại đây
            border_left = "2px solid #f1c40f" if phach == khuong else "none" # Màu vàng cho vạch đầu
