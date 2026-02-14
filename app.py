import streamlit as st
import pandas as pd
import os
from auth_cart import *

st.set_page_config(page_title="Marketplace Tawar", layout="wide")

PRODUCT_FILE = "products.csv"
OFFER_FILE = "offers.csv"

# ===== Buat file tawaran jika belum ada =====
if not os.path.exists(OFFER_FILE):
    pd.DataFrame(
        columns=["product_id", "product_name", "buyer", "offer_price", "status"]
    ).to_csv(OFFER_FILE, index=False)

# ===== LOGIN WAJIB =====
if "user" not in st.session_state:
    login_page()
    st.stop()

username = st.session_state.user
role = st.session_state.role

# ===== Load data =====
products = pd.read_csv(PRODUCT_FILE)
offers = pd.read_csv(OFFER_FILE)

st.title("🛒 Marketplace Tawar-Menawar")
st.write(f"Login sebagai: {username} ({role})")

# ===== MENU BERDASARKAN ROLE =====
menu_list = ["Katalog Produk", "Keranjang", "Tawaran Saya"]

if role == "admin":
    menu_list.append("Admin — Kelola Tawaran")

menu = st.sidebar.selectbox("Menu", menu_list)

# =====================================
# 📦 KATALOG PRODUK
# =====================================
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
            st.write("Stok:", f"{p['stock']} {p['unit']}")
            st.write(p["description"])

            if st.button("🛒 Tambah ke Keranjang", key=f"cart_{p['product_id']}"):
                add_to_cart(username, p)

            with st.form(f"offer_{p['product_id']}"):
                offer_price = st.number_input(
                    "Harga tawaran",
                    min_value=0,
                    step=1000,
                    key=p["product_id"]
                )
                submit = st.form_submit_button("Ajukan Tawaran")

                if submit:
                    new_offer = pd.DataFrame([{
                        "product_id": p["product_id"],
                        "product_name": p["product_name"],
                        "buyer": username,
                        "offer_price": offer_price,
                        "status": "Menunggu"
                    }])

                    offers = pd.concat([offers, new_offer], ignore_index=True)
                    offers.to_csv(OFFER_FILE, index=False)

                    st.success("Tawaran dikirim!")

# =====================================
# 🧺 KERANJANG
# =====================================
elif menu == "Keranjang":
    cart_page(username)

# =====================================
# 📩 TAWARAN SAYA
# =====================================
elif menu == "Tawaran Saya":

    st.header("📨 Tawaran Saya")

    my_offers = offers[offers["buyer"] == username]

    if my_offers.empty:
        st.info("Belum ada tawaran")
    else:
        st.dataframe(my_offers)

# =====================================
# 🛠 ADMIN SAJA
# =====================================
elif menu == "Admin — Kelola Tawaran":

    st.header("📥 Semua Tawaran Masuk")

    pending = offers[offers["status"] == "Menunggu"]

    for i, off in pending.iterrows():

        st.subheader(off["product_name"])
        st.write("Pembeli:", off["buyer"])
        st.write("Harga tawar:", f"Rp {int(off['offer_price']):,}")

        col1, col2 = st.columns(2)

        if col1.button("Terima", key=f"acc_{i}"):
            offers.loc[i, "status"] = "Diterima"
            offers.to_csv(OFFER_FILE, index=False)
            st.success("Tawaran diterima!")

        if col2.button("Tolak", key=f"rej_{i}"):
            offers.loc[i, "status"] = "Ditolak"
            offers.to_csv(OFFER_FILE, index=False)
            st.warning("Tawaran ditolak")
