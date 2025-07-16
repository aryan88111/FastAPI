# import fitz
# import os
# import pdfplumber
# from fastapi import FastAPI

# app=FastAPI()

# inputPdf=fitz.open("/Users/aryangautam/Desktop/work/FastApi-python/blog/p2.pdf")
# print(inputPdf)
# # Folder to save images
# os.makedirs("extracted_images", exist_ok=True)

# print(len(inputPdf))
# listt=[]
# imageList=[]


# @app.get("/")
# def parse_pdf():
#     for pageidx, pages in enumerate(inputPdf):
#         text= pages.get_text()
#         listt.append(text)
#         images=  pages.get_images(full=True)
        
        
        
#         for idx,img in enumerate(images):
#          xref=img[0]
#          base_image = inputPdf.extract_image(xref)  # Extract image binary
#          image_bytes = base_image["image"]
#          image_ext = base_image["ext"]  # Extension (png/jpg)

#          image_filename = f"image_{idx+1}_{idx+1}.{image_ext}"
#          image_path = os.path.join("extracted_images", image_filename)
#          with open(image_path, "wb") as f:
#             f.write(image_bytes)
    
#          imageList.append(image_path)
    
#     return (listt,imageList)
# # inputPdf.close()  

# # parse_pdf();  




# @app.get("/text-table")
# def parse_pdf_table():
#     text_list = []
#     table_data = []

#     with pdfplumber.open(inputPdf) as pdf:
#         for page_index, page in enumerate(pdf.pages):
#             # Extract text
#             text = page.extract_text()
#             text_list.append(text or f"No text on page {page_index + 1}")
            
#             # Extract tables (if any)
#             tables = page.extract_tables()
#             for table in tables:
#                 table_data.append({
#                     "page": page_index + 1,
#                     "table": table
#                 })
                
                

#     return {
#         "texts": text_list,
#         "tables": table_data
#     }



import re
import fitz  # PyMuPDF
import os
import pdfplumber
from fastapi import FastAPI

app = FastAPI()

# Correct PDF file path
PDF_PATH = "/Users/aryangautam/Desktop/work/FastApi-python/blog/p4.pdf"

# Open with PyMuPDF (for image extraction only)
inputPdf = fitz.open(PDF_PATH)

#  Create folder for saving extracted images
os.makedirs("extracted_images", exist_ok=True)

#  Global cache (not recommended for production, but fine for testing)
listt = []
imageList = []

# Route 1: Extract text + images using PyMuPDF
@app.get("/")
def parse_pdf():
    # Clear previous data on re-call
    listt.clear()
    imageList.clear()

    for pageidx, pages in enumerate(inputPdf):
        text = pages.get_text()
        listt.append(text)

        images = pages.get_images(full=True)

        for idx, img in enumerate(images):
            xref = img[0]
            base_image = inputPdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = f"image_page{pageidx+1}_{idx+1}.{image_ext}"
            image_path = os.path.join("extracted_images", image_filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            imageList.append(image_path)

    return {
        "texts": listt,
        "images": imageList
    }
    
    

# Route 2: Extract text + tables using pdfplumber
@app.get("/text-table")
def parse_pdf_table():
    text_list = []
    table_data = []

    with pdfplumber.open(PDF_PATH) as pdf:
        for page_index, page in enumerate(pdf.pages):
            # Extract text
            text = page.extract_text()
            text_list.append(text or f"No text on page {page_index + 1}")

            # Extract table
            tables = page.extract_tables()
            for table in tables:
                table_data.append({
                    "page": page_index + 1,
                    "table": table
                })

    return {
        "texts": text_list,
        "tables": table_data
    }


# @app.get("/get-headings")
# def get_headings():
#     headings = []

#     with pdfplumber.open(PDF_PATH) as pdf:
#         for page_num, page in enumerate(pdf.pages, start=1):
#             text_lines = page.extract_text().split('\n')

#             for line in text_lines:
#                 # Line ke characters dekhne ke liye phir se chars ka use
#                 for char in page.chars:
#                     if char["text"] in line and float(char["size"]) > 16:
#                         headings.append({
#                             "text": line.strip(),
#                             "page": page_num,
#                             "font_size": char["size"]
#                         })
#                         break  # Ek baar add ho gaya toh break kar do

#     return {"headings": headings}


@app.get("/get-headings")
def get_headings():
    headings = []

    with pdfplumber.open(PDF_PATH) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            for line in lines: 
                line = line.strip()
                if not line or len(line) < 3:
                    continue

                # Simple heading rules
                if (
                    re.match(r"^(Chapter|Section)?\s?\d+(\.\d+)?", line, re.IGNORECASE) or  # e.g., Section 1.2
                    (line.isupper() and len(line.split()) <= 6) or                         # ALL CAPS short lines
                    (line.istitle() and len(line.split()) <= 6)                            # Title Case short lines
                ):
                    headings.append({
                        "text": line,
                        "page": page_num
                    })

    return {"headings": headings}



#    AIzaSyCmLdOuhJhcmMJiVhgTt4ITmGE1oN15MPE 
#  gemini api key

# import google.generativeai as genai
# from pydantic import BaseModel

# os.environ["GOOGLE_API_KEY"] = "AIzaSyCmLdOuhJhcmMJiVhgTt4ITmGE1oN15MPE"
# genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


# def extract_pdf_text(pdf_path: str) -> str:
#     full_text = ""
#     with pdfplumber.open(pdf_path) as pdf:
#         for i, page in enumerate(pdf.pages, start=1):
#             text = page.extract_text()
#             if text:
#                 full_text += f"\n\n--- Page {i} ---\n{text}"
#     return full_text

# # ======== GEMINI CALL FUNCTION ========
# def ask_gemini_about_pdf(pdf_text: str, question: str) -> str:
#     model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")

#     prompt = f"{pdf_text}\n\nNow answer this:\n{question}"
#     response = model.generate_content(prompt)
    
#     return response.text

# # ======== REQUEST MODEL ========
# class PDFQuery(BaseModel):
#     question: str

# @app.post("/pdf-query")
# def query_pdf(data: PDFQuery):
#     pdf_text = extract_pdf_text(PDF_PATH)
#     answer = ask_gemini_about_pdf(pdf_text, data.question)
#     return {"question": data.question, "answer": answer}