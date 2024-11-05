import os
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from dotenv import load_dotenv
from pathlib import Path
import logging

basedir = os.path.abspath(Path(__file__).parents[2])
load_dotenv(os.path.join(basedir, '.env'))

# Configuración de logger
logger = logging.getLogger(__name__)

class Config(object):
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Azure Monitor Configuration
    CONNECTION_STRING = os.environ.get('CONNECTION_STRING')
    if not CONNECTION_STRING:
        logger.warning("CONNECTION_STRING no está configurada. Algunas funcionalidades podrían no estar disponibles.")
    
    OTEL_SERVICE_NAME = "recurso-aplicada"
    
    APISPEC_SPEC = APISpec(
        title='Estructura Flask API', 
        version='1.0.0', 
        openapi_version='2.0', 
        plugins=[MarshmallowPlugin()],
        authorizations={
            'description': 'Authorization HTTP header with JWT access token, like: Authorization: Bearer asdf.qwer.zxcv',
            'in': 'header',
            'type': 'string',
            'required': True
        }
    )
    APISPEC_SECURITY_DEFINITIONS = {
        'bearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT'
        }
    }

    @staticmethod
    def init_app(app):
        pass

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI')
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST')
    CACHE_REDIS_PORT = os.environ.get('REDIS_PORT')
    CACHE_REDIS_DB = os.environ.get('REDIS_DB')
    CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    OTEL_SERVICE_NAME = "recurso-aplicada-test"

class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    OTEL_SERVICE_NAME = "recurso-aplicada-dev"
        
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI')
    OTEL_SERVICE_NAME = "recurso-aplicada-prod"
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

def factory(app: str) -> Config:
    configuration = {
        'testing': TestConfig,
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    
    return configuration[app]