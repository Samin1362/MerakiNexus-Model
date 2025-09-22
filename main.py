import os
import io
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import logging
from typing import Dict, Any
import tempfile
import sys

# Configure logging for Vercel deployment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Art Evaluator API",
    description="API for evaluating artwork images using a trained EfficientNet model",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Class names in order for prediction mapping
CLASS_NAMES = [
    "abstract_art",
    "abstract_expressionism", 
    "amateur",
    "art_nouveau",
    "baroque",
    "chinese_landscape",
    "constructivism",
    "cubism",
    "expressionism",
    "fauvism",
    "futurism",
    "high_renaissance",
    "minimalism",
    "op_art",
    "pop_art",
    "post_impressionism",
    "realism",
    "renaissance",
    "romanticism",
    "surrealism",
    "symbolism"
]

# Model configuration - Support environment variables for Vercel
MODEL_URL = os.getenv(
    "MODEL_URL", 
    "https://github.com/Samin1362/MerakiNexus-V2/raw/main/art_classification_model/subject-2%20(CSE499-B)/EfficientNet-Base/artwork_classification_model_subject_2_efficientNet.pth"
)
MODEL_PATH = os.getenv("MODEL_PATH", "model/artwork_classification_model_subject_2_efficientNet.pth")  # Local model path for Vercel
DEVICE = torch.device("cpu")  # Vercel only supports CPU

# Global model variable
model = None

# Image preprocessing transforms for EfficientNet
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

class ImageRequest(BaseModel):
    image_url: HttpUrl

class PredictionResponse(BaseModel):
    predicted_class: str
    probabilities: Dict[str, float]

def download_and_load_model():
    """Load the TorchScript model from local path or download from GitHub"""
    global model
    
    try:
        # First try to load from local path (for Vercel deployment)
        if MODEL_PATH and os.path.exists(MODEL_PATH):
            logger.info(f"Loading model from local path: {MODEL_PATH}")
            logger.info(f"Using device: {DEVICE}")
            model = torch.jit.load(MODEL_PATH, map_location=DEVICE)
            model.eval()
            logger.info("Local model loaded successfully!")
            return
        
        # Download from GitHub if no local model (fallback)
        logger.info(f"Local model not found, downloading from {MODEL_URL}")
        logger.info(f"Using device: {DEVICE}")
        
        # Create model directory if it doesn't exist
        os.makedirs("model", exist_ok=True)
        
        # Download the model file
        response = requests.get(MODEL_URL, stream=True, timeout=300)  # 5 min timeout
        response.raise_for_status()
        
        # Get total file size for progress tracking
        total_size = int(response.headers.get('content-length', 0))
        logger.info(f"Model file size: {total_size / (1024*1024):.1f} MB")
        
        # Save directly to model directory
        with open(MODEL_PATH, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total_size > 0:
                    progress = (downloaded / total_size) * 100
                    if downloaded % (1024*1024*10) == 0:  # Log every 10MB
                        logger.info(f"Download progress: {progress:.1f}%")
        
        logger.info("Download complete, loading model...")
        
        # Load the TorchScript model
        model = torch.jit.load(MODEL_PATH, map_location=DEVICE)
        model.eval()
        
        logger.info("Model loaded successfully!")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

def download_image_from_url(url: str) -> Image.Image:
    """Download and open image from URL"""
    try:
        response = requests.get(str(url), timeout=30)
        response.raise_for_status()
        
        # Open image from bytes
        image = Image.open(io.BytesIO(response.content))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        return image
        
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=408, detail="Image download timeout")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")

def preprocess_image(image: Image.Image) -> torch.Tensor:
    """Preprocess image for model input"""
    try:
        # Apply transforms
        image_tensor = transform(image)
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        # Move to device
        image_tensor = image_tensor.to(DEVICE)
        return image_tensor
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image preprocessing failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    download_and_load_model()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Art Evaluator API is running on Vercel",
        "device": str(DEVICE),
        "model_loaded": model is not None,
        "classes_count": len(CLASS_NAMES),
        "platform": "Vercel"
    }

@app.get("/classes")
async def get_classes():
    """Get list of available art classes"""
    return {"classes": CLASS_NAMES}

@app.post("/evaluate", response_model=PredictionResponse)
async def evaluate_artwork(request: ImageRequest):
    """Evaluate artwork image and return predictions"""
    
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Download image
        logger.info(f"Processing image from URL: {request.image_url}")
        image = download_image_from_url(request.image_url)
        
        # Preprocess image
        image_tensor = preprocess_image(image)
        
        # Run inference
        with torch.no_grad():
            outputs = model(image_tensor)
            
            # Apply softmax to get probabilities
            probabilities = F.softmax(outputs, dim=1)
            probabilities = probabilities.cpu().numpy()[0]
            
            # Get predicted class
            predicted_idx = probabilities.argmax()
            predicted_class = CLASS_NAMES[predicted_idx]
            
            # Create probability dictionary
            prob_dict = {
                class_name: float(prob) 
                for class_name, prob in zip(CLASS_NAMES, probabilities)
            }
            
            logger.info(f"Prediction complete. Predicted class: {predicted_class}")
            
            return PredictionResponse(
                predicted_class=predicted_class,
                probabilities=prob_dict
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
