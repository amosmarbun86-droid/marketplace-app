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
# SAFE STYLE (ANTI BOCOR CSS)
# =====================================================
st.markdown("""
<style>

body {
    background-color: #f5f7fa !important;
}

[data-testid="stAppViewContainer"] {
    background-color: #f5f7fa !important;
}

[data-testid="stHeader"] {
    background: transparent;
}

.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 14px 30px;
    z-index: 9999;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.nav-logo {
    font-weight: bold;
    font-size: 20px;
    color: #d32f2f;
}

.nav-right {
    display: flex;
    gap: 20px;
}

.block-container {
    margin-top: 100px;
}

.card {
    background: white;
    padding:18px;
    border-radius:16px;
    box-shadow:0 6px 20px rgba(0,0,0,0.08);
    margin-bottom:20px;
    transition:0.3s;
}

.card:hover {
    transform:translateY(-6px);
    box-shadow:0 14px 30px rgba(0,0,0,0.15);
}

.price {
    color:#d32f2f;
    font-weight:600;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SECURITY
# =====================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def show_loading(msg="Memproses..."):
    with st.spinner(msg):
        time.sleep(1)

# =====================================================
# FILE SETUP
# =====================================================
USER_FILE="users.csv"
PRODUCT_FILE="products.csv"
CART_FILE="cart.csv"

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

# =====================================================
# SEED 100 PRODUK
# =====================================================
def seed_products():
    products=pd.read_csv(PRODUCT_FILE)
    if len(products)>=100:
        return

    categories=["Obat Umum","Vitamin","Obat Anak",
                "Obat Flu","Herbal","Antibiotik"]

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
products["image_url"]=products["image_url"].fillna("")
cart=pd.read_csv(CART_FILE)

user=st.session_state.user
cart_count=len(cart[cart.user==user])

# =====================================================
# NAVBAR
# =====================================================
st.markdown(f"""
<div class="navbar">
    <div class="nav-logo">🚑 Toko Emergency</div>
    <div class="nav-right">
        🛒 {cart_count}
        👤 {user}
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# SEARCH
# =====================================================
search=st.text_input("🔍 Cari Produk")

if search:
    products=products[
        products["product_name"].str.contains(search,case=False,na=False)
    ]

# =====================================================
# GRID PRODUK
# =====================================================
cols=st.columns(3)

for idx,p in products.iterrows():
    col=cols[idx%3]
    with col:
        st.markdown("<div class='card'>",unsafe_allow_html=True)

        if p.image_url and os.path.exists(p.image_url):
            st.image(p.image_url,use_column_width=True)
        else:
            st.image("https://images.unsplash.com/photo-1580281657527-47b4c09841b4",
                     use_column_width=True)

        st.write(f"**{p.product_name}**")
        st.caption(p.category)
        st.write("⭐"*int(round(float(p.rating))))
        st.markdown(f"<div class='price'>Rp {int(p.price):,}</div>",
                    unsafe_allow_html=True)

        st.markdown("</div>",unsafe_allow_html=True)
