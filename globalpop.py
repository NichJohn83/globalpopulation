import tweepy
import logging
import sys
import os
import redis
import atexit
from datetime import date, timedelta


from apscheduler.schedulers.blocking import BlockingScheduler

from worldometer import api

from constants import (
    access_token,
    access_token_secret,
    consumer_key,
    consumer_secret,
    bearer_token,
)

sched = BlockingScheduler()

r = redis.Redis(
  host='redis-16523.c265.us-east-1-2.ec2.cloud.redislabs.com',
  port=16523,
  password=os.getenv('REDIS_SECRET'))


Log_Format = "%(levelname)s %(asctime)s %(funcName)20s() - %(message)s"

logging.basicConfig(
    stream=sys.stdout, filemode="w", format=Log_Format, level=logging.INFO
)

logger = logging.getLogger()

@sched.scheduled_job('cron', hour=17)
def global_population() -> dict:
    logger.info("called")
    population = get_population()
    logger.info(f"Current World Population is: {population} - {date.today()}")
    r.mset({
        date.today().strftime("%Y/%m/%d"): population
    })
    population_delta = get_population_delta(current_population=population)
    if population_delta:
        logger.info(population_delta)
    
    make_tweet(population, population_delta)


def make_tweet(population, pop_delta):
    logger.info("called")
    try:
        client = _get_twitter_client()
        tweet_text = f"Today's Population is {population:,}"

        if pop_delta is not None:
            tweet_text += f"\n({pop_delta})"

        response = client.create_tweet(text=tweet_text, user_auth=True)

        logger.info(response)
        return response
    except Exception as e:
        logger.error(e)
        raise e


def get_population() -> int:
    try:
        response = api.current_world_population()
        return response.get("current_world_population")
    except Exception as e:
        logger.error(e)
        raise e


def get_population_delta(current_population) -> int:
    """ "This function will attempt to get yesterday's population
    which should stored in redis. It will
    then do the diff. If yesterday's population is unavailable,
    we return None

    Args:
        current_population (int): today's population

    Returns:
        an integer describing the change in population from
        yesterday to today
    """

    logger.info("called")
    yesterday = date.today() + timedelta(days=-1)
    logger.info(f"Yesterday's Date: {yesterday}")
    YESTERDAY_POPULATION = r.get(yesterday.strftime("%Y/%m/%d"))
    if not YESTERDAY_POPULATION:
        return None
    
    logger.info(f"Yesterday's Population: {YESTERDAY_POPULATION}")

    return current_population - int(YESTERDAY_POPULATION) if current_population < int(YESTERDAY_POPULATION) else f'+{current_population - int(YESTERDAY_POPULATION)}'


def _get_twitter_client():
    return tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        access_token=access_token,
        access_token_secret=access_token_secret,
    )


sched.start()
