import os
DEBUG = True

'''class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}'''

SECRET_KEY = 'secret'
