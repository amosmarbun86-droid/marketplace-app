import streamlit as st
import pandas as pd
import os

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Marketplace Tawar Pro", layout="wide", page_icon="🛒")

# =====================================================
# FILE PATH
# =====================================================
USER_FILE = "users.csv"
PRODUCT_FILE = "products.csv"
CART_FILE = "cart.csv"
ORDER_FILE = "orders.csv"
OFFER_FILE = "offers.csv"

# =====================================================
# AUTO CREATE FILES
# =====================================================
def init_file(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_file(USER_FILE, ["username","password","role"])
init_file(PRODUCT_FILE, ["product_id","product_name","price","image_url","is_active","discount","best_seller"])
init_file(CART_FILE, ["user","product_id","product_name","price","qty"])
init_file(ORDER_FILE, ["order_id","user","total"])
init_file(OFFER_FILE, ["product_id","product_name","buyer","offer_price"])

# Create default admin if not exists
users_df = pd.read_csv(USER_FILE)
if "admin" not in users_df["username"].values:
    admin = pd.DataFrame([{"username":"admin","password":"admin123","role":"admin"}])
    users_df = pd.concat([users_df, admin], ignore_index=True)
