import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError, ValidationException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import DuplicateKeyError
from routers.auth.auth import router as auth_router
from routers.masterSettings.billingType import router as billing_router
from routers.masterSettings.department import router as department_router
from routers.masterSettings.process import router as process_router
from routers.client import router as client_router
from routers.project import router as project_router
from datetime import datetime, timezone
import time
import logging
import re

from database import session as sdb
session_collection = sdb.get_collection("sessions")


async def cleanup_expired_sessions():
    while True:
        # Delete sessions where the expiration time is less than the current UTC time
        session_collection.delete_many(
            {"expires_at": {"$lt": datetime.now(timezone.utc)}})

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
    "http://127.0.0.1:5173",
    "http://localhost:5173/"

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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Custom error response
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "success": False}
    )


@app.exception_handler(RequestValidationError)
async def http_exception_handler(request: Request, exc: RequestValidationError):

    return JSONResponse(
        status_code=400,
        content={"message": "Request Validation failed",
                 "details": exc.errors(), "success": False}
    )

# Include the invoice router
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(billing_router, prefix="/api/billingType",
                   tags=["billingType"])
app.include_router(department_router,
                   prefix="/api/department", tags=["department"])
app.include_router(client_router, prefix="/api/client", tags=["client"])
app.include_router(process_router, prefix="/api/process", tags=["process"])
app.include_router(project_router, prefix="/api/project", tags=["project"])
