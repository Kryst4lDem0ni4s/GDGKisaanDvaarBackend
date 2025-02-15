from firebase_admin import credentials, initialize_app, auth
from fastapi import UploadFile, File
import firebase_admin._user_identifier
import firebase_admin.auth
import firebase_admin.instance_id
import app.models.model_types as modelType
from app.helpers import ai_helpers
from app.utils import utils
from typing import Dict, Any
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
from dotenv import CREDENTIALS_FILE
import smtplib  # For sending reset emails (Note: You might need to install this library)
from app.controllers.auth import UserAuth, AuthService
  


# Initialize the Firebase Admin SDK with the downloaded service account key
router = APIRouter()

cred = credentials.Certificate(CREDENTIALS_FILE)
initialize_app(cred)

auth_service = auth
db_service = db

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
        
        # Verify phone number or email in Firebase console
        phone_number = verification_request.phone_number
        email = verification_request.email

        # Check Email validation
        if not ai_helpers._validate_email(email):
            raise ValueError("Please check your email address. Wrong format.")
            
        # Check Phone number validation  
        if not ai_helpers._validate_phone(phone_number):
            raise ValueError("Please check your phone number. Invalid or incorrect format.")

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
            status_code=status.HTTP_400 status_code,
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
        
async def forgot_password(email: str):
    """Get a reset password link for an email address"""
    try:
        user = auth.get_user_by_email(email=email)
        if user is None:
            # If not found, send a confirmation to sign in instead
            await auth.send_confirmation_email(email)
            return {"message": "Please confirm your account details or login"}
        
        return {
            "message": "Reset link sent to your email",
            "reset_url": f"https://localhost{user.uid}/password/reset?email={email}"
        }
    except Exception as e:
        db_instance = db_service()
        await db_instance.remove(f"users:{user.uid}")  # Clean up if error occurs
        raise HTTPException(
            status_code=status.HTTP_403,
            detail=str(e)
        )

async def update_password(current_user.uid, new_password):
    """Update the user's password after authentication"""
    try:
        await auth.authenticate_user(email=current_user.email, password=new_password)
        return {"message": "Password updated successfully"}
    except Exception as e:
        db_instance = db_service()
        await db_instance.remove(f"users:{current_user.uid}")  # Clean up if error occurs
        raise HTTPException(
            status_code=status.HTTP_500,
            detail=str(e)
        )
           
# @router.post("/sign-up")
# async def sign_up_user(sign_up_request: modelType.SignUpRequest):
#     try:
#         # Create a new user
#         user = auth.create_user(
#             email=sign_up_request.email,
#             password=sign_up_request.password,
#             firstname=sign_up_request.firstname,
#             lastname=sign_up_request.lastname,
#             username=sign_up_request.username,
#             password=sign_up_request.password,
#             phonenumber=sign_up_request.phonenumber
#         )
#         print('Successfully created new user:', user)
#         return user
    
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# Example usage
#new_user = sign_up_user("user@example.com", "strongpassword123")

@router.post("/api/auth/forgot-password")
async def forget_password(email: EmailRequest):
    try:
        user = await UserAuth.get_user(email.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email")

        # Simulate getting reset token (Implement actual Firebase authentication for real app)
        reset_token = generate_reset_token(user.uid)
        
        send_reset_email(reset_token)
        return {"reset_token": reset_token}
    except Exception as e:
        db_instance = db_service()
        await db_instance.remove(f"users:{user.uid}")  # Cleanup if error occurs
        raise HTTPException(status_code=status.HTTP_401, detail=str(e))

@router.put("/api/auth/update-password")
async def update_password_endpoint(user_id: str):
    try:
        data = {"uid": user_id}
        response = await AuthService.update_password(**data)
        return {"message": "Password updated"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500, detail=str(e))

@router.post("/build-profile")
async def build_new_profile(build_profile_request: modelType.ProfileData):
    try:
        # Create a new user profile
        user_profile = auth.UserInfo(
            occupation = build_profile_request.occupation,
            address = build_profile_request.address,
            state = build_profile_request.state,
            city = build_profile_request.city,
            pincode = build_profile_request.pincode,
            profile_image = build_profile_request.profile_image,
            description = build_profile_request.description
        )
        
        print('Successfully created new user profile:', user_profile)
        user = auth.get_user

        
        return user_profile
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
    
    
def get_active_user_session_info():
    """User authentication per session is possible from flutter side, TODO"""
    # Validate user's occupation (ensure they are the owner or an admin)
    # user = await User.get_current_user()
    # if user.occupation not in ["owner", "admin"]:
    #     raise HTTPException(status_code=403, detail="Only owners or admins can update service listings.")
    # https://firebase.google.com/docs/auth/android/manage-users
    
    