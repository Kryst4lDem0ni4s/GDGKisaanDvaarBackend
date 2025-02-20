from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Vision client
vision_client = vision.ImageAnnotatorClient()

class CropAnalysisRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class PestDetectionRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.post("/api/ai/crop-monitoring")
async def upload_crop_images(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
    """
    Upload image(s) for crop health analysis.
    """
    try:
        analysis_id = str(uuid.uuid4())
        image_urls = []

        for file in files:
            blob = storage.bucket().blob(f"crop-monitoring/{analysis_id}/{file.filename}")
            blob.upload_from_file(file.file)
            image_urls.append(blob.public_url)

        db.reference(f"ai/crop-monitoring/{analysis_id}").set({
            "user_id": user.uid,
            "image_urls": image_urls,
            "status": "processing"
        })

        return {"message": "Images uploaded successfully", "analysis_id": analysis_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/crop-monitoring/results/{analysisId}")
async def get_crop_analysis_results(analysisId: str, user=Depends(get_current_user)):
    """
    Retrieve crop health analysis results.
    """
    try:
        result_ref = db.reference(f"ai/crop-monitoring/{analysisId}").get()
        if not result_ref:
            raise HTTPException(status_code=404, detail="Analysis not found")
        if result_ref["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        return {"analysis": result_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai/pest-detection")
async def upload_pest_detection_images(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
    """
    Upload image(s) for pest detection.
    """
    try:
        detection_id = str(uuid.uuid4())
        image_urls = []

        for file in files:
            blob = storage.bucket().blob(f"pest-detection/{detection_id}/{file.filename}")
            blob.upload_from_file(file.file)
            image_urls.append(blob.public_url)

        db.reference(f"ai/pest-detection/{detection_id}").set({
            "user_id": user.uid,
            "image_urls": image_urls,
            "status": "processing"
        })

        return {"message": "Images uploaded successfully", "detection_id": detection_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Vision client
vision_client = vision.ImageAnnotatorClient()

class CropAnalysisRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class PestDetectionRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class ModelFeedbackRequest(BaseModel):
    analysis_id: str
    feedback: str  # Positive, Negative, or Detailed Feedback

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.post("/api/ai/crop-monitoring")
async def upload_crop_images(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
    """
    Upload image(s) for crop health analysis.
    """
    try:
        analysis_id = str(uuid.uuid4())
        image_urls = []

        for file in files:
            blob = storage.bucket().blob(f"crop-monitoring/{analysis_id}/{file.filename}")
            blob.upload_from_file(file.file)
            image_urls.append(blob.public_url)

        db.reference(f"ai/crop-monitoring/{analysis_id}").set({
            "user_id": user.uid,
            "image_urls": image_urls,
            "status": "processing"
        })

        return {"message": "Images uploaded successfully", "analysis_id": analysis_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/crop-monitoring/results/{analysisId}")
async def get_crop_analysis_results(analysisId: str, user=Depends(get_current_user)):
    """
    Retrieve crop health analysis results.
    """
    try:
        result_ref = db.reference(f"ai/crop-monitoring/{analysisId}").get()
        if not result_ref:
            raise HTTPException(status_code=404, detail="Analysis not found")
        if result_ref["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        return {"analysis": result_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai/pest-detection")
async def upload_pest_detection_images(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
    """
    Upload image(s) for pest detection.
    """
    try:
        detection_id = str(uuid.uuid4())
        image_urls = []

        for file in files:
            blob = storage.bucket().blob(f"pest-detection/{detection_id}/{file.filename}")
            blob.upload_from_file(file.file)
            image_urls.append(blob.public_url)

        db.reference(f"ai/pest-detection/{detection_id}").set({
            "user_id": user.uid,
            "image_urls": image_urls,
            "status": "processing"
        })

        return {"message": "Images uploaded successfully", "detection_id": detection_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/pest-detection/results/{analysisId}")
async def get_pest_detection_results(analysisId: str, user=Depends(get_current_user)):
    """
    Retrieve pest detection analysis results.
    """
    try:
        result_ref = db.reference(f"ai/pest-detection/{analysisId}").get()
        if not result_ref:
            raise HTTPException(status_code=404, detail="Analysis not found")
        if result_ref["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        return {"analysis": result_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai/model-feedback")
async def submit_model_feedback(request: ModelFeedbackRequest, user=Depends(get_current_user)):
    """
    Submit user feedback on AI predictions.
    """
    try:
        feedback_ref = db.reference(f"ai/feedback/{request.analysis_id}").push()
        feedback_ref.set({
            "user_id": user.uid,
            "feedback": request.feedback
        })
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/model-stats")
async def get_model_stats():
    """
    Retrieve performance statistics of AI models.
    """
    try:
        stats_ref = db.reference("ai/model-stats").get()
        return {"model_stats": stats_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision, speech_v1p1beta1 as speech
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Speech client
speech_client = speech.SpeechClient()

class AudioFeedbackRequest(BaseModel):
    audio_id: str
    feedback: str  # Positive, Negative, or Detailed Feedback

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.post("/api/ai/audio")
async def process_audio(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
    """
    Process audio input (speech-to-text conversion).
    """
    try:
        audio_id = str(uuid.uuid4())
        audio_urls = []

        for file in files:
            blob = storage.bucket().blob(f"audio/{audio_id}/{file.filename}")
            blob.upload_from_file(file.file)
            audio_urls.append(blob.public_url)

            # Google Cloud Speech-to-Text processing
            audio = speech.RecognitionAudio(uri=blob.public_url)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code="en-US"
            )
            operation = speech_client.long_running_recognize(config=config, audio=audio)

            db.reference(f"ai/audio/{audio_id}").set({
                "user_id": user.uid,
                "audio_urls": audio_urls,
                "status": "processing",
                "operation_name": operation.operation.name
            })

        return {"message": "Audio processing initiated", "audio_id": audio_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/audio/status/{audioId}")
async def get_audio_status(audioId: str, user=Depends(get_current_user)):
    """
    Retrieve the status of audio processing.
    """
    try:
        audio_ref = db.reference(f"ai/audio/{audioId}").get()
        if not audio_ref:
            raise HTTPException(status_code=404, detail="Audio analysis not found")
        if audio_ref["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        operation_name = audio_ref.get("operation_name")
        operation = speech_client.transport.operations_client.get_operation(operation_name)
        if operation.done:
            audio_ref["status"] = "completed"
            audio_ref["transcription"] = operation.response.results[0].alternatives[0].transcript
            db.reference(f"ai/audio/{audioId}").update(audio_ref)
        else:
            audio_ref["status"] = "processing"

        return {"status": audio_ref["status"], "transcription": audio_ref.get("transcription")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/ai/audio/feedback")
async def submit_audio_feedback(request: AudioFeedbackRequest, user=Depends(get_current_user)):
    """
    Collect feedback on audio processing.
    """
    try:
        feedback_ref = db.reference(f"ai/audio/feedback/{request.audio_id}").push()
        feedback_ref.set({
            "user_id": user.uid,
            "feedback": request.feedback
        })
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision, speech_v1p1beta1 as speech
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

class MarketForecastRequest(BaseModel):
    location: str
    commodity: str
    timeframe: str  # daily, weekly, monthly

class TrendAnalysisRequest(BaseModel):
    category: str
    start_date: str
    end_date: str

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.get("/api/ai/market-prices")
async def get_market_prices(location: str, commodity: str, user=Depends(get_current_user)):
    """
    Retrieve current market prices for a specific commodity at a given location.
    """
    try:
        prices_ref = db.reference(f"ai/market-prices/{location}/{commodity}").get()
        if not prices_ref:
            raise HTTPException(status_code=404, detail="Market prices not found")
        return {"prices": prices_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/demand-forecast")
async def get_demand_forecast(request: MarketForecastRequest, user=Depends(get_current_user)):
    """
    Retrieve demand forecast for a commodity based on location and timeframe.
    """
    try:
        forecast_ref = db.reference(f"ai/demand-forecast/{request.location}/{request.commodity}/{request.timeframe}").get()
        if not forecast_ref:
            raise HTTPException(status_code=404, detail="Demand forecast not found")
        return {"forecast": forecast_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/market-trends")
async def get_market_trends(request: TrendAnalysisRequest, user=Depends(get_current_user)):
    """
    Analyze and retrieve market trends for a category over a given date range.
    """
    try:
        trends_ref = db.reference(f"ai/market-trends/{request.category}").get()
        filtered_trends = [trend for trend in trends_ref if request.start_date <= trend["date"] <= request.end_date]
        return {"trends": filtered_trends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/market-prices/history")
async def get_historical_prices(location: str, commodity: str, start_date: str, end_date: str, user=Depends(get_current_user)):
    """
    Retrieve historical market prices for a commodity within a date range.
    """
    try:
        history_ref = db.reference(f"ai/market-prices-history/{location}/{commodity}").get()
        filtered_prices = [price for price in history_ref if start_date <= price["date"] <= end_date]
        return {"historical_prices": filtered_prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/demand-forecast/accuracy")
async def get_forecast_accuracy(location: str, commodity: str, user=Depends(get_current_user)):
    """
    Retrieve accuracy metrics for demand forecasting models.
    """
    try:
        accuracy_ref = db.reference(f"ai/demand-forecast-accuracy/{location}/{commodity}").get()
        if not accuracy_ref:
            raise HTTPException(status_code=404, detail="Forecast accuracy data not found")
        return {"accuracy_metrics": accuracy_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/market-trends/predictions")
async def get_trend_predictions(category: str, user=Depends(get_current_user)):
    """
    Retrieve predictive trend analysis for a specific category.
    """
    try:
        predictions_ref = db.reference(f"ai/market-trends-predictions/{category}").get()
        if not predictions_ref:
            raise HTTPException(status_code=404, detail="Trend predictions not found")
        return {"predictions": predictions_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision, speech_v1p1beta1 as speech
from config import db
import io
from typing import Optional, List
import uuid

router = APIRouter()

# Google Cloud Services
speech_client = speech.SpeechClient()

class MarketForecastRequest(BaseModel):
    location: str
    commodity: str
    timeframe: str  # daily, weekly, monthly

class TrendAnalysisRequest(BaseModel):
    category: str
    start_date: str
    end_date: str

class ResourceOptimizationRequest(BaseModel):
    resources: List[str]
    constraints: Optional[dict] = None
    optimization_goal: str  # e.g., minimize cost, maximize yield

class TransportRouteRequest(BaseModel):
    source: str
    destination: str
    stops: Optional[List[str]] = None
    optimize_for: str  # e.g., shortest, fastest, cost-effective

# Middleware for Firebase authentication
def get_current_user(user_id: str):
    try:
        user = auth.get_user(user_id)
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized user")

@router.get("/api/ai/resource-optimization")
async def get_resource_optimization(request: ResourceOptimizationRequest, user=Depends(get_current_user)):
    """
    Optimize resource allocation based on constraints and goals.
    """
    try:
        optimization_ref = db.reference("ai/resource-optimization").push()
        optimization_ref.set({
            "user_id": user.uid,
            "resources": request.resources,
            "constraints": request.constraints,
            "goal": request.optimization_goal,
            "status": "processing"
        })
        return {"message": "Resource optimization initiated", "optimization_id": optimization_ref.key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/transport-route")
async def get_transport_route(request: TransportRouteRequest, user=Depends(get_current_user)):
    """
    Get optimized transport routes for resource delivery or logistics.
    """
    try:
        route_ref = db.reference("ai/transport-routes").push()
        route_ref.set({
            "user_id": user.uid,
            "source": request.source,
            "destination": request.destination,
            "stops": request.stops,
            "optimize_for": request.optimize_for,
            "status": "processing"
        })
        return {"message": "Transport route optimization initiated", "route_id": route_ref.key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/resource-optimization/status/{optimizationId}")
async def get_resource_optimization_status(optimizationId: str, user=Depends(get_current_user)):
    """
    Get the status and results of resource optimization.
    """
    try:
        status_ref = db.reference(f"ai/resource-optimization/{optimizationId}").get()
        if not status_ref:
            raise HTTPException(status_code=404, detail="Optimization not found")
        if status_ref["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return {"optimization_status": status_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/transport-route/status/{routeId}")
async def get_transport_route_status(routeId: str, user=Depends(get_current_user)):
    """
    Get the status and details of a transport route optimization.
    """
    try:
        status_ref = db.reference(f"ai/transport-routes/{routeId}").get()
        if not status_ref:
            raise HTTPException(status_code=404, detail="Route optimization not found")
        if status_ref["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        return {"route_status": status_ref}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
