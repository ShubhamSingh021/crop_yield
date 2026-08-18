from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from catboost import CatBoostRegressor

from dotenv import load_dotenv
from pathlib import Path

import pandas as pd
import numpy as np
import requests
import os


# =========================================================
# ENVIRONMENT
# =========================================================

# Project root:
# smart-crop-ai/
# ├── .env
# ├── backend/
# │   └── main.py
# └── frontend/

BASE_DIR = Path(__file__).resolve().parent.parent

# Load root .env
load_dotenv(BASE_DIR / ".env")


# OpenWeather API key
OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)


# Frontend URL
#
# Local development:
# http://localhost:5173
#
# Production:
# https://your-app.vercel.app
#
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


# Make sure OpenWeather key exists
if not OPENWEATHER_API_KEY:

    raise RuntimeError(
        "OPENWEATHER_API_KEY is not configured."
    )


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Smart Crop Yield Prediction API",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Local Vite development
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",

        # Localhost IP
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",

        # Production frontend
        FRONTEND_URL,
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# LOAD CATBOOST MODEL
# =========================================================

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "model",
    "crop_yield_catboost.cbm"
)


# Check model
if not os.path.exists(MODEL_PATH):

    raise RuntimeError(
        f"Model not found: {MODEL_PATH}"
    )


# Load model
model = CatBoostRegressor()

model.load_model(
    MODEL_PATH
)

print(
    "CatBoost model loaded successfully."
)


# =========================================================
# LOAD CLIMATE LOOKUP
# =========================================================

CLIMATE_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "climate_lookup.csv"
)


# Check climate file
if not os.path.exists(CLIMATE_PATH):

    raise RuntimeError(
        f"Climate lookup not found: {CLIMATE_PATH}"
    )


# Load climate lookup
climate_lookup = pd.read_csv(
    CLIMATE_PATH
)


# Required columns
required_climate_columns = [
    "State",
    "District",
    "Rainfall",
    "Temperature"
]


# Check columns
missing_columns = [
    column
    for column in required_climate_columns
    if column not in climate_lookup.columns
]


if missing_columns:

    raise RuntimeError(
        "Climate lookup is missing columns: "
        + ", ".join(missing_columns)
    )


print(
    "Climate lookup loaded:",
    climate_lookup.shape
)


# =========================================================
# REQUEST SCHEMA
# =========================================================

class PredictionRequest(BaseModel):

    State: str = Field(
        ...,
        min_length=2
    )

    District: str = Field(
        ...,
        min_length=2
    )

    Crop: str = Field(
        ...,
        min_length=2
    )

    Season: str = Field(
        ...,
        min_length=2
    )

    Crop_Year: int = Field(
        ...,
        ge=1997,
        le=2100
    )

    Area: float = Field(
        ...,
        gt=0
    )


# =========================================================
# CLIMATE DATA
# =========================================================

def get_climate_data(
    state: str,
    district: str
):

    # Clean state
    state_clean = (
        state
        .strip()
        .upper()
    )


    # Clean district
    district_clean = (
        district
        .strip()
        .upper()
    )


    # Search lookup
    result = climate_lookup[
        (
            climate_lookup["State"]
            .astype(str)
            .str.strip()
            .str.upper()
            == state_clean
        )
        &
        (
            climate_lookup["District"]
            .astype(str)
            .str.strip()
            .str.upper()
            == district_clean
        )
    ]


    # No climate data
    if result.empty:

        raise ValueError(
            f"No climate data found for "
            f"{district}, {state}"
        )


    # First matching row
    row = result.iloc[0]


    return {

        "rainfall": float(
            row["Rainfall"]
        ),

        "temperature": float(
            row["Temperature"]
        )

    }


# =========================================================
# OPENWEATHER GEOCODING
# =========================================================

