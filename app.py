import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Initialize list of expenses in session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = []

st.title("Personal Expense Tracker")

# Input fields
category = st.text_input("Category")
amount = st.number_input("Amount", min_value=0.0, format="%.2f")
date_str = st.text_input("Date (YYYY-MM-DD)")

# Add expense on button click
if st.button("Add Expense"):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        st.session_state.expenses.append({'category': category, 'amount': amount, 'date': date})
        st.success(f"Added: {category} - ${amount:.2f} on {date_str}")
    except ValueError:
        st.error("Invalid date format. Use YYYY-MM-DD.")

# Function to convert DataFrame to CSV bytes
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Display expenses and summaries if any
if st.session_state.expenses:
    df = pd.DataFrame(st.session_state.expenses)
    
    st.subheader("Expenses List")
    st.dataframe(df)

    # Summary by month
    df['period'] = df['date'].dt.to_period('M').apply(lambda r: r.start_time)
    summary = df.groupby(['period', 'category'])['amount'].sum().unstack(fill_value=0)
    summary['Total'] = summary.sum(axis=1)

    st.subheader("Monthly Summary")
    st.dataframe(summary)

    # Export buttons
    if st.button("Download Expenses CSV"):
        csv = convert_df_to_csv(df)
        st.download_button(label="Download Expenses CSV", data=csv, file_name="expenses.csv", mime="text/csv")

    if st.button("Download Monthly Summary CSV"):
        summary_reset = summary.reset_index()
        csv = convert_df_to_csv(summary_reset)
        st.download_button(label="Download Summary CSV", data=csv, file_name="monthly_summary.csv", mime="text/csv")

    # Function to plot expenses
    def plot_expenses(df, period='week'):
        if period == 'week':
            df['period'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
        elif period == 'month':
            df['period'] = df['date'].dt.to_period('M').apply(lambda r: r.start_time)
        else:
            st.error("Period must be 'week' or 'month'.")
            return

        summary = df.groupby(['period', 'category'])['amount'].sum().unstack(fill_value=0)

        fig, ax = plt.subplots(figsize=(10,6))
        summary.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title(f'Expenses by Category - {period.capitalize()}')
        ax.set_xlabel('Period')
        ax.set_ylabel('Amount ($)')
        ax.legend(title='Category')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
    
    # Show monthly chart
    st.subheader("Monthly Expenses Chart")
    plot_expenses(df, period='month')

    # Show weekly chart
    st.subheader("Weekly Expenses Chart")
    plot_expenses(df, period='week')
