import streamlit as st
import pandas as pd
from datetime import date
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt

# --- PAGE CONFIG ---
st.set_page_config(page_title="Triveni Enterprises", layout="wide", page_icon="🏗️")

# --- GOOGLE SHEETS SETUP ---
@st.cache_resource
def get_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ],
    )
    return gspread.authorize(creds)

def get_sheet(sheet_name):
    client = get_client()
    return client.open("TriveniData").worksheet(sheet_name)

def delete_row(sheet_name, row_index):
    sheet = get_sheet(sheet_name)
    sheet.delete_rows(row_index)

def update_row(sheet_name, row_index, row_data):
    sheet = get_sheet(sheet_name)
    end_col = chr(65 + len(row_data) - 1)  # A, B, C...
    sheet.update(f"A{row_index}:{end_col}{row_index}", [row_data])

@st.cache_data(ttl=5)
def load_data(sheet_name, columns):
    sheet = get_sheet(sheet_name)
    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    if df.empty:
        df = pd.DataFrame(columns=columns)

    # Add index column to track row number in sheet
    df["row_index"] = range(2, len(df) + 2)  # row 1 is header

    return df

def append_data(sheet_name, row):
    sheet = get_sheet(sheet_name)
    sheet.append_row(row)

# --- LANGUAGE SYSTEM ---
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

lang = st.sidebar.radio("🌐 Language / भाषा", ["EN", "HI"],
                        index=0 if st.session_state.lang == "EN" else 1)
st.session_state.lang = lang

# --- TRANSLATIONS ---
T = {
    "EN": {
        "title": "🏗️ Triveni Enterprises",
        "login": "Secure Login",
        "password": "Enter Password",
        "login_btn": "Login",
        "wrong_pass": "Wrong password!",
        "menu": "Menu",
        "dashboard": "🏠 Dashboard",
        "new_sale": "💰 New Sale & Billing",
        "ledger": "📊 Ledger",
        "expense": "💸 Add Expense",
        "logout": "Logout",
        "status": "Business Overview",
        "income": "Total Income",
        "pending": "Total Pending",
        "expense_total": "Total Expense",
        "cust_name": "Customer Name",
        "phone": "Phone Number",
        "bill": "Total Bill (₹)",
        "paid": "Paid Amount (₹)",
        "save_bill": "Save Bill",
        "ledger_title": "Pending Ledger",
        "no_pending": "No pending dues!",
        "expense_desc": "Expense Description",
        "category": "Category",
        "amount": "Amount",
        "save_exp": "Save Expense",
        "exp_saved": "Expense saved!",
        "sales_history": "📜 Sales History",
        "payment_history": "💰 Payment History",
        "expense_history": "💸 Expense History",
        "edit_mode": "✏️ Edit Mode",
        "save_changes": "💾 Save Changes",
        "delete_selected": "🗑️ Delete Selected",
        "select_rows_delete": "Select rows to delete",
        "changes_saved": "Changes saved!",
        "rows_deleted": "Selected rows deleted!",
        "enter_name": "Please enter customer name",
        "enter_desc": "Please enter description",
        "saved": "Saved successfully!",
        "pay": "Pay",
        "payment_amount": "Payment Amount",
        "record_payment": "Record Payment",
        "payment_recorded": "Payment recorded!"
    },
    "HI": {
        "title": "🏗️ त्रिवेणी एंटरप्राइजेज",
        "login": "सुरक्षित लॉगिन",
        "password": "पासवर्ड दर्ज करें",
        "login_btn": "लॉगिन",
        "wrong_pass": "गलत पासवर्ड!",
        "menu": "मेन्यू",
        "dashboard": "🏠 डैशबोर्ड",
        "new_sale": "💰 नई बिक्री & बिल",
        "ledger": "📊 उधारी",
        "expense": "💸 खर्च दर्ज करें",
        "logout": "लॉगआउट",
        "status": "व्यापार की स्थिति",
        "income": "कुल आय",
        "pending": "कुल उधारी",
        "expense_total": "कुल खर्च",
        "cust_name": "ग्राहक का नाम",
        "phone": "मोबाइल नंबर",
        "bill": "कुल बिल राशि (₹)",
        "paid": "जमा राशि (₹)",
        "save_bill": "बिल सेव करें",
        "ledger_title": "उधारी खाता",
        "no_pending": "कोई उधारी नहीं!",
        "expense_desc": "खर्च का विवरण",
        "category": "श्रेणी",
        "amount": "रकम",
        "save_exp": "खर्च सेव करें",
        "exp_saved": "खर्च सेव हो गया!",
        "sales_history": "📜 बिक्री हिस्ट्री",
        "payment_history": "💰 भुगतान हिस्ट्री",
        "expense_history": "💸 खर्च हिस्ट्री",
        "edit_mode": "✏️ एडिट मोड",
        "save_changes": "💾 बदलाव सेव करें",
        "delete_selected": "🗑️ चयनित डिलीट करें",
        "select_rows_delete": "डिलीट करने के लिए रो चुनें",
        "changes_saved": "बदलाव सेव हो गए!",
        "rows_deleted": "चयनित रो डिलीट हो गईं!",
        "enter_name": "कृपया ग्राहक का नाम दर्ज करें",
        "enter_desc": "कृपया विवरण दर्ज करें",
        "saved": "सफलतापूर्वक सेव हो गया!",
        "pay": "भुगतान",
        "payment_amount": "भुगतान राशि",
        "record_payment": "भुगतान रिकॉर्ड करें",
        "payment_recorded": "भुगतान रिकॉर्ड हो गया!"
    }
}