def get_coordinates(
    district: str,
    state: str
):

    url = (
        "https://api.openweathermap.org/"
        "geo/1.0/direct"
    )


    params = {

        "q":
            f"{district},{state},IN",

        "limit":
            5,

        "appid":
            OPENWEATHER_API_KEY

    }


    response = requests.get(
        url,
        params=params,
        timeout=10
    )


    if response.status_code != 200:

        raise ValueError(
            "OpenWeather geocoding failed: "
            f"{response.status_code}"
        )


    locations = response.json()


    if not locations:

        raise ValueError(
            f"Location not found: "
            f"{district}, {state}"
        )


    # =====================================================
    # Prefer Indian result
    # =====================================================

    for location in locations:

        if location.get("country") == "IN":

            return {

                "latitude": float(
                    location["lat"]
                ),

                "longitude": float(
                    location["lon"]
                ),

                "country": "IN",

                "name": location.get(
                    "name",
                    district
                )

            }


    # =====================================================
    # Fallback
    # =====================================================

    location = locations[0]


    return {

        "latitude": float(
            location["lat"]
        ),

        "longitude": float(
            location["lon"]
        ),

        "country": location.get(
            "country",
            "IN"
        ),

        "name": location.get(
            "name",
            district
        )

    }


# =========================================================
# OPENWEATHER CURRENT WEATHER
# =========================================================

def get_current_weather(
    latitude: float,
    longitude: float
):

    url = (
        "https://api.openweathermap.org/"
        "data/2.5/weather"
    )


    params = {

        "lat":
            latitude,

        "lon":
            longitude,

        "appid":
            OPENWEATHER_API_KEY,

        "units":
            "metric"

    }


    response = requests.get(
        url,
        params=params,
        timeout=10
    )


    if response.status_code != 200:

        raise ValueError(
            "OpenWeather weather request failed: "
            f"{response.status_code}"
        )


    weather = response.json()


    # =====================================================
    # Temperature
    # =====================================================

    temperature = (
        weather
        .get("main", {})
        .get("temp")
    )


    if temperature is None:

        raise ValueError(
            "Temperature unavailable from OpenWeather."
        )


    # =====================================================
    # Rainfall
    # =====================================================

    rainfall = (
        weather
        .get("rain", {})
        .get("1h", 0.0)
    )


    # =====================================================
    # Description
    # =====================================================

    description = ""

    weather_list = weather.get(
        "weather",
        []
    )


    if weather_list:

        description = weather_list[0].get(
            "description",
            ""
        )


    return {

        "temperature": float(
            temperature
        ),

        "rainfall_1h": float(
            rainfall
        ),

        "description":
            description

    }


# =========================================================
# OPTIONS
# =========================================================

