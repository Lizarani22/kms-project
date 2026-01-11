import streamlit as st
import requests
from datetime import datetime


API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="🤖 KMS", layout="wide")

# ---------------- CSS (FIX WHITE TEXT ISSUE) ----------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f4f6f8;
        color: #000000;
    }

    label, p, span, div {
        color: #000000 !important;
    }

    input, textarea, select {
        color: #000000 !important;
        background-color: #ffffff !important;
    }

    button {
        color: #000000 !important;
        background-color: #e0e0e0 !important;
    }

    ::placeholder {
        color: #777777 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- SESSION STATE ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN / REGISTER ----------------
if st.session_state.user is None:
    st.title("🟢 KMS Login / Register")
    choice = st.radio("Choose action", ["Login", "Register"])

    if choice == "Register":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["user", "admin"])

        if st.button("Register"):
            resp = requests.post(
                f"{API_BASE}/register",
                json={
                    "username": username,
                    "password": password,
                    "role": role
                }
            )

            if resp.status_code == 200:
                st.success("Registered successfully. Please login.")
            else:
                st.error(resp.json().get("detail", "Registration failed"))

    if choice == "Login":
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):
            resp = requests.post(
                f"{API_BASE}/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            if resp.status_code == 200:
                data = resp.json()
                st.session_state.user = {
                    "token": data["access_token"],
                    "role": data.get("role", "user")
                }
                st.rerun()
            else:
                st.error("Invalid username or password")

# ---------------- MAIN APP ----------------
else:
    user = st.session_state.user

    st.sidebar.title("🤖 KMS")
    menu = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "New Ticket", "Knowledge Base", "Analytics", "Settings", "Logout"]
    )

    # ---------------- DASHBOARD ----------------
    if menu == "Dashboard":
        st.title("📊 Dashboard")

        stats = requests.get(f"{API_BASE}/stats").json()

        c1, c2, c3 = st.columns(3)
        c1.metric("Articles", stats["total_articles"])
        c2.metric("Recommendations", stats["total_recommendations"])
        c3.metric("System Health", "OK")

        st.write("Last updated:", datetime.now().strftime("%d %b %Y %I:%M %p"))

    # ---------------- NEW TICKET ----------------
    if menu == "New Ticket":
        st.title("🎫 New Support Ticket")

        title = st.text_input("Issue title")
        description = st.text_area("Describe the issue")
        max_rec = st.slider("Max recommendations", 1, 5, 3)

        if st.button("Analyze"):
            payload = {
                "content": f"{title}. {description}",
                "max_recommendations": max_rec
            }

            resp = requests.post(f"{API_BASE}/ticket", json=payload)

            if resp.status_code == 200:
                recs = resp.json().get("recommendations", [])

                if not recs:
                    st.info("No matching articles found")
                for r in recs:
                    st.subheader(r["title"])
                    st.write(r["content"])
                    st.caption(f"Category: {r['category']}")
            else:
                st.error("Analysis failed")

    # ---------------- KNOWLEDGE BASE ----------------
    if menu == "Knowledge Base":
        st.title("📚 Knowledge Base")

        search = st.text_input("Search")
        articles = requests.get(f"{API_BASE}/articles").json()

        for a in articles:
            if search.lower() in a["title"].lower() or search.lower() in a["category"].lower():
                st.subheader(a["title"])
                st.write(a["content"])
                st.caption(f"Category: {a['category']}")
                st.divider()

    # ---------------- ANALYTICS ----------------
    if menu == "Analytics":
        st.title("📈 Analytics")
        stats = requests.get(f"{API_BASE}/stats").json()
        st.metric("Tickets processed", stats["total_recommendations"])

    # ---------------- SETTINGS ----------------
    if menu == "Settings":
        st.title("⚙️ Settings")
        st.warning("Admin only section (logic can be added later)")

    # ---------------- LOGOUT ----------------
    if menu == "Logout":
        st.session_state.user = None
        st.rerun()
