#!/usr/bin/env python3
"""
Research Paper Agent (Quantum Medical & Computer Vision Edition)
Fetches daily new papers from arXiv and PubMed related to Quantum Computer Vision,
Quantum Medical Imaging, and Quantum Machine Learning.
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
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "ayii exbv npyg rvyz")
# Multiple recipients list
EMAIL_RECIPIENTS = ["ahsanfiaz46@gmail.com", "imab6597@gmail.com"]
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Updated Keywords for Quantum Computer Vision & Quantum Medical Imaging
KEYWORDS = [
    # Medical & Imaging Keywords
    "medical", "clinical", "radiology", "mri", "ct scan", "x-ray", "ultrasound", 
    "pathology", "image analysis", "segmentation", "classification", "diagnosis",
    # Quantum Keywords
    "quantum", "quantum machine learning", "qml", "quantum computing", 
    "quantum neural network", "qnn", "quantum circuit", "quantum image", 
    "quantum computer vision", "qubit", "quantum state"
]

DATA_FILE = "sent_quantum_papers.json"
MAX_RESULTS = 30

# ─── HELPERS ────────────────────────────────────────────

def load_sent_papers():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent_papers(paper_ids):
    with open(DATA_FILE, "w") as f:
        json.dump(list(paper_ids), f)

def is_quantum_medical_vision(title, summary):
    text = (title + " " + summary).lower()
    # Must contain at least one quantum-related keyword and one medical/vision-related keyword
    quantum_hit = any(q_kw in text for kw in KEYWORDS[12:] for q_kw in [kw])
    domain_hit = any(d_kw in text for kw in KEYWORDS[:12] for d_kw in [kw])
    
    # Alternatively, ensure "quantum" is explicitly present along with medical or vision terms
    has_quantum = "quantum" in text or "qml" in text or "qubit" in text
    has_medical_or_vision = any(term in text for term in [
        "medical", "clinical", "radiology", "mri", "ct", "image", "vision", 
        "segmentation", "classification", "pathology", "scan"
    ])
    
    return has_quantum and has_medical_or_vision

# 1. Fetch from arXiv (Targeting Quant-Ph, CS.CV, CS.LG)
def fetch_arxiv_papers():
    papers = []
    try:
        # Searching across quantum physics, computer vision, and machine learning categories
        arxiv_query = "cat:quant-ph OR cat:cs.CV OR cat:cs.LG"
        query = urllib.parse.quote(arxiv_query)
        url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results={MAX_RESULTS}&sortBy=submittedDate&sortOrder=descending"

        req = urllib.request.Request(url, headers={"User-Agent": "ResearchPaperAgent/1.0"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(data)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=48) # Extended window to catch recent quantum papers

        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            published = entry.find("atom:published", ns)
            id_elem = entry.find("atom:id", ns)
            link = entry.find("atom:link[@rel='alternate']", ns)

            if title is None or published is None or id_elem is None:
                continue

            pub_date = datetime.fromisoformat(published.text.replace("Z", "+00:00"))
            if pub_date < cutoff:
                continue

            title_text = title.text.strip().replace("\n", " ")
            summary_text = summary.text.strip().replace("\n", " ") if summary is not None else ""
            paper_id = "arxiv_" + id_elem.text.strip().split('/')[-1]
            paper_link = link.get("href") if link is not None else id_elem.text.strip()

            authors = [a.text for a in entry.findall("atom:author/atom:name", ns)[:3]]
            author_str = ", ".join(authors) + (" et al." if len(entry.findall("atom:author/atom:name", ns)) > 3 else "")

            if is_quantum_medical_vision(title_text, summary_text):
                papers.append({
                    "id": paper_id,
                    "title": title_text,
                    "summary": summary_text[:400] + "..." if len(summary_text) > 400 else summary_text,
                    "authors": author_str,
                    "link": paper_link,
                    "published": pub_date.strftime("%Y-%m-%d %H:%M UTC"),
                    "source": "arXiv"
                })
    except Exception as e:
        print(f"⚠️ Error fetching from arXiv: {e}")
    
    return papers

# 2. Fetch from PubMed (NCBI API) - Focused on Quantum + Medical Imaging
def fetch_pubmed_papers():
    papers = []
    try:
        term = '("quantum computing" OR "quantum machine learning" OR "quantum image") AND ("medical imaging" OR "radiology" OR "mri" OR "image analysis")'
        encoded_term = urllib.parse.quote(term)
        
        search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={encoded_term}&retmax=15&sort=date&retmode=json"
        req = urllib.request.Request(search_url, headers={"User-Agent": "ResearchPaperAgent/1.0"})
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            id_list = data.get("esearchresult", {}).get("idlist", [])

        if not id_list:
            return papers

        ids_str = ",".join(id_list)
        summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
        req_sum = urllib.request.Request(summary_url, headers={"User-Agent": "ResearchPaperAgent/1.0"})
        
        with urllib.request.urlopen(req_sum, timeout=30) as response:
            sum_data = json.loads(response.read().decode())
            result = sum_data.get("result", {})

        for p_id in id_list:
            if p_id not in result:
                continue
            item = result[p_id]
            title = item.get("title", "").strip().rstrip('.')
            pub_date = item.get("pubdate", "")
            source_journal = item.get("source", "PubMed Journal")
            
            papers.append({
                "id": f"pubmed_{p_id}",
                "title": title,
                "summary": f"Published in {source_journal} on {pub_date}.",
                "authors": ", ".join([au.get("name", "") for au in item.get("authors", [])[:3]]) + " et al.",
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{p_id}/",
                "published": pub_date,
                "source": "PubMed"
            })
    except Exception as e:
        print(f"⚠️ Error fetching from PubMed: {e}")

    return papers

def send_email(papers):
    if not papers:
        subject = f"😴 Quantum Medical Papers — No new papers today | {datetime.now().strftime('%b %d, %Y')}"
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: auto; background: #fff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
                h1 {{ color: #1a237e; font-size: 22px; margin-bottom: 5px; }}
                .subtitle {{ color: #666; font-size: 14px; margin-bottom: 25px; }}
                .message {{ font-size: 15px; color: #444; background: #f9f9f9; padding: 15px; border-left: 4px solid #ff9800; border-radius: 4px; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #999; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚛️ Quantum Research Paper Agent</h1>
                <div class="subtitle">Quantum Computer Vision & Medical Imaging Monitor | {datetime.now().strftime('%A, %B %d, %Y')}</div>
                <div class="message">
                    <strong>Status Update:</strong> Agent run successfully, par aaj Quantum Computer Vision / Medical Imaging se munsalik koi naya paper publish nahi hua hai. System active hai!
                </div>
                <div class="footer">
                    Sent by Quantum Research Paper Agent 🤖
                </div>
            </div>
        </body>
        </html>
        """
    else:
        subject = f"⚛️ Quantum Medical/Vision Papers — {len(papers)} new paper(s) | {datetime.now().strftime('%b %d, %Y')}"
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                .container {{ max-width: 700px; margin: auto; background: #fff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
                h1 {{ color: #1a237e; font-size: 22px; margin-bottom: 5px; }}
                .subtitle {{ color: #666; font-size: 14px; margin-bottom: 25px; }}
                .paper {{ border-left: 4px solid #673ab7; padding-left: 15px; margin-bottom: 25px; }}
                .paper-title {{ font-size: 16px; font-weight: bold; color: #512da8; margin-bottom: 5px; }}
                .paper-meta {{ font-size: 12px; color: #888; margin-bottom: 8px; }}
                .paper-summary {{ font-size: 14px; color: #444; line-height: 1.5; }}
                .paper-link {{ display: inline-block; margin-top: 8px; color: #fff; background: #673ab7; padding: 6px 14px; text-decoration: none; border-radius: 6px; font-size: 13px; }}
                .badge {{ background: #ede7f6; color: #512da8; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #999; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚛️ Quantum Research Paper Agent</h1>
                <div class="subtitle">Quantum Computer Vision & Medical Imaging Monitor | {datetime.now().strftime('%A, %B %d, %Y')}</div>
        """

        for p in papers:
            html_body += f"""
                <div class="paper">
                    <div class="paper-title">{p['title']}</div>
                    <div class="paper-meta">
                        <span class="badge">{p['source']}</span> &nbsp;|&nbsp; 👤 {p['authors']} &nbsp;|&nbsp; 📅 {p['published']}
                    </div>
                    <div class="paper-summary">{p['summary']}</div>
                    <a class="paper-link" href="{p['link']}">Read Paper →</a>
                </div>
            """

        html_body += f"""
                <div class="footer">
                    Sent by Quantum Research Paper Agent 🤖
                </div>
            </div>
        </body>
        </html>
        """

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        
        for recipient in EMAIL_RECIPIENTS:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = EMAIL_SENDER
            msg["To"] = recipient
            msg.attach(MIMEText(html_body, "html"))
            
            server.sendmail(EMAIL_SENDER, recipient, msg.as_string())

    print(f"✅ Email sent to {', '.join(EMAIL_RECIPIENTS)}. Total papers: {len(papers)}")

def main():
    print("🔍 Fetching latest Quantum Medical & Computer Vision papers...")
    sent_papers = load_sent_papers()
    
    arxiv_papers = fetch_arxiv_papers()
    pubmed_papers = fetch_pubmed_papers()
    
    all_papers = arxiv_papers + pubmed_papers

    new_papers = [p for p in all_papers if p["id"] not in sent_papers]

    if new_papers:
        print(f"📨 Found {len(new_papers)} new paper(s). Sending email...")
        send_email(new_papers)
        for p in new_papers:
            sent_papers.add(p["id"])
        save_sent_papers(sent_papers)
    else:
        print("😴 No new papers today. Sending status email...")
        send_email([])

if __name__ == "__main__":
    main()
