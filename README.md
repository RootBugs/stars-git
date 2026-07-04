# Stars-Git

> **Automate your GitHub stars workflow** — captcha solving, email generation, and authentication handling for programmatic GitHub interactions.

---

## Overview

Stars-Git is a Python-based automation toolkit designed for programmatic GitHub interactions. It handles the tricky parts of automation — captcha solving, temporary email creation, and authentication — so you can focus on the actual automation logic.

---

## Modules

### `github_auth.py`
GitHub authentication handler that manages login sessions, token refresh, and multi-factor authentication workflows.

### `captcha_solver.py`
Automated captcha solving module with support for:
- Image-based captcha recognition
- Automated submission with retry logic
- Configurable solving strategies

### `email_gen.py`
Temporary email generation for account creation:
- Generates disposable email addresses
- Integrates with temp email services
- Auto-retrieves verification links

### `config.py`
Centralized configuration management:
- Proxy settings and rotation
- User-agent rotation
- Rate limiting and delays
- Logging configuration

---

## Quick Start

```bash
# Clone and run
git clone https://github.com/RootBugs/stars-git.git
cd stars-git

# Install dependencies
pip install requests beautifulsoup4 pillow

# Configure
cp config.example.py config.py
# Edit config.py with your settings

# Run the automation
python github_auth.py
```

---

## Features

- 🔄 **Proxy Rotation** — Rotate through proxies to avoid IP bans
- 🧪 **User-Agent Spoofing** — Randomize browser fingerprints
- 🛡️ **Rate Limiting** — Smart throttling to avoid detection
- 📝 **Logging** — Detailed activity logs for debugging
- ✅ **Retry Logic** — Automatic retry on failure with exponential backoff

---

## Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `PROXY_LIST` | List of proxies to rotate | `[]` |
| `DELAY_MIN` | Min delay between actions (sec) | `2` |
| `DELAY_MAX` | Max delay between actions (sec) | `5` |
| `MAX_RETRIES` | Max retry attempts on failure | `3` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

---

## License

MIT
