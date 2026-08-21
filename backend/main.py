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

# Project structure:
#
# smart-crop-ai/
# ├── .env
# ├── backend/
# │   ├── main.py
# │   ├── model/
# │   └── data/
# └── frontend/

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")


OPENWEATHER_API_KEY = os.getenv(
    "OPENWEATHER_API_KEY"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)


if not OPENWEATHER_API_KEY:
    raise RuntimeError(
        "OPENWEATHER_API_KEY is not configured."
    )


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="Smart Crop Yield Prediction API",
    version="1.1.0"
)


# =========================================================
# CORS
# =========================================================

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
]

if FRONTEND_URL:
    allowed_origins.append(
        FRONTEND_URL.rstrip("/")
    )


app.add_middleware(
    CORSMiddleware,

    allow_origins=allowed_origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# HELPER FUNCTION
# =========================================================

def normalize_text(value: str) -> str:
    """
    Normalize text for case-insensitive matching.
    """

    return str(value).strip().upper()


# =========================================================
# LOAD CATBOOST MODEL
# =========================================================

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "model"
    / "crop_yield_catboost.cbm"
)


if not MODEL_PATH.exists():

    raise RuntimeError(
        f"Model not found: {MODEL_PATH}"
    )


model = CatBoostRegressor()

model.load_model(
    str(MODEL_PATH)
)


print(
    "CatBoost model loaded successfully."
)


# =========================================================
# LOAD CLIMATE LOOKUP
# =========================================================

CLIMATE_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "climate_lookup.csv"
)


if not CLIMATE_PATH.exists():

    raise RuntimeError(
        f"Climate lookup not found: {CLIMATE_PATH}"
    )


climate_lookup = pd.read_csv(
    CLIMATE_PATH
)


required_climate_columns = [
    "State",
    "District",
    "Rainfall",
    "Temperature",
]


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


# Create normalized columns

climate_lookup["_state_key"] = (
    climate_lookup["State"]
    .astype(str)
    .str.strip()
    .str.upper()
)


climate_lookup["_district_key"] = (
    climate_lookup["District"]
    .astype(str)
    .str.strip()
    .str.upper()
)


print(
    "Climate lookup loaded:",
    climate_lookup.shape
)


# =========================================================
# LOAD HISTORICAL CROP SUPPORT DATA
# =========================================================

HISTORICAL_DATA_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "historical_crop_data.csv"
)


historical_crop_data = None


if HISTORICAL_DATA_PATH.exists():

    try:

        historical_crop_data = pd.read_csv(
            HISTORICAL_DATA_PATH
        )


        required_historical_columns = [
            "State",
            "District",
            "Crop",
            "historical_records",
        ]


        missing_historical_columns = [

            column

            for column in required_historical_columns

            if column not in historical_crop_data.columns

        ]


        if missing_historical_columns:

            print(
                "WARNING: Historical crop data "
                "is missing columns: "
                + ", ".join(
                    missing_historical_columns
                )
            )

            historical_crop_data = None


        else:

            # Normalize State

            historical_crop_data["_state_key"] = (
                historical_crop_data["State"]
                .astype(str)
                .str.strip()
                .str.upper()
            )


            # Normalize District

            historical_crop_data["_district_key"] = (
                historical_crop_data["District"]
                .astype(str)
                .str.strip()
                .str.upper()
            )


            # Normalize Crop

            historical_crop_data["_crop_key"] = (
                historical_crop_data["Crop"]
                .astype(str)
                .str.strip()
                .str.upper()
            )


            # Convert historical records

            historical_crop_data[
                "historical_records"
            ] = pd.to_numeric(
                historical_crop_data[
                    "historical_records"
                ],
                errors="coerce"
            ).fillna(0)


            print(
                "Historical crop support loaded:",
                f"{len(historical_crop_data):,}",
                "combinations"
            )


    except Exception as error:

        print(
            "WARNING: Could not load "
            "historical_crop_data.csv:"
        )

        print(error)

        historical_crop_data = None


else:

    print(
        "WARNING: historical_crop_data.csv "
        "not found."
    )


