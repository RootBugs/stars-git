"""GitHub Star Bot - Email Generator

Generates unique email addresses and reads verification inbox.
"""
from __future__ import annotations

import imaplib
import email
import random
import time
from email.header import decode_header

import requests

from config import (
    GMAIL_BASE_EMAIL,
    GMAIL_IMAP_PASSWORD,
    GMAIL_IMAP_SERVER,
    GMAIL_IMAP_PORT,
    IMAP_PASSWORD,
    IMAP_PORT,
    IMAP_SERVER,
    IMAP_USERNAME,
    KWEN_DOMAIN,
)


_temp_tokens: dict[str, str] = {}




def generate_email(mode: str = "") -> str:
    """Generate a unique email address based on the configured mode."""
    if mode == "gmail":
        return _generate_gmail_variant()
    elif mode == "domain":
        return _generate_domain_email()
    elif mode == "temp":
        return _generate_temp_email()
    return _generate_gmail_variant()

def _generate_gmail_variant() -> str:
    """
    Generates a unique variant of the base Gmail email using dot tricks.
    Gmail ignores dots, so all variants go to the same inbox.
    """
    base = GMAIL_BASE_EMAIL
    name, domain = base.split("@")
    clean_name = name.replace(".", "")
    num = random.randint(1, 99999)
    technique = random.choice(["dot_random", "dot_all", "plus"])

    if technique == "dot_random":
        chars = list(clean_name)
        dot_positions = list(range(1, len(chars)))
        if dot_positions:
            k = min(3, len(dot_positions))
            dots = random.sample(dot_positions, k=k)
            for pos in sorted(dots, reverse=True):
                if pos < len(chars):
                    chars.insert(pos, ".")
        variant = "".join(chars)
    elif technique == "dot_all":
        variant = ".".join(clean_name)
    else:  # plus
        tags = ["git", "star", "dev", "acc", "hub", "gh", "bot", "code"]
        tag = random.choice(tags)
        variant = f"{clean_name}+{tag}.{num}"

    return f"{variant}@{domain}"

def _generate_domain_email() -> str:
    """Generates a random @kwen.in address."""
    prefixes = ["dev", "git", "star", "code", "hub", "octo", "push", "pull", "fork", "merge", "alpha", "beta"]
    indian_names = ["rohit", "rahul", "amit", "vikas", "sanjay", "manoj", "ankit", "sunil", "rajesh", "deepak", "naveen", "pankaj", "sarthak", "aryan", "karan", "tanya", "priya", "neha"]
    prefix = random.choice(prefixes)
    name = random.choice(indian_names)
    num = random.randint(1, 9999)
    return f"{prefix}_{name}.{num}@kwen.in"

def _generate_temp_email() -> str:
    """Generates a temp email using mail.tm API (free)."""
    import requests
    try:
        resp = requests.get(
            "https://api.mail.tm/domains",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        if resp.status_code != 200:
            return ""
        domains = resp.json().get("hydra:member", [])
        if not domains:
            return ""
        domain = domains[0].get("domain", "")
        if not domain:
            return ""
        username = "user" + str(random.randint(10000, 99999))
        password = "TempPass123!"
        email_addr = username + "@" + domain
        data = {"address": email_addr, "password": password}
        resp = requests.post(
            "https://api.mail.tm/accounts",
            json=data,
            timeout=10,
        )
        if resp.status_code == 201:
            token_resp = requests.post(
                "https://api.mail.tm/token",
                json={"address": email_addr, "password": password},
                timeout=10,
            )
            if token_resp.status_code == 200:
                token_data = token_resp.json()
                _temp_tokens[email_addr] = token_data.get("token", "")
                return email_addr
        return ""
    except Exception:
        return ""

def check_inbox(email_addr: str, since_minutes: int = 5) -> list[dict]:
    """Check inbox for verification emails."""
    messages = []
    if "@" in email_addr and email_addr.split("@")[1] == "gmail.com":
        return _check_gmail_inbox(email_addr, since_minutes)
    if email_addr in _temp_tokens:
        return _check_temp_inbox(email_addr, since_minutes)
    return messages


def _check_gmail_inbox(email_addr: str, since_minutes: int) -> list[dict]:
    """Check Gmail inbox via IMAP."""
    messages = []
    try:
        mail = imaplib.IMAP4_SSL(GMAIL_IMAP_SERVER, GMAIL_IMAP_PORT)
        mail.login(GMAIL_BASE_EMAIL, GMAIL_IMAP_PASSWORD)
        mail.select("inbox")
        since_date = time.time() - since_minutes * 60
        since_str = time.strftime("%d-%b-%Y", time.gmtime(since_date))
        status, data = mail.search(None, f"(SINCE {since_str})")
        if status == "OK":
            for num in data[0].split():
                status_msg, msg_data = mail.fetch(num, "(RFC822)")
                if status_msg == "OK":
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    subject = ""
                    if msg["Subject"]:
                        decoded = decode_header(msg["Subject"])
                        parts = []
                        for part_text, charset in decoded:
                            if isinstance(part_text, bytes):
                                parts.append(part_text.decode(charset or "utf-8"))
                            else:
                                parts.append(part_text)
                        subject = " ".join(parts)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    messages.append({
                        "subject": subject,
                        "body": body,
                        "from": msg["From"] or "",
                    })
        mail.logout()
    except Exception:
        pass
    return messages


def _check_temp_inbox(email_addr: str, since_minutes: int) -> list[dict]:
    """Check mail.tm inbox for verification codes."""
    import requests
    messages = []
    token = _temp_tokens.get(email_addr, "")
    if not token:
        return messages
    try:
        headers = {
            "Authorization": "Bearer " + token,
            "User-Agent": "Mozilla/5.0",
        }
        resp = requests.get(
            "https://api.mail.tm/messages",
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("hydra:member", []):
                msg_id = item.get("id", "")
                if msg_id:
                    msg_resp = requests.get(
                        "https://api.mail.tm/messages/" + msg_id,
                        headers=headers,
                        timeout=10,
                    )
                    if msg_resp.status_code == 200:
                        msg_data = msg_resp.json()
                        messages.append({
                            "subject": msg_data.get("subject", ""),
                            "body": msg_data.get("text", "") or msg_data.get("html", ""),
                            "from": msg_data.get("from", {}).get("address", ""),
                        })
    except Exception:
        pass
    return messages
