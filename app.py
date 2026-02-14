import streamlit as st import pandas as pd import os

=====================================================

CONFIG

=====================================================

st.set_page_config(page_title="Marketplace Tawar Pro", layout="wide", page_icon="🛒")

=====================================================

FILE PATH

=====================================================

USER_FILE = "users.csv" PRODUCT_FILE = "products.csv" CART_FILE = "cart.csv" ORDER_FILE = "orders.csv" OFFER_FILE = "offers.csv"

=====================================================

AUTO CREATE FILES

=====================================================

def init_file(file, columns): if not os.path.exists(file): pd.DataFrame(columns=columns).to_csv(file, index=False)

init_file(USER_FILE, ["username","password","role"]) init_file(PRODUCT_FILE, ["product_id","product_name","price","image_url","is_active","discount","best_seller"]) init_file(CART_FILE, ["user","product_id","product_name","price","qty"]) init_file(ORDER_FILE, ["order_id","user","total"]) init_file(OFFER_FILE, ["product_id","product_name","buyer","offer_price"])

Create default admin if not exists

users_df = pd.read_csv(USER_FILE) if "admin" not in users_df["username"].values: admin = pd.DataFrame([{"username":"admin","password":"admin123","role":"admin"}]) users_df = pd.concat([users_df, admin], ignore_index=True) users_df.to_csv(USER_FILE, index=False)

=====================================================

CSS TOKOPEDIA STYLE

=====================================================

st.markdown("""

<style>
.stApp {background-color:#f5f5f5;}
.card {background:white;padding:12px;border-radius:10px;border:1px solid #ddd;}
.card:hover {box-shadow:0 5px 15px rgba(0,0,0,0.1);transform:translateY(-3px);}
.price {color:#03AC0E;font-weight:bold;font-size:18px;}
.badge {background:#ff4d4d;color:white;padding:2px 6px;border-radius:5px;font-size:12px;}
.stButton>button {background:#03AC0E;color:white;border-radius:6px;width:100%;}
</style>""", unsafe_allow_html=True)

=====================================================

SESSION INIT

=====================================================

if "user" not in st.session_state: st.session_state.user = None if "role" not in st.session_state: st.session_state.role = None

=====================================================

LOGIN / REGISTER

=====================================================

def login_page(): users = pd.read_csv(USER_FILE) tab1, tab2 = st.tabs(["Login","Daftar"])

with tab1:
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        match = users[(users.username==u)&(users.password==p)]
        if not match.empty:
            st.session_state.user = u
            st.session_state.role = match.iloc[0].role
            st.rerun()
        else:
            st.error("Login gagal")

with tab2:
    u = st.text_input("Username Baru")
    p = st.text_input("Password Baru", type="password")
    role = st.selectbox("Daftar sebagai",["buyer"])
    if st.button("Daftar"):
        if u in users.username.values:
            st.warning("Username sudah ada")
        else:
            new = pd.DataFrame([{"username":u,"password":p,"role":role}])
            users = pd.concat([users,new], ignore_index=True)
            users.to_csv(USER_FILE,index=False)
            st.success("Akun berhasil dibuat")

if st.session_state.user is None: login_page() st.stop()

user = st.session_state.user role = st.session_state.role

=====================================================

LOAD DATA

=====================================================

def load_data(): return ( pd.read_csv(PRODUCT_FILE), pd.read_csv(CART_FILE), pd.read_csv(ORDER_FILE), pd.read_csv(OFFER_FILE) )

products, cart, orders, offers = load_data()

=====================================================

SIDEBAR MENU

=====================================================

menu = ["Katalog"] if role=="buyer": menu += ["Keranjang","Checkout","Riwayat"] if role=="admin": menu += ["Admin Produk","Dashboard"]

choice = st.sidebar.radio("Menu", menu)

if st.sidebar.button("Logout"): st.session_state.user = None st.session_state.role = None st.rerun()

=====================================================

SEARCH

=====================================================

search = st.text_input("🔍 Cari produk") filtered = products.copy() if "is_active" in filtered.columns: filtered = filtered[filtered.is_active==True] if search: filtered = filtered[filtered.product_name.str.contains(search,case=False)]

=====================================================

ADD CART FUNCTION

=====================================================

def add_cart(user,p): global cart exist = cart[(cart.user==user)&(cart.product_id==p.product_id)] if not exist.empty: cart.loc[exist.index,"qty"] += 1 else: new = pd.DataFrame([{ "user":user, "product_id":p.product_id, "product_name":p.product_name, "price":p.price, "qty":1 }]) cart = pd.concat([cart,new], ignore_index=True) cart.to_csv(CART_FILE,index=False)

=====================================================

KATALOG

=====================================================

if choice=="Katalog": cols = st.columns(5) for i,p in filtered.iterrows(): with cols[i%5]: st.markdown("<div class='card'>",unsafe_allow_html=True) img = p.image_url if pd.notna(p.image_url) else f"https://source.unsplash.com/300x200/?{p.product_name}" st.image(img) st.write(p.product_name) if p.get("best_seller",False): st.markdown("<span class='badge'>Best Seller</span>",unsafe_allow_html=True) price = p.price if p.get("discount",0)>0: disc = int(price*(1-p.discount/100)) st.markdown(f"<div class='price'>Rp {disc:,}</div>",unsafe_allow_html=True) st.caption(f"Diskon {p.discount}%") else: st.markdown(f"<div class='price'>Rp {price:,}</div>",unsafe_allow_html=True) if role=="buyer": if st.button("Tambah",key=f"cart{i}"): add_cart(user,p) st.success("Masuk keranjang") st.markdown("</div>",unsafe_allow_html=True)

=====================================================

KERANJANG

=====================================================

elif choice=="Keranjang": my = cart[cart.user==user] if my.empty: st.info("Keranjang kosong") else: st.dataframe(my) total = (my.price*my.qty).sum() st.subheader(f"Total: Rp {total:,}")

=====================================================

CHECKOUT

=====================================================

elif choice=="Checkout": my = cart[cart.user==user] if my.empty: st.warning("Keranjang kosong") else: total = (my.price*my.qty).sum() st.write("Total:",total) if st.button("Bayar"): oid = len(orders)+1 new = pd.DataFrame([{"order_id":oid,"user":user,"total":total}]) orders = pd.concat([orders,new], ignore_index=True) orders.to_csv(ORDER_FILE,index=False) cart = cart[cart.user!=user] cart.to_csv(CART_FILE,index=False) st.success("Checkout berhasil")

=====================================================

RIWAYAT

=====================================================

elif choice=="Riwayat": my = orders[orders.user==user] st.dataframe(my)

=====================================================

ADMIN PRODUK

=====================================================

elif choice=="Admin Produk": if role!="admin": st.stop() with st.form("add"): name = st.text_input("Nama") price = st.number_input("Harga") img = st.text_input("Image URL") disc = st.number_input("Diskon %",0,100) best = st.checkbox("Best Seller") if st.form_submit_button("Tambah"): pid = len(products)+1 new = pd.DataFrame([{ "product_id":pid, "product_name":name, "price":price, "image_url":img, "is_active":True, "discount":disc, "best_seller":best }]) products = pd.concat([products,new], ignore_index=True) products.to_csv(PRODUCT_FILE,index=False) st.success("Produk ditambah")

=====================================================

DASHBOARD

=====================================================

elif choice=="Dashboard": st.metric("Total Produk",len(products)) st.metric("Total Order",len(orders)) if not orders.empty: st.bar_chart(orders.groupby("user").total.sum())
