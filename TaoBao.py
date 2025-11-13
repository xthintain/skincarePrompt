import asyncio

from playwright.async_api import async_playwright
import json
import random
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
        with open('./cookie_tb.json', 'r', encoding='utf-8') as f:
            cookie = json.load(f)
            await context.add_cookies(cookie)
        page = await context.new_page()
        await page.goto('https://www.taobao.com/')
        await asyncio.sleep(1)
        await page.goto("https://s.taobao.com/search?commend=all&ie=utf8&initiative_id=tbindexz_20170306&page=1&preLoadOrigin=https%3A%2F%2Fwww.taobao.com&q=%E6%8A%A4%E8%82%A4%E5%93%81&search_type=item&sourceId=tb.index&spm=a21bo.jianhua%2Fa.search_manual.0&ssid=s5-e&tab=all")
        for i in range(10):
            await asyncio.sleep(3)
            await page.mouse.wheel(0, random.randint(550, 650))
            next_page = page.locator('//*[@id="search-content-leftWrap"]/div[3]/div[5]/div/div/button[2]')
            content = await page.content()
            await next_page.evaluate("el => el.scrollIntoView({behavior: 'smooth', block: 'center'})")
            with open(f'./html_tb/p{i}.html', 'w', encoding='utf-8') as f:
                f.write(str(content))
            await asyncio.sleep(1)
            await next_page.click()
            print(f"第{i}页下载完成！！！")
        await asyncio.sleep(3)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(add_cookies())
