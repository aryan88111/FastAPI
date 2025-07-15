from typing import Optional
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
from fastapi import FastAPI # pyright: ignore[reportMissingImports]
import uvicorn # pyright: ignore[reportMissingImports]
 
app=FastAPI()

# @app.get("/")
# def index():
#     return {"data":{"name":"aryan"}}
 
# @app.get("/about")
# def about():
#     return {"data":["about page"]}




@app.get("/blog")
def index(limit=10,published:bool=True,sort:Optional[str]=None):
    
    if published:
      return {"data":f"{limit} published blog list"}
    else:
      return{"data":f"{limit} bolgs"}
 
 
 
 
 
 
@app.get("/blog/unpublished")
def unpublished():
    
    return {"data":"all unpublished blogs"}


@app.get("/blog/{id}")
def show(id:int):
    #fetch blog with id
    return {"data":id}



# @app.get("/blog/{id}/comments")
# def show(id):
  
#     return {"data":{"dsgvfnds","bvbdvs"}}


@app.get("/blog/{id}/comments")
def show(id,limit=10):
  
    return {"data":{f"{limit} comment limit","dsgvfnds","bvbdvs"}}   




# post. req

class Blog(BaseModel):
    title:str
    body:str
    published:Optional[bool]
    

@app.post("/blog")
def create_blog(req:Blog):

    return {"data":f"Blog is created with title as {req.title}"}
        
        
        
# if __name__=="__main__":
#     uvicorn.run(app,host="0.0.0.0",port=9000)
    
    
        