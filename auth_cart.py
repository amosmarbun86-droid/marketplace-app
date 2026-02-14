import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"

# =====================================
# AUTO CREATE FILE
# =====================================
if not os.path.exists(USER_FILE):
    pd.DataFrame(
        columns=["username", "password", "role"]
    ).to_csv(USER_FILE, index=False)

if not os.path.exists(CART_FILE):
    pd.DataFrame(columns=[
        "buyer", "product_id", "product_name",
        "price", "qty"
    ]).to_csv(CART_FILE, index=False)

if not os.path.exists(ORDER_FILE):
    pd.DataFrame(columns=[
        "order_id", "buyer", "total"
    ]).to_csv(ORDER_FILE, index=False)


# =====================================
# 🔐 LOGIN & REGISTER
# =====================================
def login_page():

    users = pd.read_csv(USER_FILE)

    tab1, tab2 = st.tabs(["Login", "Daftar"])

    # ================= LOGIN =================
    with tab1:

        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")

        if login_btn:

            if u == "" or p == "":
                st.error("Username dan password wajib diisi")
                return

            match = users[
                (users["username"] == u) &
                (users["password"] == p)
            ]

            if not match.empty:
                st.session_state.user = u
                st.session_state.role = match.iloc[0]["role"]
                st.success("Login berhasil")
                st.rerun()
            else:
                st.error("Username / password salah")


    # ================= REGISTER =================
    with tab2:

        with st.form("register_form"):
            u = st.text_input("Username baru")
            p = st.text_input("Password baru", type="password")

            role = st.selectbox(
                "Daftar sebagai",
                ["buyer", "seller"]
            )

            register_btn = st.form_submit_button("Daftar")

        if register_btn:

            if u == "" or p == "":
                st.error("Username dan password wajib diisi")
                return

            if u in users["username"].values:
                st.error("Username sudah digunakan")
                return

            new = pd.DataFrame([{
                "username": u,
                "password": p,
                "role": role
            }])

            users = pd.concat([users, new], ignore_index=True)
            users.to_csv(USER_FILE, index=False)

            st.success("Akun berhasil dibuat! Silakan login.")