def t(key):
    return T[st.session_state.lang][key]

# --- CATEGORY MAP ---
CATEGORY_MAP = {
    "EN": ["Raw Material", "Labor", "Electricity/Diesel", "Other"],
    "HI": ["कच्चा माल", "लेबर", "बिजली/डीजल", "अन्य"]
}

# --- SHEET NAMES ---
SALES_SHEET = "Sales"
EXPENSE_SHEET = "Expenses"
PAYMENT_SHEET = "Payment"

# --- LOAD DATA ---
sales_df = load_data(SALES_SHEET, ["date", "customer", "phone", "block", "bill", "paid", "balance"])
expense_df = load_data(EXPENSE_SHEET, ["date", "desc", "cat", "amt"])
payments_df = load_data(PAYMENT_SHEET, ["date", "customer", "phone", "amount"])

# Ensure numeric
sales_df["paid"] = pd.to_numeric(sales_df.get("paid"), errors="coerce").fillna(0)
sales_df["balance"] = pd.to_numeric(sales_df.get("balance"), errors="coerce").fillna(0)
sales_df["phone"] = sales_df["phone"].astype(str)
expense_df["amt"] = pd.to_numeric(expense_df.get("amt"), errors="coerce").fillna(0)
payments_df["amount"] = pd.to_numeric(payments_df.get("amount"), errors="coerce").fillna(0)
payments_df["phone"] = payments_df["phone"].astype(str)

# --- LOGIN ---
def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.title(t("title"))
        st.subheader(t("login"))

        with st.form("login_form"):
            pwd = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login_btn"))

            if submitted:
                if pwd == st.secrets["db_password"]:
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error(t("wrong_pass"))

        st.stop()
    return True

