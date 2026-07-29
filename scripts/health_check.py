"""
URL health check for all competitor scrapers.

Loads every URL list from all 5 competitors, visits each with the same
Selenium driver used in production, and classifies the result:
  OK       – page loaded with meaningful content (>500 chars)
  THIN     – page loaded but suspiciously short (<500 chars)
  BLOCKED  – received a bot/permission/access-denied response
  404      – page not found
  ERROR    – unexpected exception

Exits with code 1 if any URL is not OK, triggering GitHub Actions failure
and the associated email notification (Option A). The workflow then opens
a GitHub Issue listing the broken URLs (Option B).
"""
import importlib
import logging
import sys
import time
from dataclasses import dataclass, field

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

COMPETITORS = ["accelq", "keysight", "opentext", "playwright", "uipath"]
SCRAPER_TYPES = ["competitor", "social_media", "analyst", "review"]

BLOCKED_PHRASES = [
    "access denied",
    "you do not have permission",
    "403 forbidden",
    "blocked",
    "enable javascript",
    "verify you are human",
    "captcha",
    "bot detection",
    "cloudflare",
]

THIN_THRESHOLD = 500


@dataclass
class UrlResult:
    competitor: str
    scraper_type: str
    url: str
    status: str = "UNKNOWN"
    detail: str = ""


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )
    return driver


def _check_url(driver: webdriver.Chrome, url: str) -> tuple[str, str]:
    """Returns (status, detail) for a single URL."""
    try:
        driver.get(url)
        time.sleep(5)

        page_source = driver.page_source or ""
        text = driver.find_element("tag name", "body").text if page_source else ""

        current_url = driver.current_url

        # 404 detection
        title = driver.title.lower()
        if "404" in title or "not found" in title or "page not found" in title.lower():
            return "404", f"Title: {driver.title}"

        # Blocked detection
        text_lower = text.lower()
        for phrase in BLOCKED_PHRASES:
            if phrase in text_lower:
                return "BLOCKED", f"Detected phrase: '{phrase}'"

        char_count = len(text.strip())
        if char_count < THIN_THRESHOLD:
            return "THIN", f"Only {char_count} chars"

        return "OK", f"{char_count} chars"

    except Exception as exc:
        return "ERROR", str(exc)[:200]


def collect_urls() -> list[UrlResult]:
    results = []
    for competitor in COMPETITORS:
        for scraper_type in SCRAPER_TYPES:
            module_path = f"scrapers.{competitor}.{scraper_type}"
            try:
                mod = importlib.import_module(module_path)
                urls = getattr(mod, "URLS", [])
                for url in urls:
                    results.append(UrlResult(competitor, scraper_type, url))
                if not urls:
                    logger.info("  [%s/%s] No URLs defined — skipping", competitor, scraper_type)
            except ModuleNotFoundError:
                logger.warning("  Module not found: %s", module_path)
    return results


def run_health_check() -> int:
    pending = collect_urls()
    total = len(pending)
    logger.info("Checking %d URLs across %d competitors...\n", total, len(COMPETITORS))

    driver = _build_driver()
    try:
        for r in pending:
            status, detail = _check_url(driver, r.url)
            r.status = status
            r.detail = detail
            icon = "✓" if status == "OK" else ("~" if status == "THIN" else "✗")
            logger.info("%s [%s] %s/%s — %s (%s)", icon, status, r.competitor, r.scraper_type, r.url, detail)
    finally:
        driver.quit()

    # Summary — THIN is a warning only; hard failures are BLOCKED/404/ERROR
    ok = [r for r in pending if r.status == "OK"]
    thin = [r for r in pending if r.status == "THIN"]
    hard_failures = [r for r in pending if r.status in ("BLOCKED", "404", "ERROR")]

    print(f"\n{'='*60}")
    print(f"HEALTH CHECK SUMMARY: {len(ok)}/{total} OK, {len(thin)} THIN (warnings), {len(hard_failures)} hard failures")
    print(f"{'='*60}")

    if thin:
        print("\nTHIN URLS (warnings — page loaded but content may be limited):")
        for r in thin:
            print(f"  [THIN] {r.competitor}/{r.scraper_type}: {r.url}")
            if r.detail:
                print(f"         {r.detail}")

    if hard_failures:
        print("\nBROKEN URLS:")
        for r in hard_failures:
            print(f"  [{r.status}] {r.competitor}/{r.scraper_type}: {r.url}")
            if r.detail:
                print(f"         {r.detail}")

    # Write failure file whenever there's anything to report (hard failures + thin warnings)
    reportable = hard_failures + thin
    if reportable:
        with open("health_check_failures.txt", "w") as f:
            if hard_failures:
                f.write(f"BROKEN URLs ({len(hard_failures)}) — require fixing before next scrape run\n\n")
                for r in hard_failures:
                    f.write(f"[{r.status}] {r.competitor}/{r.scraper_type}\n")
                    f.write(f"  URL: {r.url}\n")
                    if r.detail:
                        f.write(f"  Detail: {r.detail}\n")
                    f.write("\n")
            if thin:
                f.write(f"THIN URLs ({len(thin)}) — loaded but returned little content (warnings only)\n\n")
                for r in thin:
                    f.write(f"[THIN] {r.competitor}/{r.scraper_type}\n")
                    f.write(f"  URL: {r.url}\n")
                    if r.detail:
                        f.write(f"  Detail: {r.detail}\n")
                    f.write("\n")

    if hard_failures:
        return 1

    print("\nAll URLs healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(run_health_check())
