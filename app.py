import asyncio
from fastapi import FastAPI,Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routers.auth.auth import router as auth_router
from datetime import datetime, timezone
import time


from database import session as sdb
session_collection = sdb.get_collection("sessions")


async def cleanup_expired_sessions():
    while True:
        # Delete sessions where the expiration time is less than the current UTC time
        session_collection.delete_many({"expires_at": {"$lt": datetime.now(timezone.utc)}})
        
        # Wait for an hour before checking again
        await asyncio.sleep(3600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Background task for cleaning expired sessions
    task = asyncio.create_task(cleanup_expired_sessions())

    try:
        yield  # Startup phase completed, app is running
    finally:
        # Shutdown phase, clean up tasks
        print("Application shutdown")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            print("Cleanup task cancelled during shutdown")


app = FastAPI(lifespan=lifespan)


# frontend DNS
origins = [
    "http://127.0.0.1:3000",

]


# for jwt token
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# every request milli sec
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response



# Include the invoice router
app.include_router(auth_router,prefix="/api/auth",tags=["auth"])


