from fastapi import APIRouter, HTTPException
from google.cloud import translate_v2 as translate
from app.models.model_types import TranslationRequest

router = APIRouter()

# Initialize Google Translate client
translate_client = translate.Client()

@router.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """
    Translate content to a target language using Google Translate API.
    """
    try:
        # Check if the target language is supported
        supported_languages = ["en", "es", "fr", "de", "hi", "zh"]
        if request.target_language not in supported_languages:
            raise HTTPException(status_code=400, detail="Unsupported target language.")

        # Translate the text
        translation = translate_client.translate(request.text, target_language=request.target_language)

        return {"translated_text": translation["translatedText"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
