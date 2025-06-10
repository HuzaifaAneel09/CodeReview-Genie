import redis
import os
import json
from dotenv import load_dotenv
from utils.logger import logger

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Create redis client
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

CACHE_TTL = 60 * 60  # 1 hour TTL

def get_cached_repo(owner, repo):
    key = f"repo:{owner}/{repo}"
    try:
        value = r.get(key)
        if value:
            logger.info(f"Cache HIT for {key}")
            return json.loads(value)
        else:
            logger.info(f"Cache MISS for {key}")
            return None
    except Exception as e:
        logger.error(f"Redis GET error for {key}: {e}", exc_info=True)
        return None

def set_cached_repo(owner, repo, data):
    key = f"repo:{owner}/{repo}"
    try:
        r.setex(key, CACHE_TTL, json.dumps(data))
        logger.info(f"Cached data for {key}")
    except Exception as e:
        logger.error(f"Redis SET error for {key}: {e}", exc_info=True)

def invalidate_repo_cache(owner, repo):
    key = f"repo:{owner}/{repo}"
    try:
        r.delete(key)
        logger.info(f"Cache invalidated for {key}")
    except Exception as e:
        logger.error(f"Redis DEL error for {key}: {e}", exc_info=True)
