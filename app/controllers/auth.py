# from fastapi import UploadFile, File
# import app.models.model_types as modelType
# from app.helpers import ai_helpers
# from app.utils import utils
# import json
# from typing import *
# import os
# import firebase_admin
# from firebase_admin import credentials, auth
# from fastapi import HTTPException

# # Initialize the Firebase Admin SDK with the downloaded service account key
# cred = credentials.Certificate("D:/DdriveCodes/SIH/app/helpers/kisaandvaar-firebase-adminsdk-t83e9-f6d6bf9844.json")
# firebase_admin.initialize_app(cred)


# # async def sign_up_user(sign_up_request: modelType.SignUpRequest):
# #     try:
# #         # Create a new user
# #         user = auth.create_user(
# #             email=sign_up_request.email,
# #             password=sign_up_request.password,
# #         )
# #         print('Successfully created new user:', user.uid)
# #         return user
# #     except Exception as e:
# #         print(f"Error creating user: {e}")
# #         return None

# async def sign_up_user(sign_up_request: modelType.SignUpRequest):
#     try:
#         # Create a new user
#         user = auth.create_user(
#             email=sign_up_request.email,
#             password=sign_up_request.password,
#             display_name=sign_up_request.username,
#             phone_number=sign_up_request.phonenumber
#         )
#         print('Successfully created new user:', user)
#         return user
    
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# async def login(login_request: modelType.LoginRequest):
#     try:
#         user = await auth.get_user_by_email(
#             email=login_request.email
#             )

#         return user
    
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Invalid email or password")

# # Example usage
# #new_user = sign_up_user("user@example.com", "strongpassword123")

from fastapi import HTTPException, status, FastAPI
import smtplib  # For sending reset emails (Note: You might need to install this library)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase_admin import db as db_service
from firebase_admin import auth
from models.model_types import ProfileData



app = FastAPI()

class UserAuth:

    @staticmethod
    async def get_user(email: str):
        try:
            db_instance = db_service()
            user = await db_instance.remove(f"users/{email}")
            return user
        except Exception as e:
            db_instance = db_service()
            await db_instance.remove(f"users:{user.uid}")  # Cleanup if error occurs
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    @staticmethod
    async def get_current_user():
        """Placeholder function to get the current user."""
        if ProfileData is not None:
            return ProfileData
        else:
            return ProfileData(uid="dummy_uid", email="dummy@example.com")


class AuthService:
    
    @staticmethod
    def generate_reset_token(email: str):
        try:
            # Generate a password reset link using Firebase Authentication
            auth.generate_password_reset_link(email)
            return {"reset_token": "https://example.com/reset?token=..."}  # Replace with actual token URL
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def send_reset_email(reset_token: str, email: str):
        # Implement email sending logic here. This might involve using SMTP or a service like SendGrid/Mailgun.
        sender_email = "your_email@example.com"  # Replace with your actual email address
        receiver_email = email
        password = "your_email_password"  # Replace with your actual email password
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = "Password Reset Request"
        body = f"Click the link to reset your password: {reset_token}"
        message.attach(MIMEText(body, 'plain'))
        
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, password)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def update_password(user_id: str, new_password: str):
        try:
            db_instance = db_service()
            user = await db_instance.remove(f"users/{user_id}")
            if user:  # Update password in Firebase
                auth.update_user(uid=user.uid, password=new_password)
            return {"message": "Password updated successfully"}
        except Exception as e:
            db_instance = db_service()
            await db_instance.remove(f"users:{user_id}")  # Cleanup if error occurs
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @staticmethod
    async def forgot_password(email: str):
        """Get a reset password link for an email address"""
        try:
            user = auth.get_user_by_email(email=email)
            if user is None:
                # If not found, send a confirmation to sign in instead
                await auth.generate_email_verification_link(email)
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

async def get_active_user_session_info():
    """Get information about the active user session."""
    try:
        # Validate user's occupation (ensure they are the owner or an admin)
        user = await UserAuth.get_current_user() 
        if user.role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Only owners or admins can update service listings.")
        
        # Get the active user session info from Firebase Authentication
        user_info = auth.get_user(user.uid)  # Assuming 'user.uid' is the user identifier
        
        return {
            # "uid": user_info.uid,
            "email": user_info.email,
            "display_name": user_info.display_name,
            "photo_url": user_info.photo_url,
            # Add other relevant information as needed
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
