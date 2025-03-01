from fastapi import APIRouter, HTTPException
from google.cloud import translate_v2 as translate
from app.models.model_types import TranslationRequest

router = APIRouter()

# Initialize Google Translate client
translate_client = translate.Client()

supported_indian_languages = ["hi", "pa", "ta", "te", "bn", "gu", "ml", "kn", "mr", "ne"]

@router.post("/api/translate")
async def translate_text(request: TranslationRequest):
    """
    Translate content to a target language using Google Translate API.
    """
    try:
        # Check if the target language is supported
        
        if request.target_language not in supported_indian_languages:
            raise HTTPException(status_code=400, detail="Unsupported target language.")

        # Translate the text
        translation = translate_client.translate(request.text, target_language=request.target_language)

        return {"translated_text": translation["translatedText"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
