from openai import AsyncOpenAI
from links import read_links, save_links
import feedparser
import asyncio
import aiohttp
import logging
import config
import json
import time

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher

from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

MODEL = "pai-001-light-beta"
client = AsyncOpenAI(api_key=config.OPENAI_KEY, base_url="https://api.pawan.krd/v1")

links = []

async def parse_text(html: str) -> dict:
  result = await client.chat.completions.create(model=MODEL, messages=[
    {
      "role": "system",
      "content": config.PROMPT
    },
    {
      "role": "user",
      "content": html
    }
  ])

  try:
    content = result.choices[0].message.content.strip("```json").strip("```").strip()
  except:
    logging.warning(f"OpenAI's \"{MODEL}\" returned empty response.")
    return { "coins": [], "positive": False, "description": "" }
   
  try:
    response = json.loads(content)
    if not isinstance(response, dict):
      raise RuntimeError(f"OpenAI's \"{MODEL}\" responded with \"{content}\" which is not a parsable JSON (not object).")
    
    return response
  except json.JSONDecodeError:
    raise RuntimeError(f"OpenAI's \"{MODEL}\" responded with \"{content}\" which is not a parsable JSON.")

async def on_startup(bot: Bot):
  # try:
  #   await bot.send_message(config.ADMIN_ID, "Bot is working!")
  # except Exception as e:
  #   print(e)
  await receive_rss()

async def parse_feed(session: aiohttp.ClientSession, feed: str):
  async with session.get(feed) as response:
    if response.status != 200:
      raise RuntimeError(f"{response.status} (\"{feed}\"): {response.reason or '*'}")

    unparsed_feed = await response.text()
    return feedparser.parse(unparsed_feed)

async def create_timemap(session: aiohttp.ClientSession) -> dict:
  timemap = {}
  for rss in config.RSS:
    try:
      feed = await parse_feed(session, rss)
      latest = max([entry.published_parsed for entry in feed.entries if hasattr(entry, 'published_parsed')], default=time.strptime("2020-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"))

      timemap[rss] = latest
    except Exception as e:
      logging.error(e)

  return timemap

async def receive_rss():
  async with aiohttp.ClientSession() as session:
    rss_timemap = await create_timemap(session)
    
    while True:
      for rss, last_checked in rss_timemap.items():
        async with session.get(rss) as response:
          if response.status != 200:
            logging.log(logging.ERROR, f"{response.status} (\"{rss}\"): {response.reason or '*'}")
            continue

          unparsed_feed = await response.text()
          feed = feedparser.parse(unparsed_feed)

          for entry in feed.entries:
            try:
              published = entry.published_parsed
            except AttributeError:
              continue
            
            if entry.link in links:
              continue

            if published <= last_checked:
              continue

            rss_timemap[rss] = published

            try:
              content = "\n\n".join([c["value"] for c in entry.content if c.get("value") is not None]) if hasattr(entry, 'content') else entry.summary
              html = f'<div>{entry.title}\n{content}</div>'
              response = await parse_text(html)

              logging.info(f"{entry.link} -> {response}")
              if len(response["coins"]) < 1:
                continue

              signal = 'Up' if response["positive"] else 'Down'
              msg = f"<a href=\"{entry.link}\">{signal} signal</a>\n<b>Coins</b>: {' | '.join(response['coins'])}\n\n{response['description']}"
              await bot.send_message(config.CHANNEL_ID, msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception as e:
              logging.error(f"error passing to OpenAI ({entry.link}): {e}\n{entry}")
              continue
            
            links.append(entry.link)
      await asyncio.sleep(config.INTERVAL)

async def on_shutdown():
  print("Shutting down gracefully...")
  await save_links(links)
  await dp.storage.close()

async def main():
  global links
  links = await read_links()
  
  dp.startup.register(on_startup)
  dp.shutdown.register(on_shutdown)

  await dp.start_polling(bot)