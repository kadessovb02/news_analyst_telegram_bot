import requests
import openai
from telegram.ext import Updater
from datetime import datetime, timedelta
import textwrap
import random
import time
import os
from dotenv import load_dotenv

class NewsAnalystBot:

    def __init__(self, openai_api_key, news_api_key, bot_token):
        self.openai_api_key = openai_api_key
        self.news_api_key = news_api_key
        self.bot_token = bot_token

        openai.api_key = self.openai_api_key

        self.updater = Updater(token=self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.prompt = ("You're a news trader analyst: analyze, remove unnecessary info and "
                       "summarize this news into 1-2 sentences with key facts (names, numbers, statistics)."
                       " Add hashtags and make it more interesting by adding text well-readable formatting and "
                       "emoji for the Telegram channel in english:")

    def fetch_news(self):
        response = requests.get(f'https://newsdata.io/api/1/news?apikey={self.news_api_key}&q=bitcoin&language=en')
        response.raise_for_status()
        news_json = response.json()
        return news_json.get('results', [])

    def read_existing_links(self):
        with open('news_links.txt', 'r') as file:
            existing_links = file.read().split('\n')
        return existing_links

    def write_existing_links(self, links):
        with open('news_links.txt', 'w') as file:
            file.write('\n'.join(links))

    def sleep_random(self):
        sleep_duration = random.uniform(100, 750)
        print("Sleeping for", sleep_duration, "seconds...")
        time.sleep(sleep_duration)
        print("Awake!")

    def process_news(self, news, existing_links, channel_chat_id):
        now = datetime.now()
        for i, result in enumerate(news):
            link = result.get('link')
            if link in existing_links:
                print(f'Новость {link} уже была обработана')
                continue
            post_date = result.get('pubDate')
            content = result.get('content')
            date = datetime.strptime(post_date, "%Y-%m-%d %H:%M:%S")
            three_days_ago = now - timedelta(days=5)
            if date > three_days_ago:
                self.sleep_random()
                if content:
                    chunks = textwrap.wrap(content, 2048)
                    for chunk in chunks:
                        chat_model = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{
                                "role": "assistant",
                                "content": self.prompt + chunk
                            }]
                        )
                        summarized_news = chat_model.choices[0].message['content']
                        self.dispatcher.bot.send_message(chat_id=channel_chat_id, text=summarized_news)
                    existing_links.append(link)
                else:
                    print(f'Новость #{i} не содержит содержимого')
            else:
                print("Дата не свежая")
        return existing_links


if __name__ == '__main__':

    origins = ["*"]
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    openai_api_key = os.environ["OPENAI_API_KEY"]
    news_api_key = os.environ["NEWS_API_KEY"]
    bot_token = os.environ["BOT_TOKEN"]
    channel_chat_id = int(os.environ["CHANNEL_CHAT_ID"])

    bot = NewsAnalystBot(openai_api_key, news_api_key, bot_token)
    news = bot.fetch_news()
    existing_links = bot.read_existing_links()
    updated_links = bot.process_news(news, existing_links, channel_chat_id)
    bot.write_existing_links(updated_links)
