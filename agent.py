#!/usr/bin/env python3
"""
Research Paper Agent
Fetches daily new papers from arXiv related to Medical Images + Deep Learning
and sends email digest.
"""

import os
import json
import smtplib
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from xml.etree import ElementTree as ET

# ─── CONFIG ─────────────────────────────────────────────
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "ahsan.firebase15@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "olvq jmzs ezly pdpu")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "ahsan.firebase15@gmail.com")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# arXiv search query: Medical Images + Deep Learning
ARXIV_QUERY = "cat:eess.IV OR cat:cs.CV OR cat:cs.LG"  # broad, filtered by keywords below
KEYWORDS = ["medical", "clinical", "radiology", "mri", "ct scan", "x-ray", "ultrasound", 
            "pathology", "histology", "dermatology", "ophthalmology", "mammogram",
            "deep learning", "neural network", "cnn", "transformer", "segmentation",
            "classification", "detection", "diagnosis", "image analysis"]

DATA_FILE = "sent_papers.json"
MAX_RESULTS = 50

# ─── HELPERS ────────────────────────────────────────────

def load_sent_papers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_papers(paper_ids):
    with open(DATA_FILE, "w") as f:
        json.dump(list(paper_ids), f)

def is_medical_deep_learning(title, summary, categories):
    text = (title + " " + summary + " " + " ".join(categories)).lower()
    medical_hit = any(kw in text for kw in KEYWORDS[:12])
    dl_hit = any(kw in text for kw in KEYWORDS[12:])
    return medical_hit and dl_hit

def fetch_arxiv_papers():
    """Fetch recent papers from arXiv (last 48 hours to be safe)."""
    # arXiv API
    query = urllib.parse.quote(ARXIV_QUERY)
    url = (
        f"http://export.arxiv.org/api/query?"
        f"search_query={query}&"
        f"start=0&max_results={MAX_RESULTS}&"
        f"sortBy=submittedDate&sortOrder=descending"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ResearchPaperAgent/1.0"}
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()

    # Parse XML
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }
    root = ET.fromstring(data)
    entries = root.findall("atom:entry", ns)

    papers = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=30)

    for entry in entries:
        title = entry.find("atom:title", ns)
        summary = entry.find("atom:summary", ns)
        published = entry.find("atom:published", ns)
        id_elem = entry.find("atom:id", ns)
        link = entry.find("atom:link[@rel='alternate']", ns)

        # Authors
        authors = entry.findall("atom:author/atom:name", ns)
        author_names = [a.text for a in authors[:3]]
        if len(authors) > 3:
            author_names.append("et al.")

        # Categories
        categories = [c.get("term") for c in entry.findall("atom:category", ns)]

        if title is None or published is None or id_elem is None:
            continue

        pub_date = datetime.fromisoformat(published.text.replace("Z", "+00:00"))

        # Only papers from last ~24 hours
        if pub_date < cutoff:
            continue

        title_text = title.text.strip().replace("\n", " ")
        summary_text = summary.text.strip().replace("\n", " ") if summary is not None else ""
        paper_id = id_elem.text.strip()
        paper_link = link.get("href") if link is not None else paper_id

        if is_medical_deep_learning(title_text, summary_text, categories):
            papers.append({
                "id": paper_id,
                "title": title_text,
                "summary": summary_text[:400] + "..." if len(summary_text) > 400 else summary_text,
                "authors": ", ".join(author_names),
                "link": paper_link,
                "published": pub_date.strftime("%Y-%m-%d %H:%M UTC"),
                "categories": ", ".join(categories)
            })

    return papers

def send_email(papers):
    if not papers:
        print("No new papers to send.")
        return

    subject = f"📄 Daily Medical DL Papers — {len(papers)} new paper(s) | {datetime.now().strftime('%b %d, %Y')}"

    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 700px; margin: auto; background: #fff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
            h1 {{ color: #1a237e; font-size: 22px; margin-bottom: 5px; }}
            .subtitle {{ color: #666; font-size: 14px; margin-bottom: 25px; }}
            .paper {{ border-left: 4px solid #3949ab; padding-left: 15px; margin-bottom: 25px; }}
            .paper-title {{ font-size: 16px; font-weight: bold; color: #283593; margin-bottom: 5px; }}
            .paper-meta {{ font-size: 12px; color: #888; margin-bottom: 8px; }}
            .paper-summary {{ font-size: 14px; color: #444; line-height: 1.5; }}
            .paper-link {{ display: inline-block; margin-top: 8px; color: #fff; background: #3949ab; padding: 6px 14px; text-decoration: none; border-radius: 6px; font-size: 13px; }}
            .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #999; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔬 Research Paper Agent</h1>
            <div class="subtitle">Medical Images + Deep Learning | {datetime.now().strftime('%A, %B %d, %Y')}</div>
    """

    for p in papers:
        html_body += f"""
            <div class="paper">
                <div class="paper-title">{p['title']}</div>
                <div class="paper-meta">👤 {p['authors']} &nbsp;|&nbsp; 📅 {p['published']} &nbsp;|&nbsp; 🏷️ {p['categories']}</div>
                <div class="paper-summary">{p['summary']}</div>
                <a class="paper-link" href="{p['link']}">Read Paper →</a>
            </div>
        """

    html_body += f"""
            <div class="footer">
                Sent by Research Paper Agent 🤖<br>
                Repo: github.com/ahsanfiaz15/research-paper-agent
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECIPIENT
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())

    print(f"✅ Email sent with {len(papers)} paper(s).")

def main():
    print("🔍 Fetching latest papers from arXiv...")
    sent_papers = load_sent_papers()
    papers = fetch_arxiv_papers()

    # Filter out already sent
    new_papers = [p for p in papers if p["id"] not in sent_papers]

    if new_papers:
        print(f"📨 Found {len(new_papers)} new paper(s). Sending email...")
        send_email(new_papers)
        # Mark as sent
        for p in new_papers:
            sent_papers.add(p["id"])
        save_sent_papers(sent_papers)
    else:
        print("😴 No new papers today.")
        # Still send a "no papers" email so you know it's working
        send_email([])

if __name__ == "__main__":
    main()
