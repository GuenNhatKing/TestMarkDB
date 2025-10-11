import pymysql
pymysql.install_as_MySQLdb()

from .celery import app as celery_app

__all__ = ('celery_app',)

# Run celery: celery -A root worker --loglevel=INFO --pool=threads