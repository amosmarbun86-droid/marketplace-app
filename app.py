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
    st.session_state.role = "guest"

if "cart" not in st.session_state:
    st.session_state.cart = []

# ===============================
# LOGIN PAGE
# ===============================
if st.session_state.user is None:
    login_page()
    st.stop()

username = st.session_state.user
role = st.session_state.role

# ===============================
# FILE CONFIG
# ===============================
PRODUCT_FILE = "products.csv"
OFFER_FILE = "offers.csv"

products = pd.read_csv(PRODUCT_FILE)
offers = pd.read_csv(OFFER_FILE)

# ===============================
# HEADER
# ===============================
st.title("🛒 Marketplace Tawar-Menawar")
st.write(f"Login sebagai: **{username}** ({role})")

# ===============================
# MENU ROLE BASED
# ===============================
menu_list = ["Katalog Produk"]

if role == "buyer":
    menu_list += ["Keranjang", "Tawaran Saya"]

if role == "admin":
    menu_list += ["Admin - Kelola Produk", "Admin - Kelola Tawaran"]

menu = st.sidebar.selectbox("Menu", menu_list)

# ===============================
# KATALOG
# ===============================
if menu == "Katalog Produk":

    active_products = products[products["is_active"] == True]

    for _, p in active_products.iterrows():

        st.subheader(p["product_name"])
        st.write("Harga:", p["price"])

        if role == "buyer":

            if st.button("Tambah ke Keranjang", key=f"cart{p['product_id']}"):
                add_to_cart(username, p)
                st.success("Masuk keranjang")

            with st.form(f"offer{p['product_id']}"):

                price = st.number_input("Tawar", 0)

                if st.form_submit_button("Kirim Tawaran"):

                    new = pd.DataFrame([{
                        "product_id": p["product_id"],
                        "product_name": p["product_name"],
                        "buyer": username,
                        "offer_price": price
                    }])

                    offers = pd.concat([offers, new], ignore_index=True)
                    offers.to_csv(OFFER_FILE, index=False)

                    st.success("Tawaran dikirim")

# ===============================
# BUYER MENU
# ===============================
elif menu == "Keranjang":

    if role != "buyer":
        st.error("Akses ditolak")
        st.stop()

    show_cart(username)

elif menu == "Tawaran Saya":

    if role != "buyer":
        st.error("Akses ditolak")
        st.stop()

    my = offers[offers["buyer"] == username]
    st.dataframe(my)

# ===============================
# ADMIN MENU
# ===============================
elif menu == "Admin - Kelola Produk":

    if role != "admin":
        st.error("Akses ditolak")
        st.stop()

    st.dataframe(products)

elif menu == "Admin - Kelola Tawaran":

    if role != "admin":
        st.error("Akses ditolak")
        st.stop()

    st.dataframe(offers)
