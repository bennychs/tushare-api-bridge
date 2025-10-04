from fastapi import FastAPI
import tushare as ts
import pandas as pd
import json
import os

# 从环境变量中读取Tushare TOKEN，这更安全
TS_TOKEN = os.getenv('TUSHARE_TOKEN')

app = FastAPI()
ts.set_token(TS_TOKEN)
pro = ts.pro_api()

@app.get("/")
def read_root():
    return {"message": "Tushare API Bridge is running!"}

@app.get("/stock/daily")
def get_stock_daily(ts_code: str, start_date: str, end_date: str):
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        result = df.to_json(orient="records")
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}