from fastapi import Depends, HTTPException, status, FastAPI
import smtplib  # For sending reset emails (Note: You might need to install this library)
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from firebase_admin import db
from firebase_admin import auth
import firebase_admin
from ..models.model_types import ProfileData
import google.auth.transport.requests
from google.oauth2 import service_account
import os

scopes = os.getenv("SCOPES")

app = FastAPI()

class UserAuth:
        
    @staticmethod
    async def get_user(email: str):
        """Retrieve user UID from Firebase Auth."""
        try:
            user = auth.get_user_by_email(email)
            return user.uid  # Return the actual UID
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        
    @staticmethod
    async def get_current_user(email: str):
        """Fetch user profile from Firebase."""
        try:
            user = auth.get_user_by_email(email)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url
            }
        except Exception as e:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    def get_current_user(token: str = Depends(auth.verify_id_token)):
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    @staticmethod
    def get_admin_user(token: str = Depends(auth.verify_id_token)):
        """
        Verifies if the user is an admin by checking the Firebase custom claims.
        """
        if token.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Access forbidden: Admins only.")
        return token
    
    @staticmethod
    def _get_access_token():
        """Retrieve a valid access token that can be used to authorize requests.

        :return: Access token.
        """
        credentials = service_account.Credentials.from_service_account_file(
            'service-account.json', scopes=scopes)
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

class AuthService:
    
    @staticmethod
    def get_db_reference(user_id: str, path: str = "settings"):
        return db.reference(f"users/{user_id}/{path}")  
    
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
    async def update_password(email: str, new_password: str):
        """Update user password in Firebase."""
        try:
            user = auth.get_user_by_email(email)
            auth.update_user(user.uid, password=new_password)
            return {"message": "Password updated successfully"}
        except Exception as e:
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
            db_instance = db()
            await db_instance.remove(f"users:{user.uid}")  # Clean up if error occurs
            raise HTTPException(
                status_code=status.HTTP_403,
                detail=str(e)
            )
    @staticmethod
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
                "uid": user_info.uid,
                "email": user_info.email,
                "display_name": user_info.display_name,
                "photo_url": user_info.photo_url,
                # Add other relevant information as needed
            }
        
        except Exception as e:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
