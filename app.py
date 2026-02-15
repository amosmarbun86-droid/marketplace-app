import streamlit as st
import pandas as pd
import os
import hashlib

st.set_page_config(page_title="Toko Emergency", page_icon="🚑", layout="wide")

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.navbar {
    position:fixed;
    top:0; left:0; right:0;
    background:white;
    padding:10px;
    display:flex;
    justify-content:space-between;
    box-shadow:0 2px 10px rgba(0,0,0,0.1);
    z-index:999;
}
.logo {
    font-weight:bold;
    color:#ee4d2d;
}
.hero {
    background:linear-gradient(135deg,#ff6a00,#ee0979);
    padding:20px;
    color:white;
    border-radius:10px;
    margin-top:60px;
    margin-bottom:20px;
}
.card {
    background:white;
    padding:10px;
    border-radius:10px;
    margin-bottom:15px;
    box-shadow:0 2px 10px rgba(0,0,0,0.1);
}
.price {
    color:#ee4d2d;
    font-weight:bold;
}
.old {
    text-decoration:line-through;
    color:grey;
    font-size:12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FILE SETUP
# =========================
USER_FILE="users.csv"
PRODUCT_FILE="products.csv"
CART_FILE="cart.csv"

def init_file(file,cols):
    if not os.path.exists(file):
        pd.DataFrame(columns=cols).to_csv(file,index=False)

init_file(USER_FILE,["username","password","role"])
init_file(PRODUCT_FILE,["id","name","price","discount","seller"])
init_file(CART_FILE,["user","product_id","name","price","qty"])

# =========================
# HASH FUNCTION
# =========================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

# =========================
# AUTO CREATE ADMIN
# =========================
users = pd.read_csv(USER_FILE)

if users.empty:
    admin = pd.DataFrame([{
        "username":"admin",
        "password":hash_password("admin"),
        "role":"admin"
    }])
    admin.to_csv(USER_FILE,index=False)

# =========================
# SESSION
# =========================
if "user" not in st.session_state:
    st.session_state.user=None

if "role" not in st.session_state:
    st.session_state.role=None

# =========================
# LOGIN REGISTER
# =========================
def login():

    users=pd.read_csv(USER_FILE)

    tab1,tab2=st.tabs(["Login","Register"])

    with tab1:

        u=st.text_input("Username")
        p=st.text_input("Password",type="password")

        if st.button("Login"):

            match=users[
                (users.username==u) &
                (users.password==hash_password(p))
            ]

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

            st.success("Register berhasil")

# =========================
# STOP jika belum login
# =========================
if st.session_state.user is None:

    login()
    st.stop()

user=st.session_state.user
role=st.session_state.role

products=pd.read_csv(PRODUCT_FILE)
cart=pd.read_csv(CART_FILE)

# =========================
# NAVBAR
# =========================
cart_count=len(cart[cart.user==user])

st.markdown(f"""
<div class="navbar">
<div class="logo">🚑 Toko Emergency</div>
<div>{role.upper()} | 🛒 {cart_count}</div>
</div>
""", unsafe_allow_html=True)

# =========================
# LOGOUT
# =========================
if st.button("Logout"):
    st.session_state.user=None
    st.session_state.role=None
    st.rerun()

# =========================
# ADMIN
# =========================
if role=="admin":

    st.title("Dashboard Admin")

    st.subheader("Users")
    st.dataframe(pd.read_csv(USER_FILE))

    st.subheader("Products")
    st.dataframe(products)

# =========================
# SELLER
# =========================
elif role=="seller":

    st.title("Dashboard Seller")

    name=st.text_input("Nama Produk")
    price=st.number_input("Harga",0)
    discount=st.slider("Discount",0,90,0)

    if st.button("Tambah Produk"):

        new_id=1
        if not products.empty:
            new_id=products.id.max()+1

        new=pd.DataFrame([{
            "id":new_id,
            "name":name,
            "price":price,
            "discount":discount,
            "seller":user
        }])

        products=pd.concat([products,new])
        products.to_csv(PRODUCT_FILE,index=False)

        st.success("Produk ditambah")
        st.rerun()

    st.subheader("Produk Saya")

    my=products[products.seller==user]

    st.dataframe(my)

# =========================
# BUYER
# =========================
elif role=="buyer":

    st.markdown("""
    <div class="hero">
    Promo Hari Ini 🔥
    </div>
    """, unsafe_allow_html=True)

    cols=st.columns(2)

    for idx,p in products.iterrows():

        col=cols[idx%2]

        with col:

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.write(p["name"])

            price=p["price"]
            discount=p["discount"]

            if discount>0:

                new_price=int(price*(100-discount)/100)

                st.markdown(
                    f"<span class='old'>Rp {price:,}</span>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<div class='price'>Rp {new_price:,}</div>",
                    unsafe_allow_html=True
                )

                final=new_price

            else:

                st.markdown(
                    f"<div class='price'>Rp {price:,}</div>",
                    unsafe_allow_html=True
                )

                final=price

            if st.button("Tambah",key=idx):

                new=pd.DataFrame([{
                    "user":user,
                    "product_id":p["id"],
                    "name":p["name"],
                    "price":final,
                    "qty":1
                }])

                cart=pd.concat([cart,new])
                cart.to_csv(CART_FILE,index=False)

                st.success("Masuk cart")
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Cart Saya")

    mycart=cart[cart.user==user]

    st.dataframe(mycart)

    total=mycart.price.sum()

    st.write("Total:", total)
