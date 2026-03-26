# mistral.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_ENDPOINT = os.getenv("AZUREAI_ENDPOINT", "")
MISTRAL_KEY = os.getenv("AZUREAI_API_KEY", "")
MISTRAL_MODEL = os.getenv("MODEL_NAME", "mistral-document-ai-2512-2")


def process_mistral_ocr(file_base64: str, mime_type: str):

    if not MISTRAL_KEY or not MISTRAL_ENDPOINT:
        return {"error": "Missing Mistral credentials"}

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_KEY}"
    }

    payload = {
        "model": MISTRAL_MODEL,
        "document": {
            "type": "document_url",
            "document_url": f"data:{mime_type};base64,{file_base64}"
        },
        "include_image_base64": True
    }

    try:
        response = requests.post(
            MISTRAL_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=180
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {"error": f"Mistral API Error: {str(e)}"}