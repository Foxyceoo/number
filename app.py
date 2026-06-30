import streamlit as st
import pandas as pd
import json
import io

# Cấu hình tên trang
st.set_page_config(page_title='"Number" one Foxy')
st.title("Bộ chuyển đổi sheet số")

# Hàm lấy số từ key (giữ nguyên logic của bạn)
def get_number_from_key(key_str):
    try: return (int(key_str.split('Key')[1]) % 15) + 1
    except: return ""

# 1. KHU VỰC TẢI FILE VÀ XỬ LÝ DỮ LIỆU
if uploaded_file := st.file_uploader("Sheet số (123)", type=["json"]):
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
    
    st.markdown(f"<h2 style='text-align: center;'>{song_name}</h2>", unsafe_allow_html=True)
    
    # 2. KHU VỰC HIỂN THỊ BẢNG TRÊN WEB (CSS & HTML)
    style = """
    <style>
        table { 
            border-collapse: collapse; 
            text-align: center; 
            font-size: 16px; 
            width: 100%; 
            margin-bottom: 40px; 
            color: inherit; 
        }
        td { 
            height: 60px; 
            vertical-align: top; 
            padding-top: 5px; 
            font-weight: bold; 
            width: 40px; 
            /* Kẻ ngang: Dùng màu xám nhạt (cùng tông theme) */
            border-top: 0px solid rgba(128, 128, 128, 0.3);
            border-bottom: 0px solid rgba(128, 128, 128, 0.3);
            /* Kẻ dọc: Giữ nguyên màu đậm để phân chia phách */
            border-right: 1px solid #555; 
            border-left: none;
        }
    </style>
    <script>
        function adjustTheme() {
            const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            document.body.style.color = isDarkMode ? '#FFFFFF' : '#000000';
            document.body.style.backgroundColor = 'transparent';
        }
        window.onload = adjustTheme;
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', adjustTheme);
    </script>
    """
    
    all_html = style
    for khuong in range(0, max_beat + 32, 32):
        # Thêm class 'khuong-nhac' để PDF biết chỗ ngắt trang
        html_content = "<div class='khuong-nhac'><table><tr>"
        for phach in range(khuong, khuong + 32):
            vals = sorted(time_map.get(phach, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            border_right = "1px solid #555"
            if (phach + 1) % 4 == 0: border_right = "2px solid #aaa"
            if (phach + 1) % 16 == 0: border_right = "4px solid #00008c"
            
            border_left = "4px solid #00008c" if phach == khuong else "none"
            
            cell_content = "<br>".join(map(str, vals)) if vals else ""
            html_content += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        html_content += "</tr></table></div>"
        all_html += html_content
    
    components.html(f"<html><body>{all_html}</body></html>", height=800, scrolling=True)

    if st.button("Tải về Excel (Bố cục Lưới)"):
        # 1. Chuẩn bị dữ liệu dạng lưới 16 cột
        grid_data = []
        for i in range(0, max_beat + 1, 16):
            row = []
            for j in range(16):
                phach = i + j
                if phach <= max_beat:
                    # Lấy danh sách nốt và nối lại bằng dấu xuống dòng để hiển thị trong ô
                    vals = sorted(time_map.get(phach, []), reverse=True)
                    row.append("\n".join(map(str, vals)))
                else:
                    row.append("")
            grid_data.append(row)
    
        # 2. Tạo DataFrame từ dữ liệu lưới
        df = pd.DataFrame(grid_data)
    
        # 3. Xuất file Excel vào bộ nhớ đệm
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, header=False)
            # Lấy workbook và worksheet để định dạng ô vuông
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
        
            # Định dạng ô cho giống lưới: độ rộng cột vừa phải, căn giữa
            format_cell = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
            for i in range(16):
                worksheet.set_column(i, i, 5, format_cell) # Độ rộng cột = 5
            for i in range(len(grid_data)):
                worksheet.set_row(i, 40, format_cell)      # Chiều cao hàng = 40
            
        buffer.seek(0)
    
        st.download_button(
            label="📥 Tải file Excel về máy",
           data=buffer,
            file_name=f"{song_name}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
