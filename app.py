import json
from flask import Flask, request, jsonify
import modules.db as db, modules.cwa as cwa

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    account = data.get("account")
    password = data.get("password")

    return db.login(account, password)

@app.route("/getForecast", methods=["POST"])
def getForecast():
    data = request.json
    longitude = data.get("longitude")
    latitude = data.get("latitude")
    
    result = cwa.queryForecastByLocation(longitude, latitude)
    message = result.text
    
    if result.status_code == 200:
        data = result.json()
        return jsonify({"message": "成功取得預報資料", "data": data}), 200
    else:
        print(f"請求失敗，狀態碼: {result.status_code}, 錯誤訊息: {result.text}")
        return jsonify({"message": message}), 404
    
@app.route("/getWeather", methods=["POST"])
def getWeather():
    data = request.json
    longitude = data.get("longitude")
    latitude = data.get("latitude")
    
    result = cwa.queryWeatherByLocation(longitude, latitude)
    message = result.text
    
    if result.status_code == 200:
        data = result.json()
        return jsonify({"message": "成功取得天氣資料", "data": data}), 200
    else:
        print(f"請求失敗，狀態碼: {result.status_code}, 錯誤訊息: {result.text}")
        return jsonify({"message": message}), 404

if __name__ == "__main__":
    app.run(debug=True)