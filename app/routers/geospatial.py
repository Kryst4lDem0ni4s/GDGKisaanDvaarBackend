from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
import requests
import os
from firebase_admin import messaging
from app.models.model_types import Location, LocationAlertSubscription, MovementTracking
from app.routers.ai import get_current_user

router = APIRouter()

# Firestore client initialization
db = firestore.Client()

# Google Maps API key from environment variables
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Helper function to search nearby places using Google Places API
def search_nearby_places(location: Location, place_type: str):
    """
    Helper function to search nearby places (e.g., farms, cold storage, transport providers)
    using Google Places API.
    """
    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location.latitude},{location.longitude}&radius=5000&type={place_type}&key={google_maps_api_key}"
    response = requests.get(url)
    return response.json()

@router.get("/api/geospatial/maps")
async def get_geospatial_maps():
    """
    Retrieve geospatial data such as farms, cold storage, transport providers on a map.
    """
    try:
        # Query Firestore for geospatial data (e.g., farms, storage)
        geo_ref = db.collection("geospatial_data")
        geo_data = geo_ref.stream()

        geospatial_info = []
        for data in geo_data:
            geospatial_info.append(data.to_dict())

        return {"geospatial_info": geospatial_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/geospatial/search")
async def search_geospatial(location: Location, place_type: str):
    """
    Search for nearby places (e.g., farms, cold storage, transport providers) based on user's location.
    """
    try:
        # Validate place_type (ensure it is a valid type such as 'farm', 'cold_storage', etc.)
        valid_place_types = ['farm', 'cold_storage', 'transport', 'restaurant', 'hospital']
        if place_type not in valid_place_types:
            raise HTTPException(status_code=400, detail="Invalid place type.")

        # Call the Google Places API to search for nearby places
        search_results = search_nearby_places(location, place_type)

        return {"results": search_results["results"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/geospatial/alerts")
async def get_geospatial_alerts(location: Location, user=Depends(get_current_user)):
    """
    Retrieve location-based notifications or alerts for the user.
    """
    try:
        # Fetch alerts based on user preferences and location
        alerts_ref = db.collection("location_alerts").where("user_id", "==", user.uid)
        alerts = alerts_ref.stream()

        alert_data = []
        for alert in alerts:
            alert_info = alert.to_dict()
            # Filter alerts by proximity to user's location if needed
            # Placeholder: Just return all alerts for now
            alert_data.append(alert_info)

        return {"alerts": alert_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/geospatial/alerts/subscribe")
async def subscribe_to_alerts(subscription: LocationAlertSubscription, user=Depends(get_current_user)):
    """
    Subscribe users to location-based alerts (e.g., weather, market changes).
    """
    try:
        # Save subscription preferences to Firestore
        user_alert_ref = db.collection("user_alerts").document(user.uid)
        user_alert_ref.set({
            "latitude": subscription.latitude,
            "longitude": subscription.longitude,
            "radius": subscription.radius,
            "alert_type": subscription.alert_type
        })

        return {"message": "Successfully subscribed to location-based alerts."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/geospatial/alerts/preferences")
async def get_user_alert_preferences(user=Depends(get_current_user)):
    """
    Retrieve user preferences for location-based alerts.
    """
    try:
        # Fetch user alert preferences from Firestore
        user_alert_ref = db.collection("user_alerts").document(user.uid)
        user_alert = user_alert_ref.get()

        if not user_alert.exists:
            raise HTTPException(status_code=404, detail="No alert preferences found for user.")
        
        return {"preferences": user_alert.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/geospatial/movement")
async def track_goods_movement(movement: MovementTracking, user=Depends(get_current_user)):
    """
    Track the movement of goods through the supply chain.
    """
    try:
        # Record movement data in Firestore
        movement_ref = db.collection("goods_movement").document(movement.product_id)
        movement_ref.set({
            "user_id": user.uid,
            "origin": movement.origin,
            "destination": movement.destination,
            "timestamp": movement.timestamp,
            "status": movement.status
        })

        return {"message": "Goods movement tracked successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/geospatial/movement/analytics")
async def get_movement_analytics(user=Depends(get_current_user)):
    """
    Retrieve geospatial analytics on the movement of goods, such as average delivery times and route optimization.
    """
    try:
        # Fetch all movement data from Firestore
        movement_ref = db.collection("goods_movement")
        movements = movement_ref.stream()

        total_time = 0
        total_deliveries = 0

        for movement in movements:
            movement_data = movement.to_dict()
            # Calculate delivery time (using timestamps) and other analytics
            # Placeholder: Simulating average delivery time calculation
            if movement_data["status"] == "delivered":
                total_time += 1  # Placeholder for actual time calculation
                total_deliveries += 1

        # Calculate average delivery time
        avg_delivery_time = total_time / total_deliveries if total_deliveries else 0

        return {
            "average_delivery_time": avg_delivery_time,
            "total_deliveries": total_deliveries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

