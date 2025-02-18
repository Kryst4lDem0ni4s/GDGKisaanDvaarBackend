from firebase_admin import credentials, initialize_app, auth
from fastapi import UploadFile, File, requests
import firebase_admin._user_identifier
import firebase_admin.auth
import firebase_admin.instance_id
import app.models.model_types as modelType
from app.helpers import ai_helpers
from app.utils import utils
from typing import Dict, Any, List
from pydantic import EmailStr, Field
from fastapi import HTTPException, status
from app.helpers.ai_helpers import EmailAddress, PhoneNumber
from app.models.model_types import UserInDB, UserCreate
from app.helpers import ai_helpers
from app.utils import utils
from firebase_admin import db
from app.models.model_types import UserInDB, UserCreate
import firebase_admin
from fastapi import APIRouter, Depends
import firebase_admin
from fastapi import APIRouter, HTTPException
import dotenv 
import smtplib  # For sending reset emails (Note: You might need to install this library)
from app.controllers.auth import UserAuth, AuthService
from pydantic import BaseModel



# Initialize the Firebase Admin SDK with the downloaded service account key
router = APIRouter()

cred = credentials.Certificate(dotenv.CREDENTIALS_FILE)
FCM_SERVER_KEY = "YOUR_FCM_SERVER_KEY"
FCM_URL = "https://fcm.googleapis.com/fcm/send"

initialize_app(cred)

auth_service = auth
db_service = db

class EmailRequest(BaseModel):
    email: str
    
class UpdatePasswordRequest(BaseModel):
    uid: str
    new_password: str
    
    
@router.post("/sync")
async def sync_data(data: List[Dict[str, Any]]):
    """
    API to sync offline data when the user comes online.
    """
    try:
        ref = db.reference("synced_data")
        for item in data:
            item_id = item.get("id")
            ref.child(item_id).set(item)
        return {"status": "success", "message": "Data synced successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sync")
async def fetch_updates():
    """
    Fetch updates for offline users when they come online.
    """
    try:
        ref = db.reference("synced_data")
        updates = ref.get()
        return {"updates": updates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/send-notification")
async def send_notification(device_token: str, title: str, body: str):
    """
    Send push notification to a device using Firebase Cloud Messaging.
    """
    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": device_token,
        "notification": {
            "title": title,
            "body": body
        }
    }
    response = requests.post(FCM_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return {"status": "success", "message": "Notification sent"}
    else:
        raise HTTPException(status_code=500, detail=response.text)

@router.post("/register")
async def register(
    login_request: modelType.LoginRequest,
    verification_request: modelType.SignUpRequest
):
    try:
        # Verify either email or phone number during registration
        user = await auth_service.get_user_by_email(
            email=verification_request.email
        )
        if user is not None:
            db_instance = db_service()
            await db_instance.remove(f"users/{user.uid}")
            raise ValueError("User already registered")

        # Verify password
        if verification_request.password == login_request.password:
            db_instance = db_service()
            await db_instance.remove(f"users/{user.uid}")
            return user
        
        # # Verify phone number or email in Firebase console
        # phone_number = verification_request.phone_number
        # email = verification_request.email

        # # Check Email validation
        # if not ai_helpers._validate_email(email):
        #     raise ValueError("Please check your email address. Wrong format.")
            
        # # Check Phone number validation  
        # if not ai_helpers._validate_phone(phone_number):
        #     raise ValueError("Please check your phone number. Invalid or incorrect format.")

        # Create new user without verifying existing registration
        user = await auth_service.create_user(
            email=verification_request.email,
            password=verification_request.password,
            firstname=verification_request.firstname,
            lastname=verification_request.lastname,
            username=verification_request.username,
            password=verification_request.password,
            phonenumber=verification_request.phone_number
        )

        return {"user": user}
    
    except Exception as e:
        db_instance = db_service()
        await db_instance.remove(f"users:{user.uid}")  # Clean up if error occurs
        raise HTTPException(
            status_code=status.HTTP_400,
            detail=str(e),
        )
        

@router.post("/login")
async def login(login_request: modelType.LoginRequest):
    try:
        user = await auth_service.get_user_by_email(
            email=login_request.email,
            password=login_request.password
        )
        
        if user:
            return {"user": user}
            
        raise HTTPException(status_code=status.HTTP_401, detail="Invalid credentials")
    
    except Exception as e:
        db_instance = db_service()
        await db_instance.remove(f"users:{user.uid}")  # Clean up if error occurs
        raise HTTPException(
            status_code=status.HTTP_403,
            detail=str(e)
        )
        
@router.post("/logout")
async def logout(email: str):
    try:
        user = await auth_service.authenticate_user(
            email=email
        )
        
        if user is not None:
            db_instance = db_service()
            await db_instance.remove(f"users:{user.uid}")
            return {"status": "success"}
            
        raise HTTPException(status_code=status.HTTP_401, detail="User not found")

    except Exception as e:
        db_instance = db_service()
        await db_instance.remove(f"users:{user.uid}")  # Clean up if error occurs
        raise HTTPException(
            status_code=status.HTTP_500,
            detail=str(e)
        )
           
@router.post("/api/auth/forgot-password")
async def forget_password(email: EmailRequest):
    try:
        user = await UserAuth.get_user(email.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email")

        # Generate a password reset link using Firebase Authentication
        reset_token = AuthService.generate_reset_token(email.email)
        AuthService.send_reset_email(reset_token, email.email)
        return {"reset_token": reset_token}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/api/auth/update-password")
async def update_password(request: UpdatePasswordRequest):
    try:
        user = await UserAuth.get_user(request.uid)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        await AuthService.update_password(request.uid, request.new_password)
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/build-profile")
async def build_new_profile(build_profile_request: modelType.ProfileData):
    try:
        # Create a new user profile
        user_profile = auth.UserInfo(
            email = build_profile_request.email,
            first_name = build_profile_request.first_name,
            last_name = build_profile_request.last_name,
            gender = build_profile_request.gender,
            age = build_profile_request.age,
            phone_number = build_profile_request.phone_number,
            occupation = build_profile_request.occupation,
            address = build_profile_request.address,
            state = build_profile_request.state,
            city = build_profile_request.city,
            pincode = build_profile_request.pincode,
            profile_image = build_profile_request.profile_image,
            description = build_profile_request.description
        )
        
        print('Successfully created new user profile:', user_profile)

        # user = auth.get_user

        return user_profile
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
    
    
@router.get("/active-user-session")
async def active_user_session():
    return AuthService.get_active_user_session_info()
    
    