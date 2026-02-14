import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"

# ===== AUTO CREATE FILE =====
if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["username", "password"]).to_csv(USER_FILE, index=False)

if not os.path.exists(CART_FILE):
    pd.DataFrame(columns=[
        "buyer", "product_id", "product_name",
        "price", "qty"
    ]).to_csv(CART_FILE, index=False)

if not os.path.exists(ORDER_FILE):
    pd.DataFrame(columns=[
        "order_id", "buyer", "total"
    ]).to_csv(ORDER_FILE, index=False)


# =====================================
# 🔐 LOGIN & REGISTER
# =====================================
def login_page():

    users = pd.read_csv(USER_FILE)

    tab1, tab2 = st.tabs(["Login", "Daftar"])

    # LOGIN
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if ((users["username"] == u) & (users["password"] == p)).any():
                st.session_state.user = u
                st.success("Login berhasil")
                st.rerun()
            else:
                st.error("Username/password salah")

    # REGISTER
    with tab2:
        u = st.text_input("Username baru")
        p = st.text_input("Password baru", type="password")

        if st.button("Daftar"):
            new = pd.DataFrame([{"username": u, "password": p}])
            users = pd.concat([users, new], ignore_index=True)
            users.to_csv(USER_FILE, index=False)
            st.success("Akun berhasil dibuat")


# =====================================
# 🛒 TAMBAH KE KERANJANG
# =====================================
def add_to_cart(user, product):

    cart = pd.read_csv(CART_FILE)

    new_item = pd.DataFrame([{
        "buyer": user,
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "price": product["price"],
        "qty": 1
    }])

    cart = pd.concat([cart, new_item], ignore_index=True)
    cart.to_csv(CART_FILE, index=False)

    st.success("Produk masuk keranjang")


# =====================================
# 🧺 HALAMAN KERANJANG
# =====================================
def cart_page(user):

    cart = pd.read_csv(CART_FILE)
    my_cart = cart[cart["buyer"] == user]

    st.header("🧺 Keranjang Saya")

    if my_cart.empty:
        st.info("Keranjang kosong")
        return

    st.dataframe(my_cart)

    total = (my_cart["price"] * my_cart["qty"]).sum()
    st.subheader(f"Total: Rp {int(total):,}")

    if st.button("Checkout"):

        orders = pd.read_csv(ORDER_FILE)

        new_order = pd.DataFrame([{
            "order_id": len(orders) + 1,
            "buyer": user,
            "total": total
        }])

        orders = pd.concat([orders, new_order], ignore_index=True)
        orders.to_csv(ORDER_FILE, index=False)

        # Kosongkan keranjang user
        cart = cart[cart["buyer"] != user]
        cart.to_csv(CART_FILE, index=False)

        st.success("Checkout berhasil!")
