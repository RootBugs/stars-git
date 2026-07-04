"""GitHub Star Bot - Authentication & Starring

Handles GitHub login, account creation, and starring repos via Selenium.
"""
from __future__ import annotations

import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from captcha_solver import solve_hcaptcha, take_captcha_screenshot
from config import HEADLESS
from email_gen import check_inbox, generate_email


_created_accounts: dict[str, str] = {}


def create_driver():
    """Create and return a Selenium WebDriver instance (Chrome)."""
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    return driver


def login_to_github(driver, email, password):
    """Log in to GitHub with given credentials. Returns True on success."""
    try:
        driver.get("https://github.com/login")
        wait = WebDriverWait(driver, 10)
        email_input = wait.until(EC.presence_of_element_located((By.ID, "login_field")))
        email_input.send_keys(email)
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)
        return "dashboard" in driver.current_url or "github.com/" == driver.current_url.rstrip("/")
    except Exception as e:
        print(f"Login failed: {e}")
        return False

def create_account(driver, email, username, password):
    """Create a new GitHub account. Returns True on success."""
    try:
        driver.get("https://github.com/signup")
        wait = WebDriverWait(driver, 10)
        time.sleep(2)

        # Enter email
        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        time.sleep(2)

        # Solve captcha if present
        try:
            iframe = driver.find_element(By.CSS_SELECTOR, "iframe[title*='captcha'], iframe[src*='hcaptcha']")
            driver.switch_to.frame(iframe)
            screenshot = take_captcha_screenshot(driver)
            driver.switch_to.default_content()
            token = solve_hcaptcha(
                api_key="",
                site_key="",
                page_url=driver.current_url,
                screenshot_b64=screenshot,
                email=email,
            )
        except Exception:
            pass

        # Enter username
        username_input = wait.until(EC.presence_of_element_located((By.ID, "login")))
        username_input.clear()
        username_input.send_keys(username)
        username_input.send_keys(Keys.RETURN)
        time.sleep(1)

        # Enter password
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Check for email verification
        if "verify" in driver.current_url.lower() or "pending" in driver.current_url.lower():
            print(f"Email verification needed for {email}")
            verification_code = _get_verification_code(email)
            if verification_code:
                code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
                code_input.send_keys(verification_code)
                code_input.send_keys(Keys.RETURN)
                time.sleep(3)

        success = "github.com" in driver.current_url and "signup" not in driver.current_url
        if success:
            _created_accounts[email] = username
        return success
    except Exception as e:
        print(f"Account creation failed: {e}")
        return False

def star_repository(driver, repo_url: str) -> bool:
    """Star a repository. Returns True if starred successfully."""
    try:
        driver.get(repo_url)
        wait = WebDriverWait(driver, 10)
        time.sleep(2)

        # Find and click the star button
        star_button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR,
            "button[data-component='StarButton'], button[aria-label*='star']",
        )))
        star_button.click()
        time.sleep(2)
        print(f"Starred: {repo_url}")
        return True
    except Exception as e:
        print(f"Failed to star {repo_url}: {e}")
        return False

def _get_verification_code(email: str, max_wait: int = 120) -> str | None:
    """Poll inbox for GitHub verification code."""
    import re
    print(f"  Waiting for verification code sent to {email}...")
    for i in range(max_wait // 5):
        messages = check_inbox(email, since_minutes=5)
        for msg in messages:
            if "github" in msg.get("from", "").lower():
                body = msg.get("body", "")
                # Look for verification code pattern
                match = re.search(r"verification[\s:]+([a-z0-9]{6,})", body, re.IGNORECASE)
                if match:
                    code = match.group(1)
                    print(f"  Found verification code: {code}")
                    return code
        time.sleep(5)
    return None


def create_and_star(username_base: str, password: str, repo_urls: list[str]) -> dict[str, bool]:
    """Create a GitHub account and star given repos.

    Returns dict mapping repo_url -> success bool.
    """
    results = {}
    email = generate_email()
    if not email:
        print("Failed to generate email")
        return results
    username = username_base + str(random.randint(100, 999))
    driver = create_driver()
    try:
        account_ok = create_account(driver, email, username, password)
        if not account_ok:
            login_ok = login_to_github(driver, email, password)
            if not login_ok:
                print(f"Could not create or login with {email}")
                return results

        for url in repo_urls:
            results[url] = star_repository(driver, url)
            time.sleep(random.uniform(2, 5))
    finally:
        driver.quit()
    return results
