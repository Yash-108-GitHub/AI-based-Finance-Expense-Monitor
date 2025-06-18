import streamlit as st
import sqlite3
from streamlit_option_menu import option_menu
import re  # For regex validation

st.set_page_config( page_title="Welcome ")


# Connect to SQLite database
conn = sqlite3.connect('users.db', check_same_thread=False)
cur = conn.cursor()


f_conn = sqlite3.connect('data.db')  # Check this filename
f_cur = f_conn.cursor()

# Create Users table
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    username TEXT PRIMARY KEY,
    email TEXT,
    password TEXT
)
''')
conn.commit()

# Function to register a new user
def register_user(name, username, email, password):
    try:
        cur.execute('''
        INSERT INTO users (name, username, email, password)
        VALUES (?, ?, ?, ?)
        ''', (name, username, email, password))
        conn.commit()
        return True #skip when error
    except sqlite3.IntegrityError:
        return False

# Function to verify user login
def login_user(username, password):
    cur.execute('''
    SELECT name,username FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = cur.fetchone() #.fetchone() retrieves one matching row and it returns that row and we stored it Tuple_variable => "user"
    return user 

# Title
st.title("Welcome")


# Main section
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    container = st.container()
    with container: 
        selected_login = option_menu(
            menu_title=None, 
            options=["Sign Up", "Login"],
            orientation="horizontal",
            icons=["person-plus", "box-arrow-in-right"],  # Optional: Add icons for better UX
        )

        if selected_login == "Sign Up":
            with st.form("sign_up_form", clear_on_submit=True):

                st.markdown('<span style="color:white;">Enter Full Name <span style="color:red;">*</span></span>', unsafe_allow_html=True)
                name = st.text_input("", placeholder="e.g. John Doe",label_visibility="collapsed")

                st.markdown('<span style="color:white;">Enter User Name <span style="color:red;">*</span></span>', unsafe_allow_html=True)
                username = st.text_input("", placeholder="e.g. @John123",label_visibility="collapsed")

                st.markdown('<span style="color:white;">Email Id <span style="color:red;">*</span></span>', unsafe_allow_html=True)
                email = st.text_input("", placeholder="e.g. john@example.com",label_visibility="collapsed")
 

                st.markdown('<span style="color:white;">Password <span style="color:red;">*</span></span>', unsafe_allow_html=True)
                password = st.text_input("", type="password", placeholder="",label_visibility="collapsed")
                st.caption("Password must have 8 characters and contain both letters(A-Z) and numbers (0-9) with special synbols(@,#).")

                # password = st.text_input("Password", type="password")

                if st.form_submit_button("Sign Up"):
                    if not name or not username or not email or not password:
                        st.warning("Please fill in all fields before signing up.")

                    #Username varification
                    elif not re.match(r"^@[\w]{6,14}$", username):
                        st.error("Username must start with '@' and be 6–14 characters long (letters and numbers only, no spaces or special characters).")

                    # Email validation
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        st.error("Please enter a valid email address.")

                    # Password strength validation
                    elif len(password) < 8 or \
                        not re.search(r"[A-Z]", password) or \
                        not re.search(r"[0-9]", password) or \
                        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                        st.error("Password must be at least 8 characters long and include an uppercase letter, number, and special symbol.")
                    else:
                        if register_user(name, username, email, password):
                            st.success("Successfully registered! Please log in.")
                        else:
                            st.error("Username already exists. Please use a different username.")
                    

        elif selected_login == "Login":
            with st.form("login_form", clear_on_submit=True):
                
                st.markdown('<span style="color:white;">Enter User Name <span style="color:red;">*</span></span>', unsafe_allow_html=True)
                username = st.text_input("", placeholder="e.g. @John123",label_visibility="collapsed")

                st.markdown('<span style="color:white;">Password <span style="color:red;">*</span></span>', unsafe_allow_html=True)
                password = st.text_input("", type="password", placeholder="",label_visibility="collapsed")

                if st.form_submit_button("Login"):
                    user = login_user(username , password)
                    if username.strip() == "" or password.strip() == "": #if user doesn't enter input
                        st.error("please enter input")
                    elif user:
                        st.session_state["user"] = user[0]
                        st.session_state["username"] = user[1]
                        st.success(f"Logged in as {user[0]}")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                    

#this code will execute after login
else:

   # Example main content for logged-in users
    if st.session_state["user"]:
        st.write(f"Hello, {st.session_state['user']}!")
        st.write("This is your dashboard.")
        st.sidebar.write(f"Hellow Welcome home!, {st.session_state['user']}!")
        
        #store variable "username" in session state
        user = st.session_state["username"]
        currency = "INR" #we defined the currency beaus not declared it is not declared anyware.

        # Retrieve finance data for all periods
        income_data = f_cur.execute("SELECT period, amount, category FROM finance_data WHERE type = 'Income' AND username = ?", (user,)).fetchall()
        expense_data = f_cur.execute("SELECT period, amount, category FROM finance_data WHERE type = 'Expense' AND username = ?", (user,)).fetchall()

        total_income = sum(data[1] for data in income_data)
        total_expense = sum(data[1] for data in expense_data)
        remaining = total_income - total_expense
        
        #-------#line
        st.markdown( "<hr style='border: 2px solid gray; border-radius: 4px;'>", unsafe_allow_html=True)

        #display the details
              
        st.metric("Total Income:", "{:,} {}".format(total_income, currency), )
        st.markdown( "<hr style='border: 1px solid gray; border-radius: 4px;'>", unsafe_allow_html=True)

        st.metric("Total Expense:", "{:,} {}".format(total_expense, currency), )
        st.markdown( "<hr style='border: 1px solid gray; border-radius: 4px;'>", unsafe_allow_html=True)

        st.metric("Total Remaining:", "{:,} {}".format(remaining, currency))
        st.markdown( "<hr style='border: 1px solid gray; border-radius: 4px;'>", unsafe_allow_html=True)

        if st.sidebar.button("Logout"):
            st.session_state["user"] = None
            st.rerun()
    

    else:
        st.write("Please log in to see your dashboard.")