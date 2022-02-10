FROM gcr.io/uwit-mci-axdd/django-container:1.3.8 as app-container

USER root

RUN apt-get update && apt-get install mysql-client libmysqlclient-dev -y

RUN mkdir /data
RUN chown -R acait:acait /data

USER acait

ADD --chown=acait:acait sis_provisioner/VERSION /app/sis_provisioner/
ADD --chown=acait:acait setup.py /app/
ADD --chown=acait:acait requirements.txt /app/

RUN . /app/bin/activate && pip install -r requirements.txt
RUN . /app/bin/activate && pip install mysqlclient

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ project/

FROM gcr.io/uwit-mci-axdd/django-test-container:1.3.8 as app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/
COPY --from=app-container /data/ /data/
