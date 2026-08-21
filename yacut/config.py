import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DISK_TOKEN = os.getenv('DISK_TOKEN')
    DISK_API_HOST = 'https://cloud-api.yandex.net'
    DISK_API_VERSION = 'v1'
    REQUEST_UPLOAD_URL = (
        f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources/upload')
    DOWNLOAD_LINK_URL = (
        f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources/download')
    PUBLISH_URL = f'{DISK_API_HOST}/{DISK_API_VERSION}/disk/resources/publish'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024