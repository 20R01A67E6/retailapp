# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import pyodbc
# from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import train_test_split

# # ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="Retail Analytics",
#     page_icon="🛒",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# # ─── SESSION STATE ─────────────────────────────────────────────────────────────
# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
# if "view" not in st.session_state:
#     st.session_state.view = "login"  # can be "login", "signup"

# # ─── DATABASE CONNECTION ───────────────────────────────────────────────────────

# def get_connection():
#     conn_str = (
#         "DRIVER={ODBC Driver 18 for SQL Server};"
#         "SERVER=retail-server-yourname.database.windows.net;"
#         "DATABASE=retaildb;"
#         "UID=azureadmin;"
#         "PWD=StrongPass123!;"
#         "Encrypt=yes;"
#         "TrustServerCertificate=no;"
#         "Connect Timeout=30;"
#     )
#     return pyodbc.connect(conn_str)
# # ─── LOGIN SCREEN ──────────────────────────────────────────────────────────────
# def login_page():
#     st.title("🔒 Login to Your Account")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         # users.csv with columns Username,Email,Password
#         try:
#             users = pd.read_csv("users.csv")
#         except FileNotFoundError:
#             st.error("No users exist—please sign up first.")
#             return

#         if ((users.Username == username) & (users.Password == password)).any():
#             st.success(f"Welcome back, {username}!")
#             st.session_state.logged_in = True
#             # no rerun call needed—Streamlit will automatically refresh
#         else:
#             st.error("❌ Invalid credentials.")

#     if st.button("Create new account"):
#         st.session_state.view = "signup"

# # ─── SIGNUP SCREEN ─────────────────────────────────────────────────────────────
# def signup_page():
#     st.title("✍️ Create a New Account")
#     username = st.text_input("Choose a Username")
#     email    = st.text_input("Enter Email")
#     pwd      = st.text_input("Create Password", type="password")
#     confirm  = st.text_input("Confirm Password", type="password")

#     if st.button("Sign Up"):
#         if not all([username, email, pwd, confirm]):
#             st.error("❌ Please fill in all fields.")
#         elif pwd != confirm:
#             st.error("❌ Passwords do not match.")
#         else:
#             # load or initialize
#             try:
#                 users = pd.read_csv("users.csv")
#             except FileNotFoundError:
#                 users = pd.DataFrame(columns=["Username","Email","Password"])

#             if username in users.Username.values:
#                 st.error("❌ Username already taken.")
#             else:
#                 new = pd.DataFrame([{"Username":username,"Email":email,"Password":pwd}])
#                 users = pd.concat([users,new], ignore_index=True)
#                 users.to_csv("users.csv", index=False)
#                 st.success("✅ Account created! Please log in.")
#                 st.session_state.view = "login"

#     if st.button("← Back to Login"):
#         st.session_state.view = "login"

# # ─── DASHBOARD ─────────────────────────────────────────────────────────────────
# def dashboard_page():
#     st.title("📊 Retail Dashboard")
#     conn = get_connection()
#     df   = pd.read_sql("SELECT * FROM dbo.transactions", conn)
#     if df.empty:
#         st.warning("No transactions found.")
#         return

#     st.metric("Total Sales ($)",    f"{df.Spend.sum():,.2f}")
#     st.metric("Total Units Sold",   f"{df.Units.sum():,}")
#     st.metric("Total Transactions", f"{df.Basket_num.nunique():,}")
#     st.markdown("---")
#     st.subheader("📈 Sales Over Time")
#     df["Date"] = pd.to_datetime(df["Date"])
#     trend = df.groupby("Date")["Spend"].sum().reset_index()
#     fig   = px.line(trend, x="Date", y="Spend")
#     st.plotly_chart(fig, use_container_width=True)

# # ─── ML MODELS PAGE ────────────────────────────────────────────────────────────
# def ml_models_page():
#     st.title("🧠 ML Models – Predict Spend")
#     conn = get_connection()
#     df   = pd.read_sql("SELECT Spend,Units,Week_num,Year FROM dbo.transactions", conn)
#     if df.empty:
#         st.warning("No data for model.")
#         return

