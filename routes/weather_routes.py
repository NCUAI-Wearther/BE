from flask import Blueprint, request, jsonify
import requests
from config import Config

weather_bp = Blueprint('weather_bp', __name__)
CWA_API_URL = Config.CWA_API_URL
CWA_API_KEY = Config.CWA_API_KEY

# 以經緯度查詢空氣品質指標與氣象觀測資料
@weather_bp.route('/current', methods=['GET'])
def get_current_weather():
    try:
        longitude = request.args.get('longitude')
        latitude = request.args.get('latitude')
        
        if not longitude or not latitude:
            return jsonify({
                'success': False,
                'message': 'Longitude and latitude are required'
            }), 400

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": CWA_API_KEY
        }

        query = f"""
        query aqi {{
          aqi(longitude: {longitude}, latitude: {latitude}) {{
            sitename,
            county,
            station {{
              WeatherElement {{
                Weather,
                AirTemperature,
                RelativeHumidity,
                DailyExtreme {{
                  DailyHigh {{
                    TemperatureInfo {{
                      AirTemperature,
                      Occurred_At {{
                        DateTime
                      }}
                    }}
                  }},
                  DailyLow {{
                    TemperatureInfo {{
                      AirTemperature,
                      Occurred_At {{
                        DateTime
                      }}
                    }}
                  }}
                }}
              }}
            }},
            town {{
              ctyName,
              townName,
              villageName
              forecast72hr{{
                  ProbabilityOfPrecipitation{{
                    ElementName,
                    Time{{
                      StartTime,
                      EndTime
                      ProbabilityOfPrecipitation
                    }}
                  }}
              }}
            }}
          }}
        }}
        """

        cwa_response = requests.post(CWA_API_URL, json={"query": query}, headers=headers)

        if cwa_response.status_code != 200 or 'errors' in cwa_response.json():
            return jsonify({
                'success': False,
                'message': f'External API error: {cwa_response.status_code}, {cwa_response.text}'
            }), 500

        data = cwa_response.json()
        aqi_data = data.get('data', {}).get('aqi', {})
        weather = aqi_data[0]['station']['WeatherElement']
        
        ctyName =aqi_data[0]['town']['ctyName']
        townName =aqi_data[0]['town']['ctyName']
        villageName =aqi_data[0]['town']['villageName']
        max_temp = weather['DailyExtreme']['DailyHigh']['TemperatureInfo']['AirTemperature']
        min_temp = weather['DailyExtreme']['DailyLow']['TemperatureInfo']['AirTemperature']
        current_temp = weather['AirTemperature']
        humidity = weather['RelativeHumidity']
        weather_condition = weather['Weather']

        probabilities = aqi_data[0]['town']['forecast72hr']['ProbabilityOfPrecipitation']['Time']
        probability = max(probabilities[0]['ProbabilityOfPrecipitation'],probabilities[1]['ProbabilityOfPrecipitation'])
        response = {
          "ctyName": ctyName,
          "townName":townName,
          "villageName":villageName,
          "max_temp": float(max_temp),
          "min_temp": float(min_temp),
          "current_temp": float(current_temp),
          "humidity": float(humidity),
          "weather_condition": weather_condition,
          "probability":probability
        }
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting current weather data: {str(e)}'
        }), 500