"""Playwright-based client for connect.garmin.com/gc-api/ web proxy.

Routes all API calls through a headless Chromium page.evaluate(fetch())
to inherit Chromium's TLS fingerprint and bypass Cloudflare 403 blocks.
"""

import json
from pathlib import Path
from typing import Any

SESSION_FILE = Path("~/.garmin-connect-mcp/session.json").expanduser()


class GarminClient:
    def __init__(self) -> None:
        if not SESSION_FILE.exists():
            raise RuntimeError(
                f"No session found at {SESSION_FILE}. "
                "Run 'pdm run garmin-auth' first."
            )
        session = json.loads(SESSION_FILE.read_text())
        if "cookies" not in session:
            raise RuntimeError(
                f"Session file at {SESSION_FILE} uses old format. "
                "Run 'pdm run garmin-auth' again."
            )
        self._csrf_token: str = session["csrf_token"]
        self._cookies: list[dict] = session["cookies"]
        self._pw = None
        self._browser = None
        self._page = None
        self._display_name: str | None = None

    async def _ensure_init(self) -> None:
        if self._page is not None:
            return
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=True)
        context = await self._browser.new_context()
        await context.add_cookies([
            {"name": c["name"], "value": c["value"], "domain": c["domain"], "path": "/"}
            for c in self._cookies
        ])
        self._page = await context.new_page()
        # Navigate to static endpoint — no Cloudflare redirect, establishes origin
        await self._page.goto(
            "https://connect.garmin.com/site-status/garmin-connect-status.json",
            wait_until="domcontentloaded",
            timeout=30000,
        )

    async def get(self, path: str, **params: Any) -> Any:
        await self._ensure_init()
        url = f"/gc-api/{path.lstrip('/')}"
        if params:
            from urllib.parse import urlencode
            url += f"?{urlencode(params)}"
        result = await self._page.evaluate(
            """async ({url, csrfToken}) => {
                const resp = await fetch(url, {
                    headers: {"connect-csrf-token": csrfToken, "Accept": "*/*"}
                });
                const text = await resp.text();
                return {status: resp.status, body: text};
            }""",
            {"url": url, "csrfToken": self._csrf_token},
        )
        if result["status"] == 401:
            raise RuntimeError("Session expired — run 'pdm run garmin-auth'")
        if result["status"] == 204 or not result["body"]:
            return None
        if result["status"] != 200:
            raise RuntimeError(f"Garmin API {result['status']}: {path} — {result['body']}")
        return json.loads(result["body"])

    async def get_display_name(self) -> str:
        if not self._display_name:
            settings = await self.get("userprofile-service/userprofile/settings")
            self._display_name = settings["displayName"]
        return self._display_name

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()
        self._browser = None
        self._page = None
        self._pw = None
