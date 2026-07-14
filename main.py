import pdfplumber
import requests
import ollama


# -----------------------------
# Extract Resume Text
# -----------------------------
def extract_resume_text(pdf_file):
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# -----------------------------
# Extract Skills using Ollama
# -----------------------------
def extract_skills(resume_text):

    prompt = f"""
    Analyze the resume below and extract the top technical skills.

    Resume:
    {resume_text}

    Return ONLY a comma-separated list of skills.
    """

    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"].strip()


# -----------------------------
# Fetch Jobs from Arbeitnow
# -----------------------------
def fetch_jobs():

    url = "https://www.arbeitnow.com/api/job-board-api"

    try:
        response = requests.get(url, timeout=20)

        if response.status_code == 200:
            data = response.json()

            jobs = []

            for job in data.get("data", []):

                jobs.append({
                    "title": job.get("title", ""),
                    "company": job.get("company_name", ""),
                    "location": job.get("location", ""),
                    "url": job.get("url", ""),
                    "description": job.get("description", "")
                })

            return jobs

        return []

    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []


# -----------------------------
# Rank Jobs using Ollama
# -----------------------------
def rank_jobs(resume_text, jobs):

    ranked_jobs = []

    for job in jobs[:30]:

        prompt = f"""
        Resume:
        {resume_text}

        Job Title:
        {job['title']}

        Job Description:
        {job['description'][:1500]}

        Evaluate how well this job matches the resume.

        Return ONLY a score between 0 and 100.
        """

        try:

            response = ollama.chat(
                model="qwen2.5:3b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            score_text = response["message"]["content"]

            score = int(
                "".join(filter(str.isdigit, score_text)) or 0
            )

            score = min(score, 100)

        except Exception as e:
            print(f"Error scoring job: {e}")
            score = 0

        job["match_score"] = score
        ranked_jobs.append(job)

    ranked_jobs.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return ranked_jobs[:10]


# -----------------------------
# Main Recommendation Function
# -----------------------------
def recommend_jobs(resume_file):

    resume_text = extract_resume_text(resume_file)

    skills = extract_skills(resume_text)

    jobs = fetch_jobs()

    ranked_jobs = rank_jobs(
        resume_text,
        jobs
    )

    return {
        "skills": skills,
        "jobs": ranked_jobs
    }