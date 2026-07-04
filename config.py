"""
GitHub Star Bot - Configuration
Edit these settings before running the bot.
"""

# === CAPTCHA SETTINGS ===

# If True, sends captcha screenshots to a local relay server
# where you solve them manually via web dashboard
USE_LOCAL_CAPTCHA_SERVER = True

# Local relay server URL (used when USE_LOCAL_CAPTCHA_SERVER = True)
CAPTCHA_SERVER_URL = "http://localhost:5001"

# 2Captcha API key (fallback when local server is off)
CAPTCHA_API_KEY = "your_2captcha_api_key_here"

# hCaptcha site key for GitHub
GITHUB_HCAPTCHA_SITEKEY = "4c672d35-0701-42b2-936c-855e849f0c6c"

# === EMAIL SETTINGS ===

# How to generate email addresses
# "gmail"  - use Gmail dot trick variants (recommended, requires App Password)
# "domain" - use a custom domain catch-all address (e.g. @kwen.in)
# "temp"   - use disposable temp mail (free, may get blocked)
EMAIL_MODE = "gmail"

# === Gmail Settings (for EMAIL_MODE = "gmail") ===
GMAIL_BASE_EMAIL = "kwen.stars@gmail.com"
GMAIL_IMAP_SERVER = "imap.gmail.com"
GMAIL_IMAP_PORT = 993
GMAIL_IMAP_PASSWORD = "your_app_password_here"

# === Custom Domain Settings (for EMAIL_MODE = "domain") ===
KWEN_DOMAIN = "kwen.in"
IMAP_SERVER = "imap.yourdomain.com"
IMAP_PORT = 993
IMAP_USERNAME = "your@email.com"
IMAP_PASSWORD = "your_imap_password"

# === BROWSER ===

# Headless mode (set to False to see the browser)
HEADLESS = True
