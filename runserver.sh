
cd ewc19

export MYSQL_DATABASE='interview'
export MYSQL_USER='biobot'
export MYSQL_PASSWORD='MYSQLPASSWORD'
export MYSQL_HOST='127.0.0.1'
export MYSQL_PORT='3306'

python manage.py runserver
