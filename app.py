import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ==============================
# BASIC LOGIN (Hard-coded)
# ==============================
USERNAME = "admin"
PASSWORD = "soomro"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==============================
# LOGIN PAGE
# ==============================
if not st.session_state.logged_in:
    st.title("🔐 Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()

# ==============================
# PATH SETUP
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")

MED_FILE = os.path.join(DATA_FOLDER, "medicines.csv")
SALES_FILE = os.path.join(DATA_FOLDER, "sales.csv")
SUG_FILE = os.path.join(DATA_FOLDER, "suggestions.csv")

os.makedirs(DATA_FOLDER, exist_ok=True)

# ==============================
# CREATE FILES
# ==============================
if not os.path.exists(MED_FILE):
    pd.DataFrame(
        columns=["Medicine Name", "Company", "Price", "Stock"]
    ).to_csv(MED_FILE, index=False)

if not os.path.exists(SALES_FILE):
    pd.DataFrame(
        columns=["Date", "Medicine Name", "Quantity", "Total Price"]
    ).to_csv(SALES_FILE, index=False)

if not os.path.exists(SUG_FILE):
    pd.DataFrame(
        columns=["Date", "Suggestion"]
    ).to_csv(SUG_FILE, index=False)

# ==============================
# FUNCTIONS
# ==============================
def load_csv(path):
    return pd.read_csv(path)

def save_csv(df, path):
    df.to_csv(path, index=False)

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("💊 Medical Panel")

menu = st.sidebar.radio(
    "Menu",
    [
        "🏠 Home",
        "➕ Add Medicine",
        "💰 Sell Medicine",
        "🧾 Bill Preview",
        "📊 Sales Report",
        "📈 Sales Charts",
        "💡 Suggestions",
        "🚪 Logout"
    ]
)

# ==============================
# HOME
# ==============================
if menu == "🏠 Home":
    st.title("Medical Management System")
    st.write("Complete Medical Store App with Login & Suggestions")

# ==============================
# ADD MEDICINE
# ==============================
elif menu == "➕ Add Medicine":
    st.title("Add Medicine")

    name = st.text_input("Medicine Name")
    company = st.text_input("Company Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)

    if st.button("Save"):
        if name and company:
            df = load_csv(MED_FILE)
            df.loc[len(df)] = [name, company, price, stock]
            save_csv(df, MED_FILE)
            st.success("Medicine Added")
        else:
            st.error("All fields required")

# ==============================
# SELL MEDICINE
# ==============================
elif menu == "💰 Sell Medicine":
    st.title("Sell Medicine")

    med_df = load_csv(MED_FILE)

    if med_df.empty:
        st.warning("No medicine available")
    else:
        med = st.selectbox("Select Medicine", med_df["Medicine Name"])
        qty = st.number_input("Quantity", min_value=1)

        row = med_df[med_df["Medicine Name"] == med].iloc[0]

        if st.button("Sell"):
            if qty <= row["Stock"]:
                total = qty * row["Price"]

                med_df.loc[
                    med_df["Medicine Name"] == med, "Stock"
                ] -= qty
                save_csv(med_df, MED_FILE)

                sales_df = load_csv(SALES_FILE)
                sales_df.loc[len(sales_df)] = [
                    datetime.now().strftime("%Y-%m-%d"),
                    med,
                    qty,
                    total
                ]
                save_csv(sales_df, SALES_FILE)

                st.session_state["bill"] = {
                    "Medicine": med,
                    "Qty": qty,
                    "Total": total
                }

                st.success(f"Sold | Total Rs {total}")
            else:
                st.error("Insufficient stock")

# ==============================
# BILL PREVIEW
# ==============================
elif menu == "🧾 Bill Preview":
    st.title("Bill Preview")

    bill = st.session_state.get("bill")

    if bill:
        st.write("Medicine:", bill["Medicine"])
        st.write("Quantity:", bill["Qty"])
        st.write("Total:", bill["Total"])
    else:
        st.info("No bill generated")

# ==============================
# SALES REPORT
# ==============================
elif menu == "📊 Sales Report":
    st.title("Sales Report")

    df = load_csv(SALES_FILE)
    if df.empty:
        st.info("No sales found")
    else:
        st.dataframe(df)
        st.write("Total Sales Rs:", df["Total Price"].sum())

# ==============================
# SALES CHARTS
# ==============================
elif menu == "📈 Sales Charts":
    st.title("Sales Charts")

    df = load_csv(SALES_FILE)
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"])
        daily = df.groupby("Date")["Total Price"].sum()
        st.line_chart(daily)
    else:
        st.info("No data")

# ==============================
# SUGGESTIONS
# ==============================
elif menu == "💡 Suggestions":
    st.title("Suggestions / Feedback")

    msg = st.text_area("Write your suggestion")

    if st.button("Submit"):
        if msg:
            df = load_csv(SUG_FILE)
            df.loc[len(df)] = [
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                msg
            ]
            save_csv(df, SUG_FILE)
            st.success("Suggestion submitted")
        else:
            st.error("Empty suggestion not allowed")

# ==============================
# LOGOUT
# ==============================
elif menu == "🚪 Logout":
    st.session_state.logged_in = False
    st.rerun()
