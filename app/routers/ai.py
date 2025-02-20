from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from firebase_admin import firestore, auth, storage
from google.cloud import vision
from config import db
import io
from typing import Optional, List
import uuid
import os
import logging
from flask import Flask, request, jsonify
from google.cloud import vision, storage, firestore
import requests
import binascii

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

def upload_to_storage(file, filename):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_file(file)
    return blob.public_url

def analyze_image(image_content):
    image = vision.Image(content=image_content)
    response = vision_client.label_detection(image=image)
    if response.error.message:
        raise Exception(response.error.message)
    return [label.description for label in response.label_annotations]

# Remote Sensing Endpoints
@router.post('/api/ai/remote-sensing', methods=['POST'])
def trigger_remote_sensing():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image_file = request.files['image']
    image_content = image_file.read()
    
    # Generate unique task ID
    task_id = binascii.hexlify(os.urandom(8)).decode('utf-8')
    
    # Upload to GCS
    filename = f"remote-sensing/{task_id}.jpg"
    image_url = upload_to_storage(image_file, filename)
    
    # Analyze with Vision API
    try:
        labels = analyze_image(image_content)
        result = {"image_url": image_url, "labels": labels, "status": "completed"}
    except Exception as e:
        result = {"image_url": image_url, "error": str(e), "status": "failed"}
    
    # Store in Firestore
    db.collection('remote_sensing_results').document(task_id).set(result)
    return jsonify({"taskId": task_id}), 202

@router.get('/api/ai/remote-sensing/results/<task_id>')
def get_remote_sensing_results(task_id):
    doc_ref = db.collection('remote_sensing_results').document(task_id).get()
    if not doc_ref.exists:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(doc_ref.to_dict()), 200

# Weather Endpoint
@router.get('/api/ai/weather')
def get_weather():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if not lat or not lon:
        return jsonify({"error": "Latitude and longitude required"}), 400
    
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Weather API error"}), 500
    return jsonify(response.json()), 200

# Crop Monitoring Endpoints
@router.post('/api/ai/crop-monitoring')
def trigger_crop_monitoring():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image_file = request.files['image']
    image_content = image_file.read()
    
    task_id = binascii.hexlify(os.urandom(8)).decode('utf-8')
    filename = f"crop-monitoring/{task_id}.jpg"
    image_url = upload_to_storage(image_file, filename)
    
    try:
        labels = analyze_image(image_content)
        health_status = "Healthy" if "Healthy" in labels else "Diseased"
        result = {"image_url": image_url, "labels": labels, "status": health_status}
    except Exception as e:
        result = {"image_url": image_url, "error": str(e), "status": "failed"}
    
    db.collection('crop_monitoring_results').document(task_id).set(result)
    return jsonify({"taskId": task_id}), 202

@router.get('/api/ai/crop-monitoring/results/<task_id>')
def get_crop_monitoring_results(task_id):
    doc_ref = db.collection('crop_monitoring_results').document(task_id).get()
    if not doc_ref.exists:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(doc_ref.to_dict()), 200

# Pest Detection Endpoints
@router.post('/api/ai/pest-detection')
def trigger_pest_detection():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image_file = request.files['image']
    image_content = image_file.read()
    
    task_id = binascii.hexlify(os.urandom(8)).decode('utf-8')
    filename = f"pest-detection/{task_id}.jpg"
    image_url = upload_to_storage(image_file, filename)
    
    try:
        labels = analyze_image(image_content)
        pest_detected = any(label in ["insect", "bug", "pest"] for label in labels)
        result = {"image_url": image_url, "labels": labels, "pest_detected": pest_detected}
    except Exception as e:
        result = {"image_url": image_url, "error": str(e), "status": "failed"}
    
    db.collection('pest_detection_results').document(task_id).set(result)
    return jsonify({"taskId": task_id}), 202

@router.get('/api/ai/pest-detection/results/<task_id>')
def get_pest_detection_results(task_id):
    doc_ref = db.collection('pest_detection_results').document(task_id).get()
    if not doc_ref.exists:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(doc_ref.to_dict()), 200

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from google.cloud import storage
from google.cloud import firestore
import uuid
import os

router = APIRouter()