# =========================================================
# REQUEST MODEL
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
# HISTORICAL SUPPORT / SUITABILITY
# =========================================================

def check_crop_location_support(
    crop: str,
    state: str,
    district: str,
):

    # -----------------------------------------------------
    # Historical file unavailable
    # -----------------------------------------------------

    if historical_crop_data is None:

        return {

            "level": "unknown",

            "label":
                "Historical support unavailable",

            "reason": (
                "The prediction model generated an "
                "estimate, but historical crop-location "
                "support data is unavailable."
            ),

            "historical_records": None,

            "data_source": None,

        }


    crop_key = normalize_text(crop)

    state_key = normalize_text(state)

    district_key = normalize_text(district)


    # -----------------------------------------------------
    # Exact match
    # State + District + Crop
    # -----------------------------------------------------

    exact_match = historical_crop_data[

        (
            historical_crop_data["_state_key"]
            == state_key
        )

        &

        (
            historical_crop_data["_district_key"]
            == district_key
        )

        &

        (
            historical_crop_data["_crop_key"]
            == crop_key
        )

    ]


    if not exact_match.empty:

        records = int(
            exact_match[
                "historical_records"
            ].iloc[0]
        )


        # Strong support

        if records >= 10:

            return {

                "level": "high",

                "label":
                    "Strong historical support",

                "reason": (
                    f"{records} historical records were "
                    f"found for {crop} in "
                    f"{district}, {state}."
                ),

                "historical_records":
                    records,

                "data_source":
                    "Historical agricultural dataset",

            }


        # Moderate support

        if records >= 3:

            return {

                "level": "medium",

                "label":
                    "Moderate historical support",

                "reason": (
                    f"{records} historical records were "
                    f"found for {crop} in "
                    f"{district}, {state}."
                ),

                "historical_records":
                    records,

                "data_source":
                    "Historical agricultural dataset",

            }


        # Very limited support

        return {

            "level": "low",

            "label":
                "Very limited historical support",

            "reason": (
                f"Only {records} historical record(s) "
                f"were found for {crop} in "
                f"{district}, {state}."
            ),

            "historical_records":
                records,

            "data_source":
                "Historical agricultural dataset",

        }


    # -----------------------------------------------------
    # Crop exists in same State
    # but not in selected District
    # -----------------------------------------------------

    state_match = historical_crop_data[

        (
            historical_crop_data["_state_key"]
            == state_key
        )

        &

        (
            historical_crop_data["_crop_key"]
            == crop_key
        )

    ]


    if not state_match.empty:

        total_records = int(
            state_match[
                "historical_records"
            ].sum()
        )


        return {

            "level": "medium",

            "label":
                "State-level historical support",

            "reason": (
                f"Historical records exist for "
                f"{crop} in {state}, but no records "
                f"were found specifically for "
                f"{district}."
            ),

            "historical_records":
                total_records,

            "data_source":
                "Historical agricultural dataset",

        }


    # -----------------------------------------------------
    # Crop exists elsewhere in India
    # -----------------------------------------------------

    crop_match = historical_crop_data[

        historical_crop_data["_crop_key"]
        == crop_key

    ]


    if not crop_match.empty:

        total_records = int(
            crop_match[
                "historical_records"
            ].sum()
        )


        return {

            "level": "low",

            "label":
                "Low historical support",

            "reason": (
                f"{crop} exists in the historical "
                f"dataset, but no records were found "
                f"for {state}."
            ),

            "historical_records":
                total_records,

            "data_source":
                "Historical agricultural dataset",

        }


    # -----------------------------------------------------
    # Crop completely absent
    # -----------------------------------------------------

    return {

        "level": "low",

        "label":
            "No historical support",

        "reason": (
            f"No historical records were found "
            f"for {crop}."
        ),

        "historical_records": 0,

        "data_source":
            "Historical agricultural dataset",

    }


# =========================================================
# PREDICTION CONFIDENCE
# =========================================================

