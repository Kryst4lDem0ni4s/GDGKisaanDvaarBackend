from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
from app.models.model_types import AcknowledgeAlert, SensorConfig, SensorData, SensorThresholds
from app.controllers.auth import UserAuth

router = APIRouter()

# Firestore initialization
db = firestore.Client()
sensors_ref = db.collection("sensors_data")

@router.post("/api/sensors/data")
async def ingest_sensor_data(data: SensorData, user=Depends(UserAuth.get_current_user)):
    """
    Ingest sensor readings (e.g., temperature, humidity, soil moisture) into the system.
    """
    try:
        sensor_id = data.sensor_id
        sensor_data = {
            "user_id": user.uid,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "soil_moisture": data.soil_moisture,
            "timestamp": data.timestamp
        }
        
        # Save data to Firestore
        sensors_ref.document(sensor_id).collection("readings").add(sensor_data)
        
        return {"message": "Sensor data ingested successfully", "sensor_id": sensor_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/sensors/data/{sensorId}")
async def get_sensor_data(sensorId: str, user=Depends(UserAuth.get_current_user)):
    """
    Retrieve sensor readings for a specific sensor by its ID.
    """
    try:
        # Fetch sensor data from Firestore
        readings_ref = sensors_ref.document(sensorId).collection("readings")
        readings = readings_ref.stream()
        
        sensor_data = []
        for reading in readings:
            sensor_data.append(reading.to_dict())
        
        if not sensor_data:
            raise HTTPException(status_code=404, detail="No data found for the sensor.")
        
        return {"sensor_id": sensorId, "data": sensor_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/sensors/alerts")
async def get_sensor_alerts(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve all sensor alerts (e.g., threshold breaches) for a user.
    """
    try:
        # Fetch sensor alerts for the user
        alerts_ref = db.collection("sensor_alerts").where("user_id", "==", user.uid)
        alerts = alerts_ref.stream()

        alert_data = []
        for alert in alerts:
            alert_data.append(alert.to_dict())

        return {"alerts": alert_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/sensors/{sensorId}/config")
async def update_sensor_config(sensorId: str, config: SensorConfig, user=Depends(UserAuth.get_current_user)):
    """
    Update the configuration for a specific sensor (e.g., thresholds).
    """
    try:
        # Update sensor configuration in Firestore
        config_ref = sensors_ref.document(sensorId).collection("config").document("settings")
        config_ref.set({
            "threshold_temperature": config.threshold_temperature,
            "threshold_humidity": config.threshold_humidity,
            "threshold_soil_moisture": config.threshold_soil_moisture,
            "user_id": user.uid
        })

        return {"message": "Sensor configuration updated successfully", "sensor_id": sensorId}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/sensors/{sensorId}/status")
async def get_sensor_status(sensorId: str, user=Depends(UserAuth.get_current_user)):
    """
    Retrieve the status of a specific sensor (e.g., online/offline, last connected).
    """
    try:
        # Fetch sensor status from Firestore
        status_ref = sensors_ref.document(sensorId).collection("status").document("current_status")
        status_data = status_ref.get()
        
        if not status_data.exists:
            raise HTTPException(status_code=404, detail="Sensor status not found")
        
        return {"sensor_id": sensorId, "status": status_data.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/sensors/thresholds")
async def set_sensor_thresholds(thresholds: SensorThresholds, user=Depends(UserAuth.get_current_user)):
    """
    Set global or per-sensor thresholds for various readings (temperature, humidity, etc.).
    If sensor_id is provided, thresholds are set per sensor.
    """
    try:
        # Determine whether to set global or per-sensor thresholds
        if thresholds.sensor_id:
            # Set per-sensor thresholds
            sensor_config_ref = sensors_ref.document(thresholds.sensor_id).collection("config").document("thresholds")
            sensor_config_ref.set({
                "temperature_threshold": thresholds.temperature_threshold,
                "humidity_threshold": thresholds.humidity_threshold,
                "soil_moisture_threshold": thresholds.soil_moisture_threshold,
                "user_id": user.uid
            })
            return {"message": "Per-sensor thresholds set successfully", "sensor_id": thresholds.sensor_id}

        else:
            # Set global thresholds
            global_config_ref = db.collection("sensor_global_config").document("thresholds")
            global_config_ref.set({
                "temperature_threshold": thresholds.temperature_threshold,
                "humidity_threshold": thresholds.humidity_threshold,
                "soil_moisture_threshold": thresholds.soil_moisture_threshold,
                "user_id": user.uid
            })
            return {"message": "Global thresholds set successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/sensors/diagnostics")
async def get_sensors_diagnostics(user=Depends(UserAuth.get_current_user)):
    """
    Retrieve aggregated diagnostics for multiple sensors (e.g., average temperature, overall sensor status).
    """
    try:
        # Retrieve sensor data from Firestore
        all_sensors_ref = sensors_ref.stream()

        total_temperature = 0
        total_humidity = 0
        total_soil_moisture = 0
        active_sensors = 0
        sensor_count = 0

        for sensor in all_sensors_ref:
            sensor_data = sensor.to_dict()
            readings_ref = sensors_ref.document(sensor.id).collection("readings").stream()

            for reading in readings_ref:
                data = reading.to_dict()
                total_temperature += data.get("temperature", 0)
                total_humidity += data.get("humidity", 0)
                total_soil_moisture += data.get("soil_moisture", 0)
                sensor_count += 1

                # Check if the sensor is active
                if data.get("status", "inactive") == "active":
                    active_sensors += 1

        if sensor_count == 0:
            raise HTTPException(status_code=404, detail="No sensor data found.")

        avg_temperature = total_temperature / sensor_count
        avg_humidity = total_humidity / sensor_count
        avg_soil_moisture = total_soil_moisture / sensor_count

        return {
            "average_temperature": avg_temperature,
            "average_humidity": avg_humidity,
            "average_soil_moisture": avg_soil_moisture,
            "active_sensors": active_sensors,
            "total_sensors": sensor_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/sensors/alerts/acknowledge")
async def acknowledge_alert(alert_data: AcknowledgeAlert, user=Depends(UserAuth.get_current_user)):
    """
    Allow users to acknowledge alerts, marking them as handled or reviewed.
    """
    try:
        alert_ref = db.collection("sensor_alerts").document(alert_data.alert_id)
        alert_doc = alert_ref.get()

        if not alert_doc.exists:
            raise HTTPException(status_code=404, detail="Alert not found")

        alert_info = alert_doc.to_dict()

        # Ensure the user has the right to acknowledge the alert
        if alert_info["user_id"] != user.uid:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        # Update the alert as acknowledged
        alert_ref.update({
            "acknowledged": alert_data.acknowledged,
            "acknowledged_timestamp": firestore.SERVER_TIMESTAMP
        })

        return {"message": "Alert acknowledged successfully", "alert_id": alert_data.alert_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
