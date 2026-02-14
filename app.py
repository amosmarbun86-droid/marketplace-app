# =====================================================
# MARKETPLACE TAWAR PRO - FINAL VERSION (NO ERROR)
# Full Professional Marketplace System
# =====================================================

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Marketplace Tawar Pro", layout="wide", page_icon="🛒")

# =====================================================
# FILE CONFIG
# =====================================================
USER_FILE = "users.csv"
PRODUCT_FILE = "products.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"
IMAGE_FOLDER = "images"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

# =====================================================
# INIT FILE FUNCTION
# =====================================================
def init_file(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_file(USER_FILE, ["username","password","role"])
init_file(PRODUCT_FILE, ["product_id","product_name","price","image","discount","best_seller","active"])
init_file(CART_FILE, ["user","product_id","product_name","price","qty","image"])
init_file(ORDER_FILE, ["order_id","user","product","price","qty","total","date"])

# =====================================================
# CREATE DEFAULT ADMIN
# =====================================================
users = pd.read_csv(USER_FILE)
if "admin" not in users.username.values:
    admin = pd.DataFrame([{
        "username":"admin",
        "password":"admin123",
        "role":"admin"
    }])
    users = pd.concat([users, admin], ignore_index=True)
    users.to_csv(USER_FILE, index=False)

# =====================================================
# CSS STYLE
# =====================================================
st.markdown("""
<style>
.stApp {background-color:#f1f3f6}
.card {
 background:white;
 padding:10px;
 border-radius:10px;
 border:1px solid #ddd;
 transition:0.3s;
}
.card:hover {
 box-shadow:0 4px 15px rgba(0,0,0,0.15);
 transform:translateY(-3px);
}
.price {color:#03ac0e;font-weight:bold;font-size:18px}
.oldprice {text-decoration:line-through;color:gray}
.badge {background:red;color:white;padding:2px 6px;border-radius:5px;font-size:11px}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION
# =====================================================
if "user" not in st.session_state:
    st.session_state.user = None

if "role" not in st.session_state:
    st.session_state.role = None

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            users = pd.read_csv(USER_FILE)
            match = users[(users.username==username)&(users.password==password)]

            if not match.empty:
                st.session_state.user = username
                st.session_state.role = match.iloc[0].role
                st.rerun()
            else:
                st.error("Username atau password salah")

    with tab2:
        new_user = st.text_input("Username baru")
        new_pass = st.text_input("Password baru", type="password")

        if st.button("Register"):
            users = pd.read_csv(USER_FILE)

            if new_user in users.username.values:
                st.warning("Username sudah ada")
            else:
                users = pd.concat([users, pd.DataFrame([{
                    "username":new_user,
                    "password":new_pass,
                    "role":"buyer"
                }])], ignore_index=True)

                users.to_csv(USER_FILE, index=False)
                st.success("Akun berhasil dibuat")


# =====================================================
# STOP IF NOT LOGIN
# =====================================================
if st.session_state.user is None:
    login_page()
    st.stop()

user = st.session_state.user
role = st.session_state.role

# =====================================================
# LOAD DATA
# =====================================================
products = pd.read_csv(PRODUCT_FILE)
cart = pd.read_csv(CART_FILE)
orders = pd.read_csv(ORDER_FILE)

# =====================================================
# SIDEBAR
# =====================================================
menu = ["Katalog"]

if role == "buyer":
    menu += ["Keranjang", "Checkout", "Riwayat"]

if role == "admin":
    menu += ["Admin Produk", "Dashboard"]

choice = st.sidebar.radio("Menu", menu)

if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# =====================================================
# FUNCTIONS
# =====================================================
def add_cart(product):

    global cart

    exist = cart[(cart.user==user)&(cart.product_id==product.product_id)]

    if not exist.empty:
        cart.loc[exist.index, "qty"] += 1
    else:
        cart = pd.concat([cart, pd.DataFrame([{
            "user":user,
            "product_id":product.product_id,
            "product_name":product.product_name,
            "price":product.price,
            "qty":1,
            "image":product.image
        }])], ignore_index=True)

    cart.to_csv(CART_FILE, index=False)


def remove_cart(index):

    global cart

    cart = cart.drop(index)
    cart.to_csv(CART_FILE, index=False)


# =====================================================
# KATALOG
# =====================================================
if choice == "Katalog":

    search = st.text_input("🔍 Cari produk")

    view = products.copy()

    if search:
        view = view[view.product_name.str.contains(search, case=False, na=False)]

    cols = st.columns(5)

    for i, product in view.iterrows():

        with cols[i % 5]:

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            image = product.image if pd.notna(product.image) and product.image != "" else "https://via.placeholder.com/150"

            st.image(image)

            st.write(product.product_name)

            if product.best_seller:
                st.markdown("<span class='badge'>Best Seller</span>", unsafe_allow_html=True)

            if product.discount > 0:
                new_price = int(product.price * (1 - product.discount/100))
                st.markdown(f"<div class='price'>Rp {new_price:,}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='oldprice'>Rp {product.price:,}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='price'>Rp {product.price:,}</div>", unsafe_allow_html=True)

            if role == "buyer":
                if st.button("Tambah", key=f"add{i}"):
                    add_cart(product)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# =====================================================
# CART
# =====================================================
elif choice == "Keranjang":

    my_cart = cart[cart.user==user]

    total = 0

    for i, row in my_cart.iterrows():

        col1, col2, col3, col4 = st.columns([1,3,2,1])

        with col1:
            st.image(row.image, width=60)

        with col2:
            st.write(row.product_name)
            st.write(f"Qty: {row.qty}")

        with col3:
            subtotal = row.price * row.qty
            total += subtotal
            st.write(f"Rp {subtotal:,}")

        with col4:
            if st.button("❌", key=f"del{i}"):
                remove_cart(i)
                st.rerun()

    st.divider()

    st.subheader(f"Total: Rp {total:,}")


# =====================================================
# CHECKOUT
# =====================================================
elif choice == "Checkout":

    my_cart = cart[cart.user==user]

    total = (my_cart.price * my_cart.qty).sum()

    st.subheader(f"Total bayar: Rp {total:,}")

    if st.button("Bayar sekarang"):

        new_orders = []

        for _, row in my_cart.iterrows():

            new_orders.append({
                "order_id": len(orders)+1,
                "user": user,
                "product": row.product_name,
                "price": row.price,
                "qty": row.qty,
                "total": row.price*row.qty,
                "date": datetime.now()
            })

        orders = pd.concat([orders, pd.DataFrame(new_orders)], ignore_index=True)

        orders.to_csv(ORDER_FILE, index=False)

        cart = cart[cart.user != user]
        cart.to_csv(CART_FILE, index=False)

        st.success("Pembayaran berhasil")


# =====================================================
# RIWAYAT
# =====================================================
elif choice == "Riwayat":

    my_orders = orders[orders.user==user]

    st.dataframe(my_orders)


# =====================================================
# ADMIN PRODUK
# =====================================================
elif choice == "Admin Produk":

    name = st.text_input("Nama produk")
    price = st.number_input("Harga")
    discount = st.slider("Diskon", 0, 90)
    best = st.checkbox("Best Seller")

    file = st.file_uploader("Upload gambar", type=["png","jpg","jpeg"])

    if st.button("Tambah produk"):

        image_path = ""

        if file:
            image_path = os.path.join(IMAGE_FOLDER, file.name)
            with open(image_path, "wb") as f:
                f.write(file.getbuffer())

        products = pd.concat([products, pd.DataFrame([{
            "product_id": len(products)+1,
            "product_name": name,
            "price": price,
            "image": image_path,
            "discount": discount,
            "best_seller": best,
            "active": True
        }])], ignore_index=True)

        products.to_csv(PRODUCT_FILE, index=False)

        st.success("Produk berhasil ditambahkan")


# =====================================================
# DASHBOARD
# =====================================================
elif choice == "Dashboard":

    st.metric("Total Produk", len(products))
    st.metric("Total Transaksi", len(orders))

    if not orders.empty:
        chart = orders.groupby("product").total.sum()
        st.bar_chart(chart)