#     X = df[["Units","Week_num","Year"]]
#     y = df["Spend"]
#     Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=0.2,random_state=42)
#     mdl = LinearRegression().fit(Xtr,ytr)
#     st.success(f"Model R² Score: {mdl.score(Xte,yte):.2f}")

#     units  = st.number_input("Units",   min_value=1,  value=1)
#     week   = st.number_input("Week",    min_value=1,  value=1)
#     year   = st.number_input("Year",    min_value=2000,value=2020)
#     if st.button("Predict Spend"):
#         p=mdl.predict([[units,week,year]])[0]
#         st.metric("Predicted Spend", f"${p:.2f}")

# # ─── SEARCH HSHD PAGE ──────────────────────────────────────────────────────────
# def search_page():
#     st.title("🔎 Search Household Data")
#     hshd = st.text_input("Enter Household Number")
#     if st.button("Search") and hshd:
#         conn = get_connection()
#         sql = """
#             SELECT t.Hshd_num,t.Basket_num,t.Date,t.Product_num,
#                    p.Department,p.Commodity,
#                    t.Spend,t.Units,t.Store_region,t.Week_num,t.Year,
#                    h.Loyalty_flag,h.Age_range,h.Marital_status,
#                    h.Income_range,h.Homeowner_desc,h.Hshd_composition,
#                    h.Hshd_size,h.Children
#             FROM dbo.transactions t
#             JOIN dbo.products    p ON t.Product_num = p.Product_num
#             JOIN dbo.households  h ON t.Hshd_num     = h.Hshd_num
#             WHERE t.Hshd_num = ?
#             ORDER BY t.Date,t.Basket_num
#         """
#         df = pd.read_sql(sql, conn, params=[hshd])
#         if df.empty:
#             st.warning("No records found.")
#         else:
#             st.dataframe(df, use_container_width=True)

# # ─── UPLOAD DATA PAGE ──────────────────────────────────────────────────────────
# def upload_page():
#     st.title("📤 Upload New Data")
#     table = st.selectbox("Table", ["households","products","transactions"])
#     file  = st.file_uploader("CSV", type="csv")
#     if file and st.button("Upload"):
#         df = pd.read_csv(file)
#         conn= get_connection()
#         cur = conn.cursor()
#         cur.execute(f"DELETE FROM dbo.{table}")  # optional
#         conn.commit()
#         cols = df.columns.tolist()
#         ph   = ",".join("?"*len(cols))
#         sql  = f"INSERT INTO dbo.{table}({','.join(cols)}) VALUES({ph})"
#         for row in df.itertuples(index=False):
#             cur.execute(sql, row)
#         conn.commit()
#         cur.close()
#         st.success(f"Inserted {len(df)} rows into {table}.")

# # ─── MAIN ROUTER ───────────────────────────────────────────────────────────────
# def main():
#     if not st.session_state.logged_in:
#         # hide sidebar
#         st.markdown("<style>div[data-testid='stSidebar']{visibility:hidden;}</style>",
#                     unsafe_allow_html=True)

#         # show login or signup
#         if st.session_state.view == "signup":
#             signup_page()
#         else:
#             login_page()

#     else:
#         # reveal sidebar
#         st.markdown("<style>div[data-testid='stSidebar']{visibility:visible;}</style>",
#                     unsafe_allow_html=True)

#         st.sidebar.title("Navigation")
#         choice = st.sidebar.radio("Go to",
#                      ["Dashboard","ML Models","Search HSHD","Upload New Data"])
#         if choice == "Dashboard":
#             dashboard_page()
#         elif choice == "ML Models":
#             ml_models_page()
#         elif choice == "Search HSHD":
#             search_page()
#         else:
#             upload_page()

# if __name__ == "__main__":
#     main()

