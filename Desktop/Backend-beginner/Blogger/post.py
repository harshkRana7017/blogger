from pydantic import BaseModel
from typing import List, Optional

class Post(BaseModel):
    title:str
    content:str
    id:Optional[int]
    category:str
    tags:List[str]

class PostUpdate(BaseModel):
    title:Optional[str] =None
    content:Optional[str] =None
    category:Optional[str]=None
    tags:Optional[List[str]] =None
