from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb+srv://anandhakrishnanr868_db_user:w7atCTWvuAmB4Par@agromarket.amjhuf7.mongodb.net/
DATABASE_NAME=orphanage_db"

client = AsyncIOMotorClient(MONGO_URL)

database = client.bulliying
users_collection = database.users
posts_collection = database.posts
comments_collection = database.comments
removed_collection = database.removed_cmts

def create_unique_index():
 users_collection.create_index("email",unique=True)
