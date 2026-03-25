from motor.motor_asyncio import AsyncIOMotorClient
import os

# We pull the URI from Render's environment variables
# If it's missing, we provide the direct link as a backup to STOP the 'localhost' error
MONGO_URL = os.getenv("MONGO_URI", "mongodb+srv://anandhakrishnanr868_db_user:w7atCTWvuAmB4Par@agromarket.amjhuf7.mongodb.net/")

# Initialize the client
client = AsyncIOMotorClient(MONGO_URL)

# Define the database (Check your spelling: you have 'bulliying' with two 'i's)
database = client.bulliying 

# Define collections
users_collection = database.users
posts_collection = database.posts
comments_collection = database.comments
removed_collection = database.removed_cmts

async def create_unique_index():
    try:
        await users_collection.create_index("email", unique=True)
        print("✅ Unique index on email created successfully.")
    except Exception as e:
        print(f"⚠️ Index creation skipped or failed: {e}")
