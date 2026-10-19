                        <div style="
                            min-height: 19.5px;
                            line-height: 19.5px;
                            font-size: 15px;
                            font-weight: bold;
                            text-align: center;
                            font-family: monospace, sans-serif;
                        ">{symbol}</div>
                        """)

                all_nums = "".join(note_html)

                cell_content = f"""
                <div style="
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: flex-start;
                    min-height: 60px;
                ">
                    {all_nums}
                </div>
                """
            else:
                # Đồng bộ chiều cao ô trống
                cell_content = "<div style='min-height: 60px;'></div>"

            html_content += f"<td style='width: {cell_width_pct}%; border-right: {border_right}; border-left: {border_left}; padding: 2px 0 !important; vertical-align: top; box-sizing: border-box;'>{cell_content}</td>"
        
        html_content += "</tr></table>"
        all_khuong_html.append(html_content)
        
    # =========================================================================
    # 5. XẾP DÒNG NHẠC VÀO TRANG GIẤY CHUẨN & TỰ ĐỘNG BÙ KHUÔNG ẨN (8 DÒNG/TRANG)
    # =========================================================================
    display_html = ""
    lines_per_page = 8  # Đã đổi thành 8 dòng theo ý bạn nè!
    
    # Danh sách chứa HTML của từng trang sau khi gom đủ 8 dòng
    pages_list = []
    
    for idx in range(0, len(all_khuong_html), lines_per_page):
        chunk = all_khuong_html[idx : idx + lines_per_page]
        
        page_content = "<div class='sheet-page'>"
        
        # 1. Chèn các khuông nhạc có dữ liệu thực tế vào trước
        for khuong_html in chunk:
            page_content += f"<div class='khuong-wrapper'>{khuong_html}</div>"
        
        # 2. TRƯỜNG HỢP TRANG CUỐI THIẾU DÒNG: Tự động bù các khuông nhạc ẩn cho đủ 8 dòng
        if len(chunk) < lines_per_page:
            needed_lines = lines_per_page - len(chunk)
            
            # Tạo một khung bảng trống có kích thước y hệt khuông thật để giữ dáng hàng
            cell_width_pct = 100.0 / bits_per_page
            empty_table = "<table style='table-layout: fixed; width: 94% !important; border-collapse: collapse; margin: 0 auto !important; padding: 0;'><tr>"
            for _ in range(bits_per_page):
                empty_table += f"<td style='width: {cell_width_pct}%; padding: 2px 0 !important; vertical-align: top; box-sizing: border-box;'><div style='min-height: 60px;'></div></td>"
            empty_table += "</tr></table>"
            
            # Bù thêm số dòng ẩn cần thiết
            for _ in range(needed_lines):
                page_content += f"<div class='khuong-wrapper' style='visibility: hidden;'>{empty_table}</div>"
        
        page_content += "</div>"
        pages_list.append(page_content)
        
    # Chuỗi HTML đầy đủ để hiển thị trên Web xem trước
    html_to_render = page_style + "".join(pages_list)
    
    # Tính chiều cao hiển thị trên web (8 dòng thì trang sẽ cao hơn một chút)
    total_pages = len(pages_list)
    calculated_height = total_pages * 1200 + 100


    # Khoảng cách trước nút xuất PDF
    st.write('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    # Nút xuất PDF
    if "trigger_print" not in st.session_state:
        st.session_state.trigger_print = False

    if st.button("Xuất PDF", key="btn_to_pdf_layout"):
        if not pages_list:
            st.error("Không có dữ liệu trang để in!")
        else:
            st.session_state.trigger_print = True

    # Xử lý in bản nhạc
    if st.session_state.get("trigger_print", False):
        st.session_state.trigger_print = False

        html_for_print = page_style + "".join(pages_list)
        safe_html_json = json.dumps(html_for_print)
        print_id = int(time.time())

        js_code_print = f"""
        <script>
        (function() {{
            // ID lượt in: {print_id}
            var htmlContent = {safe_html_json};
            var printWindow = window.open('', '_blank');

            if (!printWindow) {{
                alert('Trình duyệt đã chặn cửa sổ bật lên. Hãy cho phép popup để xuất PDF nhé!');
                return;
            }}

            printWindow.document.write(
                '<html><head><title>In Toàn Bộ Sheet Nhạc</title></head><body>'
                + htmlContent +
                '</body></html>'
            );

            printWindow.document.close();
            printWindow.focus();

            setTimeout(function() {{
                printWindow.print();
            }}, 500);
        }})();
        </script>
        """

        components.html(js_code_print, height=0)

    # Hiển thị bản nhạc      
