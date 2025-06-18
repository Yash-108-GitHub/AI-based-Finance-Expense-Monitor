import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime
import calendar
from streamlit_option_menu import option_menu
import plotly.express as px

import plotly.graph_objects as go

import geocoder
import requests
import os
import streamlit as st
import sqlite3



st.set_page_config(layout ="wide")

# Ensure the user is logged in
#Check if a user is logged in
#❌ st.session_state does NOT check login automatically
#✅ You must manually set and check a "user" key in st.session_state
#✅ Use it to store login status across pages and reruns
if "user" not in st.session_state or st.session_state["user"] is None:   #"user" is a variable , user=none
    st.warning("Please log in to access this page.")
    st.stop() # halts the running if the user is not logged in


# Connect to SQLite database
conn = sqlite3.connect('data.db', check_same_thread=False)
cur = conn.cursor()

# Check if the finance_data table already exists and has the correct columns
cur.execute("PRAGMA table_info(finance_data)")
columns = [col[1] for col in cur.fetchall()]

     #yash#
if 'username' not in columns:
    # Rename the finance_data table to new_finance_data
    cur.execute("ALTER TABLE finance_data RENAME TO new_finance_data")
    conn.commit()

    # Create the finance_data table with the correct columns
    cur.execute('''
    CREATE TABLE IF NOT EXISTS finance_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        period TEXT,
        type TEXT,
        category TEXT,
        amount INTEGER,
        remarks TEXT
    )
    ''')
    conn.commit()

    # copy new_finance_data  into finance_data
    cur.execute('''
    INSERT INTO finance_data (username, period, type, category, amount, remarks)
    SELECT username, period, type, category, amount, remarks FROM new_finance_data
    ''')
    conn.commit()

    # Drop the temporary table
    cur.execute("DROP TABLE new_finance_data")
    conn.commit()


