# import streamlit as st
# import yfinance as yf
# import pandas as pd
# import sqlite3
# from datetime import datetime
# import calendar
# from streamlit_option_menu import option_menu
# import plotly.express as px
# import plotly.graph_objects as go
# import geocoder
# import requests
# import time

# time.sleep(5)

# st.set_page_config(layout="wide")

# # List of company names and ticker symbols
# excel_file = r"C:\Users\Yashm\Desktop\finance-tracker-main\ftt\Ticker_Company.xlsx"
# company_data = pd.read_excel(excel_file)

# if company_data.empty or "Company_Name" not in company_data.columns or "Symbol" not in company_data.columns:
#     st.error("Error: Invalid or empty Excel file. Please check the data.")
#     st.stop()

# # Extract company names and ticker symbols
# company_names = company_data["Company_Name"].tolist()
# ticker_symbols = company_data["Symbol"].tolist()

# # Dropdown menu for selecting a company
# selected_company = st.selectbox("Select a Company", company_names)

# # Find the corresponding ticker symbol
# selected_ticker_symbol = ticker_symbols[company_names.index(selected_company)]

# st.write("Selected Ticker Symbol:", selected_ticker_symbol)

# if selected_ticker_symbol:
#     # Retrieve historical data for selected stock
#     tickerData = yf.Ticker(selected_ticker_symbol)
#     tickerDf = tickerData.history(period='1d', start='2024-12-22', end=datetime.today().strftime('%Y-%m-%d'))
#     time.sleep(1)
# # Create tabs
# tab1, tab2, tab3 = st.tabs(["Closing Prices", " Stock Volume", "High Vs Low of Stock Prices"])

# with tab1:
#     st.title("Closing Prices")
#     if not tickerDf.empty:
#         st.write(f"Stock Data for {selected_ticker_symbol}:")
#         st.line_chart(tickerDf["Close"])
#         st.divider()
#     else:
#             st.warning("No data available for the entered symbol. Please enter a valid stock ticker symbol.")

# with tab2:
#     st.title("Stock Volume")
#     if not tickerDf.empty:
#         st.line_chart(tickerDf["Volume"])
#         st.caption('Chart for Stock Volume.')
#     else:
#             st.warning("No data available for the entered symbol. Please enter a valid stock ticker symbol.")

# with tab3:
#     st.title("High Vs Low of Stock Prices")
#     if not tickerDf.empty:
#         high_low_data = tickerDf[['High', 'Low']]
#         st.bar_chart(high_low_data)
#         st.caption('Chart for High Vs Low of Stock Prices.')
#     else:
#         st.warning("No data available for the entered symbol. Please enter a valid stock ticker symbol.")


import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import time

st.set_page_config(layout="wide")

# Load Excel file
excel_file = r"C:\Users\Yashm\Desktop\finance-tracker-main\ftt\Ticker_Company.xlsx"

try:
    company_data = pd.read_excel(excel_file)
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

if company_data.empty or "Company_Name" not in company_data.columns or "Symbol" not in company_data.columns:
    st.error("Excel file must contain 'Company_Name' and 'Symbol' columns.")
    st.stop()

company_names = company_data["Company_Name"].tolist()
ticker_symbols = company_data["Symbol"].tolist()

selected_company = st.selectbox("Select a Company", company_names)
selected_ticker_symbol = ticker_symbols[company_names.index(selected_company)]
st.write("Selected Ticker Symbol:", selected_ticker_symbol)

# Cache the fetch to avoid rate limits
@st.cache_data(ttl=3600)
def fetch_ticker_data(ticker_symbol):
    time.sleep(2)  # Sleep to help avoid hitting rate limits
    ticker = yf.Ticker(ticker_symbol)
    data = ticker.history(
        period='1d',
        start='2024-12-22',
        end=datetime.today().strftime('%Y-%m-%d')
    )
    return data

# Fetch only once per run
if "tickerDf" not in st.session_state:
    st.session_state["tickerDf"] = pd.DataFrame()

if st.button("Fetch Stock Data"):
    try:
        df = fetch_ticker_data(selected_ticker_symbol)
        if df.empty:
            st.warning("No data returned. Possibly rate-limited. Try again later.")
        else:
            st.session_state["tickerDf"] = df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")

tickerDf = st.session_state["tickerDf"]

# Tabs for different graphs
tab1, tab2, tab3 = st.tabs(["Closing Prices", "Stock Volume", "High Vs Low"])

with tab1:
    st.title("Closing Prices")
    if not tickerDf.empty:
        st.line_chart(tickerDf["Close"])
    else:
        st.info("No closing price data available.")

with tab2:
    st.title("Stock Volume")
    if not tickerDf.empty:
        st.line_chart(tickerDf["Volume"])
    else:
        st.info("No volume data available.")

with tab3:
    st.title("High vs Low Prices")
    if not tickerDf.empty:
        st.bar_chart(tickerDf[["High", "Low"]])
    else:
        st.info("No high/low data available.")