# Initialize GCP clients
storage_client = storage.Client()
db = firestore.Client()

# Define Firebase database collection
ai_ref = db.collection("ai")

@router.post("/api/ai/remote-sensing")
async def trigger_remote_sensing_analysis(files: list[UploadFile] = File(...), user=Depends(get_current_user)):
    """
    Trigger remote sensing analysis by uploading geospatial data or images for processing.
    """
    try:
        task_id = str(uuid.uuid4())
        file_urls = []
        
        # Upload files to Google Cloud Storage
        for file in files:
            blob = storage_client.bucket("your-bucket-name").blob(f"remote-sensing/{task_id}/{file.filename}")
            blob.upload_from_file(file.file)
            file_urls.append(blob.public_url)

        # Trigger remote sensing processing (use GCP AI/ML tools like Earth Engine or others)
        # This could be a separate Cloud Function or an external service
        processing_status = "Processing started"  # Simplified processing initiation

        # Save task info to Firestore DB
        ai_ref.document(task_id).set({
            "user_id": user.uid,
            "status": "processing",
            "file_urls": file_urls,
            "processing_status": processing_status
        })

        return {"message": "Remote sensing analysis initiated", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/ai/remote-sensing/results/{taskId}")
async def get_remote_sensing_results(taskId: str, user=Depends(get_current_user)):
    """
    Retrieve the result of remote sensing analysis.
    """
    try:
        task_ref = ai_ref.document(taskId).get()
        if not task_ref.exists:
            raise HTTPException(status_code=404, detail="Remote sensing analysis not found")
        
        task_data = task_ref.to_dict()

        # Check if user is authorized to access the task data
        if task_data["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Check if processing is done
        if task_data["status"] == "completed":
            return {"status": task_data["status"], "file_urls": task_data["file_urls"]}
        else:
            return {"status": task_data["status"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import requests

@router.get("/api/ai/weather")
async def get_weather_data(location: str):
    """
    Retrieve weather data for a given location.
    """
    try:
        # Use a weather API (e.g., OpenWeather, GCP Weather API, etc.)
        weather_api_key = os.getenv("WEATHER_API_KEY")
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}"
        response = requests.get(weather_url)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch weather data")

        weather_data = response.json()
        return {
            "location": location,
            "temperature": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "description": weather_data["weather"][0]["description"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
from datetime import datetime

router = APIRouter()

# Initialize Firestore client
db = firestore.Client()

# Reference to the AI requests collection
ai_ref = db.collection("ai_requests")

@router.get("/api/ai/history")
async def get_ai_history(user=Depends(get_current_user)):
    """
    Retrieve history of AI analysis requests for the current user.
    """
    try:
        # Fetch all AI request history
        query = ai_ref.where("user_id", "==", user.uid).order_by("timestamp", direction=firestore.Query.DESCENDING)
        results = query.stream()

        history = []
        for doc in results:
            history.append(doc.to_dict())

        if not history:
            return {"message": "No AI analysis history found."}

        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
from datetime import datetime
import uuid

router = APIRouter()

# Firestore initialization
db = firestore.Client()
ai_ref = db.collection("ai_processing_queue")

@router.post("/api/ai/queue")
async def add_to_ai_queue(file_url: str, analysis_type: str, user=Depends(get_current_user)):
    """
    Add a request to an AI processing queue.
    """
    try:
        task_id = str(uuid.uuid4())
        queued_status = "queued"  # The job is in the queue waiting for processing

        # Store the task details in the Firestore queue collection
        ai_ref.document(task_id).set({
            "user_id": user.uid,
            "file_url": file_url,
            "analysis_type": analysis_type,
            "status": queued_status,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return {"message": "AI analysis job added to the queue", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends
import uuid
from google.cloud import firestore
from datetime import datetime

router = APIRouter()

# Firestore client
db = firestore.Client()
ai_ref = db.collection("ai_scheduled_tasks")

@router.post("/api/ai/schedule")
async def schedule_ai_task(task_type: str, schedule_time: str, user=Depends(get_current_user)):
    """
    Schedule periodic AI tasks.
    """
    try:
        task_id = str(uuid.uuid4())

        # Validate the schedule time format (assuming it is in ISO format)
        try:
            scheduled_time = datetime.fromisoformat(schedule_time)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format. Use ISO format.")

        # Add the task details to Firestore for scheduling
        ai_ref.document(task_id).set({
            "user_id": user.uid,
            "task_type": task_type,
            "scheduled_time": scheduled_time,
            "status": "scheduled",
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        # Logic for actual scheduling (e.g., using Cloud Scheduler to trigger an action at the specified time)
        # This step will require setting up Google Cloud Scheduler or a similar service to trigger periodic tasks

        return {"message": "AI task scheduled successfully", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from google.cloud import storage, vision
from google.cloud import firestore
import uuid

router = APIRouter()

# Initialize GCP clients
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
db = firestore.Client()

# Firestore reference for storing AI job metadata
ai_ref = db.collection("ai_requests")

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from google.cloud import storage, vision
from google.cloud import firestore
import uuid

router = APIRouter()

# Initialize GCP clients
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
db = firestore.Client()

# Firestore reference for storing AI job metadata
ai_ref = db.collection("ai_requests")

@router.post("/api/ai/process")
async def process_ai_job(file: UploadFile = File(...), user=Depends(get_current_user)):
    """
    Process a new AI job immediately (e.g., image analysis via Google Cloud Vision).
    """
    try:
        task_id = str(uuid.uuid4())
        
        # Upload the image to Google Cloud Storage
        blob = storage_client.bucket("your-bucket-name").blob(f"ai/jobs/{task_id}/{file.filename}")
        blob.upload_from_file(file.file)
        file_url = blob.public_url
        
        # Perform image analysis using Google Cloud Vision API
        image = vision.Image(source=vision.ImageSource(image_uri=file_url))
        response = vision_client.label_detection(image=image)

        # Save job metadata to Firestore
        ai_ref.document(task_id).set({
            "user_id": user.uid,
            "file_url": file_url,
            "status": "processing",
            "labels": [label.description for label in response.label_annotations],
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        
        return {"message": "AI job processing started", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

   
@router.get("/api/ai/results/{taskId}")
async def get_ai_results(taskId: str, user=Depends(get_current_user)):
    """
    Retrieve the results of an AI task once completed.
    """
    try:
        # Fetch the AI task results from Firestore
        task_ref = ai_ref.document(taskId).get()
        
        if not task_ref.exists:
            raise HTTPException(status_code=404, detail="AI task not found")
        
        task_data = task_ref.to_dict()

        # Check if the user is authorized to view the results
        if task_data["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Return the AI task results
        return {
            "task_id": taskId,
            "status": task_data["status"],
            "labels": task_data.get("labels", []),
            "file_url": task_data["file_url"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/ai/model-stats")
async def get_ai_model_stats():
    """
    Retrieve AI model performance statistics or metrics (e.g., accuracy, loss, etc.).
    """
    try:
        # For simplicity, we'll simulate model stats retrieval.
        # In a real-world case, you'd retrieve this from Vertex AI or another ML model tracking system.
        model_stats = {
            "accuracy": 0.85,  # Placeholder for model accuracy
            "loss": 0.15,  # Placeholder for model loss
            "timestamp": str(datetime.utcnow())
        }

        return {"model_stats": model_stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class AIFeedback(BaseModel):
    task_id: str
    feedback: str  # User feedback about AI predictions
    rating: int  # Rating of the AI prediction (e.g., 1-5)

@router.post("/api/ai/feedback")
async def submit_ai_feedback(feedback_data: AIFeedback, user=Depends(get_current_user)):
    """
    Submit feedback for AI predictions to improve model accuracy.
    """
    try:
        # Fetch the AI task from Firestore
        task_ref = ai_ref.document(feedback_data.task_id).get()
        
        if not task_ref.exists:
            raise HTTPException(status_code=404, detail="AI task not found")
        
        task_data = task_ref.to_dict()

        # Check if the user is authorized to provide feedback
        if task_data["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")
        
        # Save the feedback data to Firestore
        feedback_ref = ai_ref.document(feedback_data.task_id).collection("feedbacks").add({
            "feedback": feedback_data.feedback,
            "rating": feedback_data.rating,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        return {"message": "Feedback submitted successfully", "feedback_id": feedback_ref.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
