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
    
# Table for user accounts, including fields such as userID (primary key), email, phone number, hashed password
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
    
# Order model
class Order(BaseModel):
    farmerId: str
    buyerId: str
    product: str
    quantity: int
    price: float
    status: str = "Pending"

# Order status update model
class OrderStatusUpdate(BaseModel):
    status: str
    
# Model for Order Cancellation
class OrderCancellation(BaseModel):
    reason: str

# Model for Order Feedback
class OrderFeedback(BaseModel):
    rating: int  # 1 to 5
    comment: str
    
class CropAnalysisRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class PestDetectionRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class CropAnalysisRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class PestDetectionRequest(BaseModel):
    image_urls: List[str]  # Optional if uploading files directly

class ModelFeedbackRequest(BaseModel):
    analysis_id: str
    feedback: str  # Positive, Negative, or Detailed Feedback

class AudioFeedbackRequest(BaseModel):
    audio_id: str
    feedback: str  # Positive, Negative, or Detailed Feedback

class MarketForecastRequest(BaseModel):
    location: str
    commodity: str
    timeframe: str  # daily, weekly, monthly

class TrendAnalysisRequest(BaseModel):
    category: str
    start_date: str
    end_date: str


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


# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

class NewMessageRequest(BaseModel):
    sender_id: str
    content: str

# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

class NewMessageRequest(BaseModel):
    sender_id: str
    content: str

class BotQueryRequest(BaseModel):
    query: str


# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

class NewMessageRequest(BaseModel):
    sender_id: str
    content: str

class BotQueryRequest(BaseModel):
    query: str

class ForumThreadRequest(BaseModel):
    title: str
    content: str
    category: str
    created_by: str
    

# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

class NewMessageRequest(BaseModel):
    sender_id: str
    content: str

class BotQueryRequest(BaseModel):
    query: str

class ForumThreadRequest(BaseModel):
    title: str
    content: str
    category: str
    created_by: str

class ForumCommentRequest(BaseModel):
    content: str
    created_by: str

class UpdateThreadRequest(BaseModel):
    title: str = None
    content: str = None
    category: str = None


class VoteRequest(BaseModel):
    vote: str  # "up" or "down"

class ReportRequest(BaseModel):
    reason: str
    reported_by: str

class ModerateThreadRequest(BaseModel):
    action: str  # "lock", "unlock", "delete", "warn"
    moderator_id: str
    reason: Optional[str] = None

class LocationAlertSubscription(BaseModel):
    latitude: float
    longitude: float
    radius: int  # in meters
    alert_type: str  # Weather, Market, etc.


class MovementTracking(BaseModel):
    product_id: str
    origin: str
    destination: str
    timestamp: str  # ISO format timestamp
    status: str  # e.g., 'in transit', 'delivered'

# Chat conversation models
class NewConversationRequest(BaseModel):
    participants: list[str]  # List of user IDs

class UpdateConversationRequest(BaseModel):
    archived: bool = False
    metadata: dict = {}

class NewMessageRequest(BaseModel):
    sender_id: str
    content: str

class BotQueryRequest(BaseModel):
    query: str

class ForumThreadRequest(BaseModel):
    title: str
    content: str
    category: str
    created_by: str

class ForumCommentRequest(BaseModel):
    content: str
    created_by: str

class UpdateThreadRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class VoteRequest(BaseModel):
    vote: str  # "up" or "down"

class ReportRequest(BaseModel):
    reason: str
    reported_by: str

class ModerateThreadRequest(BaseModel):
    action: str  # "lock", "unlock", "delete", "warn"
    moderator_id: str
    reason: Optional[str] = None

class GroupRequest(BaseModel):
    name: str
    description: str
    created_by: str
    members: List[str] = []

class UpdateGroupRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    members: Optional[List[str]] = None


class GroupInviteRequest(BaseModel):
    email: str
    invited_by: str


class MarketplaceQueryRequest(BaseModel):
    query: str
    category: Optional[str] = None
    farm: Optional[str] = None
    pincode: Optional[str] = None
    sorted_by: Optional[str] = None  # ratings, price, quantity
    radius: Optional[int] = None  # in km
    filters: Optional[dict] = None  # multiple filters


class NotificationRequest(BaseModel):
    title: str
    body: str
    user_id: str
    type: Optional[str] = "general"


class NotificationRequest(BaseModel):
    title: str
    body: str
    user_id: str
    type: Optional[str] = "general"

class NotificationSubscriptionRequest(BaseModel):
    topic: str

class OnboardingTask(BaseModel):
    task_id: str
    task_name: str
    completed: bool
    
class OnboardingTaskUpdate(BaseModel):
    task_id: str
    completed: bool


class RetailPartner(BaseModel):
    name: str
    location: str
    contact_info: str
    business_type: str
    rating: float
    user_id: str
    
