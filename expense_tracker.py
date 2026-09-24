import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f8f9fa;
}

h1 {
    color: #4F46E5;
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------

if 'expenses' not in st.session_state:

    st.session_state.expenses = pd.DataFrame(
        columns=[
            'Date',
            'Category',
            'Amount',
            'Description'
        ]
    )


# ---------------------------------------------------
# ADD EXPENSE FUNCTION
# ---------------------------------------------------

def add_expense(date_value, category, amount, description):

    new_expense = pd.DataFrame(
        [[
            date_value,
            category,
            amount,
            description
        ]],
        columns=st.session_state.expenses.columns
    )

    st.session_state.expenses = pd.concat(
        [
            st.session_state.expenses,
            new_expense
        ],
        ignore_index=True
    )


# ---------------------------------------------------
# SAVE EXPENSES
# ---------------------------------------------------

def save_expenses():

    csv_data = st.session_state.expenses.to_csv(
        index=False
    )

    st.download_button(
        label="Download Expenses CSV",
        data=csv_data,
        file_name="expenses.csv",
        mime="text/csv"
    )


# ---------------------------------------------------
# LOAD EXPENSES
# ---------------------------------------------------

def load_expenses(uploaded_file):

    if uploaded_file is not None:

        df = pd.read_csv(uploaded_file)

        required_columns = [
            'Date',
            'Category',
            'Amount',
            'Description'
        ]

        if all(
            column in df.columns
            for column in required_columns
        ):

            df['Date'] = pd.to_datetime(
                df['Date']
            ).dt.date

            st.session_state.expenses = df

            st.success(
                "Expenses loaded successfully!"
            )

        else:

            st.error(
                "Invalid CSV format!"
            )


# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("Jeel's Expense Tracker")

st.caption(
    "Track, analyze and manage your daily expenses easily."
)

st.divider()


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------

with st.sidebar:

    st.header("Add New Expense")

    expense_date = st.date_input(
        "Date",
        value=date.today()
    )

    category = st.selectbox(
        "Category",
        [
            "Food",
            "Transport",
            "Entertainment",
            "Utilities",
            "Shopping",
            "Health",
            "Education",
            "Other"
        ]
    )

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=10.0,
        format="%.2f"
    )

    description = st.text_input(
        "Description",
        placeholder="Example: Lunch, Bus ticket..."
    )

    if st.button(
        "Add Expense",
        use_container_width=True
    ):

        if amount <= 0:

            st.error(
                "Amount must be greater than ₹0."
            )

        elif description.strip() == "":

            st.error(
                "Please enter a description."
            )

        else:

            add_expense(
                expense_date,
                category,
                amount,
                description
            )

            st.success(
                "Expense added successfully!"
            )


    st.divider()

    # ------------------------------------------------
    # FILE OPERATIONS
    # ------------------------------------------------

    st.header("File Operations")

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        load_expenses(uploaded_file)

    st.download_button(
        label="Download CSV",
        data=st.session_state.expenses.to_csv(
            index=False
        ),
        file_name="expenses.csv",
        mime="text/csv",
        use_container_width=True
    )


# ---------------------------------------------------
# MAIN DATA
# ---------------------------------------------------

df = st.session_state.expenses.copy()


# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

st.subheader("Expense Overview")

if not df.empty:

    total_expense = df['Amount'].sum()

    average_expense = df['Amount'].mean()

    highest_expense = df['Amount'].max()

    total_transactions = len(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Expense",
        f"₹{total_expense:,.2f}"
    )

    col2.metric(
        "Average Expense",
        f"₹{average_expense:,.2f}"
    )

    col3.metric(
        "🔝 Highest Expense",
        f"₹{highest_expense:,.2f}"
    )

    col4.metric(
        "Transactions",
        total_transactions
    )

else:

    st.info(
        "No expenses added yet. Add your first expense from the sidebar."
    )


st.divider()


# ---------------------------------------------------
# FILTER SECTION
# ---------------------------------------------------

