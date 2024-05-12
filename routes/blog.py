from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["blog_app"]
collection = db["posts"]

# Define Pydantic models
class Post(BaseModel):
    title: str
    content: str

class Comment(BaseModel):
    text: str

# CRUD operations
@app.post("/posts/")
async def create_post(post: Post):
    post_dict = post.dict()
    result = collection.insert_one(post_dict)
    return {"id": str(result.inserted_id), **post_dict}

@app.get("/posts/{post_id}")
async def read_post(post_id: str):
    post = collection.find_one({"_id": ObjectId(post_id)})
    if post:
        return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.put("/posts/{post_id}/like")
async def like_post(post_id: str):
    result = collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes": 1}})
    if result.modified_count == 1:
        return {"message": "Post liked successfully"}
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts/{post_id}/comments")
async def create_comment(post_id: str, comment: Comment):
    comment_dict = comment.dict()
    result = collection.update_one({"_id": ObjectId(post_id)}, {"$push": {"comments": comment_dict}})
    if result.modified_count == 1:
        return {"message": "Comment added successfully"}
    raise HTTPException(status_code=404, detail="Post not found")
