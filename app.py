import streamlit as st
import pandas as pd
import json
import streamlit.components.v1 as components

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
padding_top_px = 40
padding_bottom_px = 90
margin_side = "900px"

def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---")
    uploaded_file = st.file_uploader("**Sheet 123**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")

if uploaded_file:
    data = json.load(uploaded_file)
    song_name = uploaded_file.name.replace(".json", "")
    bpm = data[0].get("bpm", 320)
    notes = data[0].get("songNotes", [])
    beat_duration = 60000 / bpm*2                       #BPM*
    time_map = {}
    for n in notes:
        beat_idx = round(n['time'] / beat_duration)
        time_map.setdefault(beat_idx, []).append(get_number_from_key(n['key']))
    max_beat = max(time_map.keys()) if time_map else 0

    style = f"""
    <style>
    ::-webkit-scrollbar {{ display: none !important; }}
    
    html, body {{ width: 100%; margin: 0; padding: 0; overflow-y: hidden !important; }}

    table {{ 
        border-collapse: collapse; 
        text-align: center; 
        table-layout: fixed !important; 
        width: {margin_side}; 
        margin: 0 auto 30px auto; 
        height: 60px !important; 
    }}

    td {{ 
        padding: 0 !important; 
        height: 60px !important; 
        width: 20px !important; 
        vertical-align: top !important; 
        border-right: 1px solid #555; 
        border-left: none; 
        overflow: hidden;
    }}

    .note-number {{ 
        font-size: 15px !important; 
        font-weight: bold !important; 
        line-height: 2 !important; 
        display: block;
    }}

    @media print {{
        .sidebar, header, .stAppDeployButton, footer {{ display: none !important; }}

        @page {{
        size: A4;
        margin: 1cm 1.2cm 1cm 0.8cm; /* Lề: trên, phải, dưới, trái */
        }}
        
        /* Điều chỉnh cỡ chữ cho nốt nhạc khi in */
        .note-number {{
            font-size: 11px !important; /*Giảm size nếu bị tràn hoặc tăng nếu muốn to rõ*/
        }}
        
        table {{
            page-break-inside: avoid !important; 
            break-inside: avoid !important; 
            margin-bottom: 56px !important; 
            display: table !important; 
            table-layout: fixed !important; /* Quan trọng: Ép bảng theo chiều rộng cố định */
            width: 100% !important;
        }}

        td {{
            width: 14px !important;       /* Cố định độ rộng ô khi in */
            min-width: 14px !important;   /* Đảm bảo ô không bị co lại nhỏ hơn mức này */
            max-width: 14px !important;   /* Đảm bảo ô không bị phình ra */
            padding: 0 !important;
            overflow: hidden !important;
            white-space: nowrap !important;
        }}

        .khuong-wrapper:last-child {{
            padding-bottom: 250mm !important; /* 300mm gần bằng chiều dài một tờ A4 */
        }}
    
        }}
        
        body {{
            overflow: visible !important;
        }}
    }}
    </style>
    """
    
    all_khuong_html = []
    line_number = 1
    for khuong in range(0, max_beat + 32, 32):
        # Đoạn code MỚI (đã bỏ ngoặc)
        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle; font-size: 10px;'>{line_number}</td>"
        for phach in range(khuong, khuong + 16):
            vals = sorted(time_map.get(phach, []), reverse=True)

            border_right = " 0px solid #d8d8d8"
            if (phach + 1) % 4 == 0:
                border_right = "0.5px solid #00008c"
            if (phach + 1) % 16 == 0:
                border_right = "2px solid #00008c"

            border_left = "2px solid #00008c" if phach == khuong else "none"

            if vals:
                top_num = vals[0]
                bottom_nums = "<br>".join(map(str, vals[1:]))
                cell_content = f"""
                <div style='display: flex; flex-direction: column; align-items: center; justify-content: flex-start; height: 50px; padding-top: 2px;'>
                    <div class='top-row'>{top_num}</div>
                    <div class='bottom-row'>{bottom_nums}</div>
                </div>
                """
            else:
                cell_content = ""

            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        all_khuong_html.append(html_content)
        line_number += 1

    PAGE_HEIGHT_LIMIT = 800
    current_page_height = 0
    display_html = f"<h1 style='text-align: center; font-size: 40px; margin-top: 20px; margin-bottom: 70px;'>{song_name}</h1>"

    for khuong_html in all_khuong_html:
        khuong_height = 110 
        
        if current_page_height + khuong_height > PAGE_HEIGHT_LIMIT:
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div><div class='page-break'></div>"
            current_page_height = khuong_height
        else:
            display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"
            current_page_height += khuong_height

    html_to_render = style + display_html
    row_height = 50 + 50
    total_height = (len(all_khuong_html) * row_height) + 100
    components.html(html_to_render, height=total_height, scrolling=False)

    if st.button("to PDF"):
        js_code = """
        <script>
            window.parent.window.print();
        </script>
        """
        components.html(js_code, height=0)
