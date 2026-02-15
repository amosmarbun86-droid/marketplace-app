import streamlit as st
import pandas as pd
import os
import random
import hashlib
import uuid

st.set_page_config(page_title="Toko Emergency", page_icon="🚑", layout="wide")

# ==============================
# SUPER MOBILE STYLE
# ==============================
st.markdown("""
<style>
html, body {
    background:#f5f5f5 !important;
    margin:0 !important;
    padding:0 !important;
}
[data-testid="stAppViewContainer"] {
    background:#f5f5f5 !important;
}
.block-container {
    max-width:100% !important;
    padding:70px 10px 100px 10px !important;
}

/* NAVBAR */
.navbar {
    position:fixed;
    top:0; left:0; right:0;
    background:white;
    padding:10px 15px;
    display:flex;
    justify-content:space-between;
    align-items:center;
    box-shadow:0 3px 12px rgba(0,0,0,0.08);
    z-index:9999;
}
.logo {
    font-size:16px;
    font-weight:700;
    color:#ee4d2d;
}

/* HERO */
.hero {
    background:linear-gradient(135deg,#ff6a00,#ee0979);
    padding:30px 20px;
    border-radius:0;
    color:white;
    margin-left:-10px;
    margin-right:-10px;
    margin-bottom:20px;
}
.hero h1 {
    font-size:20px;
    margin-bottom:8px;
}
.hero p {
    font-size:13px;
}

/* CARD */
.card {
    background:white;
    padding:10px;
    border-radius:12px;
    box-shadow:0 3px 12px rgba(0,0,0,0.08);
    margin-bottom:15px;
}
.price {
    color:#ee4d2d;
    font-weight:bold;
    font-size:14px;
}
.old-price {
    text-decoration:line-through;
    color:grey;
    font-size:11px;
}
.discount {
    background:#ee4d2d;
    color:white;
    padding:2px 4px;
    font-size:9px;
    border-radius:5px;
}
.rating {
    color:#ffa41c;
    font-size:11px;
}

/* FLOATING CART */
.floating-cart {
    position:fixed;
    bottom:20px;
    right:20px;
    background:#ee4d2d;
    color:white;
    border-radius:50%;
    width:55px;
    height:55px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:22px;
    box-shadow:0 6px 18px rgba(0,0,0,0.2);
    z-index:9999;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# FILE SETUP (SAFE)
# ==============================
USER_FILE="users.csv"
PRODUCT_FILE="products.csv"
CART_FILE="cart.csv"

def init_file(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file,index=False)

init_file(USER_FILE,["username","password"])
init_file(PRODUCT_FILE,["id","name","price","discount"])
init_file(CART_FILE,["user","product_id","name","price","qty"])

# ==============================
# HASH
# ==============================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ==============================
# SEED PRODUCT (AUTO SAFE)
# ==============================
products=pd.read_csv(PRODUCT_FILE)
if products.empty:
    data=[]
    for i in range(1,41):
        price=random.randint(20000,100000)
        discount=random.choice([0,10,20,30])
        data.append({
            "id":i,
            "name":f"Produk Kesehatan {i}",
            "price":price,
            "discount":discount
        })
    pd.DataFrame(data).to_csv(PRODUCT_FILE,index=False)
    products=pd.read_csv(PRODUCT_FILE)

# ==============================
# SESSION
# ==============================
if "user" not in st.session_state:
    st.session_state.user=None

# ==============================
# LOGIN SYSTEM
# ==============================
def login():
    tab1,tab2=st.tabs(["Login","Register"])
    users=pd.read_csv(USER_FILE)

    with tab1:
        u=st.text_input("Username")
        p=st.text_input("Password",type="password")
        if st.button("Login"):
            match=users[(users.username==u)&(users.password==hash_password(p))]
            if not match.empty:
                st.session_state.user=u
                st.rerun()
            else:
                st.error("Login gagal")

    with tab2:
        u=st.text_input("Username Baru")
        p=st.text_input("Password Baru",type="password")
        new=pd.DataFrame([{"username":u,"password":hash_password(p)}])
        users=pd.concat([users,new])
        users.to_csv(USER_FILE,index=False)
        st.success("Berhasil daftar")

if st.session_state.user is None:
    login()
    st.stop()

user=st.session_state.user
cart=pd.read_csv(CART_FILE)

# ==============================
# NAVBAR
# ==============================
cart_count=len(cart[cart.user==user])

st.markdown(f"""
<div class="navbar">
<div class="logo">🚑 Toko Emergency</div>
<div>🛒 {cart_count}</div>
</div>
""", unsafe_allow_html=True)

# ==============================
# HERO
# ==============================
st.markdown("""
<div class="hero">
<h1>Promo Spesial Hari Ini 🔥</h1>
<p>Dapatkan diskon hingga 30% untuk produk pilihan</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# PRODUK GRID 2 KOLOM
# ==============================
products=pd.read_csv(PRODUCT_FILE)
cols=st.columns(2)

for idx,p in products.iterrows():
    col=cols[idx%2]
    with col:
        st.markdown("<div class='card'>",unsafe_allow_html=True)

        product_name=p["name"] if "name" in products.columns else "Produk"
        product_price=p["price"] if "price" in products.columns else 0
        product_discount=p["discount"] if "discount" in products.columns else 0

        st.image("https://images.unsplash.com/photo-1580281657527-47b4c09841b4",use_column_width=True)
        st.write(f"**{product_name}**")

        if product_discount>0:
            new_price=int(product_price*(100-product_discount)/100)
            st.markdown(
                f"<span class='old-price'>Rp {product_price:,}</span> "
                f"<span class='discount'>-{product_discount}%</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='price'>Rp {new_price:,}</div>",unsafe_allow_html=True)
            price_used=new_price
        else:
            st.markdown(f"<div class='price'>Rp {product_price:,}</div>",unsafe_allow_html=True)
            price_used=product_price

        st.markdown("<div class='rating'>★★★★★</div>",unsafe_allow_html=True)

        if st.button("Tambah",key=f"add{idx}"):
            new=pd.DataFrame([{
                "user":user,
                "product_id":p.get("id",idx),
                "name":product_name,
                "price":price_used,
                "qty":1
            }])
            cart=pd.concat([cart,new])
            cart.to_csv(CART_FILE,index=False)
            st.rerun()

        st.markdown("</div>",unsafe_allow_html=True)

# ==============================
# FLOATING CART
# ==============================
st.markdown("""
<div class="floating-cart">🛒</div>
""",unsafe_allow_html=True)
