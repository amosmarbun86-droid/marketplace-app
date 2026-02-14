import streamlit as st
import pandas as pd
import os
from auth_cart import *

st.set_page_config(page_title="Marketplace Premium", layout="wide")

# ===============================
# BACKGROUND + CSS PREMIUM
# ===============================
st.markdown("""
<style>

.stApp {
    background-image: url("https://images.unsplash.com/photo-1522199755839-a2bacb67c546");
    background-size: cover;
    background-attachment: fixed;
}

.block-container {
    background: rgba(255,255,255,0.9);
    padding: 2rem;
    border-radius: 20px;
}

.product-card {
    background: white;
    padding: 15px;
    border-radius: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    transition: 0.3s;
    text-align: center;
}

.product-card:hover {
    transform: translateY(-5px);
}

.stButton>button {
    background: linear-gradient(90deg,#667eea,#764ba2);
    color: white;
    border-radius: 12px;
    border: none;
}

</style>
""", unsafe_allow_html=True)

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
# SIDEBAR
# ===============================
with st.sidebar:
    st.markdown(f"### 👤 {username}")
    st.markdown(f"Role: **{role}**")

    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

menu = ["Katalog"]

if role == "buyer":
    menu += ["Keranjang", "Tawaran Saya"]

if role == "admin":
    menu += ["Admin - Produk", "Admin - Tawaran"]

choice = st.sidebar.selectbox("Menu", menu)

# ===============================
# KATALOG PREMIUM
# ===============================
if choice == "Katalog":

    st.title("🛍️ Marketplace Premium")

    active_products = products[products["is_active"] == True]

    cols = st.columns(3)

    for i, p in active_products.iterrows():
        with cols[i % 3]:

            st.markdown("<div class='product-card'>", unsafe_allow_html=True)

            # Kalau ada kolom image_url di CSV
            if "image_url" in products.columns:
                st.image(p["image_url"], use_container_width=True)

            st.subheader(p["product_name"])
            st.write(f"💰 Rp {int(p['price']):,}")

            if role == "buyer":

                if st.button("🛒 Tambah", key=f"c{p['product_id']}"):
                    st.success("Masuk keranjang")

                with st.form(f"f{p['product_id']}"):
                    offer = st.number_input("Tawar", 0)
                    if st.form_submit_button("Kirim Tawaran"):
                        new = pd.DataFrame([{
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "buyer": username,
                            "offer_price": offer
                        }])
                        offers = pd.concat([offers, new], ignore_index=True)
                        offers.to_csv(OFFER_FILE, index=False)
                        st.success("Tawaran dikirim")

            st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# BUYER MENU
# ===============================
elif choice == "Keranjang":
    if role != "buyer":
        st.error("Akses ditolak")
        st.stop()
    st.header("Keranjang Buyer")

elif choice == "Tawaran Saya":
    if role != "buyer":
        st.error("Akses ditolak")
        st.stop()
    my = offers[offers["buyer"] == username]
    st.dataframe(my, use_container_width=True)

# ===============================
# ADMIN MENU
# ===============================
elif choice == "Admin - Produk":
    if role != "admin":
        st.error("Akses ditolak")
        st.stop()
    st.dataframe(products, use_container_width=True)

elif choice == "Admin - Tawaran":
    if role != "admin":
        st.error("Akses ditolak")
        st.stop()
    st.dataframe(offers, use_container_width=True)