# --- MAIN APP ---
if check_password():

    if "choice" not in st.session_state:
        st.session_state.choice = t("dashboard")

    if "cust_name" not in st.session_state:
        st.session_state.cust_name = ""

    if "phone" not in st.session_state:
        st.session_state.phone = ""

    if "pay_customer" not in st.session_state:
        st.session_state.pay_customer = None

    st.sidebar.title(t("menu"))
    
    # Add spacing to ensure sidebar dropdown goes down
    st.sidebar.markdown("---")
    st.sidebar.markdown("###")

    menu = [
        t("dashboard"),
        t("new_sale"),
        t("ledger"),
        t("expense"),
        t("sales_history"),
        t("payment_history"),
        t("expense_history")
    ]

    choice = st.sidebar.selectbox("Select", menu, index=menu.index(st.session_state.choice) if st.session_state.choice in menu else 0)

    if st.sidebar.button(t("logout")):
        st.session_state.auth = False
        st.rerun()

    # --- DASHBOARD ---
    if choice == t("dashboard"):
        st.header(t("status"))

        col1, col2, col3 = st.columns(3)

        col1.metric(t("income"), f"₹{sales_df['paid'].sum():,.2f}")
        
        # Calculate pending: sales balances minus total payments
        sales_only = sales_df[sales_df['bill'] > 0]
        sales_balance_total = sales_only['balance'].sum() if not sales_only.empty else 0
        
        payments_total = payments_df['amount'].sum() if not payments_df.empty else 0
        
        pending_amount = sales_balance_total - payments_total
        
        col2.metric(t("pending"), f"₹{max(pending_amount, 0):,.2f}")
        col3.metric(t("expense_total"), f"₹{expense_df['amt'].sum():,.2f}")

        st.markdown("---")
        if st.button("➕ " + t("new_sale")):
            st.session_state.choice = t("new_sale")
            st.rerun()

    # --- NEW SALE ---
    elif choice == t("new_sale"):
        st.subheader(t("new_sale"))

        with st.form("sale"):
            cust_input = st.text_input(t("cust_name"), value=st.session_state.cust_name, key="cust_input")

            # Create container for dropdown to ensure it drops down
            with st.container():
                st.markdown("###")  # Add some vertical space
                
                # Get matching customers
                matches = sales_df['customer'].unique() if not cust_input else sales_df[sales_df['customer'].str.lower().str.startswith(cust_input.lower())]['customer'].unique()

                selected = st.selectbox("Select existing customer (optional)", [""] + list(matches), key="select_cust")

            if selected and selected != cust_input:
                st.session_state.cust_name = selected
                st.session_state.phone = sales_df[sales_df['customer'] == selected]['phone'].iloc[0] if len(sales_df[sales_df['customer'] == selected]) > 0 else ""
                st.rerun()

            phone = st.text_input(t("phone"), value=st.session_state.phone, key="phone_input")
            bill = st.number_input(t("bill"), min_value=0.0)
            paid = st.number_input(t("paid"), min_value=0.0)

            if st.form_submit_button(t("save_bill")):
                cust = cust_input
                if cust:
                    bal = bill - paid

                    append_data(SALES_SHEET, [
                        str(date.today()),
                        cust,
                        phone,
                        "",
                        bill,
                        paid,
                        bal
                    ])

                    st.success(t("saved"))
                    st.cache_data.clear()
                    # Reset session state
                    st.session_state.cust_name = ""
                    st.session_state.phone = ""
                    st.rerun()
                else:
                    st.error(t("enter_name"))

    # --- EXPENSE ---
    elif choice == t("expense"):
        st.subheader(t("expense"))

        with st.form("exp"):
            desc = st.text_input(t("expense_desc"))
            cat = st.selectbox(t("category"), CATEGORY_MAP[st.session_state.lang])
            amt = st.number_input(t("amount"), min_value=0.0)

            if st.form_submit_button(t("save_exp")):
                if desc and amt > 0:
                    append_data(EXPENSE_SHEET, [
                        str(date.today()),
                        desc,
                        cat,
                        amt
                    ])

                    st.success(t("exp_saved"))
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(t("enter_desc"))

    # --- LEDGER ---
    elif choice == t("ledger"):
        st.subheader(t("ledger"))

        # Calculate net balance for each customer
        # Sum balances from sales (bill > 0)
        sales_balances = sales_df[sales_df['bill'] > 0].groupby('customer').agg({'balance': 'sum', 'phone': 'first'}).reset_index()
        sales_balances.columns = ['customer', 'sales_balance', 'phone']
        
        # Calculate total payments made by each customer from payments sheet
        if not payments_df.empty:
            payments = payments_df.groupby('customer')['amount'].sum().reset_index()
            payments.columns = ['customer', 'total_paid']
            pending_customers = sales_balances.merge(payments, on='customer', how='left')
            pending_customers['total_paid'] = pending_customers['total_paid'].fillna(0)
            pending_customers['balance'] = pending_customers['sales_balance'] - pending_customers['total_paid']
            pending_customers = pending_customers[['customer', 'balance', 'phone']]
        else:
            pending_customers = sales_balances.rename(columns={'sales_balance': 'balance'})
        
        pending_customers = pending_customers[pending_customers['balance'] > 0]

        if pending_customers.empty:
            st.info(t("no_pending"))
        else:
            for _, row in pending_customers.iterrows():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{row['customer']}** - {row['phone']}")
                with col2:
                    st.write(f"Pending: ₹{row['balance']:,.2f}")
                with col3:
                    if st.button(t("pay"), key=f"pay_{row['customer']}"):
                        st.session_state.pay_customer = row['customer']
                        st.rerun()

        if st.session_state.pay_customer:
            st.markdown("---")
            st.subheader(f"{t('pay')} for {st.session_state.pay_customer}")
            pending = float(pending_customers[pending_customers['customer'] == st.session_state.pay_customer]['balance'].iloc[0])
            phone = str(pending_customers[pending_customers['customer'] == st.session_state.pay_customer]['phone'].iloc[0])

            with st.form("pay_form"):
                amount = st.number_input(t("payment_amount"), min_value=0.0, max_value=pending, value=pending, step=0.01)
                if st.form_submit_button(t("record_payment")):
                    append_data(PAYMENT_SHEET, [
                        str(date.today()),
                        st.session_state.pay_customer,
                        phone,
                        float(amount)
                    ])
                    st.success(t("payment_recorded"))
                    st.cache_data.clear()
                    st.session_state.pay_customer = None
                    st.rerun()

    # --- SALES HISTORY ---
    elif choice == t("sales_history"):
        st.subheader(t("sales_history"))

        # Filter to show only actual sales (bill > 0)
        sales_only_df = sales_df[sales_df['bill'] > 0]

        if sales_only_df.empty:
            st.info("No sales data available.")
        else:
            st.dataframe(sales_only_df.drop(columns=["row_index"]), use_container_width=True)

            # Delete in view mode
            st.subheader("Delete Records")
            selected_rows = st.multiselect(
                t("select_rows_delete"),
                sales_only_df.index,
                format_func=lambda x: f"{sales_only_df.loc[x, 'customer']} - {sales_only_df.loc[x, 'date']}",
                key="sales_delete_view"
            )

            if st.button(t("delete_selected"), key="delete_sales_view"):
                if selected_rows:
                    for i in sorted(selected_rows, reverse=True):
                        delete_row(SALES_SHEET, int(sales_only_df.loc[i, "row_index"]))

                    st.success(t("rows_deleted"))
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("No rows selected for deletion.")

    # --- PAYMENT HISTORY ---
    elif choice == t("payment_history"):
        st.subheader(t("payment_history"))

        if payments_df.empty:
            st.info("No payment data available.")
        else:
            st.dataframe(payments_df.drop(columns=["row_index"]), use_container_width=True)

            # Delete in view mode
            st.subheader("Delete Records")
            selected_rows = st.multiselect(
                t("select_rows_delete"),
                payments_df.index,
                format_func=lambda x: f"{payments_df.loc[x, 'customer']} - {payments_df.loc[x, 'date']}",
                key="payments_delete_view"
            )

            if st.button(t("delete_selected"), key="delete_payments_view"):
                if selected_rows:
                    for i in sorted(selected_rows, reverse=True):
                        delete_row(PAYMENT_SHEET, int(payments_df.loc[i, "row_index"]))

                    st.success(t("rows_deleted"))
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("No rows selected for deletion.")

    # --- EXPENSE HISTORY ---
    elif choice == t("expense_history"):
        st.subheader(t("expense_history"))

        if expense_df.empty:
            st.info("No expense data available.")
        else:
            # Expense Breakdown Pie Chart at top
            st.subheader("Expense Breakdown")
            expense_by_cat = expense_df.groupby("cat")["amt"].sum()
            
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = plt.cm.tab10.colors[:len(expense_by_cat)]
            wedges, texts, autotexts = ax.pie(expense_by_cat.values, labels=expense_by_cat.index, autopct='%1.1f%%', startangle=90, colors=colors)
            for text, color in zip(texts, colors):
                text.set_color(color)
            ax.axis('equal')
            fig.patch.set_alpha(0)
            st.pyplot(fig)

            st.markdown("---")

            # Expense records below
            st.dataframe(expense_df.drop(columns=["row_index"]), use_container_width=True)

            # Delete in view mode
            st.subheader("Delete Records")
            selected_rows = st.multiselect(
                t("select_rows_delete"),
                expense_df.index,
                format_func=lambda x: f"{expense_df.loc[x, 'desc']} - {expense_df.loc[x, 'date']}",
                key="expense_delete_view"
            )

            if st.button(t("delete_selected"), key="delete_expense_view"):
                if selected_rows:
                    for i in sorted(selected_rows, reverse=True):
                        delete_row(EXPENSE_SHEET, int(expense_df.loc[i, "row_index"]))

                    st.success(t("rows_deleted"))
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.warning("No rows selected for deletion.")