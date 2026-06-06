import os
import urllib.parse
class Config:

    SECRET_KEY = 'markethub'

    

    SQLALCHEMY_TRACK_MODIFICATIONS = False
   

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_123'
    
    password = urllib.parse.quote_plus('rakshitha@3302')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:{password}@localhost/markethub_db'
    

