import os
from fastapi import FastAPI, BackgroundTasks
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from polygon import RESTClient
from typing import List
from dotenv import load_dotenv

from database import engine, get_db, Base
from models import OptionData, OptionDataRequest, OptionDataResponse

from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Create tables
Base.metadata.create_all(bind=engine)

def collect_and_store_data(request: OptionDataRequest):
    client = RESTClient(os.getenv("POLYGON_API_KEY"))
    db = next(get_db())
    try:
        for a in client.list_aggs(request.symbol, request.multiplier, request.timespan, request.from_date, request.to_date):
            option_data = {
                'symbol': request.symbol,
                'timestamp': datetime.fromtimestamp(a.timestamp / 1000),
                'volume': a.volume,
                'vwap': a.volume_weighted_average_price,
                'open': a.open,
                'close': a.close,
                'high': a.high,
                'low': a.low,
                'transactions': a.transactions
            }
            
            stmt = insert(OptionData).values(**option_data)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=['symbol', 'timestamp']
            )
            db.execute(stmt)
        
        db.commit()
        print(f"Data for {request.symbol} from {request.from_date} to {request.to_date} stored successfully.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
        raise
    finally:
        db.close()

@app.post("/collect_data/")
async def api_collect_data(request: OptionDataRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(collect_and_store_data, request)
    return {"message": f"Data collection for {request.symbol} has been initiated."}

@app.get("/option_data/", response_model=List[OptionDataResponse])
async def get_option_data(symbol: str, start_date: str, end_date: str):
    db = next(get_db())
    try:
        data = db.query(OptionData).filter(
            OptionData.symbol == symbol,
            OptionData.timestamp.between(start_date, end_date)
        ).all()
        return data
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)