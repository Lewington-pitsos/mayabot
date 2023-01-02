import random
import logging
import praw
import time
import json

with open("secrets.json") as f:
    data = json.load(f)

DOG_WORDS = ["woof", "dog", "bark", "doggo", "pupper", "dogg", "maya", "who's a good girl?"]
REPLIES = ["woof", "borf", "*pant pant pant*", "*wag wag*", "ruf", "arf", "woof woof", "whine"]
MAX_COMMENTS_PER_DAY = 4


# Replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET with your own API keys
reddit = praw.Reddit(
  client_id=data['client_id'], 
  client_secret=data['secret'], 
  username=data['username'],
  password=data['password'],
  user_agent="maya_bot_woof_woof/1.0.0"
)

user_id = reddit.user.me().id
subreddit = reddit.subreddit('atrioc')

def is_interesting(comment):
  for word in DOG_WORDS:
    if word in comment.lower():
      return True
  return False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("About to start listening to comment stream")
counter = 0
reset_time = time.time()

for comment in subreddit.stream.comments(skip_existing=True):
    if is_interesting(comment.body) and comment.author.id != user_id:
        if counter >= MAX_COMMENTS_PER_DAY:
            current_time = time.time()
            if current_time - reset_time >= 86400:
                counter = 0
                reset_time = current_time
            else:
                continue
        try:
            comment.reply(random.choice(REPLIES))
            logging.info("Replied to comment %s with ID %s", comment.body, comment.id)
            counter += 1
        except Exception as e:
            logging.error("Failed to reply to comment with ID %s: %s", comment.id, e)
    else:
        logging.debug("Comment with ID %s is not interesting", comment.id)