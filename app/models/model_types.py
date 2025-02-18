from fastapi import UploadFile
from pydantic import BaseModel, root_validator
from pydantic import BaseModel, EmailStr, constr, Field
from typing import *

class UserSettings(BaseModel):
    notifications_enabled: bool
    dark_mode: bool
    privacy_level: str  # Example: "public" or "private"

class Language(BaseModel):
    language: str

class Query(BaseModel):
    query: str
    
class SignUpRequest(BaseModel):
    email: str
    username: str
    password: str
    phonenumber: str = Field(..., pattern=r'^\+91\d{10}$')

class InventoryItem(BaseModel):
    name: str
    category: str
    quantity: int
    description: Optional[str] = None
    price: Optional[float] = None

class LoginRequest(BaseModel):
    email: str
    password: str
    
class EmailRequest(BaseModel):
    email: str
    
class UpdatePasswordRequest(BaseModel):
    uid: str
    new_password: str

# class Profile(BaseModel):
#     fullname: str
#     password: constr(min_length=8)
#     phonenumber: str = Field(..., pattern=r'^\+91\d{10}$')
#     address: str
#     email: str
#     city: str
#     pincode:str = Field(..., pattern=r'^\d{6}$')
class ProfileData(BaseModel):
    def __init__(self, uid, email, first_name, last_name, gender, age, phone_number, occupation, role, address, state, city, pincode, profile_image, description):
        self.uid = uid
        self.email = email
        self.first_name = first_name
        self.profile_image = last_name
        self.gender = gender
        self.profile_image = age
        self.gender = phone_number
        self.occupation = occupation
        self.role = role
        self.address = address
        self.state = state
        self.city = city
        self.pincode = pincode
        self.profile_image = profile_image
        self.description = description

class CropData(BaseModel):
    cropname: str
    quantity: int
    qualitygrade: str