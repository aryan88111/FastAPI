from pydantic import BaseModel

class BlogCreate(BaseModel):
    title: str
    body: str

class BlogResponse(BlogCreate):
    id: int

    class Config:
        orm_mode = True
