import asyncio

from playwright.async_api import async_playwright
import json

async def add_cookies():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,
                                          args=[  # ③ 关闭 WebGL 等指纹
                                              "--disable-blink-features=AutomationControlled",
                                              "--disable-web-security",
                                              "--disable-features=VizDisplayCompositor",
                                              "--no-sandbox",
                                              "--disable-dev-shm-usage"
                                          ]
                                          )
        context = await browser.new_context()
        with open('./cookie.json', 'r', encoding='utf-8') as f:
            cookie = json.load(f)
            await context.add_cookies(cookie)
        page = await context.new_page()
        await page.goto('https://www.jd.com/')
        await asyncio.sleep(1)
        await page.goto("https://re.jd.com/search?keyword=%E6%8A%A4%E8%82%A4%E5%93%81")
        for i in range(10):
            await asyncio.sleep(3)
            next_page = page.locator("a.pn-next").filter(has_text="下一页")
            content = await page.content()
            await next_page.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
            with open(f'./html/p{i}.html', 'w', encoding='utf-8') as f:
                f.write(str(content))
            await asyncio.sleep(1)
            await next_page.click()
        await asyncio.sleep(1)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(add_cookies())
