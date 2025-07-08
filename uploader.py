import os
import asyncio
from playwright.async_api import async_playwright

INSTAGRAM_USERNAME = os.getenv("IG_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("IG_PASSWORD")

async def upload_to_instagram_dry():
    print("🚀 Launching Instagram dry-mode uploader...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 375, "height": 812},  # iPhone X dimensions
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 "
                "Mobile/15E148 Safari/604.1"
            )
        )

        mobile_page = await context.new_page()
        print("🔐 Navigating to Instagram login page...")
        await mobile_page.goto("https://www.instagram.com/accounts/login/", timeout=60000)
        await mobile_page.wait_for_timeout(5000)

        # Accept cookies if prompted
        try:
            await mobile_page.get_by_text("Only allow essential cookies").click(timeout=3000)
        except:
            pass

        # Login
        print("🔐 Logging in to Instagram...")
        await mobile_page.get_by_label("Phone number, username or email address").fill(INSTAGRAM_USERNAME)
        await mobile_page.get_by_label("Password").fill(INSTAGRAM_PASSWORD)
        await mobile_page.get_by_role("button", name="Log in").click()

        # Wait for login to complete
        await mobile_page.wait_for_timeout(8000)

        print("📱 Navigating to post upload UI (mobile emulation)...")
        await mobile_page.goto("https://www.instagram.com/", timeout=60000)
        await mobile_page.wait_for_timeout(8000)  # Give time to load post button

        # Screenshot for debug (optional)
        # await mobile_page.screenshot(path="screen_before_click.png")

        print("📤 Uploading reel in dry mode...")
        try:
            await mobile_page.get_by_label("New post", exact=True).click(timeout=10000)
        except Exception as e:
            print("❌ Could not find 'New post' button:", e)
            await browser.close()
            return

        print("✅ Dry-mode upload logic reached (no publishing).")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(upload_to_instagram_dry())
