นายภฤศ ตัณฑ์วรกุล 6601012610083

git clone https://github.com/Nextjingjing/quizw12

cd quizw12

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate
