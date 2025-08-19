# from typing import Optional
# from pydantic import BaseModel # pyright: ignore[reportMissingImports]
# from fastapi import FastAPI # pyright: ignore[reportMissingImports]
# import uvicorn # pyright: ignore[reportMissingImports]
 
# app=FastAPI()

# # @app.get("/")
# # def index():
# #     return {"data":{"name":"aryan"}}
 
# # @app.get("/about")
# # def about():
# #     return {"data":["about page"]}




# @app.get("/blog")
# def index(limit=10,published:bool=True,sort:Optional[str]=None):
    
#     if published:
#       return {"data":f"{limit} published blog list"}
#     else:
#       return{"data":f"{limit} bolgs"}
 
 
 
 
 
 
# @app.get("/blog/unpublished")
# def unpublished():
    
#     return {"data":"all unpublished blogs"}


# @app.get("/blog/{id}")
# def show(id:int):
#     #fetch blog with id
#     return {"data":id}



# # @app.get("/blog/{id}/comments")
# # def show(id):
  
# #     return {"data":{"dsgvfnds","bvbdvs"}}


# @app.get("/blog/{id}/comments")
# def show(id,limit=10):
  
#     return {"data":{f"{limit} comment limit","dsgvfnds","bvbdvs"}}   




# # post. req

# class Blog(BaseModel):
#     title:str
#     body:str
#     published:Optional[bool]
    

# @app.post("/blog")
# def create_blog(req:Blog):

#     return {"data":f"Blog is created with title as {req.title}"}
        
        
        
# # if __name__=="__main__":
# #     uvicorn.run(app,host="0.0.0.0",port=9000)
    
    
        # server.py
# from fastapi import FastAPI, HTTPException, Query
# from fastapi.middleware.cors import CORSMiddleware
# import requests
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/api/company")
# def get_company(name: str = Query(..., description="Company name to search")):
#     try:
#         # os.getenv("PRIVCO_API_KEY")
#         url = f"https://api.privco.com/v2/search?name={name}"
#         headers = {
#             "Accept": "application/json",
#             "x-api-key": os.getenv("PRIVCO_API_KEY")
#         }
#         # print(os.getenv("PRIVCO_API_KEY"))
#         response = requests.get(url, headers=headers)
#         response.raise_for_status()  # Raise error for non-200 status
#         return response.json()
#     except requests.RequestException as e:
#         return {"error": str(e)}
    

   

# @app.get("/api/{profile_type}/{profile_id}")
# def get_financials(profile_type: str,profile_id: str,):
#     try:
#         print(profile_id,profile_type,"m backed se aaya hu")
#         url = f"https://api.privco.com/v2/financials/{profile_type}/{profile_id}"
#         headers = {
#             "Accept": "application/json",
#             "x-api-key": os.getenv("PRIVCO_API_KEY")
#         }
       
       

#         response = requests.get(url, headers=headers)
#         response.raise_for_status()

#         return response.json()


     

#     except requests.exceptions.RequestException as e:
#         raise HTTPException(status_code=500, detail=f"Data fetch failed: {str(e)}")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=5000)
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import json
from typing import Any, List, Dict, Union
import tempfile
import ijson  # streaming JSON parser
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JSON to CSV Converter", version="1.0.0")

class MultipleJsonInput(BaseModel):
    json_objects: str  # This will contain multiple JSON objects separated by newlines
    
    class Config:
        schema_extra = {
            "example": {
                "json_objects": """{"name": "John", "age": 30, "city": "New York"}
{"name": "Jane", "age": 25, "city": "Los Angeles"}
{"name": "Bob", "age": 35, "city": "Chicago"}"""
            }
        }

def flatten_json(data: Union[List[Dict], Dict]) -> pd.DataFrame:
    """
    Flatten JSON data into a pandas DataFrame
    """
    if isinstance(data, list):
        if not data:
            return pd.DataFrame()
        return pd.json_normalize(data)
    elif isinstance(data, dict):
        return pd.json_normalize([data])
    else:
        raise HTTPException(status_code=400, detail="Unsupported JSON format")

def parse_multiple_json_objects(text: str) -> List[Dict]:
    """
    Parse multiple JSON objects from text (NDJSON format or separated by newlines)
    """
    records = []
    lines = text.strip().split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        try:
            record = json.loads(line)
            if isinstance(record, dict):
                records.append(record)
            elif isinstance(record, list):
                records.extend(record)
            else:
                logger.warning(f"Skipping non-object JSON on line {i+1}: {type(record)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON on line {i+1}: {e}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid JSON on line {i+1}: {str(e)}"
            )
    
    return records

