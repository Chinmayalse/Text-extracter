import os
import json
import time
import tempfile
import logging
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from typing import Dict, Any
from contextlib import contextmanager
import cv2
import numpy as np
import easyocr
import pytesseract
import pypdfium2 as pdfium
from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

from pocketbase import PocketBase
from pocketbase.client import Record

pb_client = PocketBase(' http://127.0.0.1:8090')

# Create results folder if it doesn't exist
RESULTS_FOLDER = "results"
if not os.path.exists(RESULTS_FOLDER):
    os.makedirs(RESULTS_FOLDER)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Groq(api_key="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")

class Color:
    """
    Class to handle color and grayscale operations on images.
    """
    def isolate_report(self, image_path):
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cropped = gray[y:y+h, x:x+w]
        image_array = np.array(cropped)
        return int(np.mean(image_array)), 35 if np.std(image_array) < 50 else 0


class PDFConvert:
    """
    Class for converting PDF documents to images.
    """
    def convert_pdf_to_images(self, file_path, scale=300/72, output_folder='.'):
        pdf_file = pdfium.PdfDocument(file_path)
        page_indices = [i for i in range(len(pdf_file))]
        renderer = pdf_file.render(
            pdfium.PdfBitmap.to_pil,
            page_indices=page_indices,
            scale=scale,
        )
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        image_paths = []
        for i, image in zip(page_indices, renderer):
            image_file_path = os.path.join(output_folder, f'page_{i+1}.jpg')
            image.save(image_file_path, format='JPEG', optimize=True)
            image_paths.append(image_file_path)
        return image_paths


class ImageConvert:
    """
    Class for handling image pre-processing and text extraction.
    """
    def __init__(self):
        self.col = Color()
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def process_image(self, image_path):
        """
        Processes the image to extract text using both EasyOCR and Tesseract.
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        bg, diff = self.col.isolate_report(image_path)
        if diff == 0:
            preprocessed_image = resized
        else:
            bg -= diff
            _, thresh = cv2.threshold(resized, bg, 255, cv2.THRESH_BINARY)
            denoised = cv2.fastNlMeansDenoising(thresh, None, h=30)
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
            preprocessed_image = cv2.filter2D(denoised, -1, kernel)

        # EasyOCR
        reader = easyocr.Reader(['en'], gpu=False)
        text_ = reader.readtext(preprocessed_image)
        threshold = 0.25
        all_texts = []
        for t_ in text_:
            bbox, text, score = t_
            if score > threshold:
                all_texts.append(text)
        extracted_text = "\n".join(all_texts)

        # Tesseract
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(preprocessed_image, config=custom_config)

        return 'Extraction 1\n' + extracted_text + '\nExtraction 2\n' + text

    def extract_text_from_images(self, image_paths):
        """
        Extracts text from a list of image paths.
        """
        all_texts = []
        for image_path in image_paths:
            text = self.process_image(image_path)
            all_texts.append(text)
        return all_texts


class TextResponse(BaseModel):
    """
    Response model for returning extracted and corrected text.
    """
    extracted_text: str
    corrected_text: str


pdf_converter = PDFConvert()
image_converter = ImageConvert()

from pydantic import BaseModel

# class ChatbotRequest(BaseModel):
#     message: str
#     extracted_data: dict

# class ChatbotResponse(BaseModel):
#     response: str

# @app.post("/chatbot", response_model=ChatbotResponse)
# async def chatbot(request: ChatbotRequest):
#     user_message = request.message
#     extracted_data = request.extracted_data

#     # Prepare the context for the LLM
#     context = f"""
#     You are an AI assistant specialized in interpreting medical test results. 
#     Here's the extracted data from the medical report:
#     {json.dumps(extracted_data, indent=2)}

#     Please answer the user's question based on this data. If the question is not related to the provided data, politely inform the user that you can only answer questions about the given test results.
#     """

#     try:
#         # Use Groq to generate a response
#         completion = client.chat.completions.create(
#             model="llama3-70b-8192",
#             messages=[
#                 {"role": "system", "content": context},
#                 {"role": "user", "content": user_message}
#             ],
#             temperature=0.5,
#             max_tokens=500,
#         )

#         # Extract the response from the Groq completion
#         response = completion.choices[0].message.content

