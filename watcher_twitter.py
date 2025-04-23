
import asyncio
import json
import os
import time
from playwright.async_api import async_playwright
from telegram import Bot

# === CONFIGURATION ===
USERNAME = "elonmusk"  # имя пользователя, за которым следим (без @)
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # твой Telegram chat_id
BOT_TOKEN = os.getenv("BOT_TOKEN")  # токен бота
CACHE_FILE = "storage/follow_cache.json"
CHECK_INTERVAL = 60  # в секундах

bot = Bot(token=BOT_TOKEN)

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return []
    with open(CACHE_FILE, "r") as f:
        return json.load(f)

def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

async def fetch_following():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://twitter.com/{USERNAME}/following")
        await page.wait_for_selector("article", timeout=10000)

        handles = await page.eval_on_selector_all(
            "div[data-testid='UserCell'] div[dir='ltr'] > span", 
            "els => els.map(e => e.textContent.trim())"
        )

        await browser.close()
        return sorted(set([h.lstrip("@") for h in handles if h]))

async def check_updates():
    print("👀 Старт проверки...")
    current = await fetch_following()
    previous = load_cache()

    added = sorted(set(current) - set(previous))

    if added:
        msg = f"📈 @{USERNAME} подписался на:\n" + "\n".join([f"@{a}" for a in added])
        await bot.send_message(chat_id=CHAT_ID, text=msg)
    else:
        print("📭 Нет новых подписок")

    save_cache(current)

async def main_loop():
    while True:
        try:
            await check_updates()
        except Exception as e:
            print("⚠️ Ошибка:", e)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main_loop())