def calculate_confidence(suitability: dict):

    """
    Calculate a data-support confidence score.

    IMPORTANT:
    This is not the mathematical probability that the
    prediction is correct.

    It represents how strongly the requested crop and
    location are supported by historical data.
    """

    level = (
        suitability.get(
            "level",
            "unknown"
        )
        .strip()
        .lower()
    )


    records = suitability.get(
        "historical_records",
        0
    )


    if records is None:

        records = 0


    try:

        records = int(records)

    except (
        ValueError,
        TypeError,
    ):

        records = 0


    # -----------------------------------------------------
    # HIGH CONFIDENCE
    # -----------------------------------------------------

    if level == "high":

        if records >= 50:

            score = 95

        elif records >= 25:

            score = 90

        elif records >= 10:

            score = 85

        else:

            score = 80


        return {

            "score": score,

            "label":
                "High Confidence",

            "level":
                "high",

            "reason": (
                f"The selected crop and location have "
                f"{records} direct historical record(s). "
                f"The prediction has strong historical "
                f"data support."
            ),

        }


    # -----------------------------------------------------
    # MEDIUM CONFIDENCE
    # -----------------------------------------------------

    if level == "medium":

        if records >= 50:

            score = 75

        elif records >= 20:

            score = 70

        elif records >= 3:

            score = 65

        else:

            score = 60


        return {

            "score": score,

            "label":
                "Moderate Confidence",

            "level":
                "medium",

            "reason": (
                f"The prediction is supported by "
                f"{records} related historical record(s), "
                f"but direct crop-location coverage is "
                f"limited."
            ),

        }


    # -----------------------------------------------------
    # LOW CONFIDENCE
    # -----------------------------------------------------

    if level == "low":

        if records >= 100:

            score = 50

        elif records >= 20:

            score = 45

        elif records > 0:

            score = 35

        else:

            score = 25


        return {

            "score": score,

            "label":
                "Low Confidence",

            "level":
                "low",

            "reason": (
                "Historical data support for this exact "
                "crop and location is limited. The model "
                "can generate an estimate, but it should "
                "be interpreted cautiously."
            ),

        }


    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    return {

        "score": 20,

        "label":
            "Very Low Confidence",

        "level":
            "unknown",

        "reason": (
            "Historical crop-location support data is "
            "unavailable, so the prediction cannot be "
            "validated against known historical records."
        ),

    }


# =========================================================
# GET CLIMATE DATA
# =========================================================

def get_climate_data(
    state: str,
    district: str,
):

    state_key = normalize_text(
        state
    )

    district_key = normalize_text(
        district
    )


    result = climate_lookup[

        (
            climate_lookup["_state_key"]
            == state_key
        )

        &

        (
            climate_lookup["_district_key"]
            == district_key
        )

    ]


    if result.empty:

        raise ValueError(
            f"No climate data found for "
            f"{district}, {state}"
        )


    row = result.iloc[0]


    return {

        "rainfall":
            float(
                row["Rainfall"]
            ),

        "temperature":
            float(
                row["Temperature"]
            ),

    }


# =========================================================
# OPENWEATHER GEOCODING
# =========================================================

def get_coordinates(
    district: str,
    state: str,
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
            OPENWEATHER_API_KEY,

    }


    response = requests.get(
        url,
        params=params,
        timeout=15
    )


    response.raise_for_status()


    locations = response.json()


    if not locations:

        raise ValueError(
            f"Location not found: "
            f"{district}, {state}"
        )


    location = locations[0]


    return {

        "name":
            location.get(
                "name",
                district
            ),

        "latitude":
            float(
                location["lat"]
            ),

        "longitude":
            float(
                location["lon"]
            ),

        "country":
            location.get(
                "country",
                "IN"
            ),

    }


# =========================================================
# CURRENT WEATHER
# =========================================================

