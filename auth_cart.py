import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"

# =========================
# AUTO CREATE USER FILE
# =========================
if not os.path.exists(USER_FILE):
    pd.DataFrame(
        columns=["username", "password", "role"]
    ).to_csv(USER_FILE, index=False)

# =========================
# AUTO CREATE / FIX ADMIN
# =========================
def ensure_admin():
    users = pd.read_csv(USER_FILE)

    admin = users[users["username"] == "admin"]

    if admin.empty:
        new_admin = pd.DataFrame([{
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }])
        users = pd.concat([users, new_admin], ignore_index=True)
        users.to_csv(USER_FILE, index=False)
    else:
        idx = admin.index[0]
        users.loc[idx, "role"] = "admin"
        users.to_csv(USER_FILE, index=False)

ensure_admin()

# =========================
# LOGIN PAGE
# =========================
def login_page():

    users = pd.read_csv(USER_FILE)

    tab1, tab2 = st.tabs(["Login", "Daftar"])

    # LOGIN
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                match = users[
                    (users["username"] == username) &
                    (users["password"] == password)
                ]

                if not match.empty:
                    st.session_state.user = {
                        "username": username,
                        "role": match.iloc[0]["role"]
                    }
                    st.rerun()
                else:
                    st.error("Username / password salah")

    # REGISTER
    with tab2:
        with st.form("register_form"):
            username = st.text_input("Username baru")
            password = st.text_input("Password baru", type="password")
            role = st.selectbox("Role", ["buyer", "seller"])
            submit = st.form_submit_button("Daftar")

            if submit:
                if username == "" or password == "":
                    st.error("Tidak boleh kosong")
                    return

                if username in users["username"].values:
                    st.error("Username sudah ada")
                    return

                new_user = pd.DataFrame([{
                    "username": username,
                    "password": password,
                    "role": role
                }])

                users = pd.concat([users, new_user], ignore_index=True)
                users.to_csv(USER_FILE, index=False)

                st.success("Akun dibuat, silakan login")
                st.rerun()