if not df.empty:

    st.subheader("Filter Expenses")

    col1, col2 = st.columns(2)

    with col1:

        selected_categories = st.multiselect(
            "Select Category",
            options=df['Category'].unique(),
            default=df['Category'].unique()
        )

    with col2:

        min_date = min(df['Date'])
        max_date = max(df['Date'])

        selected_dates = st.date_input(
            "Select Date Range",
            value=(min_date, max_date)
        )

    filtered_df = df[
        df['Category'].isin(
            selected_categories
        )
    ]

    if len(selected_dates) == 2:

        start_date = selected_dates[0]
        end_date = selected_dates[1]

        filtered_df = filtered_df[
            (filtered_df['Date'] >= start_date) &
            (filtered_df['Date'] <= end_date)
        ]

else:

    filtered_df = df


# ---------------------------------------------------
# EXPENSE TABLE
# ---------------------------------------------------

st.subheader("Expense Records")

if not filtered_df.empty:

    display_df = filtered_df.copy()

    display_df['Amount'] = display_df[
        'Amount'
    ].apply(
        lambda x: f"₹{x:,.2f}"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.warning(
        "No expenses found for the selected filters."
    )


# ---------------------------------------------------
# DELETE EXPENSE
# ---------------------------------------------------

if not df.empty:

    st.subheader("Delete Expense")

    expense_index = st.selectbox(
        "Select expense to delete",
        options=df.index,
        format_func=lambda x:
        f"{df.loc[x, 'Date']} | "
        f"{df.loc[x, 'Category']} | "
        f"₹{df.loc[x, 'Amount']}"
    )

    if st.button(
        "Delete Selected Expense"
    ):

        st.session_state.expenses = (
            st.session_state.expenses.drop(
                expense_index
            ).reset_index(drop=True)
        )

        st.success(
            "Expense deleted successfully!"
        )

        st.rerun()


st.divider()


# ===================================================
# VISUALIZATION SECTION
# ===================================================

if not filtered_df.empty:

    st.header("Expense Analytics")

    # ------------------------------------------------
    # CATEGORY BAR CHART
    # ------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Expense by Category"
        )

        category_data = (
            filtered_df
            .groupby('Category')['Amount']
            .sum()
            .sort_values(
                ascending=False
            )
        )

        fig, ax = plt.subplots(
            figsize=(8, 5)
        )

        sns.barplot(
            x=category_data.values,
            y=category_data.index,
            ax=ax
        )

        ax.set_xlabel(
            "Total Expense (₹)"
        )

        ax.set_ylabel(
            "Category"
        )

        st.pyplot(fig)

        plt.close(fig)


    # ------------------------------------------------
    # PIE CHART
    # ------------------------------------------------

    with col2:

        st.subheader(
            "Expense Distribution"
        )

        category_data = (
            filtered_df
            .groupby('Category')['Amount']
            .sum()
        )

        fig, ax = plt.subplots(
            figsize=(7, 5)
        )

        ax.pie(
            category_data.values,
            labels=category_data.index,
            autopct='%1.1f%%',
            startangle=90
        )

        ax.set_title(
            "Category-wise Distribution"
        )

        st.pyplot(fig)

        plt.close(fig)


    # ------------------------------------------------
    # MONTHLY EXPENSE TREND
    # ------------------------------------------------

    st.subheader(
        "Monthly Expense Trend"
    )

    trend_df = filtered_df.copy()

    trend_df['Date'] = pd.to_datetime(
        trend_df['Date']
    )

    trend_df['Month'] = (
        trend_df['Date']
        .dt.to_period('M')
        .astype(str)
    )

    monthly_expense = (
        trend_df
        .groupby('Month')['Amount']
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(
        figsize=(12, 5)
    )

    sns.lineplot(
        data=monthly_expense,
        x='Month',
        y='Amount',
        marker='o',
        ax=ax
    )

    ax.set_xlabel(
        "Month"
    )

    ax.set_ylabel(
        "Expense (₹)"
    )

    plt.xticks(
        rotation=45
    )

    st.pyplot(fig)

    plt.close(fig)


    # ------------------------------------------------
    # TOP EXPENSES
    # ------------------------------------------------

    st.subheader(
        "Top 5 Expenses"
    )

    top_expenses = (
        filtered_df
        .sort_values(
            by='Amount',
            ascending=False
        )
        .head(5)
    )

    st.dataframe(
        top_expenses,
        use_container_width=True,
        hide_index=True
    )


else:

    st.info(
        "Add expenses to see analytics and charts."
    )


# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------

st.divider()

st.caption(
    "Jeel's Expense Tracker "
)