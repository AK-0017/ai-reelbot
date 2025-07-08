import os
import asyncio
from playwright.async_api import async_playwright

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
VIDEO_PATH = "temp/final_reel.mp4"
CAPTION_PATH = "temp/single_script.txt"


async def upload_to_instagram_dry():
    print("\n🚀 Launching Instagram dry-mode uploader...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Go to Instagram login
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_timeout(3000)

        # 2. Accept cookies if needed
        try:
            await page.locator("text=Only allow essential cookies").click(timeout=3000)
        except:
            pass

        # 3. Log in
        await page.fill("input[name='username']", USERNAME)
        await page.fill("input[name='password']", PASSWORD)
        await page.click("text=Log in")
        await page.wait_for_timeout(5000)

        # 4. Skip save login info / notifications
        for skip_text in ["Not Now", "Turn On Notifications"]:
            try:
                await page.locator(f"text={skip_text}").click(timeout=5000)
            except:
                continue

        # 5. Go to Create Post (mobile emulation needed)
        print("📱 Navigating to post upload UI (mobile emulation)...")
        await context.close()

        iphone = p.devices["iPhone 12"]
        mobile_context = await browser.new_context(**iphone)
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto("https://www.instagram.com/")
        await mobile_page.wait_for_timeout(5000)

        # 6. Click + button (upload)
        print("📤 Uploading reel in dry mode...")
        await mobile_page.locator("svg[aria-label='New post']").click()
        await mobile_page.wait_for_timeout(2000)

        # 7. Upload file
        file_input = mobile_page.locator("input[type='file']")
        await file_input.set_input_files(VIDEO_PATH)
        await mobile_page.wait_for_timeout(5000)

        # 8. Press Next (twice)
        for _ in range(2):
            try:
                await mobile_page.locator("text=Next").click(timeout=5000)
                await mobile_page.wait_for_timeout(3000)
            except:
                pass

        # 9. Add caption
        with open(CAPTION_PATH, "r", encoding="utf-8") as f:
            caption = f.read()
        await mobile_page.fill("textarea", caption[:2200])
        await mobile_page.wait_for_timeout(2000)

        print("✅ Dry-mode done. Post is ready but NOT published.")
        print("🛑 Leaving page open for 10 seconds so you can inspect if headless=False")
        await mobile_page.wait_for_timeout(10000)

        # 10. Close browser
        await browser.close()

        # 11. Cleanup
        if os.path.exists(VIDEO_PATH):
            os.remove(VIDEO_PATH)
        if os.path.exists(CAPTION_PATH):
            os.remove(CAPTION_PATH)
        print("🧹 Cleaned up temp files.")


if __name__ == "__main__":
    asyncio.run(upload_to_instagram_dry())
