import requests
import json

url = "https://opendata.cwa.gov.tw/linked/graphql"
api_key = "CWA-BF79A9FE-5D5B-4C81-B925-EBD37EDD9655"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"{api_key}"
}

# 以經緯度查詢行政區與鄉鎮天氣預報資料
def queryForecastByLocation(longitude, latitude):
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
      }}
    }}
  }}
}}
"""

  response = requests.post(url, json={"query": query}, headers=headers)
  if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))  # 格式化輸出 JSON
  else:
    print(f"請求失敗，狀態碼: {response.status_code}, 錯誤訊息: {response.text}")
  return response

# 以經緯度查詢空氣品質指標與氣象觀測資料
def queryWeatherByLocation(longitude, latitude):
    query = f"""
    query aqi {{
      aqi(longitude: {longitude}, latitude: {latitude}) {{
        sitename
        county
        aqi
        pollutant
        status
        so2
        co
        o3
        o3_8hr
        pm10
        pm2_5
        no2
        nox
        no
        wind_speed
        wind_direc
        publishtime
        co_8hr
        pm2_5_avg
        pm10_avg
        so2_avg
        longitude
        latitude
        siteid
        station {{
          stationId
          locationName
          latitude
          longitude
          time {{
            obsTime
          }}
          weatherElement {{
            elementName
            elementValue
          }}
        }}
        town {{
          ctyCode
          ctyName
          townCode
          townName
          villageCode
          villageName
        }}
      }}
    }}
    """
    
    response = requests.post(url, json={"query": query}, headers=headers)
    return response

# result = queryWeatherByLocation(120.635324, 24.030304)
# print(result)