# 🧠 ResumeIQ

> **Upload your resume. Get an honest score. Land the job.**

ResumeIQ is an AI-powered resume analyzer built with Flask. Drop in your PDF or TXT resume alongside a job description, and get instant feedback — a score, skill breakdown, ATS tips, and actionable suggestions to help you stand out.

🌐 **Live Demo:** [resumeiq-rtgu.onrender.com](https://resumeiq-rtgu.onrender.com)

---

## ✨ Features

- 📄 **Upload PDF or TXT** resumes with drag-and-drop simplicity
- 🤖 **AI-powered analysis** via Claude (falls back to rule-based scoring offline)
- 🎯 **Job match score** — see how well your resume fits the target role
- 🔍 **Section detection** — finds Education, Experience, Projects, Skills, Contact
- 🛠️ **Skill extraction** — identifies technical and soft skills
- 💡 **Smart suggestions** — concrete, actionable improvements
- 🤖 **ATS tips** — beat applicant tracking systems
- 🛡️ **Safe & private** — uploaded files are deleted immediately after analysis

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Wawa-12-C/ResumeIQ.git 
cd ResumeIQ
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key *(optional)*

```bash
export ANTHROPIC_API_KEY=your_key_here
export SECRET_KEY=your_secret_key
```

### 4. Run the app

```bash
python src/app.py
```

Open [https://resumeiq-rtgu.onrender.com](https://resumeiq-rtgu.onrender.com) in your browser.

---

## 🧪 Running Tests

```bash
python -m unittest discover -s tests
```

---

## 🗂️ Project Structure

```
ResumeIQ/
├── src/
│   ├── app.py              # Flask routes & entry point
│   ├── ai_analyzer.py      # Claude AI integration + fallback
│   ├── resume_analyzer.py  # Rule-based scoring logic
│   ├── file_handler.py     # PDF/TXT extraction & cleanup
│   └── config.py           # App configuration
├── templates/
│   └── index.html          # Frontend UI
├── tests/
│   └── test_main.py        # Unit & integration tests
├── requirements.txt
└── README.md
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| AI Analysis | Anthropic Claude API |
| PDF Parsing | PyMuPDF |
| Frontend | HTML, CSS, Jinja2 |
| Testing | unittest |
| Hosting | Render |

---

## 📦 Requirements

- Python 3.10+
- `ANTHROPIC_API_KEY` environment variable *(optional)*

---

## 👤 Author

Built as a Software Engineering Basics course project.

---

*Made with 🧋 and Python*