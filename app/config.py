from pydantic import EmailStr
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
        # DATABASE_URL: str
        # MONGO_INITDB_DATABASE: str
        # OPENAI_API_KEY: str
        # CLIENT_ORIGIN: str
        # EMAIL_FROM: EmailStr

        # # Existing settings
        # CLIENT_ORIGIN: str

        # Cognito settings
        # COGNITO_USER_POOL_ID: str
        # COGNITO_REGION: str
        # COGNITO_CLIENT_ID: str
        # COGNITO_CLIENT_SECRET: str
        # AWS_ACCESS_KEY_ID: str
        # AWS_SECRET_ACCESS_KEY: str
        # AZURE_ENDPOINT: str
        # API_KEY: str
        # API_VERSION: str
        # BASE_DIR: str
        # CREDENTIALS_FILE: str


        class Config:
                env_file = './.env'

# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# cred_file = os.path.join(base_dir, "app/helpers/kisaandvaar-firebase-adminsdk-t83e9-f6d6bf9844.json")
# settings = Settings(base_dir, cred_file)
settings = Settings()
