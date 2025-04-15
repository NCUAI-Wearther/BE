from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

import modules.db as db
import modules.cwa as cwa
import modules.model as model

app = FastAPI(title="Wearther API", description="天氣穿著推薦API")

# 啟用CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# region 使用者
@app.post("/login", response_model=model.UserResponse)
async def login(request: model.UserLogin):
    response = db.login(request.email, request.password)
    print("response", response)
    if not response:
        raise HTTPException(status_code=401, detail="登入失敗")
    return response

@app.post("/register", response_model=model.MessageResponse)
async def register(request: model.UserCreate):
    success, status = db.register(request.username, request.email, request.password, request.profile_pic_url)
    if not success or status >= 400:
        raise HTTPException(status_code=400, detail=success)
    return {"message": "註冊成功"}
# endregion

# region 天氣API
@app.post("/getForecast", response_model=model.ForecastResponse)
async def get_forecast(request: model.LocationRequest):
    result = cwa.queryForecastByLocation(request.longitude, request.latitude)
    if result.status_code != 200:
        print(f"請求失敗，狀態碼: {result.status_code}, 錯誤訊息: {result.text}")
        raise HTTPException(status_code=result.status_code, detail=result.text)
    return {"message": "成功取得預報資料", "data": result.json()}

@app.post("/getWeather", response_model=model.WeatherResponse)
async def get_weather(request: model.LocationRequest):
    result = cwa.queryWeatherByLocation(request.longitude, request.latitude)
    if result.status_code != 200:
        print(f"請求失敗，狀態碼: {result.status_code}, 錯誤訊息: {result.text}")
        raise HTTPException(status_code=result.status_code, detail=result.text)
    return {"message": "成功取得天氣資料", "data": result.json()}
# endregion

# region OUTFITS
@app.post("/outfits", response_model=model.OutfitResponse)
async def create_outfit(outfit: model.OutfitCreate):
    created_outfit = db.create_outfit(outfit.outfits)
    if not created_outfit:
        raise HTTPException(status_code=500, detail="創建穿著失敗")
    return created_outfit

@app.get("/outfits", response_model=List[model.OutfitResponse])
async def get_outfits():
    outfits = db.get_outfits()
    if outfits is None:
        raise HTTPException(status_code=500, detail="獲取穿著列表失敗")
    return outfits
# endregion

# 健康檢查端點
@app.get("/health", response_model=model.MessageResponse)
async def health_check():
    return {"message": "健康狀態良好", "service": "wearther-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)