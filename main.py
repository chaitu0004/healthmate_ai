import sqlite3
import hashlib
import streamlit as st
import os


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# =====================================================
# LOAD ENV + LLM
# =====================================================


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE2_API_KEY"),
    temperature=0.3
)

# =====================================================
# DATABASE SETUP
# =====================================================
db_name = "healthmate.db"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    with sqlite3.connect(db_name) as conn:

        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
           userid INTEGER PRIMARY KEY AUTOINCREMENT,
           first_name TEXT NOT NULL,
           last_name TEXT NOT NULL,
           date_of_birth TEXT NOT NULL,
           email TEXT UNIQUE NOT NULL,
           password TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
           fileid INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id INTEGER NOT NULL,
           file_name TEXT NOT NULL,
           file_path TEXT NOT NULL,
           FOREIGN KEY (user_id) REFERENCES users(userid)
        )
        """)

# =====================================================
# AUTH FUNCTIONS
# =====================================================
def sign_up(first_name, last_name, dob, email, password):
    with sqlite3.connect(db_name) as conn:
        try:
            conn.execute("""
                INSERT INTO users(first_name, last_name, date_of_birth, email, password)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, dob, email, hash_password(password)))
            conn.commit()
            return True, "Account created successfully."
        except sqlite3.IntegrityError:
            return False, "Email already registered."

def login(email, password):
    with sqlite3.connect(db_name) as conn:
        user = conn.execute("""
            SELECT * FROM users
            WHERE email=? AND password=?
        """, (email, hash_password(password))).fetchone()
        return user if user else None

# =====================================================
# FILE MANAGEMENT
# =====================================================
def save_file(user_id, file_name, file_path):
    with sqlite3.connect(db_name) as conn:
        conn.execute("""
            INSERT INTO files(user_id, file_name, file_path)
            VALUES (?, ?, ?)
        """, (user_id, file_name, file_path))
        conn.commit()

def get_files(user_id):
    with sqlite3.connect(db_name) as conn:
        return conn.execute("""
            SELECT file_name, file_path
            FROM files
            WHERE user_id=?
        """, (user_id,)).fetchall()

def delete_file(user_id, file_name):
    with sqlite3.connect(db_name) as conn:
        conn.execute("""
            DELETE FROM files
            WHERE user_id=? AND file_name=?
        """, (user_id, file_name))
        conn.commit()

# =====================================================
# RAG SETUP
# =====================================================
embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

def get_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_text(text)

def create_vector_store(chunks):
    return FAISS.from_texts(chunks, embeddings)

def retrieve_context(query, db):
    docs = db.similarity_search(query, k=3)
    return [doc.page_content for doc in docs]

# =====================================================
# CURABOT SYSTEM PROMPT
# =====================================================
system_instruction = """
Your name is Curabot.
You are a professional medical doctor.

Responsibilities:
1. Identify possible diseases from symptoms.
2. Suggest medication if appropriate.
3. Provide prevention methods.
4. Maintain natural, human-like conversation.
5. Politely refuse non-medical or abusive queries.
6. If the condition appears serious or life-threatening, suggest seeking professional medical attention.


Be accurate. Do not hallucinate.
"""

def generate_response(query, context_chunks, history):
    context = "\n".join(context_chunks)
    history_text = "\n".join(history)

    full_prompt = f"""
    Context:
    {context}

    Conversation History:
    {history_text}

    User Question:
    {query}

    Provide a professional medical response.
    """

    response = llm.invoke([
        SystemMessage(content=system_instruction),
        HumanMessage(content=full_prompt)
    ])

    return response.content






init_db()

import streamlit as st
import sqlite3
import hashlib
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# =============================
# CONFIG
# =============================
st.set_page_config(
    page_title="HealthMate Assistant",
    layout="wide"
)

# =============================
# CUSTOM DARK UI (NO WHITE TEXT ISSUE)
# =============================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0e1117;
    color: #ffffff;
}

.block-container {
    padding-top: 4rem;
}

