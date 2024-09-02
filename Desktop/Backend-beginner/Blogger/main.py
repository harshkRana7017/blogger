from typing import Optional
from fastapi import FastAPI, Request, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database import SessionLocal
from models import BlogPost
from post import Post, PostUpdate
from datetime import datetime


app = FastAPI()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# endpoints
@app.get("/")
def root_route(request: Request):
    return {"message":"server working"}

@app.get("/posts")
def read_posts(term:Optional[str]= Query(None, min_length=1),db: Session=Depends(get_db)):
    if term is None:
        posts =db.query(BlogPost).all()
        return posts
    else:
        query= db.query(BlogPost).filter(or_(BlogPost.title.ilike(f"%{term}%"), BlogPost.category.ilike(f"%{term}%"), BlogPost.content.ilike(f"%{term}%")))
        posts =query.all()
        return posts



@app.get("/post/{post_id}")
def read_post(post_id:int, db:Session=Depends(get_db)):
    post=db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.post("/post")
def create_posts( postData:Post, db:Session=Depends(get_db)):
    post = BlogPost(
        title=postData.title,
        content=postData.content, 
        category=postData.category, 
        tags=postData.tags, 
        id=postData.id )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@app.put("/post/{post_id}")
def update_post(post_id:int, postData:PostUpdate, db:Session=Depends(get_db)):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if postData.title:
        post.title = postData.title
    if postData.content:
        post.content = postData.content
    if postData.category:
        post.category = postData.category
    if postData.tags is not None:
        post.tags = postData.tags

    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "tags": post.tags,
        "updatedAt": datetime.utcnow()
    }

@app.delete("/post/{post_id}")
def delete_post(post_id:int, db:Session=Depends(get_db)):
    post =db.query(BlogPost).filter(BlogPost.id==post_id).first()
    db.delete(post)
    db.commit()
    return {"detail":"Post deleted sucessfully"}