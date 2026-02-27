# 🩺 HealthMate AI

HealthMate AI is an AI-powered medical assistant built using Streamlit and Google Gemini API.  
It provides symptom-based medical consultation and medical report analysis through an interactive web interface.

---

## 🚀 Features

- 🔐 Secure User Authentication (SQLite + SHA-256 password hashing)
- 💬 AI-powered medical consultation with conversation memory
- 📄 PDF medical report analysis and summarization
- 📊 Dynamic dashboard metrics (Users, Reports Analyzed)
- 🔒 Secure API key management using environment variables
- 🧠 Context-aware responses using LLM integration

---

## 🛠️ Tech Stack

- Python
- Streamlit
- SQLite
- LangChain
- Google Gemini API
- Git & GitHub

---

## 📂 Project Structure

healthmate_ai/
│
├── main.py
├── requirements.txt
├── .gitignore
├── snapshots/
└── README.md

---

## ⚙️ Installation & Setup

1. Clone the repository:

git clone https://github.com/your-username/healthmate_ai.git
cd healthmate_ai

2. Create a virtual environment:

python -m venv .venv
.venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt

4. Create a `.env` file in the root directory and add:

GOOGLE2_API_KEY=your_api_key_here

5. Run the application:

streamlit run main.py

---

## 🔐 Environment Variables

This project uses environment variables to securely store API keys.

Make sure your `.env` file is included in `.gitignore` to prevent exposing sensitive information.

---

## 🎯 Future Improvements

- Role-based consultant dashboard
- Advanced medical analytics
- Cloud deployment
- Enhanced contextual retrieval for reports

---

## 👨‍💻 Author

sai chaitanya bonthu
AI & Full Stack Enthusiast
