import streamlit as st
import pandas as pd
import os
import random
import hashlib
import time

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Toko Emergency",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================================
# UTILS
# =====================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_loading(msg="Memproses..."):
    with st.spinner(msg):
        time.sleep(1)

def safe_read_csv(file, columns):
    if not os.path.exists(file):
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df
    try:
        df = pd.read_csv(file)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns]
    except:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

# =====================================================
# FILE SETUP
# =====================================================
USER_FILE = "users.csv"
PRODUCT_FILE = "products.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"

USER_COLS = ["username","password","role"]
PRODUCT_COLS = [
    "product_id","product_name","category",
    "price","stock","image_url","rating","seller"
]
CART_COLS = [
    "user","product_id","product_name",
    "price","qty","seller"
]
ORDER_COLS = [
    "order_id","user","product","total","seller","admin_fee"
]

users = safe_read_csv(USER_FILE, USER_COLS)
products = safe_read_csv(PRODUCT_FILE, PRODUCT_COLS)
cart = safe_read_csv(CART_FILE, CART_COLS)
orders = safe_read_csv(ORDER_FILE, ORDER_COLS)

# Fix NaN image_url
products["image_url"] = products["image_url"].fillna("")

# =====================================================
# SEED 100 PRODUK OTOMATIS
# =====================================================
def seed_products():
    global products
    if len(products) >= 100:
        return

    categories = ["Obat Umum","Vitamin","Antibiotik",
                  "Obat Flu","Obat Anak",
                  "Herbal","Alat Kesehatan"]

    names = [
        "Paracetamol","Ibuprofen","Amoxicillin",
        "Vitamin C","Panadol","Bodrex",
        "Promag","Antangin","Sanmol",
        "Imboost","Betadine","OBH"
    ]

    data = []
    for i in range(1,101):
        data.append({
            "product_id": i,
            "product_name": random.choice(names)+f" {i}",
            "category": random.choice(categories),
            "price": random.randint(10000,150000),
            "stock": random.randint(5,100),
            "image_url": "",
            "rating": round(random.uniform(3.5,5.0),1),
            "seller": "admin"
        })

    products = pd.DataFrame(data)
    products.to_csv(PRODUCT_FILE,index=False)

seed_products()
products = pd.read_csv(PRODUCT_FILE)
products["image_url"] = products["image_url"].fillna("")

# =====================================================
# ADMIN DEFAULT
# =====================================================
if "admin" not in users["username"].values:
    users = pd.concat([users,pd.DataFrame([{
        "username":"admin",
        "password":hash_password("admin123"),
        "role":"admin"
    }])])
    users.to_csv(USER_FILE,index=False)

# =====================================================
# SESSION
# =====================================================
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# =====================================================
# LOGIN
# =====================================================
def login():
    tab1, tab2 = st.tabs(["Login","Register"])
    users = pd.read_csv(USER_FILE)

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            match = users[
                (users.username==u) &
                (users.password==hash_password(p))
            ]
            if not match.empty:
                show_loading("Login berhasil...")
                st.session_state.user=u
                st.session_state.role=match.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Login gagal")

    with tab2:
        u = st.text_input("Username Baru")
        p = st.text_input("Password Baru", type="password")
        role = st.selectbox("Role",["buyer","seller"])
        if st.button("Register"):
            new = pd.DataFrame([{
                "username":u,
                "password":hash_password(p),
                "role":role
            }])
            users = pd.concat([users,new])
            users.to_csv(USER_FILE,index=False)
            st.success("Berhasil daftar")

if st.session_state.user is None:
    login()
    st.stop()

# =====================================================
# UI
# =====================================================
st.markdown("""
<style>
.stApp {background:#f5f7fa;}
.card {
background:white;
padding:18px;
border-radius:16px;
box-shadow:0 6px 18px rgba(0,0,0,0.1);
margin-bottom:20px;
transition:0.3s;
}
.card:hover {
transform:translateY(-6px);
box-shadow:0 12px 30px rgba(0,0,0,0.2);
}
.price {color:#d32f2f;font-weight:600;}
</style>
""", unsafe_allow_html=True)

st.title("🚑 Toko Emergency")

# =====================================================
# KATALOG
# =====================================================
for i,p in products.iterrows():
    st.markdown("<div class='card'>",unsafe_allow_html=True)

    if isinstance(p.image_url,str) and p.image_url and os.path.exists(p.image_url):
        st.image(p.image_url,use_column_width=True)
    else:
        st.image("https://images.unsplash.com/photo-1580281657527-47b4c09841b4",
                 use_column_width=True)

    st.write(f"**{p.product_name}**")
    st.caption(f"Kategori: {p.category}")
    st.caption(f"Stok: {int(p.stock)}")
    st.write("⭐"*int(round(float(p.rating))))
    st.markdown(f"<div class='price'>Rp {int(p.price):,}</div>",
                unsafe_allow_html=True)

    st.markdown("</div>",unsafe_allow_html=True)

# =====================================================
# LOGOUT
# =====================================================
if st.button("Logout"):
    st.session_state.user=None
    st.session_state.role=None
    st.rerun()
