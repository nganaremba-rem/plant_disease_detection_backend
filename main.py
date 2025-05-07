# app.py
import io
import logging
import os
from typing import Any, Dict, List

import torch
import uvicorn
import yaml
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi_mail import FastMail, MessageSchema, MessageType
from PIL import Image
from starlette.responses import JSONResponse
from transformers import AutoImageProcessor, AutoModelForImageClassification, pipeline

from controller.mailing_configs import EmailSchema, ResultsForUI, conf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Load configuration
def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        # Provide default configuration if file cannot be loaded
        return {
            "model_path": "ViT-Base-model",
            "allowed_extensions": ["jpg", "jpeg", "png"],
            "max_file_size_mb": 10,
            "host": "0.0.0.0",
            "port": 8000,
        }


# Initialize FastAPI app
app = FastAPI(title="Plant Disease Classification API")
config = load_config()

# Load the model
logger.info(f"Loading model from {config['model_path']}...")
try:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device set to use {device}")

    model_path = os.path.join(os.getcwd(), config["model_path"])
    image_processor = AutoImageProcessor.from_pretrained(model_path)
    model = AutoModelForImageClassification.from_pretrained(model_path)
    classifier = pipeline(
        "image-classification",
        image_processor=image_processor,
        model=model,
        device=device,
    )
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise RuntimeError(f"Failed to load model: {e}")


# Validation functions
def validate_image(file: UploadFile) -> bool:
    """Validate if the uploaded file is an allowed image type and size."""
    # Check file extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in config["allowed_extensions"]:
        return False

    # Check file size (in bytes)
    max_size_bytes = config["max_file_size_mb"] * 1024 * 1024
    return True


@app.post("/classify/", response_class=JSONResponse)
async def classify_image(file: UploadFile = File(...)):
    """
    Classify an uploaded plant image and return the disease classification results.
    """
    try:
        # Validate input file
        if not validate_image(file):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file. Allowed extensions: {config['allowed_extensions']}, Max size: {config['max_file_size_mb']}MB",
            )

        # Read and process image
        contents = await file.read()
        try:
            image = Image.open(io.BytesIO(contents)).convert("RGB")
        except Exception as e:
            logger.error(f"Error opening the image: {e}")
            raise HTTPException(
                status_code=400, detail=f"Error processing image: {str(e)}"
            )

        # Classify the image
        results = classifier(image)

        # Format results
        formatted_results = [
            {"label": res["label"], "score": round(res["score"], 4)} for res in results
        ]

        return {"classification_results": formatted_results}

    except Exception as e:
        print("Error: ", e)
        logger.error(f"Error classifying image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": config["model_path"]}


@app.post("/send-email/")
async def simple_send(email: EmailSchema, data: List[ResultsForUI]) -> JSONResponse:
    template_data = {"data": data}

    message = MessageSchema(
        subject="Plant Disease Detection Alert",
        recipients=email.model_dump().get("email"),
        template_body=template_data,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name="plant_disease_alert.html")
    return JSONResponse(
        status_code=200, content={"message": "Disease alert email has been sent"}
    )


if __name__ == "__main__":
    # Downgrade pydantic to version 1.10.12 to fix Undefined import error
    # pip install pydantic==1.10.12
    uvicorn.run(
        "main:app",
        host=config["host"],
        port=config["port"],
        reload=False,  # Set to False in production
    )
