from fastapi import FastAPI
from pymongo import MongoClient
import redis
import os

app = FastAPI()

# MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017")
client = MongoClient(mongo_url)
db = client["mydb"]

# Redis (safe connection)
redis_host = os.getenv("REDIS_HOST", "redis")
cache = redis.Redis(host=redis_host, port=6379, decode_responses=True)


@app.get("/")
def home():
    return {"message": "FastAPI + Mongo + Redis 🚀"}


@app.get("/user")
def get_user():

    # Step 1: check cache
    cached_data = cache.get("user")

    if cached_data:
        return {
            "source": "redis cache",
            "data": cached_data
        }

    # Step 2: fetch from MongoDB
    user = db.users.find_one({}, {"_id": 0})

    if not user:
        user = {"message": "No user found"}

    # Step 3: store in cache
    cache.set("user", str(user), ex=30)

    return {
        "source": "mongodb",
        "data": str(user)
    }