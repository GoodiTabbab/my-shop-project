
من اجل الطلب الثاني
pip install waitress
waitress-serve --threads=100 --connection-limit=2000 --backlog=2048 --port=8000 core.wsgi:application 


#seeding
python manage.py shell -c "exec(open('seed.py', encoding='utf-8').read())"

 python manage.py shell -c "exec(open('seed_carts.py', encoding='utf-8').read())"



pip install django-prometheus

ننزل بروميثيوس 3.5.3 ونغير فايل اليامل
Download | Prometheus
cd C:\prometheus
.\prometheus.exe

http://localhost:9090


Download Grafana


من اجل الطلب الثالث
1-Install Redis on your machine and start the redis server
Run each command in a separate terminal window
1-celery -A core worker -l info
2-run python server
3-run : locust 
Watch the celery window while pushing notifications