class UpdatePartnerDetails(BaseModel):
    partner_id: str
    name: str = None
    location: str = None
    contact_info: str = None
    business_type: str = None
    rating: float = None

class ColdStoragePartner(BaseModel):
    name: str
    location: str
    capacity: int  # In terms of volume or quantity
    contact_info: str
    user_id: str

class UpdatePartnerDetails(BaseModel):
    partner_id: str
    name: str = None
    location: str = None
    fleet_size: int = None  # For transport partners
    capacity: int = None  # For cold storage partners
    contact_info: str = None

# Payment request model
class PaymentRequest(BaseModel):
    amount: int  # Amount in paise (₹10 = 1000 paise)
    currency: str = "INR"
    receipt_id: str
    user_id: str

# Payment confirmation model
class PaymentConfirmation(BaseModel):
    payment_id: str
    order_id: str
    signature: str

# Refund request model
class RefundRequest(BaseModel):
    payment_id: str
    amount: int = None  # Partial or full refund


# Payment history request model
class PaymentHistoryRequest(BaseModel):
    user_id: str

# Integration token model
class IntegrationTokenRequest(BaseModel):
    provider: str  # e.g., 'razorpay', 'stripe', 'paypal'
    token: str


class SensorData(BaseModel):
    sensor_id: str
    temperature: float
    humidity: float
    soil_moisture: float
    timestamp: str  # ISO format


class SensorConfig(BaseModel):
    threshold_temperature: float
    threshold_humidity: float
    threshold_soil_moisture: float


class SensorThresholds(BaseModel):
    temperature_threshold: float
    humidity_threshold: float
    soil_moisture_threshold: float
    sensor_id: str = None  # If None, set global thresholds


class AcknowledgeAlert(BaseModel):
    alert_id: str
    acknowledged: bool


class InventorySyncItem(BaseModel):
    item_id: str
    action: str  # 'add', 'edit', 'remove'
    name: str
    category: str
    quantity: int
    price: float
    image_url: str = None  # Optional for edit/add actions

class SyncInventoryRequest(BaseModel):
    items: List[InventorySyncItem]


class OrderSyncItem(BaseModel):
    order_id: str
    action: str  # 'add', 'update', 'cancel'
    order_status: str
    items: List[dict]  # List of items in the order, can include product IDs, quantities, etc.
    delivery_address: str = None
    payment_status: str = None

class SyncOrderRequest(BaseModel):
    orders: List[OrderSyncItem]


class UserSettingsSync(BaseModel):
    user_id: str
    language: str  # e.g., "en", "es", "fr"
    notifications_enabled: bool
    theme: str  # e.g., "dark", "light"


class SyncConflictResolution(BaseModel):
    document_id: str
    field_name: str
    local_value: str
    server_value: str
    resolution_action: str  # 'overwrite', 'merge'


class SyncAsset(BaseModel):
    asset_name: str
    asset_url: str  # URL of the asset in cloud storage or file system

class TraceabilityScanRequest(BaseModel):
    code_type: str  # e.g., QR, Barcode
    code_value: str

class TraceabilityDocumentRequest(BaseModel):
    product_id: str
    document_type: str  # e.g., Invoice, Certificate
    document_url: str

class ReviewRequest(BaseModel):
    product_id: str
    rating: int  # 1 to 5
    comment: Optional[str] = None
    user_id: str


class TraceabilityScanRequest(BaseModel):
    code_type: str  # e.g., QR, Barcode
    code_value: str

class TraceabilityDocumentRequest(BaseModel):
    product_id: str
    document_type: str  # e.g., Invoice, Certificate
    document_url: str

class ReviewRequest(BaseModel):
    product_id: str
    rating: int  # 1 to 5
    comment: Optional[str] = None
    user_id: str

class ModerateReviewRequest(BaseModel):
    review_id: str
    action: str  # "approve", "reject", "flag"
    reason: Optional[str] = None
    moderator_id: str


class TranslationRequest(BaseModel):
    text: str
    target_language: str  # e.g., 'en', 'es', 'fr', etc.


class LogData(BaseModel):
    user_id: str
    log_type: str  # e.g., "error", "event"
    message: str
    timestamp: str
    metadata: Dict[str, str] = {}  # Additional data


class AIFeedback(BaseModel):
    task_id: str
    feedback: str  # User feedback about AI predictions
    rating: int  # Rating of the AI prediction (e.g., 1-5)


class CartItemRequest(BaseModel):
    item_id: str
    quantity: int
    
# Models for request bodies
class Location(BaseModel):
    latitude: float
    longitude: float


class ChatMessageSyncItem(BaseModel):
    conversation_id: str
    message_id: str
    sender_id: str
    message: str
    timestamp: str

class SyncChatRequest(BaseModel):
    messages: List[ChatMessageSyncItem]