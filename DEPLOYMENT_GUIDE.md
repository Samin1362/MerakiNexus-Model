# 🚀 Deploying Art Evaluator API to Vercel

This guide will walk you through deploying your FastAPI artwork evaluation service to Vercel.

## 📋 Prerequisites

- GitHub repository with your code
- Vercel account (free at https://vercel.com)
- Your repository should contain:
  - `main.py` (FastAPI server)
  - `requirements.txt` (Python dependencies)
  - `vercel.json` (Vercel configuration)
  - `model/` directory with PyTorch model file

## 🔧 Pre-Deployment Setup

### 1. Prepare Your Repository

Make sure your GitHub repository contains these files:

```
your-repo/
├── main.py                                           # FastAPI server
├── requirements.txt                                  # Python dependencies
├── vercel.json                                      # Vercel configuration
├── model/                                           # Model directory
│   ├── .gitkeep                                     # Keep directory in Git
│   └── artwork_classification_model_subject_2_efficientNet.pth  # PyTorch model
├── README.md                                        # Documentation
└── DEPLOYMENT_GUIDE.md                             # This guide
```

### 2. Model File Setup

**Option 1: Include Model in Repository (Recommended for < 100MB)**

```bash
# Download the model to your local model directory
cd model/
wget https://github.com/Samin1362/MerakiNexus-V2/raw/main/art_classification_model/subject-2%20(CSE499-B)/EfficientNet-Base/artwork_classification_model_subject_2_efficientNet.pth
```

**Option 2: Download at Runtime (For larger models)**

- The code will automatically download the model if not found locally
- First request will be slower but subsequent requests will be fast

### 3. Verify Your Configuration Files

**vercel.json:**

```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "functions": {
    "main.py": {
      "maxDuration": 30
    }
  },
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

**requirements.txt:**

```
fastapi==0.104.1
uvicorn==0.24.0
torch==2.1.0
torchvision==0.16.0
Pillow==10.0.1
requests==2.31.0
pydantic==2.5.0
python-multipart==0.0.6
matplotlib==3.7.2
```

## 🌐 Deploying to Vercel

### Step 1: Create a Vercel Account

1. Go to https://vercel.com
2. Sign up using GitHub (recommended for easy repo access)
3. Verify your email if required

### Step 2: Import Your Project

1. **Login to Vercel Dashboard**
2. **Click "New Project"** or "Add New..."
3. **Select "Import Git Repository"**

### Step 3: Connect Your Repository

1. **Connect your GitHub account** if not already connected
2. **Select your repository** containing the FastAPI code
3. **Click "Import"**

### Step 4: Configure the Project

**Project Settings:**

- **Project Name**: `art-evaluator-api` (or your preferred name)
- **Framework Preset**: Other (Vercel will auto-detect Python)
- **Root Directory**: `.` (leave as root)
- **Build Command**: Leave empty (Vercel will use defaults)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### Step 5: Environment Variables (Optional)

Add these if you want to customize:

| Variable Name    | Value                                                           | Description                   |
| ---------------- | --------------------------------------------------------------- | ----------------------------- |
| `PYTHON_VERSION` | `3.11`                                                          | Python version                |
| `MODEL_URL`      | `https://github.com/...`                                        | Custom model URL if different |
| `MODEL_PATH`     | `model/artwork_classification_model_subject_2_efficientNet.pth` | Local model path              |

### Step 6: Deploy

1. **Click "Deploy"**
2. **Wait for deployment** (first deploy takes 3-5 minutes)
3. **Monitor build logs** in the Vercel dashboard

## 📊 Monitoring Deployment

### Build Process

Watch the build logs for:

1. ✅ Python environment setup
2. ✅ Dependencies installation
3. ✅ Function deployment
4. ✅ Domain assignment

### Expected Build Output

```
Installing dependencies...
✓ Installed fastapi, torch, torchvision, etc.
Building...
✓ Detected `main.py`
✓ Lambda function created
✓ Deployment completed
```

### Expected Runtime Logs

```
2024-01-XX XX:XX:XX - __main__ - INFO - Loading model from local path: model/artwork_classification_model_subject_2_efficientNet.pth
2024-01-XX XX:XX:XX - __main__ - INFO - Using device: cpu
2024-01-XX XX:XX:XX - __main__ - INFO - Local model loaded successfully!
```

## 🧪 Testing Your Deployed API

Once deployed, you'll get a URL like: `https://art-evaluator-api-xxxx.vercel.app`

### Test Health Check

```bash
curl https://your-vercel-url.vercel.app/
```

Expected response:

```json
{
  "message": "Art Evaluator API is running on Vercel",
  "device": "cpu",
  "model_loaded": true,
  "classes_count": 21,
  "platform": "Vercel"
}
```

### Test Available Classes

```bash
curl https://your-vercel-url.vercel.app/classes
```

Expected response:

```json
{
  "classes": [
    "abstract_art",
    "abstract_expressionism",
    "amateur",
    ...
  ]
}
```

### Test Artwork Evaluation

```bash
curl -X POST "https://your-vercel-url.vercel.app/evaluate" \
     -H "Content-Type: application/json" \
     -d '{"image_url": "https://upload.wikimedia.org/wikipedia/en/4/4c/Les_Demoiselles_d%27Avignon.jpg"}'
```

Expected response:

```json
{
  "predicted_class": "cubism",
  "probabilities": {
    "abstract_art": 0.01,
    "cubism": 0.85,
    "expressionism": 0.08,
    ...
  }
}
```

## 🔧 Troubleshooting

### Common Issues

**1. Build Fails - Dependencies**

```
Error: Could not install packages due to an EnvironmentError
```

**Solution:**

- Check `requirements.txt` has all packages
- Verify PyTorch version is compatible with Vercel
- Consider using CPU-only PyTorch version

**2. Function Timeout**

```
Error: Function exceeded maximum duration of 10s
```

**Solution:**

- Increase `maxDuration` in `vercel.json` to 30s
- Optimize model loading (use smaller model if possible)
- Consider upgrading to Pro plan for longer timeouts

**3. Model Loading Fails**

```
Error: [Errno 2] No such file or directory: 'model/...'
```

**Solution:**

- Ensure model file is in the `model/` directory
- Check file name matches exactly
- Verify model file was committed to Git

**4. Memory Limit Exceeded**

```
Error: Function exceeded memory limit
```

**Solution:**

- Use Pro plan for higher memory limits
- Optimize model size
- Consider model quantization

### Performance Optimization

**For Free Tier:**

- Functions have 10s timeout and 1024MB memory limit
- Cold starts can take 1-3 seconds
- No persistent storage between requests

**For Pro Tier ($20/month):**

- 60s timeout and higher memory limits
- Better performance and reliability
- Priority support

## 🔄 Auto-Deploy Setup

Vercel automatically sets up CI/CD:

1. **Every push to main branch** triggers a new deployment
2. **Pull requests** get preview deployments
3. **Custom domains** can be added in project settings

## 📈 Monitoring & Analytics

Access logs and analytics:

1. **Vercel Dashboard** → Your Project → Functions tab
2. **View real-time logs** and performance metrics
3. **Set up monitoring** for errors and response times

## ⚙️ Advanced Configuration

### Custom Domain

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

### Environment-Specific Deployments

```bash
# Production deployment
vercel --prod

# Preview deployment
vercel

# Development
vercel dev
```

### Serverless Function Optimization

```json
{
  "functions": {
    "main.py": {
      "maxDuration": 30,
      "memory": 1024,
      "runtime": "python3.11"
    }
  }
}
```

## 🎯 Production Best Practices

### 1. Model Optimization

- **Use quantized models** for faster loading
- **Consider model compression** techniques
- **Cache model in memory** between requests

### 2. Error Handling

- **Implement retry logic** for model downloads
- **Add request validation** for image URLs
- **Set up error monitoring** with Sentry

### 3. Security

- **Add rate limiting** to prevent abuse
- **Validate image URLs** to prevent SSRF attacks
- **Use environment variables** for sensitive data

### 4. Performance

- **Enable compression** for responses
- **Use CDN** for static assets
- **Monitor response times** and optimize accordingly

## 💡 Tips for Success

1. **Model Size**: Keep models < 250MB for Vercel free tier
2. **Cold Starts**: First request may be slow, subsequent requests are fast
3. **Monitoring**: Use Vercel Analytics to track usage
4. **Debugging**: Check function logs in Vercel dashboard
5. **Updates**: Push to GitHub automatically deploys to Vercel

## 🔗 Useful Links

- **Vercel Docs**: https://vercel.com/docs
- **Python on Vercel**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **FastAPI**: https://fastapi.tiangolo.com/
- **PyTorch**: https://pytorch.org/

---

**Your Art Evaluator API is now live on Vercel! 🎨**

Access your API at: `https://your-project-name.vercel.app`

Need help? Check the Vercel docs or contact support!
