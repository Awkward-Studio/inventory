FROM python:3.11.4

WORKDIR /usr/src/app

# system deps for postgres client
RUN apt-get update \
 && apt-get install -y libpq-dev gcc \
 && rm -rf /var/lib/apt/lists/*

# install Python deps
COPY inventory_api/requirements.txt ./
RUN pip3 install --upgrade pip \
 && pip3 install -r requirements.txt

# copy code
COPY inventory_api ./

EXPOSE 8000

# migrate → create superuser if missing → start gunicorn
CMD python manage.py migrate --noinput && \
    if ! python manage.py shell -c "import os,sys; from django.contrib.auth import get_user_model; sys.exit(0 if get_user_model().objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).exists() else 1)"; then \
        python manage.py createsuperuser --noinput \
          --username \"$DJANGO_SUPERUSER_USERNAME\" \
          --email    \"$DJANGO_SUPERUSER_EMAIL\"; \
    fi && \
    exec gunicorn -w \"$NUM_WORKERS\" -b 0.0.0.0:8000 inventory_api.wsgi