def get_current_weather(
    latitude: float,
    longitude: float,
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
            "metric",

    }


    response = requests.get(
        url,
        params=params,
        timeout=15
    )


    response.raise_for_status()


    weather = response.json()


    rainfall_1h = weather.get(
        "rain",
        {}
    ).get(
        "1h",
        0
    )


    description = "Unknown"


    if weather.get("weather"):

        description = weather[
            "weather"
        ][0].get(
            "description",
            "Unknown"
        )


    return {

        "temperature":
            float(
                weather["main"]["temp"]
            ),

        "rainfall_1h":
            float(
                rainfall_1h
            ),

        "description":
            description,

    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
def home():

    return {

        "message":
            "Smart Crop Yield Prediction API is running.",

        "historical_support_loaded":
            historical_crop_data is not None,

    }


# =========================================================
# OPTIONS
# =========================================================

@app.get("/options")
def get_options():

    states = sorted(

        climate_lookup["State"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()

    )


    districts = {}


    for state in states:

        state_key = normalize_text(
            state
        )


        state_districts = climate_lookup[

            climate_lookup["_state_key"]
            == state_key

        ]["District"]


        districts[state] = sorted(

            state_districts
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()

        )


    crops = sorted(

        historical_crop_data["Crop"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()

    ) if historical_crop_data is not None else []


    seasons = [

        "Autumn",

        "Kharif",

        "Rabi",

        "Summer",

        "Whole Year",

        "Winter",

    ]


    return {

        "states":
            states,

        "districts":
            districts,

        "crops":
            crops,

        "seasons":
            seasons,

    }


# =========================================================
# PREDICT
# =========================================================

@app.post("/predict")
def predict(
    data: PredictionRequest
):

    try:

        # =============================================
        # 1. HISTORICAL CLIMATE
        # =============================================

        climate = get_climate_data(
            data.State,
            data.District
        )


        rainfall = climate[
            "rainfall"
        ]


        temperature = climate[
            "temperature"
        ]


        # =============================================
        # 2. HISTORICAL SUPPORT
        # =============================================

        suitability = (
            check_crop_location_support(

                crop=data.Crop,

                state=data.State,

                district=data.District,

            )
        )


        # =============================================
        # 3. CONFIDENCE
        # =============================================

        confidence = calculate_confidence(
            suitability
        )


        # =============================================
        # 4. LOCATION
        # =============================================

        location = get_coordinates(
            data.District,
            data.State
        )


        # =============================================
        # 5. CURRENT WEATHER
        # =============================================

        current_weather = (
            get_current_weather(

                location["latitude"],

                location["longitude"],

            )
        )


        # =============================================
        # 6. MODEL INPUT
        # =============================================

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
                    temperature,

            }

        ])


        # =============================================
        # 7. MODEL PREDICTION
        # =============================================

        prediction_log = model.predict(
            input_data
        )[0]


        # =============================================
        # 8. CONVERT LOG TARGET
        # =============================================

        prediction = np.expm1(
            prediction_log
        )


        prediction = max(
            0,
            float(prediction)
        )


        # =============================================
        # 9. RESPONSE
        # =============================================

        return {

            "success":
                True,


            "predicted_yield":
                round(
                    prediction,
                    2
                ),


            "unit":
                "Yield (tonnes/hectare",


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


            # =========================================
            # SUITABILITY
            # =========================================

            "suitability":
                suitability,


            # =========================================
            # CONFIDENCE
            # =========================================

            "confidence":
                confidence,


            # =========================================
            # CLIMATE USED BY MODEL
            # =========================================

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
                    ),

            },


            # =========================================
            # CURRENT WEATHER
            # =========================================

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
                    ],

            },


            # =========================================
            # LOCATION
            # =========================================

            "location": {

                "district":
                    location[
                        "name"
                    ],

                "state":
                    data.State,

                "country":
                    location[
                        "country"
                    ],

                "latitude":
                    location[
                        "latitude"
                    ],

                "longitude":
                    location[
                        "longitude"
                    ],

            },

        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    except requests.exceptions.Timeout:

        raise HTTPException(
            status_code=504,
            detail=(
                "OpenWeather request timed out."
            )
        )


    except requests.exceptions.RequestException:

        raise HTTPException(
            status_code=502,
            detail=(
                "Could not retrieve weather "
                "or location data."
            )
        )


    except Exception as error:

        print(
            "Prediction error:",
            error
        )


        raise HTTPException(
            status_code=500,
            detail=(
                "Prediction failed. "
                "Please try again."
            )
        )