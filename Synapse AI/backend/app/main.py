from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import io
import os
from googletrans import Translator
from pydantic import BaseModel
import re

# Initialize Tesseract and set paths
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA_PREFIX = r"C:\Program Files\Tesseract-OCR\tessdata"

os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to restrict access
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the Google Translate API
translator = Translator()

def clean_text(text):
    """
    Clean the text while preserving paragraph structure.
    """
    # Split text into lines
    lines = text.split('\n')
    
    # Process each line
    processed_lines = []
    current_line = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            if current_line:
                # Join current paragraph and add it
                processed_lines.append(' '.join(current_line))
                current_line = []
            processed_lines.append('')  # Preserve paragraph break
            continue
            
        # Clean the line
        cleaned_line = line.strip()
        if cleaned_line:
            current_line.append(cleaned_line)
    
    # Add any remaining paragraph
    if current_line:
        processed_lines.append(' '.join(current_line))
    
    # Join lines with double newlines to preserve paragraph structure
    return '\n\n'.join(processed_lines)

# Pydantic model for translation request
class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"

@app.post("/api/ocr")
async def ocr(file: UploadFile, language: str = Form(...)):
    try:
        supported_languages = ["eng", "spa", "mal", "fra"]
        if language not in supported_languages:
            return {"error": f"Language {language} not supported. Choose from {supported_languages}"}

        if file.filename.lower().endswith('.pdf'):
            file_content = await file.read()
            pdf_images = convert_from_bytes(file_content)
            text = ""
            for pdf_image in pdf_images:
                text += pytesseract.image_to_string(pdf_image, lang=language)
        else:
            image = Image.open(io.BytesIO(await file.read()))
            text = pytesseract.image_to_string(image, lang=language)

        # Clean the text while preserving paragraphs
        cleaned_text = clean_text(text)
        return {"text": cleaned_text, "language": language}

    except Exception as e:
        print(f"OCR Error: {e}")  # Log error for debugging
        return {"error": str(e)}

@app.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """
    Translate the extracted text to English.
    """
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="No text provided for translation.")

        # Clean the text before translation
        cleaned_text = clean_text(request.text)

        # Map OCR language codes to Google Translate language codes
        language_map = {
            "eng": "en",
            "spa": "es",
            "mal": "ml",
            "fra": "fr",
            "auto": "auto"
        }

        # Get the correct language code for Google Translate
        source_lang = language_map.get(request.source_lang, "auto")

        # Perform translation
        translated = translator.translate(cleaned_text, src=source_lang, dest="en")
        
        if not translated or not translated.text:
            raise HTTPException(status_code=500, detail="Translation failed - no result received")

        return {"translated_text": translated.text}

    except Exception as e:
        print(f"Translation Error: {e}")  # Log error for debugging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Welcome to the OCR API!"}
