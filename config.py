import json
import os


with open("config.json") as f:
  config = json.loads(f.read())

RSS = config["rss"]
BOT_TOKEN = config["bot_token"]
CHANNEL_ID = config["channel_id"]
OPENAI_KEY = config["openai_key"]
PROMPT = config["prompt"]
INTERVAL = float(config["interval"])
CACHE_DIRNAME = config["cache"]["dirname"]
os.makedirs(CACHE_DIRNAME, exist_ok=True)

CACHE_FILES = config["cache"]["files"]
for filename in CACHE_FILES.values():
  file = os.path.join(CACHE_DIRNAME, filename)
  if not os.path.exists(file):
    with open(file, "w") as f:
      pass