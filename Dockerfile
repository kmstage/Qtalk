FROM tiangolo/uwsgi-nginx-flask:python3.7
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt
ENV STATIC_URL /static
ENV STATIC_PATH /app/Qtalk/static
COPY ./app /app
RUN python3 create_db.py

