from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

import uuid

import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient

from config import settings

from blogmax.routers.blog_routers import router as blog_routers
from blogmax.routers.user_routers import router as user_routers
from blogmax.routers.dashboard import router as dashboard_routers
from blogmax.routers.comment_routers import router as comment_routers

from blogmax.models import User

from utils.hashing import Hash
from config import create_access_token

app = FastAPI()
client = AsyncIOMotorClient(settings.DB_URL)
db = client[settings.DB_NAME]

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb_client.close()


# redirect / to /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(blog_routers, tags=["blog"], prefix="/api/blogs")
app.include_router(user_routers, tags=["user"], prefix="/api/users")
app.include_router(dashboard_routers, tags=["dashboard"], prefix="/api/dashboard")
app.include_router(comment_routers, tags=["comment"], prefix="/api")


# ----------------- User -----------------
@app.post("/api/auth/register", tags=["auth"])
async def create_user(request: User):
    hashed_password = Hash.bcrypt(request.password)
    user_object = dict(request)

    if await db["users"].find_one({"username": user_object["username"]}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username already exists"
        )

    user_object["password"] = hashed_password
    # remove id from request
    user_object.pop("id")
    user_object["_id"] = str(uuid.uuid4())
    insert_user = await db["users"].insert_one(user_object)
    access_token = create_access_token(data={"sub": user_object["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", tags=["auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"username": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not Hash.verify(user["password"], form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        reload=settings.DEBUG_MODE,
        port=settings.SERVER_PORT,
    )
