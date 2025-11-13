from playwright.async_api import async_playwright
import asyncio
import json

async def JD():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                                   args=[  # ③ 关闭 WebGL 等指纹
                                                       "--disable-blink-features=AutomationControlled",
                                                       "--disable-web-security",
                                                       "--disable-features=VizDisplayCompositor",
                                                       "--no-sandbox",
                                                       "--disable-dev-shm-usage"
                                                   ]
                                                   )
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(
            "https://www.jd.com/")
        await asyncio.sleep(15)
        cookie = await context.cookies()
        with open('./cookie.json', 'w', encoding='utf-8') as f:
            json.dump(cookie, f, ensure_ascii=False, indent=4)
        await browser.close()
        return cookie

async def TB():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False,
                                                   args=[  # ③ 关闭 WebGL 等指纹
                                                       "--disable-blink-features=AutomationControlled",
                                                       "--disable-web-security",
                                                       "--disable-features=VizDisplayCompositor",
                                                       "--no-sandbox",
                                                       "--disable-dev-shm-usage"
                                                   ]
                                                   )
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.taobao.com/")
        await asyncio.sleep(15)
        cookie = await context.cookies()
        with open('./cookie_tb.json', 'w', encoding='utf-8') as f:
            json.dump(cookie, f, ensure_ascii=False, indent=4)
        await browser.close()
        return cookie


if __name__ == '__main__':
    asyncio.run(TB())