import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from data import fetch_data
from model import train_and_predict

app = FastAPI(title="Stock Predictor API")

allowed_origins = ["http://localhost:5173"]
if os.environ.get("FRONTEND_URL"):
    allowed_origins.append(os.environ["FRONTEND_URL"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/predict")
def predict(ticker: str = "AAPL"):
    df = fetch_data(ticker)

    if df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for '{ticker}'")

    result = train_and_predict(df)
    result["ticker"] = ticker.upper()
    return result