@app.post("/convert-json-file-to-csv/")
async def convert_json_file_to_csv(file: UploadFile = File(...)):
    """
    Convert JSON file to CSV. Supports both single JSON objects/arrays and NDJSON format.
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must have .json extension")
    
    try:
        contents = await file.read()
        
        # Try to decode the file content
        try:
            content_str = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
        
        # Parse JSON content
        records = []
        
        # First try parsing as a single JSON (object or array)
        try:
            data = json.loads(content_str)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]
            else:
                raise ValueError("JSON must be array or object")
        except json.JSONDecodeError:
            # If not valid single JSON, try parsing as NDJSON
            records = parse_multiple_json_objects(content_str)
        
        if not records:
            raise HTTPException(status_code=400, detail="No valid JSON objects found in file")
        
        # Convert to DataFrame and CSV
        df = flatten_json(records)
        
        # Create CSV buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        # Generate filename
        base_filename = file.filename.replace('.json', '')
        csv_filename = f"{base_filename}.csv"
        
        logger.info(f"Successfully converted {len(records)} JSON objects to CSV")
        
        return StreamingResponse(
            io.StringIO(buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/convert-json-body-to-csv/")
async def convert_json_body_to_csv(request: Request):
    """
    Convert JSON from request body to CSV. 
    Supports single JSON object, JSON array, or multiple JSON objects (NDJSON).
    """
    try:
        body = await request.body()
        body_text = body.decode("utf-8").strip()
        
        if not body_text:
            raise HTTPException(status_code=400, detail="Empty request body")
        
        records = []
        
        # Try parsing as single JSON first
        try:
            data = json.loads(body_text)
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]
            else:
                raise ValueError("JSON must be array or object")
        except json.JSONDecodeError:
            # If not valid single JSON, try parsing as multiple JSON objects
            records = parse_multiple_json_objects(body_text)
        
        if not records:
            raise HTTPException(status_code=400, detail="No valid JSON objects found")
        
        # Convert to DataFrame and CSV
        df = flatten_json(records)
        
        # Create CSV buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        logger.info(f"Successfully converted {len(records)} JSON objects to CSV")
        
        return StreamingResponse(
            io.StringIO(buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=converted_data.csv"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert-multiple-json-to-csv/")
async def convert_multiple_json_to_csv(input_data: MultipleJsonInput):
    """
    Convert multiple JSON objects to CSV using structured input.
    Each JSON object should be on a separate line.
    
    Example input:
    {
        "json_objects": "{\"name\": \"John\", \"age\": 30}\n{\"name\": \"Jane\", \"age\": 25}"
    }
    """
    try:
        if not input_data.json_objects.strip():
            raise HTTPException(status_code=400, detail="json_objects field cannot be empty")
        
        # Parse multiple JSON objects
        records = parse_multiple_json_objects(input_data.json_objects)
        
        if not records:
            raise HTTPException(status_code=400, detail="No valid JSON objects found")
        
        # Convert to DataFrame and CSV
        df = flatten_json(records)
        
        # Create CSV buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        logger.info(f"Successfully converted {len(records)} JSON objects to CSV")
        
        return StreamingResponse(
            io.StringIO(buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=multiple_json_converted.csv"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing multiple JSON input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Memory-efficient streaming endpoint for very large JSON files
@app.post("/convert-large-json-file-to-csv/")
async def convert_large_json_file_to_csv(file: UploadFile = File(...)):
    """
    Memory-efficient conversion for large JSON files using streaming.
    Best for files that might not fit in memory.
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must have .json extension")
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()
            tmp_path = tmp.name
        
        # Try streaming JSON parsing for large files
        records = []
        
        try:
            with open(tmp_path, "r", encoding="utf-8") as f:
                # Try to parse as JSON array with streaming
                try:
                    parser = ijson.items(f, "item")
                    records = list(parser)
                except (ijson.JSONError, ValueError):
                    # If that fails, try parsing the whole file
                    f.seek(0)
                    content = f.read()
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            records = data
                        elif isinstance(data, dict):
                            records = [data]
                    except json.JSONDecodeError:
                        # Last resort: try NDJSON
                        records = parse_multiple_json_objects(content)
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing JSON file: {str(e)}")
        
        if not records:
            raise HTTPException(status_code=400, detail="No valid JSON objects found in file")
        
        # Convert to DataFrame and CSV
        df = flatten_json(records)
        
        # Create CSV buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        # Generate filename
        base_filename = file.filename.replace('.json', '')
        csv_filename = f"{base_filename}_converted.csv"
        
        logger.info(f"Successfully converted {len(records)} JSON objects from large file to CSV")
        
        return StreamingResponse(
            io.StringIO(buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing large JSON file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "JSON to CSV Converter API",
        "endpoints": [
            "POST /convert-json-file-to-csv/ - Upload JSON file",
            "POST /convert-json-body-to-csv/ - Send JSON in request body",
            "POST /convert-multiple-json-to-csv/ - Send multiple JSON objects with structured input",
            "POST /convert-large-json-file-to-csv/ - Memory-efficient conversion for large files"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)