import streamlit as st
import pandas as pd
import os
import random
import hashlib
import uuid

st.set_page_config(page_title="Toko Emergency", page_icon="🚑", layout="wide")

# ==============================
# STYLE MARKETPLACE
# ==============================
st.markdown("""
<style>

html, body {
    background: #f5f5f5 !important;
}

[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

.block-container {
    max-width: 1200px !important;
    padding-top: 130px !important;
}

/* NAVBAR */
.navbar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: white;
    padding: 12px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    z-index: 9999;
}

.logo {
    font-size: 22px;
    font-weight: 800;
    color: #ee4d2d;
}

.search-box input {
    width: 400px !important;
    border-radius: 20px !important;
}

/* HERO */
.hero {
    background: linear-gradient(135deg,#ff6a00,#ee0979);
    padding: 60px;
    border-radius: 20px;
    color: white;
    margin-bottom: 40px;
}

/* CARD */
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.price {
    color: #ee4d2d;
    font-weight: bold;
    font-size: 18px;
}

.old-price {
    text-decoration: line-through;
    color: grey;
    font-size: 14px;
}

.discount {
    background: #ee4d2d;
    color: white;
    padding: 2px 6px;
    font-size: 12px;
    border-radius: 6px;
}

.rating {
    color: #ffa41c;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# FILE SETUP
# ==============================
USER_FILE="users.csv"
PRODUCT_FILE="products.csv"
CART_FILE="cart.csv"
ORDER_FILE="orders.csv"

def init_file(file, cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file,index=False)

init_file(USER_FILE,["username","password"])
init_file(PRODUCT_FILE,["id","name","category","price","discount"])
init_file(CART_FILE,["user","product_id","name","price","qty"])
init_file(ORDER_FILE,["order_id","user","total","status"])

# ==============================
# HASH
# ==============================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ==============================
# SEED PRODUCT
# ==============================
if len(pd.read_csv(PRODUCT_FILE)) == 0:
    data=[]
    for i in range(1,41):
        price=random.randint(20000,100000)
        discount=random.choice([0,10,20,30])
        data.append({
            "id":i,
            "name":f"Produk Kesehatan {i}",
            "category":"Obat",
            "price":price,
            "discount":discount
        })
    pd.DataFrame(data).to_csv(PRODUCT_FILE,index=False)

# ==============================
# SESSION
# ==============================
if "user" not in st.session_state:
    st.session_state.user=None
if "page" not in st.session_state:
    st.session_state.page="home"

# ==============================
# LOGIN
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
products=pd.read_csv(PRODUCT_FILE)
cart=pd.read_csv(CART_FILE)
orders=pd.read_csv(ORDER_FILE)

# ==============================
# NAVBAR
# ==============================
cart_count=len(cart[cart.user==user])

st.markdown(f"""
<div class="navbar">
<div class="logo">🚑 Toko Emergency</div>
<div>🛒 {cart_count} | 👤 {user}</div>
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
# SEARCH
# ==============================
search=st.text_input("🔍 Cari Produk")

if search:
    products=products[products["name"].str.contains(search,case=False)]

# ==============================
# GRID PRODUK 4 KOLOM
# ==============================
cols = st.columns(4)

for idx, p in products.iterrows():
    col = cols[idx % 4]
    with col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # ==== SAFE COLUMN HANDLING ====
        product_name = p["name"] if "name" in products.columns else p.get("product_name", "Produk")
        product_price = p["price"] if "price" in products.columns else 0
        product_discount = p["discount"] if "discount" in products.columns else 0

        st.image("https://images.unsplash.com/photo-1580281657527-47b4c09841b4", use_column_width=True)

        st.write(f"**{product_name}**")

        if product_discount and product_discount > 0:
            old_price = product_price
            new_price = int(old_price * (100 - product_discount) / 100)
            st.markdown(
                f"<span class='old-price'>Rp {old_price:,}</span> "
                f"<span class='discount'>-{product_discount}%</span>",
                unsafe_allow_html=True
            )
            st.markdown(f"<div class='price'>Rp {new_price:,}</div>", unsafe_allow_html=True)
            price_used = new_price
        else:
            st.markdown(f"<div class='price'>Rp {product_price:,}</div>", unsafe_allow_html=True)
            price_used = product_price

        st.markdown("<div class='rating'>★★★★★</div>", unsafe_allow_html=True)

        if st.button("Tambah", key=f"add{idx}"):
            new = pd.DataFrame([{
                "user": user,
                "product_id": p.get("id", idx),
                "name": product_name,
                "price": price_used,
                "qty": 1
            }])
            cart = pd.concat([cart, new])
            cart.to_csv(CART_FILE, index=False)
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
