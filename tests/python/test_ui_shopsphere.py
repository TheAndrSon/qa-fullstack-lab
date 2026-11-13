import os

import pytest

playwright_api = pytest.importorskip("playwright.sync_api")


@pytest.mark.ui
def test_login_and_add_to_cart():
    base_url = os.environ.get("BASE_URL")
    if not base_url:
        pytest.skip("Set BASE_URL=http://127.0.0.1:8000 and start the app")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except Exception as exc:  # noqa: BLE001
            pytest.skip(f"Chromium is not installed: {exc}")
        page = browser.new_page()
        page.goto(base_url)
        page.get_by_role("link", name="Войти").click()
        page.fill("input[name=email]", "alice@example.com")
        page.fill("input[name=password]", "User123!")
        page.get_by_role("button", name="Войти").click()
        page.wait_for_load_state("networkidle")
        page.get_by_role("link", name="Aurora Headphones").click()
        page.get_by_role("button", name="В корзину").click()
        page.wait_for_load_state("networkidle")
        assert "Корзина" in page.title()
        assert "Aurora Headphones" in page.content()
        browser.close()