@app.get("/options")
def get_options():

    try:

        # =================================================
        # STATES
        # =================================================

        states = sorted(
            climate_lookup["State"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


        # =================================================
        # DISTRICTS BY STATE
        # =================================================

        districts = {}


        for state in states:

            state_data = climate_lookup[
                climate_lookup["State"]
                .astype(str)
                .str.upper()
                == state.upper()
            ]


            districts[state] = sorted(
                state_data["District"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )


        # =================================================
        # CROPS
        # =================================================

        crops = sorted([

            "Arecanut",
            "Arhar/Tur",
            "Bajra",
            "Banana",
            "Barley",
            "Black pepper",
            "Cardamom",
            "Cashewnut",
            "Castor seed",
            "Coconut",
            "Coriander",
            "Cotton(lint)",
            "Cowpea(Lobia)",
            "Dry chillies",
            "Garlic",
            "Ginger",
            "Gram",
            "Groundnut",
            "Jowar",
            "Jute",
            "Khesari",
            "Linseed",
            "Maize",
            "Masoor",
            "Mesta",
            "Moong(Green Gram)",
            "Moth",
            "Niger seed",
            "Oilseeds total",
            "Onion",
            "Other Cereals",
            "Other Kharif Pulses",
            "Other Rabi Pulses",
            "Other Summer Pulses",
            "other oilseeds",
            "Peas & beans (Pulses)",
            "Potato",
            "Ragi",
            "Rapeseed &Mustard",
            "Rice",
            "Safflower",
            "Sannhamp",
            "Sesamum",
            "Small millets",
            "Soyabean",
            "Sugarcane",
            "Sunflower",
            "Sweet potato",
            "Tapioca",
            "Tobacco",
            "Urad",
            "Wheat",
            "other misc. pulses"

        ])


        # =================================================
        # SEASONS
        # =================================================

        seasons = [

            "Autumn",
            "Kharif",
            "Rabi",
            "Summer",
            "Whole Year",
            "Winter"

        ]


        return {

            "success":
                True,

            "states":
                states,

            "districts":
                districts,

            "crops":
                crops,

            "seasons":
                seasons

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# PREDICTION
# =========================================================

@app.post("/predict")
def predict(
    data: PredictionRequest
):

    try:

        # =================================================
        # 1. HISTORICAL CLIMATE
        # =================================================

        climate = get_climate_data(
            data.State,
            data.District
        )


        rainfall = climate["rainfall"]

        temperature = climate["temperature"]


        # =================================================
        # 2. LOCATION
        # =================================================

        location = get_coordinates(
            data.District,
            data.State
        )


        # =================================================
        # 3. CURRENT WEATHER
        # =================================================

        current_weather = get_current_weather(
            location["latitude"],
            location["longitude"]
        )


        # =================================================
        # 4. MODEL INPUT
        # =================================================

        input_data = pd.DataFrame([
            {

                "Crop":
                    data.Crop,

                "State":
                    data.State,

                "District":
                    data.District,

                "Season":
                    data.Season,

                "Crop_Year":
                    data.Crop_Year,

                "Area":
                    data.Area,

                "Rainfall":
                    rainfall,

                "Temperature":
                    temperature

            }
        ])


        # =================================================
        # 5. PREDICT LOG YIELD
        # =================================================

        prediction_log = model.predict(
            input_data
        )[0]


        # =================================================
        # 6. CONVERT BACK TO ACTUAL YIELD
        # =================================================

        prediction = np.expm1(
            prediction_log
        )


        # Prevent negative prediction
        prediction = max(
            0,
            prediction
        )


        # =================================================
        # 7. RESPONSE
        # =================================================

        return {

            "success":
                True,


            # =================================================
            # PREDICTION
            # =================================================

            "predicted_yield":
                round(
                    float(prediction),
                    2
                ),

            "unit":
                "dataset yield units",


            # =================================================
            # USER INPUT INFORMATION
            # =================================================

            "crop":
                data.Crop,

            "season":
                data.Season,

            "area":
                round(
                    float(data.Area),
                    2
                ),

            "prediction_year":
                data.Crop_Year,


            # =================================================
            # CLIMATE USED BY MODEL
            # =================================================

            "climate_used_for_prediction": {

                "rainfall_mm":
                    round(
                        rainfall,
                        2
                    ),

                "temperature_c":
                    round(
                        temperature,
                        2
                    )

            },


            # =================================================
            # CURRENT WEATHER
            # =================================================

            "current_weather": {

                "temperature_c":
                    round(
                        current_weather[
                            "temperature"
                        ],
                        2
                    ),

                "rainfall_mm_1h":
                    round(
                        current_weather[
                            "rainfall_1h"
                        ],
                        2
                    ),

                "description":
                    current_weather[
                        "description"
                    ]

            },


            # =================================================
            # LOCATION
            # =================================================

            "location": {

                "district":
                    location["name"],

                "state":
                    data.State,

                "country":
                    location["country"],

                "latitude":
                    location["latitude"],

                "longitude":
                    location["longitude"]

            }

        }


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail="OpenWeather request timed out."
        )


    except requests.exceptions.RequestException as e:

        raise HTTPException(
            status_code=502,
            detail=f"OpenWeather error: {str(e)}"
        )


    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def root():

    return {

        "status":
            "running",

        "message":
            "Smart Crop Yield Prediction API",

        "model":
            "CatBoost",

        "weather":
            "OpenWeather",

        "climate":
            "Historical district climate lookup"

    }