#         return ChatbotResponse(response=response)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    # # List all tests
    # if re.search(r'\b(list|all|available)\s+(tests|results)\b', message):
    #     tests = [test["bio_marker"] for test in extracted_data.get("test_results", [])]
    #     return ChatbotResponse(response=f"The available tests are: {', '.join(tests)}")
    
    # # Get specific test result
    # if "result" in message or "value" in message:
    #     for test in extracted_data.get("test_results", []):
    #         if test["bio_marker"].lower() in message:
    #             return ChatbotResponse(response=f"The result for {test['bio_marker']} is {test['result']} {test['units']}. The reference range is {test['reference_range']}.")
    
    # # Get normal range
    # if "normal" in message or "range" in message:
    #     for test in extracted_data.get("test_results", []):
    #         if test["bio_marker"].lower() in message:
    #             return ChatbotResponse(response=f"The normal range for {test['bio_marker']} is {test['reference_range']}.")
    
    # # Get test information
    # if "what is" in message or "tell me about" in message:
    #     for test in extracted_data.get("test_results", []):
    #         if test["bio_marker"].lower() in message:
    #             return ChatbotResponse(response=f"{test['bio_marker']} is a test that measures {test.get('note', 'No additional information available.')}. The normal range is {test['reference_range']}.")
    
    # return ChatbotResponse(response="I'm sorry, I don't have information about that. You can ask about specific test results, normal ranges, or general information about a test. You can also ask for a list of all available tests.")


@contextmanager
def temporary_file(suffix=None):
    """
    Context manager to handle temporary file creation and deletion.
    """
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        os.close(fd)
        yield path
    finally:
        try:
            os.unlink(path)
        except PermissionError:
            pass


@app.post("/process_pdf", response_model=TextResponse)
async def process_pdf(pdf_file: UploadFile = File(...)):
    """
    API endpoint to process a PDF file, extract text, and correct it using Groq API.
    """
    temp_pdf_path = None
    try:
        # Create a temporary file for the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf_path = temp_pdf.name
            content = await pdf_file.read()
            temp_pdf.write(content)

        # Convert PDF to images and extract text
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = pdf_converter.convert_pdf_to_images(temp_pdf_path, output_folder=temp_dir)
            extracted_texts = image_converter.extract_text_from_images(image_paths)

        combined_text = "\n\n".join(extracted_texts)

        # Use Groq API to correct and structure the extracted text
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an expert at processing medical reports. Extract all
                    relevant medical test result information and return it in a 
                    structured JSON format.the numeric result of the test, if you dont find the result in 'Extraction 2' check 'Extraction 1', do not write any arbitary value.
                    """
                },
                {
                    "role": "user",
                    "content": f"Please format and correct the following medical test results:\n\n{combined_text}"
                }
            ],
            temperature=0.2,
            max_tokens=2048,
        )

        corrected_text = completion.choices[0].message.content
        logger.info(f"Raw API response: {corrected_text}")

        # Attempt to parse the response as JSON
        try:
            json_data = json.loads(corrected_text)
        except json.JSONDecodeError:
            # Handle possible JSON parsing errors
            json_start = corrected_text.find('{')
            json_end = corrected_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = corrected_text[json_start:json_end]
                json_data = json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in the API response")

        # Save the JSON data to a file
        json_file_name = f"{pdf_file.filename.split('.')[0]}_results.json"
        json_file_path = os.path.join(RESULTS_FOLDER, json_file_name)
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        # Prepare and return the response data
        response_data = {
            "extracted_text": combined_text,
            "corrected_text": corrected_text,
            "json_file_path": json_file_path,
            "json_data": json_data
        }

        return JSONResponse(content=response_data)

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing response from AI model")
    except ValueError as e:
        logger.error(f"Error processing API response: {str(e)}")
        raise HTTPException(status_code=500, detail="Invalid response format from AI model")
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing the PDF")
    finally:
        # Ensure temporary PDF file is deleted
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            for _ in range(5):
                try:
                    os.unlink(temp_pdf_path)
                    break
                except PermissionError:
                    time.sleep(1)
    # Load the extracted data
def load_extracted_data():
    try:
        with open("extracted_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

extracted_data = load_extracted_data()

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

class ChatbotRequest(BaseModel):
    message: str
    extracted_data: dict
    user_id: str | None = None

class ChatbotResponse(BaseModel):
    response: str

@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot(request: ChatbotRequest):
    logger.info(f"Received request: {request}")
    try:
        user_message = request.message
        extracted_data = request.extracted_data
        user_id = request.user_id  # This will be None if not provided

        logger.info(f"User message: {user_message}")
        logger.info(f"Extracted data: {extracted_data}")
        logger.info(f"User ID: {user_id}")
        # Prepare the context for the LLM
        context = f"""
        You are an AI assistant specialized in interpreting medical test results.first greet them saying Hello. 
        Here's the extracted data from the medical report:
        {json.dumps(extracted_data, indent=2)}

        Please answer the user's question based on this data. If the question is not related to the provided data, politely inform the user that you can only answer questions about the given test results.
        """

        logger.info("Sending request to Groq API")
        try:
            # Use Groq to generate a response
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,
                max_tokens=500,
            )

            # Extract the response from the Groq completion
            response = completion.choices[0].message.content
            logger.info(f"Received response from Groq: {response}")
        except Exception as groq_error:
            logger.error(f"Error calling Groq API: {str(groq_error)}")
            response = "I'm sorry, I encountered an error while processing your request. Please try again later."

        return ChatbotResponse(response=response)
    except Exception as e:
        logger.error(f"Error in chatbot: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
# Make sure to add these imports at the top of your file
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
