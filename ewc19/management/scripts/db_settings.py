import os

HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
USER = os.environ.get('MYSQL_USER', 'admin')
PASSWORD= os.environ.get('MYSQL_PASSWORD', 'admin')
DATABASE= os.environ.get('MYSQL_DATABASE', 'interview')
PORT = os.environ.get('MYSQL_PORT', '3306')
