"""One-time browser-based authentication for Garmin Connect.

Opens a real Chromium browser window. Log in manually to Garmin Connect,
then press Enter. Captures all garmin-domain cookies and CSRF token for
use by the MCP server via the web proxy API (connect.garmin.com/gc-api/).

    pdm run garmin-auth
"""

import asyncio
import json
import sys
from pathlib import Path

SESSION_FILE = Path("~/.garmin-connect-mcp/session.json").expanduser()


def main() -> None:
    asyncio.run(_run_login())


async def _run_login() -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context()
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        page = await context.new_page()

        await page.goto("https://connect.garmin.com/app/activities")

        print("Log in to Garmin Connect in the browser window.")
        print("Once you can see your activities list, press Enter here...")
        with open("/dev/tty") as tty:
            tty.readline()

        all_cookies = await context.cookies()
        garmin_cookie_names = [c["name"] for c in all_cookies if "garmin" in c.get("domain", "")]
        print(f"Garmin cookies found: {garmin_cookie_names}")

        csrf_token = await page.evaluate(
            "() => document.querySelector('meta[name=\"csrf-token\"]')?.content ?? null"
        )

        await browser.close()

        garmin_cookies = [
            {"name": c["name"], "value": c["value"], "domain": c["domain"]}
            for c in all_cookies
            if c.get("domain") and "garmin" in c["domain"]
        ]

        if not garmin_cookies:
            print("ERROR: No Garmin cookies found. Make sure you are fully logged in.", file=sys.stderr)
            sys.exit(1)

        session: dict = {
            "csrf_token": csrf_token or "",
            "cookies": garmin_cookies,
        }

        if csrf_token:
            print("Cookies and CSRF token captured.")
        else:
            print("Warning: CSRF token not found in page meta — some requests may fail.", file=sys.stderr)
            print("Cookies captured.")

        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        SESSION_FILE.parent.chmod(0o700)
        SESSION_FILE.write_text(json.dumps(session))
        SESSION_FILE.chmod(0o600)

        print(f"Session saved to {SESSION_FILE}")
        print("You can now start the MCP server.")


if __name__ == "__main__":
    main()
