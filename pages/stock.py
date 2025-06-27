import streamlit as st
import yfinance as yf
from datetime import datetime
import calendar
import pandas as pd

st.set_page_config(layout="wide")

# List of company names and ticker symbols
excel_file = r"C:\Users\Yashm\Desktop\finance-tracker-main\Ticker_Company.xlsx"
company_data = pd.read_excel(excel_file)

if company_data.empty or "Company_Name" not in company_data.columns or "Symbol" not in company_data.columns:
    st.error("Error: Invalid or empty Excel file. Please check the data.")
    st.stop()

# Extract company names and ticker symbols
company_names = company_data["Company_Name"].tolist()
ticker_symbols = company_data["Symbol"].tolist()

# Dropdown menu for selecting a company
selected_company = st.selectbox("Select a Company", company_names)

# Find the corresponding ticker symbol
selected_ticker_symbol = ticker_symbols[company_names.index(selected_company)]

st.write("Selected Ticker Symbol:", selected_ticker_symbol)

if selected_ticker_symbol:
    # Retrieve historical data for selected stock
    tickerData = yf.Ticker(selected_ticker_symbol)
    tickerDf = tickerData.history(period='1d', start='2024-12-22', end=datetime.today().strftime('%Y-%m-%d'))

# Create tabs
tab1, tab2, tab3 = st.tabs(["Closing Prices", " Stock Volume", "High Vs Low of Stock Prices"])

with tab1:
    st.title("Closing Prices")
    if not tickerDf.empty:
        st.write(f"Stock Data for {selected_ticker_symbol}:")
        st.line_chart(tickerDf["Close"])
        st.divider()
    else:
            st.warning("No data available for the entered symbol. Please enter a valid stock ticker symbol.")

with tab2:
    st.title("Stock Volume")
    if not tickerDf.empty:
        st.line_chart(tickerDf["Volume"])
        st.caption('Chart for Stock Volume.')
    else:
            st.warning("No data available for the entered symbol. Please enter a valid stock ticker symbol.")

with tab3:
    st.title("High Vs Low of Stock Prices")
    if not tickerDf.empty:
        high_low_data = tickerDf[['High', 'Low']]
        st.bar_chart(high_low_data)
        st.caption('Chart for High Vs Low of Stock Prices.')
    else:
        st.warning("No data available for the entered symbol. Please enter a valid stock ticker symbol.")
