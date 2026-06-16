import streamlit as st
from services.auth_service import (
    init_auth_db,
    validate_login,
    create_user
)

# Ensure DB exists
init_auth_db()


def login_page():
    st.markdown(
        """
        <div style="max-width:420px;margin:auto;">
            <div class="card">
                <h2 style="text-align:center;">🔐 Secure Login</h2>
                <p style="text-align:center;opacity:0.8;">
                    Smart Deep Web Crawler
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    tab1, tab2 = st.tabs(["✅ Login", "🆕 Register"])

    # ------------------ LOGIN ------------------
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("🚀 Login", use_container_width=True):
            if validate_login(username, password):
                st.session_state.logged_in = True
                st.success("Login successful ✅")
                st.rerun()
            else:
                st.error("Invalid username or password ❌")

    # ------------------ REGISTER ------------------
    with tab2:
        new_user = st.text_input("Create Username", key="reg_user")
        new_pass = st.text_input("Create Password", type="password", key="reg_pass")
        confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("📝 Create Account", use_container_width=True):
            if not new_user or not new_pass:
                st.error("All fields are required")
            elif new_pass != confirm:
                st.error("Passwords do not match")
            else:
                ok = create_user(new_user, new_pass)
                if ok:
                    st.success("Account created 🎉 Please login")
                else:
                    st.error("Username already exists")
