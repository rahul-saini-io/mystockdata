class Config:
    SECRET_KEY = 'dev-secret-key-for-local-development'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/mystocktrading'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MySQL connection settings
    MYSQL_HOST = 'localhost'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DATABASE = 'mystocktrading'
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = 'change-this-in-production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}