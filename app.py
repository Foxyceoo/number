def draw_table(times, time_map):
    if not times: return
    
    # Thêm 'display: inline-table' và ép 'white-space: nowrap'
    html = "<table style='width:100%; border-collapse: collapse; text-align: center; margin-bottom: 20px; font-size: 12px; table-layout: fixed; display: table;'>"
    
    for row_idx in range(2):
        html += "<tr>"
        for t in times:
            vals = sorted(time_map.get(t, []), reverse=True, key=lambda x: int(x) if x != "" else 0)
            
            # Ép style cho ô <td> không được tự xuống dòng
            cell_style = "border: 1px solid #555; height: 35px; vertical-align: top; padding: 2px; white-space: nowrap;"
            
            if row_idx == 0:
                content = str(vals[0]) if len(vals) > 0 else ""
            else:
                content = "<br>".join(map(str, vals[1:])) if len(vals) > 1 else ""
                
            html += f"<td style='{cell_style}'>{content}</td>"
        html += "</tr>"
    html += "</table>"
    st.markdown(html, unsafe_allow_html=True)
