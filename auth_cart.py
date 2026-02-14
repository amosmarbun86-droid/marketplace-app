import streamlit as st
import pandas as pd
import os

USER_FILE = "users.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"


# =====================================
# AUTO CREATE FILES
# =====================================
if not os.path.exists(USER_FILE):
    pd.DataFrame(
        columns=["username", "password", "role"]
    ).to_csv(USER_FILE, index=False)

if not os.path.exists(CART_FILE):
    pd.DataFrame(
        columns=["buyer", "product_id", "product_name", "price", "qty"]
    ).to_csv(CART_FILE, index=False)

if not os.path.exists(ORDER_FILE):
    pd.DataFrame(
        columns=["order_id", "buyer", "total"]
    ).to_csv(ORDER_FILE, index=False)


# =====================================
# AUTO CREATE / FIX ADMIN (FULL AUTO)
# =====================================
def ensure_admin():

    users = pd.read_csv(USER_FILE)

    admin_exists = users[
        users["username"] == "admin"
    ]

    # jika admin belum ada → buat
    if admin_exists.empty:

        new_admin = pd.DataFrame([{
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }])

        users = pd.concat([users, new_admin], ignore_index=True)
        users.to_csv(USER_FILE, index=False)

    # jika admin ada tapi role salah → perbaiki otomatis
    else:

        idx = admin_exists.index[0]

        if users.loc[idx, "role"] != "admin":
            users.loc[idx, "role"] = "admin"
            users.to_csv(USER_FILE, index=False)


# jalankan otomatis saat import
ensure_admin()


# =====================================
# LOGIN PAGE
# =====================================
def login_page():

    users = pd.read_csv(USER_FILE)

    tab1, tab2 = st.tabs(["Login", "Daftar"])

    # LOGIN
    with tab1:

        with st.form("login_form"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submit = st.form_submit_button("Login")

            if submit:

                match = users[
                    (users["username"] == username) &
                    (users["password"] == password)
                ]

                if not match.empty:

                    st.session_state.user = username
                    st.session_state.role = match.iloc[0]["role"]

                    st.success("Login berhasil")
                    st.rerun()

                else:
                    st.error("Username atau password salah")


    # REGISTER
    with tab2:

        with st.form("register_form"):

            username = st.text_input("Username baru")
            password = st.text_input("Password baru", type="password")

            role = st.selectbox(
                "Role",
                ["buyer", "seller"]
            )

            submit = st.form_submit_button("Daftar")

            if submit:

                if username == "" or password == "":
                    st.error("Tidak boleh kosong")
                    return

                if username in users["username"].values:
                    st.error("Username sudah ada")
                    return

                new_user = pd.DataFrame([{
                    "username": username,
                    "password": password,
                    "role": role
                }])

                users = pd.concat(users, new_user, ignore_index=True)
                users.to_csv(USER_FILE, index=False)

                st.success("Akun berhasil dibuat")


# =====================================
# ADD TO CART
# =====================================
def add_to_cart(user, product):

    cart = pd.read_csv(CART_FILE)

    existing = cart[
        (cart["buyer"] == user) &
        (cart["product_id"] == product["product_id"])
    ]

    if not existing.empty:

        cart.loc[existing.index, "qty"] += 1

    else:

        new_item = pd.DataFrame([{
            "buyer": user,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "price": product["price"],
            "qty": 1
        }])

        cart = pd.concat(cart, new_item, ignore_index=True)

    cart.to_csv(CART_FILE, index=False)

    st.success("Masuk keranjang")


# =====================================
# CART PAGE
# =====================================
def cart_page(user):

    cart = pd.read_csv(CART_FILE)

    my_cart = cart[cart["buyer"] == user]

    st.header("Keranjang")

    if my_cart.empty:
        st.info("Kosong")
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

        cart = cart[cart["buyer"] != user]
        cart.to_csv(CART_FILE, index=False)

        st.success("Checkout berhasil")
        st.rerun()
