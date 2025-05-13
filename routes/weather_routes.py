from flask import Blueprint, request, jsonify
import requests
from routes.user_routes import token_required
from config import Config

weather_bp = Blueprint('weather_bp', __name__)
CWA_API_URL = Config.CWA_API_URL
CWA_API_KEY = Config.CWA_API_KEY

# 以經緯度查詢行政區與鄉鎮天氣預報資料
@weather_bp.route('/forecast', methods=['GET'])
def get_forecast():
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
          query town {{
            town (Longitude: {longitude}, Latitude: {latitude}) {{
              ctyCode,
              ctyName,
              townCode,
              townName,
              villageCode,
              villageName,
              forecast72hr {{
                LocationName,
                Geocode,
                Latitude,
                Longitude,
                Temperature {{
                  ElementName,
                  Time {{
                    DataTime,
                    Temperature
                  }}
                }},
                ComfortIndex {{
                  ElementName,
                  Time {{
                    DataTime,
                    ComfortIndex,
                    ComfortIndexDescription
                  }}
                }},
                WindSpeed {{
                  ElementName,
                  Time {{
                    DataTime,
                    WindSpeed,
                    BeaufortScale
                  }}
                }},
                ProbabilityOfPrecipitation {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    ProbabilityOfPrecipitation
                  }}
                }},
                Weather {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    Weather,
                    WeatherCode
                  }}
                }},
                WeatherDescription {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    WeatherDescription
                  }}
                }}
              }},
              forecastWeekday {{
                LocationName,
                Geocode,
                Latitude,
                Longitude,
                Temperature {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    Temperature
                  }}
                }},
                #DewPoint,
                #MaxTemperature,
                #MinTemperature,
                #RelativeHumidity,
                #MaxApparentTemperature,
                #MinApparentTemperature,
                MaxComfortIndex {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    MaxComfortIndex,
                    MaxComfortIndexDescription
                  }}
                }},
                MinComfortIndex {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    MinComfortIndex,
                    MinComfortIndexDescription
                  }}
                }},
                ProbabilityOfPrecipitation {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    ProbabilityOfPrecipitation
                  }}
                }},
                WindSpeed {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    WindSpeed,
                    BeaufortScale
                  }}
                }},
                UVIndex {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    UVIndex,
                    UVExposureLevel
                  }}
                }},
                Weather {{
                  ElementName,
                  Time {{
                    StartTime,
                    EndTime,
                    Weather,
                    WeatherCode
                  }}
                }},
              }},
            }}
          }}
        """

        response = requests.post(CWA_API_URL, json={"query": query}, headers=headers)

        if response.status_code != 200 or 'errors' in response.json():
            return jsonify({
                'success': False,
                'message': f'CWA API error: {response.status_code}, {response.text}'
            }), 500

        data = response.json()

        town_data = data.get('data', {}).get('town', {})

        result = {
            'test': town_data
        }
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting forecast data: {str(e)}'
        }), 500

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
            aqi,
            pollutant,
            status,
            so2,
            co,
            o3,
            o3_8hr,
            pm10,
            pm2_5,
            no2,
            nox,
            no,
            wind_speed,
            wind_direc,
            publishtime,
            co_8hr,
            pm2_5_avg,
            pm10_avg,
            so2_avg,
            longitude,
            latitude,
            siteid,
            station {{
              StationId,
              StationName,
              ObsTime {{
                DateTime
              }},
              GeoInfo {{
                Coordinates {{
                  CoordinateName,
                  CoordinateFormat,
                  StationLatitude,
                  StationLongitude
                }},
                StationAltitude,
                CountyName,
                TownName,
                CountyCode,
                TownCode
              }},
              WeatherElement {{
                Weather,
                Now {{
                  Precipitation
                }},
                WindDirection,
                WindSpeed,
                AirTemperature,
                RelativeHumidity,
                AirPressure,
                GustInfo {{
                  PeakGustSpeed,
                  Occurred_At {{
                    WindDirection,
                    DateTime
                  }}
                }},
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
              ctyCode,
              ctyName,
              townCode,
              townName,
              villageCode,
              villageName
              #forecast72hr, forecastWeekday...
            }}
          }}
        }}
        """
        
        response = requests.post(CWA_API_URL, json={"query": query}, headers=headers)
        
        # 檢查 API 回應
        if response.status_code != 200 or 'errors' in response.json():
            return jsonify({
                'success': False,
                'message': f'External API error: {response.status_code}, {response.text}'
            }), 500
        
        data = response.json()

        aqi_data = data.get('data', {}).get('aqi', {})
        
        return jsonify({
            'success': True,
            'data': aqi_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting current weather data: {str(e)}'
        }), 500