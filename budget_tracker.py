import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth

# User credentials
credentials = {
    "usernames": {
        "user1": {
            "name": "John Doe",
            "password": "hashed_password",  # Replace with a hashed password
        },
        "user2": {
            "name": "Jane Smith",
            "password": "hashed_password",  # Replace with a hashed password
        },
    }
}

# Authentication
authenticator = stauth.Authenticate(
    credentials, "BudgetApp", "secret_key", cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login("Login", "sidebar")

if authentication_status:
    st.sidebar.success(f"Welcome {name}!")
elif authentication_status is False:
    st.sidebar.error("Username/password is incorrect")
    st.stop()
elif authentication_status is None:
    st.sidebar.warning("Please enter your username and password")
    st.stop()

# Initialize session state for transactions
if "transactions" not in st.session_state:
    st.session_state["transactions"] = []

# Helper functions
def add_transaction(type_, amount, category, date):
    st.session_state["transactions"].append({
        "Type": type_,
        "Amount": amount,
        "Category": category,
        "Date": date.strftime("%Y-%m-%d"),
    })

def get_summary():
    df = pd.DataFrame(st.session_state["transactions"])
    income = df[df["Type"] == "Income"]["Amount"].sum() if not df.empty else 0
    expenses = df[df["Type"] == "Expense"]["Amount"].sum() if not df.empty else 0
    balance = income - expenses
    return income, expenses, balance

# App UI
st.title("Budget Tracker App")

# Input form
st.header("Add a Transaction")
with st.form("transaction_form"):
    col1, col2, col3 = st.columns(3)
    type_ = col1.selectbox("Type", ["Income", "Expense"])
    amount = col2.number_input("Amount", min_value=0.0, format="%.2f")
    category = col3.text_input("Category")
    date = st.date_input("Date")
    submitted = st.form_submit_button("Add")
    if submitted and amount > 0 and category:
        add_transaction(type_, amount, category, date)
        st.success(f"{type_} of ${amount:.2f} in '{category}' added!")

# Display summary
st.header("Summary")
income, expenses, balance = get_summary()
st.metric("Total Income", f"${income:.2f}")
st.metric("Total Expenses", f"${expenses:.2f}")
st.metric("Balance", f"${balance:.2f}")

# Notifications
st.header("Notifications")
def check_budget():
    df = pd.DataFrame(st.session_state["transactions"])
    if not df.empty:
        total_expenses = df[df["Type"] == "Expense"]["Amount"].sum()
        budget_limit = st.number_input("Set a budget limit", min_value=0.0, step=1.0)

        if total_expenses > budget_limit:
            st.error(f"Warning: You have exceeded your budget by ${total_expenses - budget_limit:.2f}!")
        else:
            st.success(f"You are within your budget. Remaining: ${budget_limit - total_expenses:.2f}")

check_budget()

# Transaction history
st.header("Transaction History")
if st.session_state["transactions"]:
    df = pd.DataFrame(st.session_state["transactions"])
    st.dataframe(df)

# Income vs Expense Chart
st.header("Income vs Expense Chart")
def income_vs_expense_chart():
    df = pd.DataFrame(st.session_state["transactions"])
    if not df.empty:
        income = df[df["Type"] == "Income"]["Amount"].sum()
        expenses = df[df["Type"] == "Expense"]["Amount"].sum()

        fig, ax = plt.subplots()
        ax.bar(["Income", "Expenses"], [income, expenses], color=["green", "red"])
        ax.set_title("Income vs Expenses")
        st.pyplot(fig)
    else:
        st.info("No data to display.")

income_vs_expense_chart()

# Pie Chart Visualization
st.subheader("Expense Breakdown")
if st.session_state["transactions"]:
    df = pd.DataFrame(st.session_state["transactions"])
    expense_data = df[df["Type"] == "Expense"]
    if not expense_data.empty:
        expense_summary = expense_data.groupby("Category")["Amount"].sum()
        fig, ax = plt.subplots()
        expense_summary.plot.pie(ax=ax, autopct='%1.1f%%', startangle=90)
        ax.set_ylabel("")
        st.pyplot(fig)
    else:
        st.info("No transactions added yet.")