# Function to add or update data
def addOrUpdateData(username, period, category, amount, remarks, data_type):
    # Check if data already exists for the given period and category
      #tuple#
    existing_data = cur.execute("SELECT id FROM finance_data WHERE username = ? AND period = ? AND category = ? AND type = ?", 
           # | 
                            (username, period, category, data_type)).fetchone()
    if existing_data:
        # Update existing data
        cur.execute('''
            UPDATE finance_data 
            SET amount = ?, remarks = ?
            WHERE id = ?
            ''', (amount, remarks, existing_data[0]))
    else:
        # Add new data\row
        cur.execute('''
            INSERT INTO finance_data (username, period, type, category, amount, remarks)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, period, data_type, category, amount, remarks))
    conn.commit()


# Get the logged-in user's username
username = st.session_state["username"]


# Create tabs
tab1, tab2 , tab3 = st.tabs(["MY dashboard", " Finance Tracker","AI suggestions"])

with tab1:
        st.title("My Dashboard")

        # Retrieve finance data for all periods
        income_data = cur.execute("SELECT period, amount, category FROM finance_data WHERE type = 'Income' AND username = ?", (username,)).fetchall()
        expense_data = cur.execute("SELECT period, amount, category FROM finance_data WHERE type = 'Expense' AND username = ?", (username,)).fetchall()
        
        currency="INR"
        total_income = sum(data[1] for data in income_data)
        total_expense = sum(data[1] for data in expense_data)
        remaining = total_income - total_expense

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Income:", "{:,} {}".format(total_income, currency))
        col2.metric("Total Expense:", "{:,} {}".format(total_expense, currency))
        col3.metric("Total Remaining:", "{:,} {}".format(remaining, currency))
     
#--------------------------------------------------------------------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------------------------------------------#
        #** bar char for income**#

        # Convert fetched data into pandas DataFrame
        income_df = pd.DataFrame(income_data, columns=["Period", "Income","Category"])
        # Group by category and sum the income for each category
        income_grouped = income_df.groupby("Category").sum().reset_index()
        
        neon_green_palette = ['#2b9348', '#3eaf7c', '#57cc99', '#64dfdf', '#72efdd', '#64dfdf', '#72efdd', '#64dfdf', '#50c9c3', '#40b3a2']

        # Create a bar plot for total income by category
        fig2 = px.bar(income_grouped, x='Category', y='Income', title='Net Income by Category',color='Category', color_discrete_sequence=neon_green_palette)
        fig2.update_layout(xaxis_title='Category', yaxis_title='Total Income (INR)')
#-----------------------------------------------------------------------------------------------------------------------------------------------------#
        # **bar char for expense**#

        # Convert fetched data into pandas DataFrame
        expense_df = pd.DataFrame(expense_data, columns=["Period", "Expense","Category"])
        # Group by category and sum the income for each category
        expense_grouped = expense_df.groupby("Category").sum().reset_index()

        neon_colors = ['#FF005E', '#F30476', '#E7098E', '#DC0DA6', '#D011BD', '#C416D5', '#B81AED', '#4361ee', '#4895ef', '#4cc9f0']

        # Create a bar plot for total income by category
        fig3 = px.bar(expense_grouped, x='Category', y='Expense', title='Net Expenses by Category', color='Category', color_discrete_sequence=neon_colors)
        fig3.update_layout(xaxis_title='Category', yaxis_title='Total Expenses (INR)')
#--------------------------------------------------------------------------------------------------------------------------------------------------------#

        # **line chart for income vs expense**#

        #Concatenate income and expense data
        merged_df = pd.concat([income_df, expense_df])

        # Extract month and year from the period
        merged_df["Month"] = merged_df["Period"].str.split("_").str[1]

        # Group by month and sum the amounts
        grouped_df = merged_df.groupby("Month").sum().reset_index()
 
        fig1 = px.line(grouped_df, x='Month', y=['Income', 'Expense'], title='Total Income and Expense over Months' ,color_discrete_map={'Income': 'green', 'Expense': 'red'})
        fig1.update_layout(xaxis_title='Month', yaxis_title='Amount (INR)')
#--------------------------------------------------------------------------------------------------------------------------------------------------------#
  #display the graphs
        # fig 1      
        st.plotly_chart(fig1)  # Replace fig1 with the chart variable for the first chart
        st.markdown( "<hr style='border: 1px solid gray; border-radius: 4px;'>", unsafe_allow_html=True)
        st.write("")
        st.write("")
        
        #fig2&3
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig2)  # Replace fig2 with the chart variable for the second chart

        with col2:
            st.plotly_chart(fig3)  # Replace fig3 with the chart variable for the third chart

#----------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------------------------------------#


with tab2:
    st.title("Income and Expense Tracker")
    incomes = ["Salary", "Stocks", "Other Income"] #list
    expenses = ["Rent", "Utilities", "Groceries", "Car", "Insurance", "Savings", "Miscellaneous"]
    currency = "INR"

    years = [datetime.today().year, datetime.today().year + 1]
    months = list(calendar.month_name[1:]) # tuple ek ek month reurn krega.

    selected = option_menu(
        menu_title=None,
        icons=["pencil-fill", "bar-chart-fill"],

        options=["Data Entry", "Data Visualization"],
          orientation="horizontal",
    )

    if selected == "Data Entry":
        with st.form("entry_form", clear_on_submit=True): #entry_form is just n name
            col1, col2 = st.columns(2)
            month = col1.selectbox("Select Month", months, key='month')  #Select Month is label and key=month is used for store month properly
            year = col2.selectbox("Select Year", years, key='year')

            with st.expander("Income"):
                for income in incomes:
                    st.number_input(f"{income}:", min_value=0, format="%i", step=100, key=income)
            with st.expander("Expenses"):
                for expense in expenses:
                    st.number_input(f"{expense}:", min_value=0, format="%i", step=100, key=expense)
            with st.expander("Remarks"):
                comment = st.text_area("", placeholder="Enter Remarks")
            

            submitted = st.form_submit_button("Save Data")
        
            if submitted:
                period = f"{year}_{month}"
                for income in incomes:
                    addOrUpdateData(username, period, income, st.session_state[income], comment, 'Income')
                for expense in expenses:
                    addOrUpdateData(username, period, expense, st.session_state[expense], comment, 'Expense')
                st.success("Data Saved")

    elif selected == "Data Visualization":
        st.header("Data Visualization")
        periods = cur.execute("SELECT DISTINCT period FROM finance_data WHERE username = ?", (username,)).fetchall()
        periods = [period[0] for period in periods]

        with st.form("saved_periods"): #just form name
            period = st.selectbox("Select Period:", periods)
            submitted = st.form_submit_button("Plot Period")

            if submitted:
                income_data = cur.execute("SELECT category, amount FROM finance_data WHERE period = ? AND type = 'Income' AND username = ?", (period, username)).fetchall()
                expense_data = cur.execute("SELECT category, amount FROM finance_data WHERE period = ? AND type = 'Expense' AND username = ?", (period, username)).fetchall()

                incomes = {data[0]: data[1] for data in income_data}
                expenses = {data[0]: data[1] for data in expense_data}

                total_income = sum(incomes.values())# 5000 + 1000 + 2000 = 8000
                total_expense = sum(expenses.values())# 1000 + 2000 + 2000 = 5000
                remaining = total_income - total_expense #8000-5000=3000

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Income:", "{:,} {}".format(total_income, currency))
                col2.metric("Total Expense:", "{:,} {}".format(total_expense, currency))
                col3.metric("Total Remaining:", "{:,} {}".format(remaining, currency))


                income_df = pd.DataFrame.from_dict(incomes, orient='index', columns=['Amount'])
                expense_df = pd.DataFrame.from_dict(expenses, orient='index', columns=['Amount'])

                # Define custom color palette
                neon_pink_palette = ['#FF005E', '#F30476', '#E7098E', '#DC0DA6', '#D011BD', '#C416D5', '#B81AED', '#4361ee', '#4895ef', '#4cc9f0']
                neon_green_palette = ['#2b9348', '#3eaf7c', '#57cc99', '#64dfdf', '#72efdd', '#64dfdf', '#72efdd', '#64dfdf', '#50c9c3', '#40b3a2']

                income_df = pd.DataFrame.from_dict(incomes, orient='index', columns=['Amount']).reset_index()
                expense_df = pd.DataFrame.from_dict(expenses, orient='index', columns=['Amount']).reset_index()

                # Add a column to indicate the type (income or expense)
                income_df['Type'] = 'Income'
                expense_df['Type'] = 'Expense'

                # Concatenate dataframes
                #we have not displayed it and not used anywhere.
                combined_df = pd.concat([income_df, expense_df])

                # Plot pie charts for income and expenses
                fig1 = px.pie(income_df, values='Amount', names='index', title="Monthly Income Breakdown", color_discrete_sequence=neon_green_palette)
                fig1.update_traces(textposition='inside', textinfo='percent+label')

                fig2 = px.pie(expense_df, values='Amount', names='index', title="Monthly Expense Breakdown", color_discrete_sequence=neon_pink_palette)
                fig2.update_traces(textposition='inside', textinfo='percent+label')
#--------------------------------------------------------------------------------------------------------------------------------------------------#
                # Display chart
                st.plotly_chart(fig1)
                #display the table
                st.table(income_df)
                
                st.markdown( "<hr style='border: 2px solid gray; border-radius: 4px;'>", unsafe_allow_html=True)

                # Display chart
                st.plotly_chart(fig2)
                #display the table
                st.table(expense_df)



with tab3:
    # Fetching period and user data from the database (you already have this in your code)
    periods = cur.execute("SELECT DISTINCT period FROM finance_data WHERE username = ?", (username,)).fetchall()
    periods = [period[0] for period in periods]  # Fixed line: Extract the first element of each tuple

    with st.form("saved_period"):  # just form name
        period = st.selectbox("Select Period:", periods)
        submitted = st.form_submit_button("Plot Period")

        if submitted:
            # Fetch income and expense data for the selected period
            income_data = cur.execute("SELECT category, amount FROM finance_data WHERE period = ? AND type = 'Income' AND username = ?", (period, username)).fetchall()
            expense_data = cur.execute("SELECT category, amount FROM finance_data WHERE period = ? AND type = 'Expense' AND username = ?", (period, username)).fetchall()

            incomes = {data[0]: data[1] for data in income_data}
            expenses = {data[0]: data[1] for data in expense_data}

            # Calculate total income, total expenses, and remaining balance
            total_income = sum(incomes.values())  # e.g., 5000 + 1000 + 2000 = 8000
            total_expense = sum(expenses.values())  # e.g., 1000 + 2000 + 2000 = 5000
            remaining = total_income - total_expense  # e.g., 8000 - 5000 = 3000

            # Display remaining balance
            st.subheader(f"Remaining Balance for this Month: {remaining} INR")

            # AI-style investment suggestions based on remaining balance
            st.subheader("💡 Investment Suggestions for This Period")

            # List of investment suggestions based on remaining balance
            suggestions = []

            if remaining < 1000:
                suggestions.append({
                    "Investment Type": "Bank Savings Account",
                    "Description": "Consider saving in a high-interest savings account for safety.",
                    "Reason": "With a low balance, prioritizing safety and liquidity is important, according to the remaining balance."
                })
            elif 1000 <= remaining < 5000:
                suggestions.append({
                    "Investment Type": "Stock Market",
                    "Description": "Invest in low-risk stocks or ETFs for moderate returns.",
                    "Reason": "Moderate savings allow you to take on some risk, according to the remaining balance."
                })
                suggestions.append({
                    "Investment Type": "Mutual Funds",
                    "Description": "Consider mutual funds for diversified exposure with medium risk.",
                    "Reason": "Mutual funds provide diversification and a medium-risk approach, according to the remaining balance."
                })
            elif 5000 <= remaining < 10000:
                suggestions.append({
                    "Investment Type": "Stocks (Blue-Chip)",
                    "Description": "Invest in well-established companies for steady returns.",
                    "Reason": "With a larger balance, blue-chip stocks are a safe bet for long-term growth, according to the remaining balance."
                })
                suggestions.append({
                    "Investment Type": "Real Estate Fund",
                    "Description": "Explore real estate funds for steady income and growth.",
                    "Reason": "Real estate funds offer diversification and steady growth, according to the remaining balance."
                })
            elif 10000 <= remaining < 30000:
                suggestions.append({
                    "Investment Type": "Real Estate",
                    "Description": "Consider investing in rental properties for passive income.",
                    "Reason": "With a higher balance, you can invest in real estate directly for passive income, according to the remaining balance."
                })
                suggestions.append({
                    "Investment Type": "Stocks (Growth)",
                    "Description": "High-risk, high-reward investments in growth stocks.",
                    "Reason": "A larger balance allows for more aggressive investments in growth stocks, according to the remaining balance."
                })
            else:
                suggestions.append({
                    "Investment Type": "Real Estate",
                    "Description": "Consider purchasing property for long-term growth and rental income.",
                    "Reason": "With significant capital, real estate is a strong option for long-term wealth building, according to the remaining balance."
                })
                suggestions.append({
                    "Investment Type": "Stocks (Diversified Portfolio)",
                    "Description": "A diversified stock portfolio to balance risk and reward.",
                    "Reason": "At this level, diversifying across different sectors will balance risk, according to the remaining balance."
                })
                suggestions.append({
                    "Investment Type": "Education Savings",
                    "Description": "Consider investing in your education or skills for long-term growth.",
                    "Reason": "Investing in education can lead to higher earnings potential in the future, according to the remaining balance."
                })
                suggestions.append({
                    "Investment Type": "Retirement Fund",
                    "Description": "Invest in a retirement plan (e.g., 401k) for future security.",
                    "Reason": "A retirement fund helps ensure financial stability in your later years, according to the remaining balance."
                })

            # Display the investment suggestions with reasons as a table
            if suggestions:
                st.table(suggestions)
            else:
                st.info("No suggestions available for the selected data.")