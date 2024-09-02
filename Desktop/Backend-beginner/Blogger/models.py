from sqlalchemy import Column, Integer, String,ARRAY
from database import Base
class BlogPost(Base):
    __tablename__="blog_posts"

    id =Column(Integer, primary_key=True, index=True)
    title=Column(String, index=True)
    content=Column(String)
    category=Column(String)
    tags=Column(ARRAY(String))


