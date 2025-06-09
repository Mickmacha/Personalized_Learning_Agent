# 🎓 Student Profile Analysis API

An intelligent AI-powered backend service that analyzes student profiles and provides personalized career recommendations using Google Gemini and Pydantic AI.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Pydantic AI](https://img.shields.io/badge/Pydantic%20AI-0.0.13-purple.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini for intelligent profile classification
- 📊 **Career Recommendations**: Provides personalized learning paths and skill development suggestions
- 🚀 **High Performance**: Built with FastAPI for fast, async operations
- 🔍 **Type Safety**: Complete Pydantic validation for all data structures
- 📁 **Result Management**: Automatic saving and retrieval of analysis results
- 🔄 **Batch Processing**: Analyze multiple student profiles concurrently
- 📖 **Auto Documentation**: Interactive API docs with Swagger UI
- 🛡️ **Error Handling**: Comprehensive error management and status reporting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Pydantic AI    │    │  Google Gemini  │
│   Web Server    │───▶│   Agents         │───▶│   AI Models     │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   JSON Storage  │    │  Type Validation │    │  Classifications│
│   Results       │    │  Data Models     │    │  Recommendations│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd student-profile-analysis
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

On Windows:
```cmd
set GEMINI_API_KEY=your-gemini-api-key-here
```

4. **Run the server**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Quick Test

```bash
# Test the API
python test_client.py

# Or visit the interactive docs
open http://localhost:8000/docs
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/health` | Health check |
| `POST` | `/analyze` | Analyze multiple student profiles |
| `POST` | `/analyze-single` | Analyze a single student profile |
| `GET` | `/results` | List all saved analysis results |
| `GET` | `/results/{student_name}` | Get specific student's results |


## 🧪 Testing

### Run Tests

```bash
# Test the API endpoints
python test_client.py

# Manual testing with curl
curl -X GET "http://localhost:8000/health"
```

### Sample Test Data

The test client includes sample student profiles for different career paths:
- AI/ML Engineer profile
- Full-Stack Developer profile
- Blockchain Developer profile

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV GEMINI_API_KEY=""
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Deployment

```bash
# Using Gunicorn for production
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📈 Performance

- **Concurrent Processing**: Multiple students analyzed simultaneously
- **Async Operations**: Non-blocking I/O for better throughput
- **Response Times**: Typical analysis completes in 2-5 seconds per student
- **Scalability**: Easily scales with additional worker processes

## 🛠️ Development

### Adding New Features

1. **New Analysis Types**: Extend the AI agents with additional prompts


### Debug Mode

```bash
# Run with detailed logging
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --reload
```
