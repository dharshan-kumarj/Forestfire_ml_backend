from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np
import aiohttp
from src.Weather import fetch_weather_forecast  # Assuming you have the Weather module for fetching forecasts

router = APIRouter()

# Load model and scaler at startup
model = None
scaler = None

@router.on_event("startup")
async def load_model():
    global model, scaler
    model_path = 'src/model/finalmodeloutput.pkl'  # Adjust path based on your structure
    scaler_path = 'src/model/scaler.pkl'           # Adjust path based on your structure
    
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

# Input data structure for prediction
class FirePredictionInput(BaseModel):
    Oxygen: float
    Temperature: float
    Humidity: float

# Predict endpoint
@router.post("/predict")
async def predict_fire_occurrence(input_data: FirePredictionInput):
    try:
        # Convert input data into a numpy array
        input_dict = input_data.dict()
        input_features = np.array(list(input_dict.values())).reshape(1, -1)

        # Scale the input features
        scaled_features = scaler.transform(input_features)

        # Make prediction
        prediction = model.predict(scaled_features)

        # Return the result
        result = "Fire" if prediction[0] == 1 else "No Fire"
        return {"prediction": result}
    
    except Exception as e:
        return {"error": str(e)}

# Weather forecast endpoint
@router.get("/forecast/{city}")
async def get_weather_forecast(city: str):
    async with aiohttp.ClientSession() as session:
        forecast = await fetch_weather_forecast(city, session)
        return forecast
