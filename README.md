# Smart Crop Suitability & Yield Prediction System

College ML group project.

## Goal
A farmer enters only:
- Crop
- State
- City
- Land area

The system:
1. Validates crop-region suitability using historical agricultural data.
2. Gets current weather automatically from a weather API.
3. Predicts expected crop yield using an ML model trained on historical data.
4. Estimates total production from predicted yield and land area.
5. Shows current weather/risk information.

## Current data
`data/raw/APY.csv` is the agricultural Area Production Statistics dataset being used as the starting point.

## Development order
1. Data profiling
2. Data cleaning
3. Crop-region suitability engine
4. Historical weather integration
5. Feature engineering
6. ML model training/evaluation
7. FastAPI backend
8. Frontend
9. Deployment

Do not train a model before completing data validation and cleaning.
