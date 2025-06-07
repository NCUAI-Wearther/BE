import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'mysql+pymysql://root:1234@35.185.153.118:3306/wearther')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    cloud_name = "dksm412hl"
    api_key = "934399514943984"
    api_secret = "BQePHUC0mvr7rMUZZ92-LzOtLvY"

    PROJECT_ID = "amazing-pipe-462112-h2"
    
    RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '4e509b308cmshbb0dc1ac56b74fcp17ef16jsn5058e2f2a08d')
    RAPIDAPI_HOST = os.environ.get('RAPIDAPI_HOST', 'try-on-diffusion.p.rapidapi.com')
    
    CWA_API_URL = os.environ.get('CWA_API_URL', 'https://opendata.cwa.gov.tw/linked/graphql')
    CWA_API_KEY = os.environ.get('CWA_API_KEY', 'CWA-BF79A9FE-5D5B-4C81-B925-EBD37EDD9655')
