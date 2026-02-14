import streamlit as st
import pandas as pd
import os
from auth_cart import *

st.set_page_config(page_title="Marketplace Tawar", layout="wide")

# ===============================
# SESSION INIT
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

# ===============================
# LOGIN CHECK
# ===============================
if st.session_state.user is None:
    login_page()
    st.stop()

username = st.session_state.user
role = st.session_state.role

# ===============================
# FILE SETUP
# ===============================
PRODUCT_FILE = "products.csv"
OFFER_FILE = "offers.csv"

if not os.path.exists(OFFER_FILE):
    pd.DataFrame(
        columns=["product_id","product_name","buyer","offer_price"]
    ).to_csv(OFFER_FILE, index=False)

products = pd.read_csv(PRODUCT_FILE)
offers = pd.read_csv(OFFER_FILE)

# ===============================
# LOGOUT
# ===============================
with st.sidebar:
    st.write(f"Login: {username} ({role})")
    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

# ===============================
# MENU BASED ON ROLE
# ===============================
menu = ["Katalog"]

if role == "buyer":
    menu += ["Keranjang", "Tawaran Saya"]

if role == "admin":
    menu += ["Admin - Produk", "Admin - Tawaran"]

choice = st.sidebar.selectbox("Menu", menu)

# ===============================
# KATALOG
# ===============================
if choice == "Katalog":

    st.header("Katalog Produk")

    active_products = products[products["is_active"] == True]

    for _, p in active_products.iterrows():

        st.subheader(p["product_name"])
        st.write("Harga:", p["price"])

        if role == "buyer":

            if st.button("Tambah Keranjang", key=f"c{p['product_id']}"):
                st.success("Masuk keranjang")

            with st.form(f"f{p['product_id']}"):
                offer = st.number_input("Tawar", 0)
                if st.form_submit_button("Kirim"):
                    new = pd.DataFrame([{
                        "product_id": p["product_id"],
                        "product_name": p["product_name"],
                        "buyer": username,
                        "offer_price": offer
                    }])
                    offers = pd.concat([offers, new], ignore_index=True)
                    offers.to_csv(OFFER_FILE, index=False)
                    st.success("Tawaran dikirim")

# ===============================
# BUYER MENU
# ===============================
elif choice == "Keranjang":

    if role != "buyer":
        st.error("Akses ditolak")
        st.stop()

    st.write("Halaman Keranjang Buyer")

elif choice == "Tawaran Saya":

    if role != "buyer":
        st.error("Akses ditolak")
        st.stop()

    my = offers[offers["buyer"] == username]
    st.dataframe(my)

# ===============================
# ADMIN MENU
# ===============================
elif choice == "Admin - Produk":

    if role != "admin":
        st.error("Akses ditolak")
        st.stop()

    st.dataframe(products)

elif choice == "Admin - Tawaran":

    if role != "admin":
        st.error("Akses ditolak")
        st.stop()

    st.dataframe(offers)
