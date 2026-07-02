import streamlit as st
import pandas as pd
import json
import math
import streamlit.components.v1 as components

st.set_page_config(page_title='"Number" one Foxy', layout="wide")
padding_top_px = 40
padding_bottom_px = 90
margin_side = "900px"

# Hàm chuyển đổi Key thành số 1-15
def get_number_from_key(note_data):
    # note_data là list [pitch, layer], ví dụ: [7, "2"]
    # Pitch (note_data[0]) chính là vị trí phím 0-14
    pitch = int(note_data[0])
    return pitch + 1  # Vì index bắt đầu từ 0 nên cộng 1 để ra số 1-15

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    st.markdown("---")
    uploaded_file = st.file_uploader("**Sheet 123**", type=["json"])
    st.caption("Hãy chọn file JSON của bạn để bắt đầu!")
    st.markdown("---")

if uploaded_file:
    data = json.load(uploaded_file)
    song_data = data[0]
    song_name = uploaded_file.name.replace(".json", "")
    
    # Lấy danh sách các cột và số bit mỗi trang từ file
    columns = song_data.get("columns", [])
    bits_per_page = song_data.get("bitsPerPage", 16)
    
    def get_number_from_data(note_data):
        # note_data là list [pitch, key]
        return int(note_data[1])

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
        @page {{ size: A4; margin: 1cm 1.2cm 1cm 0.8cm; }}
        .note-number {{ font-size: 11px !important; }}
        table {{ page-break-inside: avoid !important; break-inside: avoid !important; margin-bottom: 56px !important; width: 100% !important; }}
        td {{ width: 14px !important; min-width: 14px !important; max-width: 14px !important; padding: 0 !important; overflow: hidden !important; white-space: nowrap !important; }}
        .khuong-wrapper:last-child {{ padding-bottom: 250mm !important; }}
        .print-footer {{ display: block !important; position: fixed !important; bottom: 10px !important; left: 10px !important; width: 100% !important; }}
    }}
    </style>
    """
    
    all_khuong_html = []
    line_number = 1
    
    # Duyệt theo từng trang (bits_per_page)
    for i in range(0, len(columns), bits_per_page):
        khuong_columns = columns[i : i + bits_per_page]
        
        html_content = f"<table><tr><td style='color: red; border: none; vertical-align: middle; font-size: 10px;'>{line_number}</td>"
        
        for col_idx, col in enumerate(khuong_columns):
            # col là [time, [[pitch, key], ...]]
            notes_in_col = col[1]
            vals = sorted([get_number_from_key(n) for n in notes_in_col], reverse=True)

            # Logic kẻ bảng
            is_new_line = (col_idx == 0)
            is_beat_4 = ((col_idx + 1) % 4 == 0)
            border_right = "0.5px solid #00008c" if (is_beat_4 or (col_idx + 1) == bits_per_page) else "0px solid #d8d8d8"
            border_left = "0.5px solid #00008c" if is_new_line else "none"

            if vals:
                top_num = vals[0]
                bottom_nums = "<br>".join(map(str, vals[1:]))
                cell_content = f"""
                <div style='display: flex; flex-direction: column; align-items: center; justify-content: flex-start; height: 50px; padding-top: 2px;'>
                    <div class='top-row' style='font-size: 15px; font-weight: bold;'>{top_num}</div>
                    <div class='bottom-row' style='font-size: 10px; line-height: 1;'>{bottom_nums}</div>
                </div>
                """
            else:
                cell_content = ""

            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        
        html_content += "</tr></table>"
        all_khuong_html.append(html_content)
        line_number += 1
        
    display_html = f"<h1 style='text-align: center; font-size: 40px; margin-top: 20px; margin-bottom: 70px;'>{song_name}</h1>"
    
    # Render HTML
    for khuong_html in all_khuong_html:
        display_html += f"<div class='khuong-wrapper'>{khuong_html}</div>"

    footer_link = "<div class='print-footer' style='text-align: left; font-size: 12px; color: gray;'>https://foxynumber.streamlit.app</div>"
    html_to_render = style + display_html + footer_link
    
    total_height = (len(all_khuong_html) * 110) + 200
    components.html(html_to_render, height=total_height, scrolling=False)

    if st.button("to PDF"):
        js_code = "<script>window.parent.window.print();</script>"
        components.html(js_code, height=0)
