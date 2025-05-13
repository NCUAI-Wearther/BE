import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
    #     'mysql+pymysql://myAdmin:Wearther04@wearther-db.mysql.database.azure.com/wearther?ssl_ca=../etc/ssl/ca-cert.pem')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'mysql+pymysql://myAdmin:Wearther04@localhost:3306/wearther')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CWA_API_URL = os.environ.get('CWA_API_URL', 'https://opendata.cwa.gov.tw/linked/graphql')
    CWA_API_KEY = os.environ.get('CWA_API_KEY', 'CWA-BF79A9FE-5D5B-4C81-B925-EBD37EDD9655')