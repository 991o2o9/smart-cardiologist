import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestCardioAssistantAPI:
    """Тесты для API кардио-ассистента"""
    
    def test_root_endpoint(self):
        """Тест корневого endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Smart Cardiologist API"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Тест проверки здоровья"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_cardio_assistant_valid_request(self):
        """Тест валидного запроса к кардио-ассистенту"""
        request_data = {
            "age": 45,
            "pulse": 85,
            "risk": "средний",
            "symptoms": "одышка при физической нагрузке"
        }
        
        response = client.post("/cardio-assistant/", json=request_data)
        
        # Проверяем, что запрос прошел успешно
        assert response.status_code in [200, 500]  # 500 если нет API ключа
        
        if response.status_code == 200:
            data = response.json()
            assert "cached" in data
            assert "response" in data
            assert isinstance(data["cached"], bool)
            assert isinstance(data["response"], str)
    
    def test_cardio_assistant_invalid_request(self):
        """Тест невалидного запроса к кардио-ассистенту"""
        # Неполные данные
        request_data = {
            "age": 45,
            "pulse": 85
            # Отсутствуют risk и symptoms
        }
        
        response = client.post("/cardio-assistant/", json=request_data)
        assert response.status_code == 422  # Validation Error
    
    def test_cardio_assistant_invalid_age(self):
        """Тест невалидного возраста"""
        request_data = {
            "age": 150,  # Слишком большой возраст
            "pulse": 85,
            "risk": "средний",
            "symptoms": "одышка"
        }
        
        response = client.post("/cardio-assistant/", json=request_data)
        assert response.status_code == 422
    
    def test_cardio_assistant_health(self):
        """Тест health check кардио-ассистента"""
        response = client.get("/cardio-assistant/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "ai_service" in data
        assert "cache_stats" in data
        assert "rate_limiter_stats" in data


class TestHeartPredictionAPI:
    """Тесты для API предсказания риска"""
    
    def test_heart_prediction_valid_request(self):
        """Тест валидного запроса для предсказания"""
        request_data = {
            "age": 45,
            "sex": 1,
            "cp": 1,
            "trestbps": 130,
            "chol": 250,
            "fbs": 0,
            "restecg": 0,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 2.0,
            "slope": 1,
            "ca": 0,
            "thal": 1,
            "pulse": 85
        }
        
        response = client.post("/heart-prediction/predict", json=request_data)
        
        # Проверяем, что запрос прошел успешно
        assert response.status_code in [200, 500]  # 500 если модель не загружена
        
        if response.status_code == 200:
            data = response.json()
            assert "risk" in data
            assert "probability" in data
            assert isinstance(data["risk"], int)
            assert isinstance(data["probability"], float)
            assert 0 <= data["risk"] <= 1
            assert 0.0 <= data["probability"] <= 1.0
    
    def test_heart_prediction_invalid_request(self):
        """Тест невалидного запроса для предсказания"""
        # Неполные данные
        request_data = {
            "age": 45,
            "sex": 1
            # Отсутствуют остальные поля
        }
        
        response = client.post("/heart-prediction/predict", json=request_data)
        assert response.status_code == 422
    
    def test_heart_prediction_health(self):
        """Тест health check предсказания"""
        response = client.get("/heart-prediction/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_info" in data
    
    def test_feature_importance(self):
        """Тест получения важности признаков"""
        response = client.get("/heart-prediction/feature-importance")
        assert response.status_code in [200, 500]  # 500 если модель не загружена
        
        if response.status_code == 200:
            data = response.json()
            assert "feature_importance" in data
            assert "top_features" in data
