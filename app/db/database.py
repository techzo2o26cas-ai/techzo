from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = ""

client = AsyncIOMotorClient(MONGO_URL)

database = client.bulliying
users_collection = database.users
posts_collection = database.posts
comments_collection = database.comments
removed_collection = database.removed_cmts

def create_unique_index():
 users_collection.create_index("email",unique=True)
