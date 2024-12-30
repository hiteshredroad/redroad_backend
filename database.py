import motor.motor_asyncio
from decouple import config

# export MONGODB_URL="mongodb://localhost:27017/"

MONGODB_URL = config('MONGODB_URL',default = "mongodb://localhost:27017/")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

# for invoice table
session = client.session
invoice = client.invoice