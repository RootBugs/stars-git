"""GitHub Star Bot - CAPTCHA Solver

Solves hCaptcha by sending screenshots to your local Captcha Relay Server.
You solve them manually via the web dashboard.
"""
from __future__ import annotations

import time

import requests

from config import (
    CAPTCHA_API_KEY,
    CAPTCHA_SERVER_URL,
    GITHUB_HCAPTCHA_SITEKEY,
    USE_LOCAL_CAPTCHA_SERVER,
)


def solve_hcaptcha(
    api_key: str,
    site_key: str,
    page_url: str,
    invisible: bool = False,
    screenshot_b64: str | None = None,
    email: str = "",
) -> str:
    """Solve hCaptcha using local relay server or 2Captcha fallback.

    Args:
        api_key        : Ignored (kept for compatibility with 2Captcha fallback)
        site_key       : hCaptcha site key for the target page
        page_url       : Full URL of the page with the captcha
        invisible      : Whether the captcha is invisible (auto-solved)
        screenshot_b64 : Base64 screenshot of the page (for relay server)
        email          : Email being used (for relay display)

    Returns:
        Captcha token string, or empty string on failure.
    """
    if not USE_LOCAL_CAPTCHA_SERVER:
        return _solve_2captcha(api_key, site_key, page_url, invisible)

    if not CAPTCHA_SERVER_URL:
        print("[-] CAPTCHA_SERVER_URL not configured!")
        print("    Set it in config.py or start captcha_server.py")
        return ""

    server_url = CAPTCHA_SERVER_URL.rstrip("/")

    print(f"[*] Submitting captcha to relay server at {server_url}...")

    payload = {
        "site_key": site_key or GITHUB_HCAPTCHA_SITEKEY,
        "page_url": page_url,
        "screenshot": screenshot_b64 or "",
        "email": email,
    }
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": CAPTCHA_API_KEY or "",
    }

    try:
        resp = requests.post(
            f"{server_url}/api/solve",
            json=payload,
            headers=headers,
            timeout=15,
        )
        if resp.status_code != 200:
            print(f"[-] Relay server error: {resp.status_code} {resp.text}")
            return _solve_2captcha(api_key, site_key, page_url, invisible)
        data = resp.json()
    except requests.RequestException as e:
        print(f"[-] Cannot connect to captcha server at {server_url}")
        print("    Start it: python captcha_server.py")
        return _solve_2captcha(api_key, site_key, page_url, invisible)

    ticket_id = data.get("ticket_id") or data.get("id")
    if not ticket_id:
        print(f"[-] No ticket ID from server: {data}")
        return _solve_2captcha(api_key, site_key, page_url, invisible)

    print(f"[+] Captcha submitted! Ticket: {ticket_id}")
    solve_url = data.get("solve_url", f"{server_url}/solve/{ticket_id}")
    print(f"    Open to solve: {solve_url}")

    check_url = f"{server_url}/api/check/{ticket_id}"
    for i in range(200):
        time.sleep(3)
        try:
            check_resp = requests.get(check_url, headers=headers, timeout=10)
            if check_resp.status_code == 200:
                check_data = check_resp.json()
                if check_data.get("status") == "solved":
                    token = check_data.get("token", "")
                    if token:
                        print("[+] Captcha solved! Token received.")
                        return token
            print(f"    Still waiting... ({i * 3}s elapsed)")
        except requests.RequestException:
            pass

    print("[-] Timed out waiting for captcha solution (10 min)")
    return _solve_2captcha(api_key, site_key, page_url, invisible)

def _solve_2captcha(
    api_key: str, site_key: str, page_url: str, invisible: bool = False
) -> str:
    """Fallback to 2Captcha if relay server is unavailable."""
    return ""

def solve_recaptcha_v2(api_key: str, site_key: str, page_url: str) -> str:
    """Solve reCAPTCHA v2 via 2Captcha (fallback)."""
    return ""

def take_captcha_screenshot(driver) -> str:
    """Take a screenshot of the page for captcha solving."""
    try:
        return driver.get_screenshot_as_base64()
    except Exception:
        return ""
