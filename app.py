import streamlit as st
import pandas as pd
import os

# =====================================
# CONFIG
# =====================================
st.set_page_config(
    page_title="Marketplace Premium",
    layout="wide",
    page_icon="🛒"
)

# =====================================
# FILE PATH
# =====================================
USER_FILE = "users.csv"
PRODUCT_FILE = "products.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"

# =====================================
# AUTO CREATE FILE
# =====================================
def init_file(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_file(USER_FILE, ["username","password","role"])
init_file(PRODUCT_FILE, ["product_id","product_name","price","image_url","discount","best"])
init_file(CART_FILE, ["user","product_id","product_name","price","qty"])
init_file(ORDER_FILE, ["order_id","user","product","total"])

# =====================================
# DEFAULT ADMIN
# =====================================
users = pd.read_csv(USER_FILE)
if "admin" not in users["username"].values:
    new = pd.DataFrame([{
        "username":"admin",
        "password":"admin123",
        "role":"admin"
    }])
    users = pd.concat([users,new])
    users.to_csv(USER_FILE,index=False)

# =====================================
# PREMIUM UI
# =====================================
st.markdown("""
<style>

.stApp {
background:
linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)),
url("https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a");
background-size:cover;
}

.banner {
background:linear-gradient(90deg,#03AC0E,#00c853);
padding:20px;
border-radius:15px;
color:white;
font-size:28px;
font-weight:bold;
text-align:center;
margin-bottom:20px;
}

.card {
background:white;
padding:15px;
border-radius:15px;
transition:0.3s;
}

.card:hover {
transform:translateY(-5px);
box-shadow:0 10px 25px rgba(0,0,0,0.2);
}

.price {
color:#03AC0E;
font-size:20px;
font-weight:bold;
}

.stButton>button {
background:#03AC0E;
color:white;
border-radius:10px;
}

section[data-testid="stSidebar"] {
background:linear-gradient(180deg,#03AC0E,#028a0f);
}

section[data-testid="stSidebar"] * {
color:white !important;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="banner">🛒 Marketplace Premium Indonesia</div>', unsafe_allow_html=True)

# =====================================
# SESSION
# =====================================
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

# =====================================
# LOGIN PAGE
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
                st.session_state.user = u
                st.session_state.role = match.iloc[0]["role"]
                st.rerun()
            else:
                st.error("Login gagal")

    with tab2:
        u = st.text_input("Username baru")
        p = st.text_input("Password baru", type="password")

        if st.button("Register"):
            new = pd.DataFrame([{
                "username":u,
                "password":p,
                "role":"buyer"
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

# =====================================
# SIDEBAR
# =====================================
menu = ["Katalog","Keranjang","Checkout","Riwayat"]

if role=="admin":
    menu += ["Admin Produk","Dashboard"]

choice = st.sidebar.radio("Menu", menu)

if st.sidebar.button("Logout"):
    st.session_state.user=None
    st.rerun()

# =====================================
# KATALOG
# =====================================
if choice=="Katalog":

    cols = st.columns(4)

    for i,p in products.iterrows():

        with cols[i%4]:

            st.markdown("<div class='card'>",unsafe_allow_html=True)

            img = p.image_url if pd.notna(p.image_url) else "https://via.placeholder.com/300"

            st.image(img)

            st.write(p.product_name)

            price = p.price

            if p.discount>0:
                new_price = int(price*(1-p.discount/100))
                st.markdown(f"<div class='price'>Rp {new_price:,}</div>",unsafe_allow_html=True)
                st.caption(f"Diskon {p.discount}%")
            else:
                st.markdown(f"<div class='price'>Rp {price:,}</div>",unsafe_allow_html=True)

            if role=="buyer":
                if st.button("Tambah", key=i):

                    exist = cart[(cart.user==user)&(cart.product_id==p.product_id)]

                    if not exist.empty:
                        cart.loc[exist.index,"qty"] +=1
                    else:
                        new = pd.DataFrame([{
                            "user":user,
                            "product_id":p.product_id,
                            "product_name":p.product_name,
                            "price":p.price,
                            "qty":1
                        }])
                        cart = pd.concat([cart,new])

                    cart.to_csv(CART_FILE,index=False)
                    st.success("Ditambahkan")

            st.markdown("</div>",unsafe_allow_html=True)

# =====================================
# KERANJANG
# =====================================
elif choice=="Keranjang":

    my = cart[cart.user==user]

    if my.empty:
        st.info("Kosong")
    else:

        for i,row in my.iterrows():

            col1,col2,col3 = st.columns([4,2,1])

            col1.write(row.product_name)
            col2.write(f"x{row.qty}")

            if col3.button("Hapus",key=i):
                cart = cart.drop(i)
                cart.to_csv(CART_FILE,index=False)
                st.rerun()

        total = (my.price*my.qty).sum()

        st.subheader(f"Total: Rp {total:,}")

# =====================================
# CHECKOUT
# =====================================
elif choice=="Checkout":

    my = cart[cart.user==user]

    if my.empty:
        st.warning("Kosong")
    else:

        total = (my.price*my.qty).sum()

        st.write("Total:", total)

        if st.button("Bayar"):

            oid = len(orders)+1

            for i,row in my.iterrows():

                new = pd.DataFrame([{
                    "order_id":oid,
                    "user":user,
                    "product":row.product_name,
                    "total":row.price*row.qty
                }])

                orders = pd.concat([orders,new])

            orders.to_csv(ORDER_FILE,index=False)

            cart = cart[cart.user!=user]
            cart.to_csv(CART_FILE,index=False)

            st.success("Checkout berhasil")

# =====================================
# RIWAYAT
# =====================================
elif choice=="Riwayat":

    my = orders[orders.user==user]

    st.dataframe(my)

# =====================================
# ADMIN PRODUK
# =====================================
elif choice=="Admin Produk":

    if role!="admin":
        st.stop()

    with st.form("add"):

        name = st.text_input("Nama produk")
        price = st.number_input("Harga")
        img = st.text_input("Image URL")
        disc = st.number_input("Diskon",0,100)
        best = st.checkbox("Best seller")

        if st.form_submit_button("Tambah"):

            pid = len(products)+1

            new = pd.DataFrame([{
                "product_id":pid,
                "product_name":name,
                "price":price,
                "image_url":img,
                "discount":disc,
                "best":best
            }])

            products = pd.concat([products,new])
            products.to_csv(PRODUCT_FILE,index=False)

            st.success("Produk ditambah")

# =====================================
# DASHBOARD
# =====================================
elif choice=="Dashboard":

    st.metric("Total Produk", len(products))
    st.metric("Total Order", len(orders))

    if not orders.empty:
        chart = orders.groupby("user").total.sum()
        st.bar_chart(chart)
