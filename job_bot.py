import os
import requests
from datetime import datetime
from openai import OpenAI
from twilio.rest import Client

# ===== CONFIG =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"  # sandbox
YOUR_WHATSAPP = os.getenv("YOUR_WHATSAPP")

client = OpenAI(api_key=OPENAI_API_KEY)
print("Fetching jobs...")
twilio = Client(TWILIO_SID, TWILIO_TOKEN)

CV = """
COO / GM / Operations executive, 25+ years experience...
Operations, transformation, P&L, IT systems, mobility, transport...
"""

KEYWORDS = ["COO", "CIO", "GM", "VP Operations", "Head of Operations", "Transformation"]

# ===== SAMPLE JOB SOURCES (can extend) =====
SOURCES = [
    "https://boards.greenhouse.io/embed/jobs?content=true",
    "https://api.lever.co/v0/postings"
]

def fetch_mock_jobs():
    # MVP: replace later with real ATS parsing
    return [
        {
            "title": "COO - Mobility Company",
            "company": "Example Mobility",
            "url": "https://example.com/job1",
            "desc": "Operations leadership, P&L, transformation"
        },
        {
            "title": "IT Manager",
            "company": "Tech Co",
            "url": "https://example.com/job2",
            "desc": "Infrastructure and support"
        }
    ]

def is_relevant(job):
    text = job["title"] + job["desc"]
    return any(k.lower() in text.lower() for k in KEYWORDS)

def score(job):
    prompt = f"""
    You are a job matching system.

    CV:
    {CV}

    Job:
    {job}

    Score relevance from 0-100 for COO/CIO/GM level executive.
    Return only number.
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        return int(res.choices[0].message.content.strip())
    except:
        return 50

def send_whatsapp(message):
    twilio.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        body=message,
        to="whatsapp:+972507836060"
    )

def run():
    jobs = fetch_mock_jobs()

    relevant = []
    for job in jobs:
        if is_relevant(job):
            job["score"] = 80
            relevant.append(job)

    relevant = sorted(relevant, key=lambda x: x["score"], reverse=True)[:5]

    msg = "🎯 Daily Executive Jobs\n\n"
    for j in relevant:
        msg += f"{j['title']} ({j['score']})\n{j['company']}\n{j['url']}\n\n"

    send_whatsapp(msg)

if __name__ == "__main__":
    while True:
        run()
        time.sleep(86400)  # פעם ביום
