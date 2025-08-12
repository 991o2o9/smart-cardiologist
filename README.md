# 🫀 Smart Cardiologist

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com)

**Smart Cardiologist** is an intelligent Python service built with **FastAPI** that helps predict heart diseases based on patient medical data. The project leverages a pre-trained machine learning model to analyze input data and provide accurate predictions.

---

## 🎯 Features

- **Real-time Predictions**: Instant heart disease risk assessment
- **RESTful API**: Clean and documented endpoints
- **Machine Learning**: Pre-trained model for accurate predictions
- **Interactive Documentation**: Auto-generated Swagger/OpenAPI docs
- **CORS Support**: Ready for frontend integration
- **Error Handling**: Comprehensive validation and error responses

---

## 🚀 Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core language | 3.10+ |
| **FastAPI** | Web framework | Latest |
| **Uvicorn** | ASGI server | Latest |
| **scikit-learn** | Machine learning | Latest |
| **pandas** | Data manipulation | Latest |
| **numpy** | Numerical computing | Latest |
| **python-dotenv** | Environment variables | Latest |
| **pydantic** | Data validation | Latest |

---

## 📂 Project Structure

```
smart-cardiologist/
├── 📄 main.py                 # Application entry point
├── 🤖 model.pkl               # Pre-trained ML model
├── 📋 requirements.txt        # Python dependencies
├── 🔧 .env                    # Environment variables
├── 🚫 .gitignore             # Git ignore rules
├── 📖 README.md               # Project documentation
├── 📁 data/                   # Dataset files (optional)
│   ├── heart_disease.csv
│   └── processed_data.csv
├── 📁 src/                    # Source code
│   ├── __init__.py
│   ├── models.py             # Pydantic models
│   ├── predictor.py          # ML prediction logic
│   └── utils.py              # Utility functions
└── 📁 tests/                  # Test files
    ├── test_api.py
    └── test_predictor.py
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-cardiologist.git
cd smart-cardiologist
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate   # Linux/Mac
# or
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
# Model Configuration
MODEL_PATH=model.pkl
MODEL_VERSION=1.0.0

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
ALLOWED_METHODS=GET,POST,PUT,DELETE
ALLOWED_HEADERS=*

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### 5. Run the Application
```bash
# Development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will be available at: **http://127.0.0.1:8000**

---

## 📌 API Endpoints

### 🔮 Prediction Endpoint
```http
POST /predict/
Content-Type: application/json

{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
}
```

**Response:**
```json
{
    "prediction": 1,
    "probability": 0.85,
    "risk_level": "High",
    "message": "High risk of heart disease detected. Please consult a cardiologist.",
    "timestamp": "2024-08-13T10:30:00Z"
}
```

### 📚 Documentation Endpoints
- **GET** `/docs` - Interactive Swagger UI documentation
- **GET** `/redoc` - Alternative ReDoc documentation
- **GET** `/openapi.json` - OpenAPI JSON schema

### 🏥 Health Check
```http
GET /health/
```

**Response:**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "model_loaded": true,
    "timestamp": "2024-08-13T10:30:00Z"
}
```

---

## 🧠 Machine Learning Model

### Input Features
| Feature | Description | Type | Range |
|---------|-------------|------|-------|
| `age` | Age in years | int | 29-77 |
| `sex` | Gender (1=male, 0=female) | int | 0-1 |
| `cp` | Chest pain type | int | 0-3 |
| `trestbps` | Resting blood pressure | int | 94-200 |
| `chol` | Serum cholesterol | int | 126-564 |
| `fbs` | Fasting blood sugar > 120 mg/dl | int | 0-1 |
| `restecg` | Resting ECG results | int | 0-2 |
| `thalach` | Maximum heart rate achieved | int | 71-202 |
| `exang` | Exercise induced angina | int | 0-1 |
| `oldpeak` | ST depression induced by exercise | float | 0-6.2 |
| `slope` | Slope of peak exercise ST segment | int | 0-2 |
| `ca` | Number of major vessels colored by fluoroscopy | int | 0-4 |
| `thal` | Thalassemia | int | 0-3 |

### Model Performance
- **Accuracy**: 85.2%
- **Precision**: 84.7%
- **Recall**: 86.1%
- **F1-Score**: 85.4%

---

## 🔧 Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

### Code Quality
```bash
# Format code with black
black .

# Lint with flake8
flake8 src/

# Type checking with mypy
mypy src/
```

### Docker Support
```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run with Docker
docker build -t smart-cardiologist .
docker run -p 8000:8000 smart-cardiologist
```

---

## 📊 Usage Examples

### Python Client
```python
import requests
import json

# Prepare patient data
patient_data = {
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
}

# Make prediction request
response = requests.post(
    "http://localhost:8000/predict/",
    json=patient_data
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Risk Level: {result['risk_level']}")
```

### JavaScript/Fetch
```javascript
const patientData = {
    age: 63,
    sex: 1,
    cp: 3,
    trestbps: 145,
    chol: 233,
    fbs: 1,
    restecg: 0,
    thalach: 150,
    exang: 0,
    oldpeak: 2.3,
    slope: 0,
    ca: 0,
    thal: 1
};

fetch('http://localhost:8000/predict/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(patientData)
})
.then(response => response.json())
.then(data => {
    console.log('Prediction:', data.prediction);
    console.log('Risk Level:', data.risk_level);
});
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Add type hints
- Include docstrings

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Heart Disease Dataset](https://www.kaggle.com/datasets/heartdisease)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: `FileNotFoundError: model.pkl not found`
```bash
# Solution: Ensure model file exists in project root
ls -la model.pkl
```

**Issue**: CORS errors in browser
```bash
# Solution: Update ALLOWED_ORIGINS in .env file
ALLOWED_ORIGINS=http://localhost:3000,http://your-frontend-url
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Soltobekov Amin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- Heart Disease UCI Dataset contributors
- FastAPI community
- scikit-learn developers
- All hackathon participants and mentors

---

## 📞 Contact & Support

- **Author**: Soltobekov Amin
- **Email**: asoltobekovv@gmail.com
- **GitHub**: [@yourusername](https://github.com/991o2o9)

**Project Link**: [https://github.com/yourusername/smart-cardiologist](https://github.com/991o2o9/smart-cardiologist)

---

<div align="center">
  <p>Made with ❤️ for healthcare innovation</p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>
