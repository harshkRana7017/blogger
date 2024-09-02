from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pathlib import Path
import json
from fastapi.templating import Jinja2Templates
from models import User
from datetime import datetime
from passwordHashing import get_hashed_password, verify_password
from getTokenFuncs import create_acess_token, decode_access_token
import jwt

templates= Jinja2Templates(directory='Templates')

app = FastAPI()
ADMIN_USERNAME='admin'
ADMIN_PASSWORD='admin@123'
ADMIN_HASHED_PASSWORD=get_hashed_password(ADMIN_PASSWORD)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


USERNAME=''
PASSWORD=''

def get_current_user(request:Request):
    token = request.cookies.get("access_token")
    try:
      payload=  decode_access_token(token)
      username:str =payload["sub"]
      is_admin:bool =payload["is_admin"]
      return {"username":username, "is_admin":is_admin}
    except jwt.PyJWTError:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/home")
def read_route(request:Request):
    user_name ="john"
    return templates.TemplateResponse("index.html", {"request":request, "user_name":user_name})


@app.get("/")
def loginForm(request: Request):
    return templates.TemplateResponse("loginForm.html", {"request":request})


# change this to confirm user
@app.post("/login" )
def login(request:Request, username:str =Form(...), password:str=Form(...)):
    USERNAME=username
    PASSWORD=password
    if USERNAME == ADMIN_USERNAME and verify_password(PASSWORD, ADMIN_HASHED_PASSWORD):
     token = create_acess_token(username, True)
    else:
     token = create_acess_token(username, False)
    response = HTMLResponse(content=templates.TemplateResponse("index.html", {"request": request, "user_name": username}).body.decode())
    response.set_cookie(key="access_token", value=token, httponly=True, max_age=3600) 
    return response
    



@app.get("/articles", response_class = HTMLResponse)
async def read_articles(request: Request, user:dict =Depends(get_current_user)):
    article_files= Path("Articles").glob("*json")
    articles= [json.loads(article_file.read_text())  for article_file in article_files]
    return templates.TemplateResponse("articleList.html", {"request":request, "articles": articles, "user":user})


@app.get('/articles/{article_id}')
async def read_article(request: Request,article_id: int):
    article_path = Path(f"Articles/{article_id}.json")
    if(article_path.exists()):
        article =json.loads(article_path.read_text())
        return templates.TemplateResponse('article.html', {"request":request, "article":article})
    
    return "Article not found"

@app.get('/article/add')
def add_articleForm(request:Request):
   return templates.TemplateResponse("addArticleForm.html", {"request":request})


@app.post('/article/add')
def add_article(request:Request,title:str =Form(...), content:str =Form(...) , user:dict=Depends(get_current_user)):
   if(user["is_admin"]):
        today_date= datetime.now().strftime('%Y-%m-%d')
        article_id =len(list(Path("Articles").glob("*json")))+1
        article_path = Path(f"Articles/{article_id}.json")
        article_path.write_text(json.dumps({"id":article_id, "title":title, "content":content, "author":USERNAME, "date": today_date}))
        return templates.TemplateResponse('article.html', {"request":request,"article":json.loads(article_path.read_text()) })
   else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get('/article/update/{article_id}')
def update_articleForm(request:Request, article_id:int, user:dict =Depends(get_current_user)):
    if user["is_admin"]:
        article_path = Path(f"Articles/{article_id}.json")
        return templates.TemplateResponse("editArticleForm.html", {"request":request, "article":json.loads(article_path.read_text())})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.post('/article/update/{article_id}')
def update_article(request:Request,article_id: int, title:str =Form(...), content:str=Form(...), user:dict=Depends(get_current_user)):
    if user["is_admin"]:
        article_path=Path(f"Articles/{article_id}.json")
        article_path.write_text(json.dumps({"id":article_id, "title":title, "content":content, "author":USERNAME, "date": datetime.now().strftime('%Y-%m-%d')}))
        return templates.TemplateResponse('article.html', {"request":request,"article":json.loads(article_path.read_text())})
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

