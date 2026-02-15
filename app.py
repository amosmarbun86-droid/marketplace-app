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
# SECURITY
# =====================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_loading(msg="Memproses..."):
    with st.spinner(msg):
        time.sleep(1)

# =====================================================
# STYLE
# =====================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {font-family: 'Poppins', sans-serif;}
.stApp {
background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)),
url("https://images.unsplash.com/photo-1505751172876-fa1923c5c528");
background-size: cover;
background-attachment: fixed;
}
.navbar {
background: linear-gradient(90deg,#d32f2f,#ff1744);
padding:15px;
border-radius:20px;
color:white;
text-align:center;
font-weight:700;
margin-bottom:20px;
}
.card {
background: rgba(255,255,255,0.95);
padding:18px;
border-radius:18px;
box-shadow:0 6px 20px rgba(0,0,0,0.2);
transition:0.3s;
margin-bottom:20px;
}
.card:hover {
transform:translateY(-8px) scale(1.02);
box-shadow:0 15px 40px rgba(0,0,0,0.4);
}
.price {color:#d32f2f;font-weight:600;font-size:18px;}
.stButton>button {
width:100%;border-radius:12px;padding:12px;
background:linear-gradient(90deg,#d32f2f,#ff1744);
color:white;border:none;
}
.bottom-nav {
position:fixed;bottom:0;left:0;right:0;
background:white;padding:10px;
display:flex;justify-content:space-around;
box-shadow:0 -5px 20px rgba(0,0,0,0.3);
}
.block-container {padding-bottom:100px;}
</style>
""", unsafe_allow_html=True)

# =====================================================
# FILE SETUP
# =====================================================
USER_FILE="users.csv"
PRODUCT_FILE="products.csv"
CART_FILE="cart.csv"
ORDER_FILE="orders.csv"

def init_file(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file,index=False)

init_file(USER_FILE,["username","password","role"])
init_file(PRODUCT_FILE,[
    "product_id","product_name","category",
    "price","stock","image_url","rating","seller"
])
init_file(CART_FILE,[
    "user","product_id","product_name",
    "price","qty","seller"
])
init_file(ORDER_FILE,[
    "order_id","user","product","total","seller","admin_fee"
])

# =====================================================
# SEED 100 PRODUK
# =====================================================
def seed_products():
    products=pd.read_csv(PRODUCT_FILE)
    if len(products)>=100: return

    categories=["Obat Umum","Obat Anak","Vitamin",
                "Obat Flu","Antibiotik",
                "Herbal","Alat Kesehatan"]

    names=["Paracetamol","Ibuprofen","Vitamin C",
           "Amoxicillin","OBH","Panadol",
           "Bodrex","Promag","Antangin",
           "Imboost","Betadine","Sanmol"]

    data=[]
    for i in range(1,101):
        data.append({
            "product_id":i,
            "product_name":random.choice(names)+f" {i}",
            "category":random.choice(categories),
            "price":random.randint(10000,150000),
            "stock":random.randint(5,100),
            "image_url":"",
            "rating":round(random.uniform(3.5,5.0),1),
            "seller":"admin"
        })
    pd.DataFrame(data).to_csv(PRODUCT_FILE,index=False)

seed_products()

# =====================================================
# ADMIN DEFAULT
# =====================================================
users=pd.read_csv(USER_FILE)
if "admin" not in users.username.values:
    users=pd.concat([users,pd.DataFrame([{
        "username":"admin",
        "password":hash_password("admin123"),
        "role":"admin"
    }])])
    users.to_csv(USER_FILE,index=False)

# =====================================================
# SESSION
# =====================================================
if "user" not in st.session_state:
    st.session_state.user=None
if "role" not in st.session_state:
    st.session_state.role=None
if "page" not in st.session_state:
    st.session_state.page="Katalog"

# =====================================================
# LOGIN
# =====================================================
def login():
    tab1,tab2=st.tabs(["Login","Register"])
    users=pd.read_csv(USER_FILE)

    with tab1:
        u=st.text_input("Username")
        p=st.text_input("Password",type="password")
        if st.button("Login"):
            match=users[(users.username==u)&
                        (users.password==hash_password(p))]
            if not match.empty:
                show_loading("Login berhasil...")
                st.session_state.user=u
                st.session_state.role=match.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Login gagal")

    with tab2:
        u=st.text_input("Username Baru")
        p=st.text_input("Password Baru",type="password")
        role=st.selectbox("Role",["buyer","seller"])
        if st.button("Register"):
            new=pd.DataFrame([{
                "username":u,
                "password":hash_password(p),
                "role":role
            }])
            users=pd.concat([users,new])
            users.to_csv(USER_FILE,index=False)
            st.success("Berhasil daftar")

if st.session_state.user is None:
    login()
    st.stop()

# =====================================================
# LOAD DATA
# =====================================================
products=pd.read_csv(PRODUCT_FILE)
cart=pd.read_csv(CART_FILE)
orders=pd.read_csv(ORDER_FILE)

user=st.session_state.user
role=st.session_state.role

st.markdown(f"<div class='navbar'>🚑 Toko Emergency | {user}</div>",unsafe_allow_html=True)

# =====================================================
# KATALOG
# =====================================================
if st.session_state.page=="Katalog":

    for i,p in products.iterrows():
        st.markdown("<div class='card'>",unsafe_allow_html=True)

        if p.image_url and os.path.exists(p.image_url):
            st.image(p.image_url,use_column_width=True)
        else:
            st.image("https://images.unsplash.com/photo-1580281657527-47b4c09841b4",
                     use_column_width=True)

        st.write(f"**{p.product_name}**")
        st.caption(f"Kategori: {p.category}")
        st.caption(f"Stok: {int(p.stock)}")
        st.write("⭐"*int(round(p.rating)))
        st.markdown(f"<div class='price'>Rp {int(p.price):,}</div>",unsafe_allow_html=True)

        if role=="buyer":
            if p.stock>0:
                if st.button("Tambah ke Keranjang",key=i):
                    products.loc[products.product_id==p.product_id,"stock"]-=1
                    products.to_csv(PRODUCT_FILE,index=False)
                    show_loading("Ditambahkan...")
                    st.rerun()
            else:
                st.error("Stok Habis")

        st.markdown("</div>",unsafe_allow_html=True)

# =====================================================
# DASHBOARD ADMIN
# =====================================================
if role=="admin":
    if st.button("📊 Dashboard Admin"):
        st.subheader("Statistik Marketplace")
        st.metric("Total Produk",len(products))
        st.metric("Total Stok",products.stock.sum())
        st.metric("Total Order",len(orders))
        st.dataframe(products)

# =====================================================
# BOTTOM NAV
# =====================================================
st.markdown("<div class='bottom-nav'>",unsafe_allow_html=True)
col1,col2=st.columns(2)

if col1.button("🏠 Home"):
    st.session_state.page="Katalog"
    st.rerun()

if col2.button("Logout"):
    st.session_state.user=None
    st.session_state.role=None
    st.rerun()

st.markdown("</div>",unsafe_allow_html=True)
