import streamlit as st
import pandas as pd
import os
from auth_cart import login_page

# ==============================
# CONFIG
# ==============================
st.set_page_config(
    page_title="Marketplace Tawar",
    page_icon="🛒",
    layout="wide"
)

# ==============================
# CSS TOKOPEDIA PRO
# ==============================
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #f5f5f5;
}

/* Topbar */
.topbar {
    background: #03AC0E;
    padding: 15px 25px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
}

/* Search */
.search-box {
    background: white;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin-bottom: 20px;
}

/* Card */
.card {
    background: white;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #e0e0e0;
    transition: 0.2s;
}

.card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.1);
    transform: translateY(-4px);
}

/* Price */
.price {
    color: #03AC0E;
    font-weight: bold;
    font-size: 18px;
}

/* Button */
.stButton>button {
    background-color: #03AC0E;
    color: white;
    border-radius: 8px;
    border: none;
    width: 100%;
}

.stButton>button:hover {
    background-color: #02930c;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: white;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# SESSION
# ==============================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

# ==============================
# LOGIN
# ==============================
if st.session_state.user is None:
    login_page()
    st.stop()

user = st.session_state.user
role = st.session_state.role

# ==============================
# FILE SETUP
# ==============================
PRODUCT_FILE = "products.csv"
OFFER_FILE = "offers.csv"

if not os.path.exists(OFFER_FILE):
    pd.DataFrame(
        columns=["product_id","product_name","buyer","offer_price"]
    ).to_csv(OFFER_FILE, index=False)

products = pd.read_csv(PRODUCT_FILE)
offers = pd.read_csv(OFFER_FILE)

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:

    st.write(f"👤 {user}")
    st.write(f"Role: {role}")

    menu = ["Katalog"]

    if role == "buyer":
        menu.append("Tawaran Saya")

    if role == "admin":
        menu.append("Admin Panel")

    choice = st.radio("Menu", menu)

    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

# ==============================
# TOPBAR
# ==============================
st.markdown(f"""
<div class="topbar">
<h3>🛒 Marketplace Tawar</h3>
</div>
""", unsafe_allow_html=True)

# ==============================
# SEARCH
# ==============================
st.markdown('<div class="search-box">', unsafe_allow_html=True)

search = st.text_input("🔍 Cari produk")

st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# FILTER DATA
# ==============================
filtered = products.copy()

if "is_active" in filtered.columns:
    filtered = filtered[filtered["is_active"] == True]

if search:
    filtered = filtered[
        filtered["product_name"].str.contains(search, case=False)
    ]

# ==============================
# KATALOG
# ==============================
if choice == "Katalog":

    cols = st.columns(5)

    for i, p in filtered.iterrows():

        with cols[i % 5]:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            img = f"https://source.unsplash.com/300x200/?{p['product_name']}"
            st.image(img)

            st.write(p["product_name"])

            st.markdown(
                f'<div class="price">Rp {int(p["price"]):,}</div>',
                unsafe_allow_html=True
            )

            if role == "buyer":

                if st.button("Tambah", key=f"cart{i}"):
                    st.success("Masuk keranjang")

                with st.form(f"offer{i}"):

                    offer = st.number_input(
                        "Harga tawar",
                        0,
                        key=f"offer_input{i}"
                    )

                    if st.form_submit_button("Kirim Tawaran"):

                        new = pd.DataFrame([{
                            "product_id": p["product_id"],
                            "product_name": p["product_name"],
                            "buyer": user,
                            "offer_price": offer
                        }])

                        offers = pd.concat(
                            [offers, new],
                            ignore_index=True
                        )

                        offers.to_csv(OFFER_FILE, index=False)

                        st.success("Tawaran dikirim")

            st.markdown('</div>', unsafe_allow_html=True)

# ==============================
# TAWARAN BUYER
# ==============================
elif choice == "Tawaran Saya":

    my = offers[offers["buyer"] == user]

    if my.empty:
        st.info("Belum ada tawaran")
    else:
        st.dataframe(my, use_container_width=True)

# ==============================
# ADMIN PANEL
# ==============================
elif choice == "Admin Panel":

    if role != "admin":
        st.error("Akses ditolak")
        st.stop()

    col1, col2 = st.columns(2)

    col1.metric("Total Produk", len(products))
    col2.metric("Total Tawaran", len(offers))

    st.subheader("Data Produk")
    st.dataframe(products, use_container_width=True)

    st.subheader("Data Tawaran")
    st.dataframe(offers, use_container_width=True)
