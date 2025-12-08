import os
import time
import json
import spacy
import fitz  # PyMuPDF
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer, util
from docx import Document

app = Flask(__name__)

# ---------- Folder Setup ----------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATA_FILE = "data.json"

# ---------- Load Jobs ----------
with open("job data/job.json", "r", encoding="utf-8") as f:
    jobs_list = json.load(f)

JOBS = {str(job["id"]): job for job in jobs_list}

# ---------- NLP & Embedding ----------
nlp = spacy.load("en_core_web_sm")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- Helper Functions ----------
def extract_skills(text):
    doc = nlp(text)
    skills = set()
    for token in doc:
        if token.pos_ in ["PROPN", "NOUN"]:
            skills.add(token.text.strip())
    return skills

def match_skills(job_skills, resume_text, threshold=0.6):
    resume_skills = extract_skills(resume_text)
    matched = []
    for skill in job_skills:
        max_sim = 0.0
        for rskill in resume_skills:
            emb_skill = embed_model.encode(skill, convert_to_tensor=True)
            emb_rskill = embed_model.encode(rskill, convert_to_tensor=True)
            sim = util.cos_sim(emb_skill, emb_rskill).item()
            if sim > max_sim:
                max_sim = sim
        if max_sim >= threshold:
            matched.append(skill)
    unmatched = [s for s in job_skills if s not in matched]
    return matched, unmatched

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def extract_resume_text(file_path):
    """Extract text from PDF, DOCX, or TXT"""
    if file_path.endswith(".pdf"):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([p.text for p in doc.paragraphs])
    else:  # TXT
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

# ---------- Routes ----------
@app.route('/')
def home():
    return redirect(url_for('apply'))

@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        job_id = request.form['job_id']
        file = request.files.get('resume')

        if not file or job_id not in JOBS:
            return "❌ Error uploading resume or selecting job!"

        job = JOBS[job_id]
        job_skills = job['skills']
        required_exp = job.get('experience', 0)

        # Save temp file to extract text
        timestamp = int(time.time())
        original_name = secure_filename(file.filename)
        temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{timestamp}_{original_name}")
        file.save(temp_path)

        # Extract text from resume
        resume_text = extract_resume_text(temp_path)
        candidate_exp = 1  # Dummy experience
        matched, unmatched = match_skills(job_skills, resume_text)
        match_percent = (len(matched)/len(job_skills))*100 if job_skills else 0
        passed = match_percent >= 60 and candidate_exp >= required_exp

        if passed:
            # Save resume permanently
            final_filename = f"{name}_{timestamp}{os.path.splitext(original_name)[1]}"
            final_path = os.path.join(UPLOAD_FOLDER, final_filename)
            os.rename(temp_path, final_path)

            # Save application data
            app_data = load_data()
            app_data.append({
                "name": name,
                "email": email,
                "phone": phone,
                "job_id": job_id,
                "matched": matched,
                "unmatched": unmatched,
                "match_percent": round(match_percent,2),
                "passed": True,
                "resume": final_filename
            })
            save_data(app_data)
        else:
            # Remove temp file for failed candidates
            os.remove(temp_path)

        # Show same message for everyone
        return "✅ Your resume has been submitted successfully!"

    return render_template('apply.html', jobs=JOBS.values())


@app.route('/admin', methods=['GET'])
def admin():
    applications = load_data()
    return render_template('admin.html', applications=applications, jobs=JOBS)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)
