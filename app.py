import streamlit as st
import json

st.set_page_config(page_title='"Number" one Foxy', layout="wide")

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---")
    uploaded_file = st.file_uploader("Sheet 123", type=["json"])
    st.markdown("---")
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")

if uploaded_file:
    data = json.load(uploaded_file)
    song_name = uploaded_file.name.replace(".json", "")
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    beat_duration = 60000 / bpm 
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append((int(n['key'].split('Key')[1]) % 15) + 1)
    max_beat = max(time_map.keys()) if time_map else 0

    # CSS cải tiến: table-layout: fixed để bảng không bị nhảy, 
    # @media print để ẩn các nút bấm khi in và ngắt trang đúng chỗ
    style = """
    <style>
        body { font-family: sans-serif; padding: 20px; }
        table { 
            border-collapse: collapse; text-align: center; font-size: 16px; 
            width: 100%; margin-bottom: 50px; table-layout: fixed; 
        }
        td { 
            height: 60px; vertical-align: top; padding-top: 10px; 
            font-weight: bold; width: 35px; border-right: 1px solid #555;
            white-space: nowrap; overflow: hidden;
        }
        .song-title { text-align: center; margin-top: 40px; margin-bottom: 90px; }
        .page-break { page-break-after: always; }
        
        @media print {
        /* Các thành phần không cần in */
        .print-btn, [data-testid="stSidebar"], header { display: none !important; }
    
        /* Ép ngắt trang cực mạnh */
        .page-break { 
            display: block; 
            page-break-after: always !important; 
            break-after: page !important; 
            height: 0 !important;
       }
    
        /* Đảm bảo nội dung không bị co lại vào 1 trang */
        body, html {
            height: auto !important;
            overflow: visible !important;
        }
    }
    </style>
    """

    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        html_content = f"<table><tr><td style='color: red; border: none; width: 30px;'>{line_number}</td>"
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

    # Ghép nội dung hiển thị (sử dụng st.markdown thay vì components.html)
    display_html = f"<h1 class='song-title'>{song_name}</h1>"
    for i in range(0, len(all_khuong_html), 8):
        display_html += "".join(all_khuong_html[i:i+8]) + "<div class='page-break'></div>"

    st.markdown(f"{style}{display_html}", unsafe_allow_html=True)

    # NÚT IN PDF
    st.markdown("""
    <style>
        .print-btn {
            display: inline-block; padding: 0.5em 1em; background-color: #ffcbcc; 
            color: #00008c; text-decoration: none; border-radius: 5px; 
            font-weight: bold; cursor: pointer; border: none; margin-top: 20px;
        }
    </style>
    <a href="#" class="print-btn" onclick="window.print(); return false;">Mở bảng in</a>
    """, unsafe_allow_html=True)
