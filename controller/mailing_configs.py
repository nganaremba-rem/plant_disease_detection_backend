from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, BaseModel
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

class EmailSchema(BaseModel):
    email: List[EmailStr]
    
class ResultsForUI(BaseModel):
    folder: str
    message: str | None = None
    hasDisease: bool | None = None
    diseaseTypes: List[dict] | None = None
    camera: int | None = None
    cameraData: dict | None = None
    image: str | None = None
    classification_results: List[dict] | None = None

    class Config:
        arbitrary_types_allowed = True

    class CameraData(BaseModel):
        farmer: str
        chilliName: str 
        chilliCode: str
        bedNumber: int | None = None



conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = 587,
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
)





