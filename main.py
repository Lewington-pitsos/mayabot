import argparse
import random
import logging
import praw
import time
import json
import datetime
from praw import models
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dry", help="perform a dry-run (no actual comments posted)",
                    action="store_true", default=False)
parser.add_argument("-c", "--config", help="path to the config file for this run",
                    action='store', type=str)
args = parser.parse_args()

with open(args.config) as f:
    data = json.load(f)

TRIGGERS = data['triggers']
REPLIES = data['replies']
MAX_COMMENTS_PER_DAY = data['max_comments_per_day']
MS_WAIT_BETWEEN_COMMENTS = data['ms_wait_between_comments']
SUBREDDIT = data['subreddit']
LAST_N = data['last_n']

praw.Reddit._prepare_untrusted_prawcore

# Replace YOUR_CLIENT_ID and YOUR_CLIENT_SECRET with your own API keys
reddit = praw.Reddit(
  client_id=data['client_id'], 
  client_secret=data['secret'], 
  username=data['username'],
  password=data['password'],
  user_agent="maya_bot_woof_woof/2.0.0"
)

user_id = reddit.user.me().id
subreddit: models.SubredditHelper = reddit.subreddit(SUBREDDIT)

def is_relevant(comment, relevant_substrings):
  for word in relevant_substrings:
    if word in comment.lower():
      return True
  return False

def already_replied(comment: models.Comment, user_id):
    comment.refresh()
    for reply in comment.replies:
        if reply.author.id == user_id:
            return True
    return False

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logging.info("About to read comments")
replies_today = 0
yesterday = time.time() - 60*60*24 + 600 # extra 10 minutes as a safety buffer.

comment: models.Comment
for comment in subreddit.comments(limit=LAST_N):
    if comment.created_utc > yesterday:
        logging.debug("Comment with ID %s posted recently", comment.id)
        if replies_today < MAX_COMMENTS_PER_DAY and\
            is_relevant(comment.body, TRIGGERS) and\
            comment.author.id != user_id and\
            not already_replied(comment, user_id):
            try:
                if replies_today > 0:        
                    logging.debug("about to sleep for 1000 ms")
                    time.sleep(MS_WAIT_BETWEEN_COMMENTS) # reddit doesn't allow multiple posts within 15 minutes from low karma bots
                
                reply = random.choice(REPLIES)
                if not args.dry:
                    comment.reply(reply)
                    logging.info("Replied to comment %s, ID %s with %s", comment.body, comment.id, reply)
                else:
                    logging.info("Would have replied to comment %s, ID %s with %s, but this is a dry run so no comments were actually posted", comment.body, comment.id, reply)
                    
                
                replies_today += 1

            except Exception as e:
                logging.error("Failed to reply to comment with ID %s: %s", comment.id, e)

logging.info("finished replying to all comments")
