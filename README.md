# ResumeIQ

ResumeIQ is a Flask-based resume analyzer website for a software engineering
basics course project. It accepts PDF or TXT resumes, extracts text, calculates a
score, and gives practical suggestions for improving the resume.

## Project Structure

```text
src/
tests/
.gitignore
README.md
requirements.txt
```

## Features

- Upload PDF or TXT resumes
- Extract text from uploaded files
- Score resumes from 0 to 100
- Detect common resume sections
- Detect technical and soft skills
- Show improvement suggestions
- Handle invalid file types, empty uploads, and oversized files

## Run the Website

```bash
pip install -r requirements.txt
python src/app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Run Tests

```bash
python -m unittest discover -s tests
```
