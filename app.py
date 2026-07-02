import streamlit as st
import pandas as pd
import json
import math
import time
import pyrebase
import requests
import streamlit.components.v1 as components

# Cấu hình Firebase
config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "databaseURL": "https://email-8c050-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

if 'user' not in st.session_state:
    st.session_state.user = None

def login_form():
    st.title("Đăng nhập")
    email = st.text_input("Email", key="email_input")
    password = st.text_input("Mật khẩu", type="password", key="pass_input")
    if st.button("Đăng nhập"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state.user = user
            st.session_state.user_name = email.split('@')[0]
            st.rerun() 
        except:
            st.error("Email hoặc mật khẩu không chính xác.")

if st.session_state.user is None:
    login_form()
    st.stop()
else:
    if 'is_loaded' not in st.session_state:
        st.session_state.is_loaded = False
    if not st.session_state.is_loaded:
        with st.spinner('Đang tải dữ liệu...'):
            time.sleep(2)
        st.session_state.is_loaded = True
        st.rerun()
    st.success(f"hello, {st.session_state.user_name}!")

if st.session_state.user is not None:
    with st.sidebar:
        st.markdown("---")
        st.write(f"**Người dùng:** {st.session_state.user_name}")
        if st.button("Đổi mật khẩu"):
            st.session_state.show_change_password = True
        if st.session_state.get("show_change_password", False):
            new_password = st.text_input("Nhập mật khẩu mới", type="password")
            if st.button("Xác nhận đổi"):
                try:
                    id_token = st.session_state.user['idToken']
                    api_key = st.secrets["FIREBASE_API_KEY"]
                    api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
                    payload = {"idToken": id_token, "password": new_password, "returnSecureToken": True}
                    response = requests.post(api_url, json=payload)
                    if response.status_code == 200:
                        st.success("Đổi mật khẩu thành công!")
                        st.session_state.show_change_password = False
                        st.rerun()
                    else:
                        st.error("Lỗi Firebase.")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")
        if st.button("Đăng xuất"):
            st.session_state.user = None
            st.rerun()

def get_symbol(value, mode):
    if mode == "1. 1.. 1...":
        mapping = {1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "1.", 9: "2.", 10: "3.", 11: "4.", 12: "5.", 13: "6.", 14: "7.", 15: "1.."}
    elif mode == "abc":
        mapping = {1: "a1", 2: "a2", 3: "a3", 4: "a4", 5: "a5", 6: "b1", 7: "b2", 8: "b3", 9: "b4", 10: "b5", 11: "c1", 12: "c2", 13: "c3", 14: "c4", 15: "c5"}
    else:
        return str(value)
    return mapping.get(value, str(value))

with st.sidebar:
    st.title("Bộ chuyển đổi sheet số")
    uploaded_file = st.file_uploader("**Nhập file của bạn**", type=["json"])
    display_mode = st.radio("Chế độ hiển thị:", ["1-15", "1. 1.. 1...", "abc"])

if uploaded_file:
    data = json.load(uploaded_file)
    song_data = data[0]
    song_name = uploaded_file.name.replace(".json", "")
    columns = song_data.get("columns", [])
    bits_per_page = 32
    
    def get_number_from_key(note_data):
        return int(note_data[0]) + 1
    
    # CSS: Mỗi bảng là 1 block riêng biệt, dùng .table-spacer để cách nhau
    style = """
    <style>
        ::-webkit-scrollbar { display: none !important; }
        .table-spacer { margin-bottom: 40px !important; }
        table { 
            border-collapse: collapse; 
            text-align: center; 
            table-layout: fixed !important; 
            width: 100% !important; 
            page-break-inside: avoid !important; 
        }
        td { 
            padding: 2px !important; 
            width: 20px !important; 
            vertical-align: top !important; 
            border-right: 1px solid #555; 
            border-left: none; 
            overflow: hidden; 
        }
        @media print {
            .sidebar, header, .stAppDeployButton, footer { display: none !important; }
            @page { size: A4; margin: 1cm; }
            table { margin-bottom: 40px !important; }
        }
    </style>
    """
    
    all_khuong_html = ""
    line_number = 1
    
    for i in range(0, len(columns), bits_per_page):
        khuong_columns = columns[i : i + bits_per_page]
        if len(khuong_columns) < bits_per_page:
            khuong_columns.extend([[0, []]] * (bits_per_page - len(khuong_columns)))

        html_table = f"<table><tr><td style='color: red; border: none; vertical-align: middle; font-size: 10px;'>{line_number}</td>"
        
        for col_idx, col in enumerate(khuong_columns):
            notes_in_col = col[1]
            raw_vals = sorted([get_number_from_key(n) for n in notes_in_col], reverse=True)
            vals = [get_symbol(v, display_mode) for v in raw_vals] if display_mode != "1-15" else raw_vals
            
            border_right = "0.5px solid #00008c" if (((col_idx + 1) % 8 == 0) or (col_idx + 1) == bits_per_page) else "0px solid #ff0000"
            border_left = "0.5px solid #00008c" if (col_idx == 0) else "none"
            
            all_nums = "<br>".join(map(str, vals))
            cell_content = f"<div style='font-size: 12px; font-weight: bold; line-height: 1.4;'>{all_nums}</div>" if vals else ""
            html_table += f"<td style='border-right: {border_right}; border-left: {border_left};'>{cell_content}</td>"
        
        html_table += "</tr></table>"
        # Đóng gói mỗi bảng vào div có class table-spacer để tạo khoảng cách
        all_khuong_html += f"<div class='table-spacer'>{html_table}</div>"
        line_number += 2
        
    display_html = f"<h1 style='text-align: center; font-size: 30px; margin-bottom: 40px;'>{song_name}</h1>" + all_khuong_html
    
    components.html(style + display_html, height=len(columns)//32 * 150 + 100, scrolling=True)
    
    if st.button("to PDF"):
        js_code = "<script>window.parent.window.print();</script>"
        components.html(js_code, height=0)
