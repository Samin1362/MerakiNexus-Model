# Art Evaluator API

A FastAPI-based web service for evaluating artwork images using a pre-trained EfficientNet model. The API can classify artwork into 21 different art styles and movements.

## Features

- **Model Loading**: Automatically downloads and loads a TorchScript model from GitHub
- **Image Processing**: Accepts image URLs and processes them with EfficientNet-compatible transforms
- **Art Classification**: Classifies artwork into 21 categories including baroque, cubism, impressionism, etc.
- **Probability Scores**: Returns confidence scores for all art categories
- **GPU Support**: Automatically uses GPU if available, falls back to CPU
- **CORS Enabled**: Ready for frontend integration
- **Error Handling**: Comprehensive error handling for invalid URLs, network issues, etc.

## Installation

1. Clone this repository or download the files
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### API Endpoints

#### Health Check

```
GET /
```

Returns server status and model information.

#### Get Available Classes

```
GET /classes
```

Returns the list of 21 art categories the model can predict.

#### Evaluate Artwork

```
POST /evaluate
Content-Type: application/json

{
  "image_url": "https://example.com/artwork.jpg"
}
```

**Response:**

```json
{
  "predicted_class": "cubism",
  "probabilities": {
    "abstract_art": 0.01,
    "abstract_expressionism": 0.02,
    "amateur": 0.01,
    "art_nouveau": 0.03,
    "baroque": 0.05,
    "chinese_landscape": 0.02,
    "constructivism": 0.04,
    "cubism": 0.75,
    "expressionism": 0.03,
    "fauvism": 0.01,
    "futurism": 0.02,
    "high_renaissance": 0.01,
    "minimalism": 0.0,
    "op_art": 0.0,
    "pop_art": 0.0,
    "post_impressionism": 0.0,
    "realism": 0.0,
    "renaissance": 0.0,
    "romanticism": 0.0,
    "surrealism": 0.0,
    "symbolism": 0.0
  }
}
```

## Art Categories

The model can classify artwork into the following 21 categories:

1. abstract_art
2. abstract_expressionism
3. amateur
4. art_nouveau
5. baroque
6. chinese_landscape
7. constructivism
8. cubism
9. expressionism
10. fauvism
11. futurism
12. high_renaissance
13. minimalism
14. op_art
15. pop_art
16. post_impressionism
17. realism
18. renaissance
19. romanticism
20. surrealism
21. symbolism

## Example Usage with curl

```bash
# Test the health endpoint
curl http://localhost:8000/

# Get available classes
curl http://localhost:8000/classes

# Evaluate an artwork
curl -X POST "http://localhost:8000/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://upload.wikimedia.org/wikipedia/en/4/4c/Les_Demoiselles_d%27Avignon.jpg"}'
```

## Error Handling

The API includes comprehensive error handling for:

- Invalid image URLs (400 Bad Request)
- Network timeouts (408 Request Timeout)
- Invalid image formats (400 Bad Request)
- Model loading failures (500 Internal Server Error)
- General server errors (500 Internal Server Error)

## Technical Details

- **Model**: EfficientNet-based TorchScript model
- **Input Size**: 224x224 pixels
- **Normalization**: ImageNet standard (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- **Device**: Automatically selects CUDA if available, otherwise CPU
- **Framework**: FastAPI with Pydantic for request/response validation

## Model Source

The model is automatically downloaded from:
`https://github.com/Samin1362/MerakiNexus-V2/raw/main/art_classification_model/subject-2%20(CSE499-B)/EfficientNet-Base/artwork_classification_model_subject_2_efficientNet.pth`

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API documentation will be available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

## 🚀 Deployment to Vercel

For detailed deployment instructions to Vercel serverless platform, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

**Quick Vercel Deploy:**

1. Push your code to GitHub (include model file in `model/` directory)
2. Create a new project on Vercel
3. Connect your GitHub repository
4. Vercel automatically detects and deploys your FastAPI app
5. Test your live API!

Your deployed API will be available at: `https://your-project-name.vercel.app`

### Model Setup for Vercel

- Place your `artwork_classification_model_subject_2_efficientNet.pth` file in the `model/` directory
- Or let the app download it automatically on first request
- Vercel supports up to 250MB for the free tier
