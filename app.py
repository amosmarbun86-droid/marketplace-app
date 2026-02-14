import streamlit as st
import pandas as pd
import os
from auth_cart import *

st.set_page_config(page_title="Marketplace Tawar", layout="wide")

# ===============================
# INIT SESSION STATE (WAJIB)
# ===============================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = "guest"

if "cart" not in st.session_state:
    st.session_state.cart = []

# ===============================
# FILE CONFIG
# ===============================
PRODUCT_FILE = "products.csv"
OFFER_FILE = "offers.csv"

# buat file offers jika belum ada
if not os.path.exists(OFFER_FILE):
    pd.DataFrame(
        columns=[
            "product_id",
            "product_name",
            "buyer",
            "offer_price"
        ]
    ).to_csv(OFFER_FILE, index=False)

# ===============================
# LOGIN CHECK
# ===============================
if st.session_state.user is None:
    login_page()
    st.stop()

# ambil session state dengan aman
username = st.session_state.get("user")
role = st.session_state.get("role", "guest")

# ===============================
# LOAD DATA
# ===============================
products = pd.read_csv(PRODUCT_FILE)
offers = pd.read_csv(OFFER_FILE)

# ===============================
# HEADER
# ===============================
st.title("🛒 Marketplace Tawar-Menawar")
st.write(f"Login sebagai: **{username}** ({role})")

# ===============================
# MENU
# ===============================
menu_list = ["Katalog Produk", "Keranjang", "Tawaran Saya"]

if role == "admin":
    menu_list.append("Admin - Kelola Tawaran")

menu = st.sidebar.selectbox("Menu", menu_list)

# ===============================
# KATALOG PRODUK
# ===============================
if menu == "Katalog Produk":

    st.header("📦 Katalog Produk")

    active_products = products[products["is_active"] == True]

    for _, p in active_products.iterrows():

        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(p["image_url"], width=150)

        with col2:
            st.subheader(p["product_name"])
            st.write("Kategori:", p["category"])
            st.write("Harga:", f"Rp {int(p['price']):,}")
            st.write("Stok:", f"{int(p['stock'])} {p['unit']}")
            st.write(p["description"])

            # tombol keranjang
            if st.button(
                "🛒 Tambah ke Keranjang",
                key=f"cart_{p['product_id']}"
            ):
                add_to_cart(username, p)
                st.success("Ditambahkan ke keranjang")

            # form tawaran
            with st.form(f"offer_{p['product_id']}"):

                offer_price = st.number_input(
                    "Harga tawaran",
                    min_value=0,
                    step=1000,
                    key=f"offer_input_{p['product_id']}"
                )

                submit = st.form_submit_button("Ajukan Tawaran")

                if submit:

                    new_offer = pd.DataFrame([{
                        "product_id": p["product_id"],
                        "product_name": p["product_name"],
                        "buyer": username,
                        "offer_price": offer_price
                    }])

                    offers = pd.concat([offers, new_offer], ignore_index=True)
                    offers.to_csv(OFFER_FILE, index=False)

                    st.success("Tawaran berhasil dikirim!")

# ===============================
# TAWARAN SAYA
# ===============================
elif menu == "Tawaran Saya":

    st.header("📄 Tawaran Saya")

    my_offers = offers[offers["buyer"] == username]

    if len(my_offers) == 0:
        st.info("Belum ada tawaran")
    else:
        st.dataframe(my_offers)

# ===============================
# ADMIN MENU
# ===============================
elif menu == "Admin - Kelola Tawaran":

    st.header("⚙️ Kelola Tawaran")

    st.dataframe(offers)
