web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn Brujitas.wsgi:application --bind 0.0.0.0:$PORT --timeout 180 --log-file -