import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# ─────────────────────────────────────────────────────────────
#  Azure SQL connection parameters – change these to yours:
# ─────────────────────────────────────────────────────────────
SERVER   = "retail-server-yourname.database.windows.net"
DATABASE = "retaildb"
UID      = "azureadmin"
PWD      = "StrongPass123!"
DRIVER   = "ODBC Driver 18 for SQL Server"

def get_connection():
    conn_str = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"UID={UID};"
        f"PWD={PWD};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)

# ─────────────────────────────────────────────────────────────
#  User‐management helpers (local users.csv)
# ─────────────────────────────────────────────────────────────
USER_FILE = "users.csv"

def load_users():
    try:
        return pd.read_csv(USER_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Username","Email","Password"])

def save_users(df):
    df.to_csv(USER_FILE, index=False)

# ─────────────────────────────────────────────────────────────
#  Session‐state initialization
# ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username  = ""
if "page" not in st.session_state:
    st.session_state.page = "login"

# ─────────────────────────────────────────────────────────────
#  LOGIN FORM
# ─────────────────────────────────────────────────────────────
def login_form():
    st.markdown("<h2 style='color:cyan;'>🔐 Login to Retail Analytics</h2>", 
                unsafe_allow_html=True)
    st.write("---")
    user = st.text_input("Username")
    pwd  = st.text_input("Password", type="password")
    login, create = st.columns(2)
    with login:
        if st.button("Login", type="primary"):
            users = load_users()
            match = users[
                (users.Username == user) & (users.Password == pwd)
            ]
            if not match.empty:
                st.success(f"Welcome back, {user}!")
                st.session_state.logged_in = True
                st.session_state.username  = user
            else:
                st.error("❌ Invalid username or password.")
    with create:
        if st.button("Create New Account"):
            st.session_state.page = "signup"

# ─────────────────────────────────────────────────────────────
#  SIGNUP FORM
# ─────────────────────────────────────────────────────────────
def signup_form():
    st.markdown("<h2 style='color:cyan;'>📝 Create a New Account</h2>",
                unsafe_allow_html=True)
    st.write("---")
    new_user  = st.text_input("Choose a Username")
    new_email = st.text_input("Email")
    pw1       = st.text_input("Password", type="password")
    pw2       = st.text_input("Confirm Password", type="password")
    submit, back = st.columns([1,1])
    with submit:
        if st.button("Sign Up", type="primary"):
            if not new_user or not new_email or not pw1:
                st.error("Please fill out all fields.")
            elif pw1 != pw2:
                st.error("Passwords do not match.")
            else:
                users = load_users()
                if new_user in users.Username.values:
                    st.error("That username already exists.")
                else:
                    users = pd.concat([users, pd.DataFrame([{
                        "Username": new_user,
                        "Email":    new_email,
                        "Password": pw1
                    }])], ignore_index=True)
                    save_users(users)
                    st.success("Account created! Please login now.")
                    st.session_state.page = "login"
    with back:
        if st.button("← Back to Login"):
            st.session_state.page = "login"

# ─────────────────────────────────────────────────────────────
#  DASHBOARD PAGE
# ─────────────────────────────────────────────────────────────
# def dashboard_page():
#     st.markdown("<h1 style='color:cyan;'>🛒 Retail Dashboard</h1>",
#                 unsafe_allow_html=True)
#     st.write("---")
#     try:
#         conn = get_connection()
#         df   = pd.read_sql("SELECT * FROM dbo.transactions", conn)
#         conn.close()
#     except Exception as e:
#         st.error(f"Connection error: {e}")
#         return

#     if df.empty:
#         st.warning("No transaction data found.")
#         return

#     df["Date"] = pd.to_datetime(df["Date"])
#     total_sales        = df["Spend"].sum()
#     total_units        = df["Units"].sum()
#     total_transactions = df["Basket_num"].nunique()

#     c1, c2, c3 = st.columns(3)
#     c1.metric("Total Sales",        f"${total_sales:,.2f}")
#     c2.metric("Total Units Sold",   f"{total_units:,}")
#     c3.metric("Total Transactions", f"{total_transactions:,}")

#     st.markdown("---")
#     st.subheader("📈 Sales Over Time")
#     sales_trend = df.groupby("Date")["Spend"].sum().reset_index()
#     fig = px.line(sales_trend, x="Date", y="Spend", 
#                   labels={"Spend":"Sales ($)","Date":"Date"})
#     st.plotly_chart(fig, use_container_width=True)

# def dashboard_page():
#     st.markdown("<h1 style='color:cyan;'>🛒 Retail KPI Dashboard</h1>", unsafe_allow_html=True)
#     st.write("---")

#     # 1) load data
#     try:
#         conn = get_connection()
#         df = pd.read_sql("SELECT * FROM dbo.transactions", conn)
#         conn.close()
#     except Exception as e:
#         st.error(f"Connection error: {e}")
#         return

#     if df.empty:
#         st.warning("No transaction data found.")
#         return

#     # parse dates
#     df["Date"] = pd.to_datetime(df["Date"])

#     # 2) Top KPI row
#     total_customers    = df["Hshd_num"].nunique()
#     total_transactions = df["Basket_num"].nunique()
#     avg_spend_per_txn  = df["Spend"].mean()
#     avg_units_per_txn  = df["Units"].mean()

#     k1, k2, k3, k4 = st.columns(4)
#     k1.metric("👥 Total Customers", f"{total_customers:,}")
#     k2.metric("🛒 Total Transactions", f"{total_transactions:,}")
#     k3.metric("💰 Avg Spend/Txn", f"${avg_spend_per_txn:,.2f}")
#     k4.metric("📦 Avg Units/Txn", f"{avg_units_per_txn:.1f}")

#     st.markdown("---")

#     # 3) Sales by Department (bar)
#     st.subheader("📊 Sales by Department")
#     dept_sales = (
#         df
#         .merge(pd.read_sql("SELECT * FROM dbo.products", get_connection()), on="Product_num")
#         .groupby("Department")["Spend"]
#         .sum()
#         .reset_index()
#         .sort_values("Spend", ascending=False)
#     )
#     fig_dept = px.bar(
#         dept_sales,
#         x="Department",
#         y="Spend",
#         text="Spend",
#         labels={"Spend":"Sales ($)"},
#     )
#     fig_dept.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
#     fig_dept.update_layout(uniformtext_minsize=8, uniformtext_mode="hide", xaxis_title=None)
#     st.plotly_chart(fig_dept, use_container_width=True)

#     st.markdown("---")

#     # 4) Trend: Price & Units per Transaction Over Time
#     st.subheader("📈 Avg Price & Units per Transaction Over Time")
#     per_basket = (
#         df.groupby(["Basket_num", "Date"])
#           .agg({"Spend": "sum","Units": "sum"})
#           .reset_index()
#     )
#     per_basket["Month"] = per_basket["Date"].dt.to_period("M").dt.to_timestamp()
#     trend = (
#         per_basket
#         .groupby("Month")[["Spend","Units"]]
#         .mean()
#         .reset_index()
#     )
#     fig_trend = px.line(
#         trend,
#         x="Month",
#         y=["Spend","Units"],
#         labels={"value": "Avg per Txn", "variable": ""},
#     )
#     st.plotly_chart(fig_trend, use_container_width=True)

#     st.markdown("---")

#     # 5) Top 7 Products by Units Sold
#     st.subheader("🏆 Top 7 Products by Units Sold")
#     top_products = (
#         df.groupby("Product_num")["Units"]
#           .sum()
#           .nlargest(7)
#           .reset_index()
#     )
#     fig_top = px.bar(
#         top_products,
#         x="Product_num",
#         y="Units",
#         text="Units",
#         labels={"Units":"Units Sold","Product_num":"Product #"}
#     )
#     fig_top.update_traces(texttemplate="%{text}", textposition="outside")
#     st.plotly_chart(fig_top, use_container_width=True)

#     st.markdown("---")

#     # 6) Sales by Region (pie)
#     st.subheader("🌐 Sales by Region")
#     region_sales = df.groupby("Store_region")["Spend"].sum().reset_index()
#     fig_region = px.pie(
#         region_sales,
#         names="Store_region",
#         values="Spend",
#         labels={"Store_region":"Region","Spend":"Sales ($)"}
#     )
#     st.plotly_chart(fig_region, use_container_width=True)

#     st.markdown("---")

#     # 7) Out‐of‐Stock placeholder
#     st.subheader("⚠️ Out-of-Stock Items")
#     st.info("**No inventory data available**, so this chart is a placeholder.")

# def dashboard_page():
#     st.markdown("<h1 style='color:cyan;'>🛒 Retail KPI Dashboard</h1>", unsafe_allow_html=True)
#     st.write("---")

#     # 1. Database fetch
#     try:
#         conn = get_connection()
#         df = pd.read_sql("SELECT * FROM dbo.transactions", conn)
#         conn.close()
#     except Exception as e:
#         st.error(f"Connection error: {e}")
#         return

#     if df.empty:
#         st.warning("No transaction data found.")
#         return

#     df["Date"] = pd.to_datetime(df["Date"])

#     # Metrics (Top KPIs)
#     total_customers    = df["Hshd_num"].nunique()
#     total_transactions = df["Basket_num"].nunique()
#     total_sales        = df["Spend"].sum()
#     avg_spend_per_txn  = df["Spend"].mean()
#     avg_units_per_txn  = df["Units"].mean()

#     ### -------- Grid Layout Starts Here --------
#     st.markdown("## 📊 KPIs Overview")
#     k1, k2, k3, k4 = st.columns(4)
#     k1.metric("👥 Total Customers", f"{total_customers:,}")
#     k2.metric("🛒 Total Transactions", f"{total_transactions:,}")
#     k3.metric("💵 Total Sales ($)", f"{total_sales:,.0f}")
#     k4.metric("💰 Avg Spend/Txn", f"${avg_spend_per_txn:,.2f}")

#     st.divider()

#     ### -------- 3 Charts in One Row --------
#     c1, c2, c3 = st.columns(3)

#     with c1:
#         st.subheader("Visitors & Transactions 📈")
#         monthly = df.copy()
#         monthly["Month"] = monthly["Date"].dt.to_period("M").dt.to_timestamp()
#         month_summary = (
#             monthly.groupby("Month")
#             .agg({"Hshd_num": "nunique", "Basket_num": "nunique"})
#             .reset_index()
#         )
#         fig1 = px.bar(month_summary, x="Month", y=["Hshd_num", "Basket_num"], barmode="group", labels={"value":"Count"})
#         st.plotly_chart(fig1, use_container_width=True)

#     with c2:
#         st.subheader("Sales by Division 🛍️")
#         try:
#             conn = get_connection()
#             products_df = pd.read_sql("SELECT * FROM dbo.products", conn)
#             conn.close()
#             sales_by_division = (
#                 df.merge(products_df, on="Product_num")
#                   .groupby("Department")["Spend"]
#                   .sum()
#                   .reset_index()
#                   .sort_values("Spend", ascending=False)
#             )
#             fig2 = px.bar(sales_by_division.head(5), x="Department", y="Spend", labels={"Spend":"Sales ($)"})
#             st.plotly_chart(fig2, use_container_width=True)
#         except:
#             st.info("Products data not available.")

#     with c3:
#         st.subheader("Avg Spend & Units per Txn 📈")
#         per_txn = (
#             df.groupby(["Basket_num", "Date"])
#               .agg({"Spend": "sum","Units": "sum"})
#               .reset_index()
#         )
#         per_txn["Month"] = per_txn["Date"].dt.to_period("M").dt.to_timestamp()
#         trend = per_txn.groupby("Month")[["Spend","Units"]].mean().reset_index()
#         fig3 = px.line(trend, x="Month", y=["Spend", "Units"], labels={"value":"Avg Value"})
#         st.plotly_chart(fig3, use_container_width=True)

#     st.divider()

#     ### -------- KPI Metrics (Middle Row) --------
#     m1, m2, m3, m4 = st.columns(4)
#     m1.metric("🔍 Avg Sales/Hour", "$178.67")  # Placeholder values
#     m2.metric("🏬 Total Sales for Depts", "$1.22M")
#     m3.metric("📦 Avg Units/Txn", f"{avg_units_per_txn:.1f}")
#     m4.metric("💸 Avg Revenue/Hour", "$273.80")

#     st.divider()

#     ### -------- 3 Charts in Bottom Row --------
#     b1, b2, b3 = st.columns(3)

#     with b1:
#         st.subheader("Top Products by Sales")
#         top_products = (
#             df.groupby("Product_num")["Units"]
#               .sum()
#               .nlargest(7)
#               .reset_index()
#         )
#         fig4 = px.bar(top_products, x="Product_num", y="Units", labels={"Units":"Units Sold"})
#         st.plotly_chart(fig4, use_container_width=True)

#     with b2:
#         st.subheader("Sales by Region 🌎")
#         region_sales = df.groupby("Store_region")["Spend"].sum().reset_index()
#         fig5 = px.pie(region_sales, names="Store_region", values="Spend")
#         st.plotly_chart(fig5, use_container_width=True)

#     with b3:
#         st.subheader("Out of Stock Placeholder ⚠️")
#         st.info("Placeholder: No stock tracking available.")
#     ### -------- Grid Layout Ends Here --------

from itertools import combinations
from collections import Counter

def dashboard_page():
    st.markdown("<h1 style='color:cyan;'>🛒 Retail KPI Dashboard</h1>", unsafe_allow_html=True)
    st.write("---")

    # 1️⃣ Fetch data
    try:
        conn = get_connection()
        df   = pd.read_sql("SELECT 3000 FROM dbo.transactions", conn)
        conn.close()
    except Exception as e:
        st.error(f"Connection error: {e}")
        return

    if df.empty:
        st.warning("No transaction data found.")
        return

    df["Date"] = pd.to_datetime(df["Date"])

    # 2️⃣ Compute Core Metrics
    total_customers    = df["Hshd_num"].nunique()
    total_transactions = df["Basket_num"].nunique()
    total_sales        = df["Spend"].sum()
    avg_clv            = (
        df.groupby("Hshd_num")["Spend"].sum().mean()
    )  # average total spend per household
    # churn = households with no purchase in last 8 weeks
    last_purchase = df.groupby("Hshd_num")["Date"].max()
    cutoff        = df["Date"].max() - pd.Timedelta(weeks=8)
    churn_rate    = (last_purchase < cutoff).mean()
    # demand forecast = naïve next‐week spend = this week’s total
    weekly = df.set_index("Date").resample("W")["Spend"].sum()
    next_week_forecast = weekly.iloc[-1]
    # avg distinct products per basket
    avg_basket_size = df.groupby("Basket_num")["Product_num"] \
                        .nunique().mean()

    # 3️⃣ Top KPI Row
    k1, k2, k3, k4 = st.columns(4, gap="small")
    k1.metric("🏆 Avg CLV ($)", f"{avg_clv:,.2f}")
    k2.metric("🚩 Churn Rate", f"{churn_rate:.1%}")
    k3.metric("🔮 Next‐Week Spend", f"${next_week_forecast:,.0f}")
    k4.metric("🧺 Avg Products/Basket", f"{avg_basket_size:.1f}")

    st.divider()

    # 4️⃣ Three Charts Row
    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        st.subheader("Visitors & Transactions")
        monthly = df.copy()
        monthly["Month"] = monthly["Date"].dt.to_period("M").dt.to_timestamp()
        ms = (
            monthly.groupby("Month")
                   .agg({"Hshd_num":"nunique","Basket_num":"nunique"})
                   .reset_index()
        )
        fig1 = px.bar(
            ms, x="Month", y=["Hshd_num","Basket_num"],
            barmode="group", labels={"value":"Count","variable":""}
        )
        fig1.update_layout(margin=dict(l=20,r=10,t=25,b=10), height=260, font_size=11)
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Sales by Department")
        products_df = pd.read_sql("SELECT * FROM dbo.products", get_connection())
        sd = (
            df.merge(products_df, on="Product_num")
              .groupby("Department")["Spend"]
              .sum()
              .nlargest(5)
              .reset_index()
        )
        fig2 = px.bar(sd, x="Department", y="Spend", labels={"Spend":"$"})
        fig2.update_layout(margin=dict(l=20,r=10,t=25,b=10), height=260, font_size=11)
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
        st.subheader("Avg Spend & Units/Txn")
        pb = (
            df.groupby(["Basket_num","Date"])
              .agg({"Spend":"sum","Units":"sum"})
              .reset_index()
        )
        pb["Month"] = pb["Date"].dt.to_period("M").dt.to_timestamp()
        tv = pb.groupby("Month")[["Spend","Units"]].mean().reset_index()
        fig3 = px.line(tv, x="Month", y=["Spend","Units"], labels={"value":"Avg/Txn"})
        fig3.update_layout(margin=dict(l=20,r=10,t=25,b=10), height=260, font_size=11)
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # 5️⃣ Bottom Row: Top Products, Region, Basket Analysis
    b1, b2, b3 = st.columns(3, gap="small")

    with b1:
        st.subheader("Top 7 Products by Units")
        tp = df.groupby("Product_num")["Units"].sum().nlargest(7).reset_index()
        fig4 = px.bar(tp, x="Product_num", y="Units", text="Units")
        fig4.update_layout(margin=dict(l=20,r=10,t=25,b=10), height=260, font_size=11)
        fig4.update_traces(textposition="outside")
        st.plotly_chart(fig4, use_container_width=True)

    with b2:
        st.subheader("Sales by Region")
        rs = df.groupby("Store_region")["Spend"].sum().reset_index()
        fig5 = px.pie(rs, names="Store_region", values="Spend")
        fig5.update_layout(margin=dict(l=20,r=10,t=25,b=10), height=260, font_size=11)
        st.plotly_chart(fig5, use_container_width=True)

    with b3:
        st.subheader("Basket Analysis – Top Pairs")
        # find top‐5 co‐purchased product pairs
        pair_counts = Counter()
        for _, sub in df.groupby("Basket_num"):
            items = sub["Product_num"].unique()
            for a, b in combinations(sorted(items), 2):
                pair_counts[(a, b)] += 1
        top_pairs = pair_counts.most_common(5)
        tp_df = pd.DataFrame(top_pairs, columns=["Pair","Count"])
        tp_df["Product A"] = tp_df["Pair"].apply(lambda x: x[0])
        tp_df["Product B"] = tp_df["Pair"].apply(lambda x: x[1])
        st.table(tp_df[["Product A","Product B","Count"]])

    st.divider()


# ─────────────────────────────────────────────────────────────
#  ML MODELS PAGE
# ─────────────────────────────────────────────────────────────
def ml_models_page():
    st.markdown("<h1 style='color:cyan;'>🤖 ML Models</h1>",
                unsafe_allow_html=True)
    st.write("Simple Linear Regression to predict Spend per basket.")
    try:
        conn = get_connection()
        df   = pd.read_sql(
            "SELECT TOP 5000 Units, Week_num, Year, Spend FROM dbo.transactions", 
            conn
        )
        conn.close()
    except Exception as e:
        st.error(f"Connection error: {e}")
        return

    if df.empty:
        st.warning("No data available for ML.")
        return

    X = df[["Units","Week_num","Year"]]
    y = df["Spend"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    model = LinearRegression().fit(X_train, y_train)
    score = model.score(X_test, y_test)
    st.success(f"R² Score: {score:.2f}")

    st.markdown("**Make a prediction**")
    u = st.number_input("Units Purchased", step=1, min_value=1, value=1)
    w = st.number_input("Week Number",    step=1, min_value=1, value=1)
    yv= st.number_input("Year",           step=1, min_value=2000, value=2020)
    if st.button("Predict Spend"):
        p = model.predict([[u,w,yv]])[0]
        st.info(f"Estimated Spend: **${p:,.2f}**")

# ─────────────────────────────────────────────────────────────
#  SEARCH HSHD PAGE
# ─────────────────────────────────────────────────────────────
def search_hshd_page():
    st.markdown("<h1 style='color:cyan;'>🔎 Search Household Data</h1>",
                unsafe_allow_html=True)
    num = st.text_input("Enter Household Number (HSHD_NUM)")
    if st.button("Search"):
        if not num:
            st.warning("Please enter a household number.")
            return
        try:
            conn = get_connection()
            query = """
                SELECT t.Hshd_num, t.Basket_num, t.Date, t.Product_num,
                       p.Department, p.Commodity,
                       t.Spend, t.Units, t.Store_region, t.Week_num, t.Year,
                       h.Loyalty_flag, h.Age_range, h.Marital_status,
                       h.Income_range, h.Homeowner_desc, h.Hshd_composition,
                       h.Hshd_size, h.Children
                FROM dbo.transactions t
                JOIN dbo.products   p ON t.Product_num = p.Product_num
                JOIN dbo.households h ON t.Hshd_num    = h.Hshd_num
                WHERE t.Hshd_num = ?
                ORDER BY t.Date, t.Basket_num, t.Product_num
            """
            df = pd.read_sql(query, conn, params=[num])
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")
            return

        if df.empty:
            st.warning("No data found for that household.")
        else:
            st.dataframe(df, use_container_width=True)

# ─────────────────────────────────────────────────────────────
#  UPLOAD NEW DATA PAGE
# ─────────────────────────────────────────────────────────────
def upload_page():
    st.markdown("<h1 style='color:cyan;'>📥 Upload New Data</h1>",
                unsafe_allow_html=True)
    tbl = st.selectbox("Select Table", ["households","products","transactions"])
    up  = st.file_uploader("Upload a CSV file", type="csv")
    if up:
        df = pd.read_csv(up)
        st.dataframe(df.head(), use_container_width=True)
        if st.button("Upload to Azure SQL"):
            try:
                conn = get_connection()
                cur  = conn.cursor()
                cur.execute(f"DELETE FROM dbo.{tbl};")
                for _, row in df.iterrows():
                    cols        = ",".join(df.columns)
                    placeholders= ",".join("?"*len(df.columns))
                    sql         = f"INSERT INTO dbo.{tbl}({cols}) VALUES({placeholders});"
                    cur.execute(sql, tuple(row))
                conn.commit()
                cur.close()
                conn.close()
                st.success(f"{len(df)} rows uploaded to {tbl}.")
            except Exception as e:
                st.error(f"Upload error: {e}")

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="Retail Analytics App",
        page_icon="🛒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    if not st.session_state.logged_in:
        # Hide any accidental sidebar until login
        st.sidebar.empty()

        if st.session_state.page == "login":
            login_form()
        else:
            signup_form()

    else:
        # Show our custom nav after login
        st.sidebar.title(f"👤 {st.session_state.username}")
        choice = st.sidebar.radio(
            "Navigation",
            ["Dashboard","ML Models","Search HSHD","Upload New Data"]
        )

        if choice == "Dashboard":
            dashboard_page()
        elif choice == "ML Models":
            ml_models_page()
        elif choice == "Search HSHD":
            search_hshd_page()
        else:
            upload_page()

if __name__ == "__main__":
    main()
