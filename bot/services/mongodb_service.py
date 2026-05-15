import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING, ASCENDING
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class MongoDBService:
    def __init__(self, uri: str, db_name: str = "bzuf_ielts"):
        self.client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=10000)
        self.db = self.client[db_name]
        self.users = self.db["users"]
        self.submissions = self.db["submissions"]

    async def setup_indexes(self):
        await self.users.create_index("telegram_id", unique=True)
        await self.submissions.create_index(
            [("user_id", ASCENDING), ("created_at", DESCENDING)]
        )
        # TTL index: auto-delete submissions older than 1 year
        await self.submissions.create_index(
            "created_at", expireAfterSeconds=365 * 24 * 3600
        )
        logger.info("MongoDB indexes ready")

    async def get_or_create_user(
        self, telegram_id: int, username: str = None, first_name: str = None
    ) -> dict:
        user = await self.users.find_one({"telegram_id": telegram_id})
        if user:
            await self.users.update_one(
                {"telegram_id": telegram_id},
                {"$set": {
                    "last_active": datetime.utcnow(),
                    "username": username,
                    "first_name": first_name,
                }},
            )
            return user
        new_user = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "phone_number": None,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow(),
            "submission_count": 0,
            "writing_count": 0,
            "speaking_count": 0,
            "avg_writing_band": 0.0,
            "avg_speaking_band": 0.0,
        }
        try:
            await self.users.insert_one(new_user)
            logger.info(f"New user: {telegram_id} (@{username})")
        except DuplicateKeyError:
            new_user = await self.users.find_one({"telegram_id": telegram_id})
        return new_user

    async def has_phone_number(self, telegram_id: int) -> bool:
        user = await self.users.find_one(
            {"telegram_id": telegram_id, "phone_number": {"$ne": None}},
            {"phone_number": 1},
        )
        return user is not None

    async def save_phone_number(self, telegram_id: int, phone_number: str):
        await self.users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"phone_number": phone_number}},
        )
        logger.info(f"Phone saved for user {telegram_id}")

    async def save_submission(self, submission_doc: dict) -> str:
        result = await self.submissions.insert_one(submission_doc)
        user_id = submission_doc["user_id"]
        sub_type = submission_doc["submission_type"]
        band = submission_doc["overall_band"]

        user = await self.users.find_one({"telegram_id": user_id})
        if not user:
            return str(result.inserted_id)

        new_total = user.get("submission_count", 0) + 1
        update = {"submission_count": new_total}

        if sub_type == "writing":
            new_count = user.get("writing_count", 0) + 1
            old_avg = user.get("avg_writing_band", 0.0)
            new_avg = ((old_avg * (new_count - 1)) + band) / new_count
            update["writing_count"] = new_count
            update["avg_writing_band"] = round(new_avg, 2)
        else:
            new_count = user.get("speaking_count", 0) + 1
            old_avg = user.get("avg_speaking_band", 0.0)
            new_avg = ((old_avg * (new_count - 1)) + band) / new_count
            update["speaking_count"] = new_count
            update["avg_speaking_band"] = round(new_avg, 2)

        await self.users.update_one({"telegram_id": user_id}, {"$set": update})
        return str(result.inserted_id)

    async def get_user_history(self, telegram_id: int, limit: int = 5) -> list[dict]:
        cursor = self.submissions.find(
            {"user_id": telegram_id},
            {"original_text": 0, "feedback.corrected_text": 0, "feedback.corrected_transcript": 0},
        ).sort("created_at", DESCENDING).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_user_stats(self, telegram_id: int) -> dict:
        user = await self.users.find_one({"telegram_id": telegram_id})
        if not user:
            return {}
        one_month_ago = datetime.utcnow() - timedelta(days=30)
        recent_count = await self.submissions.count_documents(
            {"user_id": telegram_id, "created_at": {"$gte": one_month_ago}}
        )
        return {
            "total_submissions": user.get("submission_count", 0),
            "writing_count": user.get("writing_count", 0),
            "speaking_count": user.get("speaking_count", 0),
            "avg_writing_band": user.get("avg_writing_band", 0.0),
            "avg_speaking_band": user.get("avg_speaking_band", 0.0),
            "recent_submissions": recent_count,
            "member_since": user.get("created_at", datetime.utcnow()),
        }

    async def check_rate_limit(self, telegram_id: int, max_per_hour: int = 10) -> bool:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        count = await self.submissions.count_documents(
            {"user_id": telegram_id, "created_at": {"$gte": one_hour_ago}}
        )
        return count < max_per_hour

    async def close(self):
        self.client.close()
