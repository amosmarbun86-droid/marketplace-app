import streamlit as st
import pandas as pd
import os
import random

# =====================================
# CONFIG
# =====================================
st.set_page_config(
    page_title="Toko Emergency",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================
# STYLE (MOBILE APP STYLE)
# =====================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

/* Navbar */
.navbar {
    background: linear-gradient(90deg,#d32f2f,#ff1744);
    padding: 14px;
    border-radius: 12px;
    color: white;
    text-align:center;
    font-size:18px;
    font-weight:600;
    margin-bottom:15px;
}

/* Card */
.card {
    background:white;
    padding:15px;
    border-radius:12px;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
    margin-bottom:15px;
}

.price {
    color:#d32f2f;
    font-size:18px;
    font-weight:600;
}

.stButton>button {
    width:100%;
    padding:12px;
    font-size:15px;
    border-radius:8px;
}

/* Bottom Navigation */
.bottom-nav {
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    background:white;
    display:flex;
    justify-content:space-around;
    padding:10px 0;
    box-shadow:0 -2px 10px rgba(0,0,0,0.1);
    z-index:999;
}

.bottom-nav button {
    background:none;
    border:none;
    font-size:14px;
    font-weight:600;
}

/* Safe bottom space */
.main {
    padding-bottom:80px;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# FILE SETUP
# =====================================
USER_FILE = "users.csv"
PRODUCT_FILE = "products.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"

def init_file(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_file(USER_FILE, ["username","password","role"])
init_file(PRODUCT_FILE, [
    "product_id","product_name","price","image_url",
    "discount","best","category","rating","seller"
])
init_file(CART_FILE, ["user","product_id","product_name","price","qty","seller"])
init_file(ORDER_FILE, [
    "order_id","user","product","total","seller","admin_fee"
])

# Default admin
users = pd.read_csv(USER_FILE)
if "admin" not in users["username"].values:
    users = pd.concat([users,pd.DataFrame([{
        "username":"admin","password":"admin123","role":"admin"
    }])])
    users.to_csv(USER_FILE,index=False)

# =====================================
# SESSION
# =====================================
if "user" not in st.session_state:
    st.session_state.user=None
if "role" not in st.session_state:
    st.session_state.role=None
if "page" not in st.session_state:
    st.session_state.page="Katalog"

# =====================================
# LOGIN
# =====================================
def login():
    tab1, tab2 = st.tabs(["Login","Register"])
    users = pd.read_csv(USER_FILE)

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            match = users[(users.username==u)&(users.password==p)]
            if not match.empty:
                st.session_state.user=u
                st.session_state.role=match.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Login gagal")

    with tab2:
        u = st.text_input("Username baru")
        p = st.text_input("Password baru", type="password")
        role_option = st.selectbox("Daftar sebagai", ["buyer","seller"])
        if st.button("Register"):
            new = pd.DataFrame([{
                "username":u,"password":p,"role":role_option
            }])
            users = pd.concat([users,new])
            users.to_csv(USER_FILE,index=False)
            st.success("Berhasil daftar")

if st.session_state.user is None:
    login()
    st.stop()

# =====================================
# LOAD DATA
# =====================================
products = pd.read_csv(PRODUCT_FILE)
cart = pd.read_csv(CART_FILE)
orders = pd.read_csv(ORDER_FILE)

user = st.session_state.user
role = st.session_state.role

cart_count = cart[cart.user==user]["qty"].sum()

# =====================================
# NAVBAR
# =====================================
st.markdown(f"""
<div class="navbar">
🚑 Toko Emergency | 🛒 {int(cart_count)}
</div>
""", unsafe_allow_html=True)

# =====================================
# PAGE CONTENT
# =====================================
page = st.session_state.page

# =========================
# KATALOG
# =========================
if page=="Katalog":

    search = st.text_input("🔍 Cari Produk")

    filtered = products.copy()
    if search:
        filtered = filtered[filtered.product_name.str.contains(search, case=False)]

    for i,p in filtered.iterrows():

        st.markdown("<div class='card'>",unsafe_allow_html=True)

        if pd.notna(p.image_url) and os.path.exists(p.image_url):
            st.image(p.image_url, use_column_width=True)

        st.write(f"**{p.product_name}**")
        st.caption(f"Toko: {p.seller}")
        st.write("⭐"*int(round(p.rating)))
        st.markdown(f"<div class='price'>Rp {int(p.price):,}</div>",unsafe_allow_html=True)

        if role=="buyer":
            if st.button("Tambah ke Keranjang", key=i):
                new = pd.DataFrame([{
                    "user":user,
                    "product_id":p.product_id,
                    "product_name":p.product_name,
                    "price":p.price,
                    "qty":1,
                    "seller":p.seller
                }])
                cart = pd.concat([cart,new])
                cart.to_csv(CART_FILE,index=False)
                st.rerun()

        st.markdown("</div>",unsafe_allow_html=True)

# =========================
# KERANJANG
# =========================
elif page=="Keranjang":
    my = cart[cart.user==user]
    total = (my.price*my.qty).sum()

    for i,row in my.iterrows():
        st.markdown(f"""
        <div class='card'>
        <b>{row.product_name}</b><br>
        Qty: {row.qty}<br>
        Rp {int(row.price):,}
        </div>
        """, unsafe_allow_html=True)

    st.subheader(f"Total: Rp {int(total):,}")

# =========================
# CHECKOUT
# =========================
elif page=="Checkout":
    my = cart[cart.user==user]
    total = (my.price*my.qty).sum()
    admin_fee = total*0.05

    st.write("Komisi Admin 5%:", int(admin_fee))
    st.write("Total Bayar:", int(total))

    if st.button("Bayar Sekarang"):
        oid=len(orders)+1
        for i,row in my.iterrows():
            new = pd.DataFrame([{
                "order_id":oid,
                "user":user,
                "product":row.product_name,
                "total":row.price*row.qty,
                "seller":row.seller,
                "admin_fee":row.price*row.qty*0.05
            }])
            orders=pd.concat([orders,new])
        orders.to_csv(ORDER_FILE,index=False)
        cart=cart[cart.user!=user]
        cart.to_csv(CART_FILE,index=False)
        st.success("Checkout berhasil")

# =========================
# DASHBOARD ADMIN
# =========================
elif page=="Dashboard" and role=="admin":
    st.metric("Total Produk", len(products))
    st.metric("Total Order", len(orders))
    st.metric("Total Komisi", int(orders.admin_fee.sum()))

    st.download_button(
        "Download Laporan",
        orders.to_csv(index=False),
        file_name="laporan_toko_emergency.csv"
    )

# =====================================
# BOTTOM NAVIGATION
# =====================================
st.markdown("<div class='bottom-nav'>", unsafe_allow_html=True)

col1,col2,col3,col4 = st.columns(4)

if col1.button("🏠 Home"):
    st.session_state.page="Katalog"
    st.rerun()

if col2.button("🛒 Cart"):
    st.session_state.page="Keranjang"
    st.rerun()

if col3.button("💳 Checkout"):
    st.session_state.page="Checkout"
    st.rerun()

if role=="admin":
    if col4.button("📊 Admin"):
        st.session_state.page="Dashboard"
        st.rerun()
else:
    col4.write("")

st.markdown("</div>", unsafe_allow_html=True)
