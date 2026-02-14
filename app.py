import streamlit as st
import pandas as pd
import os
from auth_cart import *

st.set_page_config(page_title="Luxury Marketplace", layout="wide", page_icon="💎")

# ==============================
# CSS LUXURY
# ==============================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg,#141E30,#243B55);
}

.block-container {
    background: rgba(255,255,255,0.95);
    padding: 35px;
    border-radius: 25px;
}

/* HERO */
.hero {
    background: linear-gradient(90deg,#8E2DE2,#4A00E0);
    padding: 50px;
    border-radius: 25px;
    color: white;
    text-align: center;
    margin-bottom: 40px;
}

/* CARD */
.card {
    background: white;
    border-radius: 20px;
    padding: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    transition: 0.3s;
}

.card:hover {
    transform: translateY(-12px);
    box-shadow: 0 20px 45px rgba(0,0,0,0.3);
}

.stButton>button {
    background: linear-gradient(90deg,#ff512f,#dd2476);
    color: white;
    border-radius: 15px;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(#8E2DE2,#4A00E0);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# LOGIN CHECK
# ==============================
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

if st.session_state.user is None:
    login_page()
    st.stop()

user = st.session_state.user
role = st.session_state.role

# ==============================
# LOAD DATA
# ==============================
products = pd.read_csv("products.csv")

if not os.path.exists("offers.csv"):
    pd.DataFrame(
        columns=["product_id","product_name","buyer","offer_price"]
    ).to_csv("offers.csv", index=False)

offers = pd.read_csv("offers.csv")

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:

    st.markdown(f"## 👤 {user}")
    st.markdown(f"Role: **{role}**")

    menu = ["🏠 Katalog"]

    if role == "buyer":
        menu.append("💰 Tawaran Saya")

    if role == "admin":
        menu.append("📊 Dashboard Admin")

    choice = st.radio("Menu", menu)

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

# ==============================
# HERO
# ==============================
st.markdown("""
<div class="hero">
<h1>💎 Luxury Marketplace</h1>
<p>Pengalaman belanja modern dan eksklusif</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# SEARCH & FILTER
# ==============================
col1, col2 = st.columns([3,1])

with col1:
    search = st.text_input("🔍 Cari produk")

with col2:
    max_price = int(products["price"].max())
    price_filter = st.slider("Filter harga", 0, max_price, max_price)

filtered = products[
    (products["is_active"] == True) &
    (products["price"] <= price_filter)
]

if search:
    filtered = filtered[
        filtered["product_name"].str.contains(search, case=False)
    ]

# ==============================
# KATALOG
# ==============================
if choice == "🏠 Katalog":

    cols = st.columns(4)

    for i, p in filtered.iterrows():

        with cols[i % 4]:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            img = f"https://source.unsplash.com/600x400/?{p['product_name']}"
            st.image(img)

            st.subheader(p["product_name"])
            st.write(f"💰 Rp {int(p['price']):,}")

            if role == "buyer":

                if st.button("🛒 Tambah", key=f"cart{i}"):
                    st.success("Ditambahkan")

                with st.form(f"offer{i}"):
                    offer = st.number_input("Tawar", 0)
                    if st.form_submit_button("Kirim Tawaran"):

                        new = pd.DataFrame([{
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "buyer": user,
                            "offer_price": offer
                        }])

                        offers = pd.concat([offers, new], ignore_index=True)
                        offers.to_csv("offers.csv", index=False)

                        st.success("Tawaran dikirim")

            st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# BUYER PAGE
# ==============================
elif choice == "💰 Tawaran Saya":

    my = offers[offers["buyer"] == user]
    st.dataframe(my, use_container_width=True)

# ==============================
# ADMIN DASHBOARD
# ==============================
elif choice == "📊 Dashboard Admin":

    if role != "admin":
        st.error("Akses ditolak")
        st.stop()

    total_produk = len(products)
    total_tawaran = len(offers)

    col1, col2 = st.columns(2)

    col1.metric("Total Produk", total_produk)
    col2.metric("Total Tawaran", total_tawaran)

    st.subheader("Data Produk")
    st.dataframe(products, use_container_width=True)

    st.subheader("Data Tawaran")
    st.dataframe(offers, use_container_width=True)
