
import asyncio
import json
import os
import time
from playwright.async_api import async_playwright
from telegram import Bot

DATA_FILE = "storage/data.json"
CACHE_DIR = "storage/following_cache"
CHECK_INTERVAL = 60

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def load_previous(username):
    path = os.path.join(CACHE_DIR, f"{username}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_current(username, data):
    path = os.path.join(CACHE_DIR, f"{username}.json")
    with open(path, "w") as f:
        json.dump(data, f)

async def fetch_following(username):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"https://twitter.com/{username}/following")
        await page.wait_for_selector("article", timeout=10000)
        handles = await page.eval_on_selector_all(
            "div[data-testid='UserCell'] div[dir='ltr'] > span",
            "els => els.map(e => e.textContent.trim())"
        )
        await browser.close()
        return sorted(set([h.lstrip("@") for h in handles if h]))

async def check_all():
    print("🔄 Проверка...")
    data = load_data()
    for chat_id, usernames in data.items():
        for username in usernames:
            try:
                current = await fetch_following(username)
                previous = load_previous(username)
                added = sorted(set(current) - set(previous))
                if added:
                    msg = f"📈 @{username} подписался на:\n" + "\n".join([f"@{a}" for a in added])
                    await bot.send_message(chat_id=chat_id, text=msg)
                save_current(username, current)
            except Exception as e:
                print(f"❌ Ошибка @{username}: {e}")

async def main_loop():
    while True:
        await check_all()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main_loop())
