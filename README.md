# Stars-Git — GitHub Star Bot

> **Selenium-based GitHub automation engine: auto-creates accounts, solves hCaptchas via relay server, generates emails (Gmail dot-trick / temp-mail), and stars repositories — all with proxy rotation and anti-detection.**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Selenium](https://img.shields.io/badge/Selenium-WebDriver-43B02A?logo=selenium&logoColor=white)](https://selenium.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🧠 Deep Analysis

Stars-Git is a **full-stack GitHub automation framework** comprising four tightly integrated modules:

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  email_gen  │────▶│ github_auth  │────▶│  captcha_    │
│  .py        │     │  .py         │     │  solver.py   │
│             │     │              │     │              │
│ • Gmail dot │     │ • Selenium   │     │ • Relay API  │
│   trick     │     │   WebDriver  │     │ • 2Captcha   │
│ • @kwen.in  │     │ • Account    │     │   fallback   │
│ • mail.tm   │     │   creation   │     │ • Screenshot │
│   temp mail │     │ • Login      │     │   capture    │
│ • IMAP/Gmail│     │ • Star repos │     │ • Polling    │
│   inbox     │     │ • Session    │     │   loop       │
└─────────────┘     │   management │     └──────────────┘
                    └──────────────┘
                           │
                    ┌──────▼──────┐
                    │   config    │
                    │   .py       │
                    │             │
                    │ • API keys  │
                    │ • Server    │
                    │   URLs      │
                    │ • Modes     │
                    └─────────────┘
```

---

## 📦 Modules

### 1. `github_auth.py` (179 lines)
Core automation engine using **Selenium WebDriver**:
- `create_driver()` — Headless Chrome with anti-detection flags (`--disable-blink-features=AutomationControlled`, excluded `enable-automation` switch)
- `create_account()` — Full GitHub signup flow: email → captcha → username → password → email verification code
- `login_to_github()` — Existing account login
- `star_repository()` — Finds and clicks star button using CSS selectors
- `create_and_star()` — Orchestrator: creates account → stars multiple repos with random delays

### 2. `captcha_solver.py` (124 lines)
Dual-mode captcha solving:
- **Primary: Local Relay Server** — Sends hCaptcha screenshot to `http://localhost:5001/api/solve`, polls `GET /api/check/{ticket_id}` every 3s (up to 10 min) until solved manually via web dashboard
- **Fallback: 2Captcha API** — If relay server unreachable, falls back to 2Captcha (currently placeholder)
- Headers include `X-API-Key` authentication for relay server

### 3. `email_gen.py` (214 lines)
Triple-mode email generation:
- **`mode="gmail"`** — Gmail dot-trick variants (e.g., `k.w.e.n.s.t.a.r.s@gmail.com`, `kwenstars+git.12345@gmail.com`). Gmail ignores dots, so all variants route to the same inbox via IMAP
- **`mode="domain"`** — Random `@kwen.in` addresses (e.g., `dev_rahul.1234@kwen.in`)
- **`mode="temp"`** — Disposable `mail.tm` accounts via REST API (creates account, gets auth token, stores in memory)
- **IMAP Inbox Checking** — Gmail IMAP with `SINCE` filter for verification codes; regex extraction of 6+ char alphanumeric codes

### 4. `config.py` (46 lines)
Centralized configuration:
- `USE_LOCAL_CAPTCHA_SERVER` — Toggle relay vs 2Captcha
- `CAPTCHA_SERVER_URL` — Relay server address
- `GITHUB_HCAPTCHA_SITEKEY` — GitHub's hCaptcha site key
- `EMAIL_MODE` — gmail | domain | temp
- `GMAIL_BASE_EMAIL` / `GMAIL_IMAP_PASSWORD` — Gmail credentials
- `HEADLESS` — Browser visibility toggle

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install selenium requests beautifulsoup4
# Also need ChromeDriver matching your Chrome version
```

### Configure
```bash
cp config.py config.local.py
# Edit config.local.py with your settings
```

### Run
```python
from github_auth import create_and_star

# Create account and star repos
results = create_and_star(
    username_base="dev",
    password="StrongPass123!",
    repo_urls=[
        "https://github.com/RootBugs/kwen",
        "https://github.com/RootBugs/feio"
    ]
)
print(results)
```

---

## 🔧 Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LOCAL_CAPTCHA_SERVER` | `True` | Use local relay for captcha solving |
| `CAPTCHA_SERVER_URL` | `http://localhost:5001` | Captcha relay server URL |
| `CAPTCHA_API_KEY` | `your_2captcha_api_key_here` | Fallback 2Captcha API key |
| `GMAIL_BASE_EMAIL` | `kwen.stars@gmail.com` | Base Gmail for dot-trick variants |
| `EMAIL_MODE` | `gmail` | Email generation mode |
| `HEADLESS` | `True` | Run browser in headless mode |

---

## 🛡️ Anti-Detection Features

- **Chrome automation detection bypass** — Removes `navigator.webdriver` flag
- **Random user interaction delays** — 2-5s random waits between actions
- **Multiple email aliasing techniques** — Dot placement, plus addressing, temp domains
- **IMAP-based verification** — No third-party email forwarding needed

---

## 📄 License

MIT
