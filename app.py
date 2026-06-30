import streamlit as st
import json

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
st.title("Bộ chuyển đổi sheet số")

# Tùy chỉnh khoảng cách tên bài hát
padding_top_px = 40
padding_bottom_px = 90

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

if uploaded_file := st.file_uploader("Tải lên file JSON", type=["json"]):
    data = json.load(uploaded_file)
    song_name = uploaded_file.name.replace(".json", "")
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    beat_duration = 60000 / bpm 
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    max_beat = max(time_map.keys()) if time_map else 0

    # CSS cải tiến: ép cứng chiều rộng ô và xóa sạch viền thừa
    style = """
    <style>
    body { font-family: sans-serif; padding: 20px; }
    table { 
        border-collapse: collapse; text-align: center; font-size: 14px; 
        width: 100%; margin-bottom: 40px; table-layout: fixed; /* Ép bảng đều */
    }
    td { 
        height: 50px; vertical-align: top; padding-top: 5px; 
        font-weight: bold; width: 30px; min-width: 30px; /* Cố định ô */
        border: none !important; border-right: 1px solid #ccc; 
    }
    .song-title { text-align: center; margin-bottom: 40px; }
    .page-break { page-break-after: always; }
    
    @media print {
        header, section[data-testid="stSidebar"], .stFileUploader, .print-btn { display: none !important; }
        body { padding: 0 !important; }
    }
    </style>
    """

    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        html_content = f"<table><tr><td style='color: red; border: none !important; width: 30px;'>{line_number}</td>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True)
            border_right = "1px solid #555" 
            if (phach + 1) % 4 == 0: border_right = "2px solid #ff0000"
            if (phach + 1) % 16 == 0: border_right = "3px solid #00008c"
            
            style_td = f"border-right: {border_right};"
            if phach == khuong: style_td += "border-left: 3px solid #00008c;"
            
            cell_content = "<br>".join(map(str, vals)) if vals else ""
            html_content += f"<td style='{style_td}'>{cell_content}</td>"
        all_khuong_html.append(html_content + "</tr></table>")
        line_number += 2

    # Ghép nội dung in nhiều trang
    display_html = f"<h1 class='song-title' style='margin-top: {padding_top_px}px;'>{song_name}</h1>"
    for i in range(0, len(all_khuong_html), 8):
        display_html += "".join(all_khuong_html[i:i+8]) + "<div class='page-break'></div>"

    # Render trực tiếp vào trang để in được nhiều trang
    st.markdown(f"{style}<body>{display_html}</body>", unsafe_allow_html=True)

    # Nút in
    st.markdown("""
    <style>.print-btn { padding: 10px 20px; background: #ffcbcc; color: #00008c; text-decoration: none; border-radius: 5px; font-weight: bold; }</style>
    <a href="#" class="print-btn" onclick="window.print(); return false;">Mở bảng in</a>
    """, unsafe_allow_html=True)
