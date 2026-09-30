### how to use
configuration file
```json
{
  "cache": {
    "dirname": ".cache",
    "files": {
      "links": "links.txt"
    }
  },
  "rss": [
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://cryptoslate.com/rss/",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://cointelegraph.com/rss/"
  ],
  "bot_token": "<TELEGRAM_BOT_TOKEN>",
  "channel_id": "<TELEGRAM_CHANNEL_ID>",
  "interval": 5,
  "openai_key": "<YOUR_OPENAI_KEY>",
  "prompt": "RESPONSE ONLY IN JSON FORMAT NO MATTER WHATS THE INPUT. You're HTML page parser. The content of HTML page will be the world news related with CRYPTOCURRENCIES, your task is to parse it in following format. {\"coins\": [\"BTC\", \"ETH\"], \"positive\": true, \"description\": \"Trump was ellected as president of the US as for 2025-2029.\"}. The \"coins\" key contains the coins that will be affected by this new, must be empty if none. The \"positive\" key contains bool value whether it WILL affect specified coins positivly IN FUTURE. The \"description\" key contains small summary of the new, if any additional comments, thats the right place for it."
}
```