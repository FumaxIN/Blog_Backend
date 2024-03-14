from fastapi import FastAPI
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

from blogmax.routers import router as blog_router

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()

app.include_router(blog_router, tags=["blog"], prefix="/blog")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        reload=settings.DEBUG_MODE,
        port=settings.SERVER_PORT,
    )
