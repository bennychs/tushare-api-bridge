from fastapi import FastAPI, Request
import tushare as ts
import pandas as pd
import json
import os
# --- 新增的库，用于计时和日志 ---
import time
from datetime import datetime

# 从环境变量中读取Tushare TOKEN
TS_TOKEN = os.getenv('TUSHARE_TOKEN')

app = FastAPI()
ts.set_token(TS_TOKEN)
pro = ts.pro_api()

@app.get("/")
def read_root():
    return {"message": "Tushare API Bridge (Upgraded Version) is running!"}

# === 全新的、强大的通用接口 (已添加详细日志) ===
@app.post("/generic")
async def get_generic_data(request: Request):
    """
    一个通用的Tushare API调用接口。
    接收一个JSON，包含要调用的api_name和params。
    """
    # --- 1. 在请求开始时，记录时间和打印日志 ---
    start_time = time.time()
    print(f"[{datetime.now()}] --- ✅ Request to /generic received. Processing start...")

    try:
        # 从请求体中获取JSON数据
        body = await request.json()
        api_name = body.get("api_name")
        params = body.get("params", {})
        # 打印收到的参数
        print(f"[{datetime.now()}] --- API Name: {api_name}, Params: {str(params)}")


        if not api_name:
            print(f"[{datetime.now()}] --- ❌ Error: api_name is required.")
            return {"error": "api_name is required."}

        # 检查Tushare Pro实例中是否存在该API方法
        if hasattr(pro, api_name):
            # 动态获取API方法
            api_method = getattr(pro, api_name)

            # --- 2. 在调用 Tushare API 前后打印日志，这是最关键的计时点 ---
            print(f"[{datetime.now()}] ---> Calling Tushare API: '{api_name}'...")
            df = api_method(**params)
            print(f"[{datetime.now()}] <--- Tushare API call finished.")


            if isinstance(df, pd.DataFrame):
                result = df.to_json(orient="records")
                # --- 3. 在返回前，计算并打印总耗时 ---
                duration = time.time() - start_time
                print(f"[{datetime.now()}] --- ✅ Request successful. Total duration: {duration:.2f} seconds.")
                return json.loads(result)
            else:
                # Tushare的某些接口可能不返回DataFrame
                duration = time.time() - start_time
                print(f"[{datetime.now()}] --- ✅ Request successful (non-DataFrame). Total duration: {duration:.2f} seconds.")
                return df
        else:
            duration = time.time() - start_time
            print(f"[{datetime.now()}] --- ❌ Error: API not found. Total duration: {duration:.2f} seconds.")
            return {"error": f"API '{api_name}' not found in Tushare Pro."}

    except Exception as e:
        # --- 4. 如果发生任何错误，也打印耗时和错误信息 ---
        duration = time.time() - start_time
        print(f"[{datetime.now()}] --- 💥 Exception occurred! Total duration: {duration:.2f} seconds. Error: {str(e)}")
        return {"error": str(e)}

# === 保留旧接口用于简单示例 ===
@app.get("/stock/company")
def get_stock_company(ts_code: str):
    try:
        df = pro.stock_company(ts_code=ts_code, fields='introduction')
        if not df.empty:
            introduction = df.iloc[0]['introduction']
            return {"introduction": introduction}
        else:
            return {"error": "Company not found."}
    except Exception as e:
        return {"error": str(e)}