.metric-box {
    background: #1c1f26;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}

.small-card {
    background: #1c1f26;
    padding: 30px;
    border-radius: 15px;
}

.chat-left {
    background: #15803d;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
            display:inline-block;
            max-width:60%;
            word-wrap:break-word;
            float:left;
            clear:both;
}

.chat-right {
    background: #1f2937;
            color:#f3f4f6;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    text-align: right;
    display:inline-block;
            max-width:60%;
            word-wrap:break-word;
            float:right;
            clear:both;
}
</style>
""", unsafe_allow_html=True)




# SESSION
# =============================
if "page" not in st.session_state:
    st.session_state.page = "login"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# =============================
# HEADER
# =============================
col1, col2, col3 = st.columns([6,1,1])

with col1:
    st.markdown("# HealthMate Assistant 🩺")

with col2:
    if st.button("Login"):
        st.session_state.page = "login"

with col3:
    if st.button("Sign Up"):
        st.session_state.page = "signup"

# =============================
# LOGIN PAGE

# =============================
# LOGIN PAGE
# =============================
if not st.session_state.logged_in:

    
    # Metrics
    with sqlite3.connect(db_name) as conn:
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        reports_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"<div class='metric-box'><h3>Users</h3><h2>{users_count}</h2></div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='metric-box'><h3>Consultants</h3><h2>5</h2></div>", unsafe_allow_html=True)

    with c3:
        st.markdown("<div class='metric-box'><h3>Reports Analyzed</h3><h2>12</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Centered Login / Signup
    col1, col2, col3 = st.columns([4,1.5,4])

    with col2:

        if st.session_state.page == "login":

            st.markdown(
                "<h3 style='text-align:center; margin-bottom:20px;font-weight:800;'>Login</h3>",
                unsafe_allow_html=True
            )

            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login Now"):
                if login(email, password):
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        elif st.session_state.page == "signup":

            st.markdown(
                "<h3 style='text-align:center; margin-bottom:20px;'>Create Account</h3>",
                unsafe_allow_html=True
            )

            fn = st.text_input("First Name")
            ln = st.text_input("Last Name")
            dob = st.text_input("Date of Birth")
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password")

            if st.button("Create Account"):
                success, message = sign_up(fn, ln, dob, email, pw)
                if success:
                    st.success(message)
                else:
                    st.error(message)


# =============================
# Cura BOT PAGE
# =============================
if st.session_state.logged_in and st.sidebar.button("Cura Bot"):
    st.session_state.page = "consult"

if st.session_state.logged_in and st.sidebar.button("MeRo Bot"):
    st.session_state.page = "report"

if st.session_state.logged_in and st.session_state.page == "consult":

    st.markdown("""
       <h2 style="font-size:40px; font-weight:600; margin-top:0px;">
        Cura Bot
        </h2>
          """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(f"<div class='chat-left'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-right'>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Describe your symptoms")
    if st.button("Send") and user_input:
        st.session_state.messages.append({"role":"user","content":user_input})

        history_messages = [SystemMessage(content=system_instruction)]

        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))
            else:
                history_messages.append(HumanMessage(content=msg["content"]))

        response = llm.invoke(history_messages)

        st.session_state.messages.append(
              {"role":"assistant","content":response.content}
    )

        st.rerun()

# =============================
# MEDICAL REPORT BOT PAGE
# =============================
# =============================
# MEDICAL REPORT BOT PAGE
# =============================
import PyPDF2

if st.session_state.logged_in and st.session_state.page == "report":

    st.markdown("""
    <h2 style="font-size:28px; font-weight:600;">
    Medical Report Bot
    </h2>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Upload Medical Report (PDF only)",
        type=["pdf"]
    )

    # Session state for report text
    if "report_text" not in st.session_state:
        st.session_state.report_text = ""

    # Session state for report chat
    if "report_messages" not in st.session_state:
        st.session_state.report_messages = []

    # =============================
    # WHEN FILE IS UPLOADED
    # =============================

    if uploaded:

        pdf_reader = PyPDF2.PdfReader(uploaded)
        text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        st.session_state.report_text = text

        # Initial automatic analysis
        if not st.session_state.report_messages:

            response = llm.invoke([
                HumanMessage(content=f"Analyze this medical report and summarize key findings:\n{text}")
            ])

            st.session_state.report_messages.append(
                {"role": "assistant", "content": response.content}
            )

    # =============================
    # DISPLAY CHAT
    # =============================
    for msg in st.session_state.report_messages:
        if msg["role"] == "assistant":
            st.markdown(
                f"<div class='chat-left'>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='chat-right'>{msg['content']}</div>",
                unsafe_allow_html=True
            )

    # =============================
    # FOLLOW-UP QUESTION INPUT
    # =============================
    if st.session_state.report_text:

        question = st.chat_input("Ask something about this report...")

        if question:

            st.session_state.report_messages.append(
                {"role": "user", "content": question}
            )

            response = llm.invoke([
                HumanMessage(content=
                    f"Based on this medical report:\n{st.session_state.report_text}\n\n"
                    f"Answer this question clearly:\n{question}"
                )
            ])

            st.session_state.report_messages.append(
                {"role": "assistant", "content": response.content}
            )

            st.rerun()
