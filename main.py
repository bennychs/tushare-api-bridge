from fastapi import FastAPI, Request
import tushare as ts
import pandas as pd
import json
import os

# 从环境变量中读取Tushare TOKEN
TS_TOKEN = os.getenv('TUSHARE_TOKEN')

app = FastAPI()
ts.set_token(TS_TOKEN)
pro = ts.pro_api()

@app.get("/")
def read_root():
    return {"message": "Tushare API Bridge (Upgraded Version) is running!"}

# === 全新的、强大的通用接口 ===
@app.post("/generic")
async def get_generic_data(request: Request):
    """
    一个通用的Tushare API调用接口。
    接收一个JSON，包含要调用的api_name和params。
    """
    try:
        # 从请求体中获取JSON数据
        body = await request.json()
        api_name = body.get("api_name")
        params = body.get("params", {})

        if not api_name:
            return {"error": "api_name is required."}

        # 检查Tushare Pro实例中是否存在该API方法
        if hasattr(pro, api_name):
            # 动态获取API方法
            api_method = getattr(pro, api_name)
            # 使用**params动态传递参数并调用方法
            df = api_method(**params)

            if isinstance(df, pd.DataFrame):
                result = df.to_json(orient="records")
                return json.loads(result)
            else:
                # Tushare的某些接口可能不返回DataFrame
                return df
        else:
            return {"error": f"API '{api_name}' not found in Tushare Pro."}

    except Exception as e:
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