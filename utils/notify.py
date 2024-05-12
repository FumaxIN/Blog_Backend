from blogmax.models import Notification, Follow, User, BlogInDB, Like
from utils.motor_utilities import create_document, read_collection
from fastapi.encoders import jsonable_encoder


async def send_blog_notification(blog, author: User):
    follow_collection = await read_collection("follows", {"following._id": author.get("_id")})
    if not follow_collection:
        print("No followers")
        return
    for follower in follow_collection.get("documents"):
        notification = Notification(**{
            "user": follower["follower"],
            "title": "New Blog Post",
            "content": f"{author.get('username')} has posted a new blog titled {blog.get('title')}",
            "redirect_url": f"/blogs/{blog.get('url')}"
        })
        await create_document("notifications", jsonable_encoder(notification))


async def send_follow_notification(follow):
    notification = Notification(**{
        "user": follow.get("following"),
        "title": "New Follower",
        "content": f"{follow.get("follower").get('username')} is now following you",
        "redirect_url": f"/users/{follow.get('follower').get('username')}"
    })
    await create_document("notifications", jsonable_encoder(notification))


async def send_like_notification(like, user=None):
    notification = Notification(**{
        "user": user,
        "title": "New Like",
        "content": f"{like.get('liker').get('username')} liked your blog titled {like.get('blog').get('title')}",
        "redirect_url": f"/blogs/{like.get('blog').get('url')}"
    })
    print(notification)
    await create_document("notifications", jsonable_encoder(notification))
