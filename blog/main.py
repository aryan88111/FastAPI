# from fastapi import FastAPI,Request,Depends
# from . import schemas 
# from pydantic import BaseModel
# import random
# import uuid

# app=FastAPI()


# from .database import SessionLocal


# # Dependency to get DB session
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# class Author(BaseModel):
#     name: str
#     email: str


# class Blog(BaseModel):
#     title: str
#     content: str
#     published: bool = True
#     views: int = 0 
    
# class Product(BaseModel):
#     name: str
#     price: float
    
# users = []

# @app.get("/users")
# def get_users():
#     return users

# @app.post("/users")
# def create_user(user: dict):
#     users.append(user)
#     return {"status": "User created"}

# @app.put("/users/{user_id}")
# def update_user(user_id: int, user: dict):
#     users[user_id] = user
#     return {"status": "User updated"}

# @app.delete("/users/{user_id}")
# def delete_user(user_id: int):
#     users.pop(user_id)
#     return {"status": "User deleted"}    

# @app.post("/cart")
# def add_products_to_cart(products: list[Product]):
#     total = sum(item.price for item in products)
#     return {"total": total, "products": products}

# @app.post("/blog")

# def creat_blog(req:schemas.Blog):
#     return  {"title":req.title, "body":req.body}




# @app.post("/optional-blog")
# def create_blog(blog: Blog):
#     return blog

# @app.post("/users/{user_id}/blogs")

# def post_blog(user_id: int, blog: Blog):
#     id=str(uuid.uuid4())
#     return {"main_id": id,"user_id":user_id, "blog": blog}
      
    
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     print("Incoming request:", request.url)
#     response = await call_next(request)
#     return response         

from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from . import schemas, models
from .database import SessionLocal, engine
from pydantic import BaseModel
import uuid

# Create all tables in DB
print("✅ Creating tables in PostgreSQL...")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# Non-DB Pydantic Models
# ---------------------------
class Author(BaseModel):
    name: str
    email: str

class Blog(BaseModel):
    title: str
    content: str
    published: bool = True
    views: int = 0 

class Product(BaseModel):
    name: str
    price: float

# ---------------------------
# In-Memory User Store
# ---------------------------
users = []

@app.get("/users")
def get_users():
    return users

@app.post("/users")
def create_user(user: dict):
    users.append(user)
    return {"status": "User created"}

@app.put("/users/{user_id}")
def update_user(user_id: int, user: dict):
    users[user_id] = user
    return {"status": "User updated"}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    users.pop(user_id)
    return {"status": "User deleted"}    

# ---------------------------
# Blog Routes (DB Connected)
# ---------------------------
@app.post("/blog", response_model=schemas.BlogResponse)
def create_blog(req: schemas.BlogCreate, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=req.title, body=req.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get("/blogs", response_model=list[schemas.BlogResponse])
def get_all_blogs(db: Session = Depends(get_db)):
    return db.query(models.Blog).all()

# ---------------------------
# Additional Routes
# ---------------------------
@app.post("/optional-blog")
def create_optional_blog(blog: Blog):
    return blog

@app.post("/users/{user_id}/blogs")
def post_blog_for_user(user_id: int, blog: Blog):
    blog_id = str(uuid.uuid4())
    return {"main_id": blog_id, "user_id": user_id, "blog": blog}

@app.post("/cart")
def add_products_to_cart(products: list[Product]):
    total = sum(item.price for item in products)
    return {"total": total, "products": products}

# ---------------------------
# Middleware
# ---------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print("Incoming request:", request.url)
    response = await call_next(request)
    return response
