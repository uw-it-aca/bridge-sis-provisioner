ARG DJANGO_CONTAINER_VERSION=1.4.1

FROM gcr.io/uwit-mci-axdd/django-container:${DJANGO_CONTAINER_VERSION} as app-container

USER root

RUN apt-get update && apt-get install mysql-client libmysqlclient-dev -y

# Add Google Cloud SDK package repository to the system
RUN curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/google-cloud-sdk.tar.gz \
    && tar zxvf google-cloud-sdk.tar.gz -C /usr/local/ \
    && /usr/local/google-cloud-sdk/install.sh
# Add Google Cloud SDK to the PATH
ENV PATH $PATH:/usr/local/google-cloud-sdk/bin

RUN mkdir /data
RUN chown -R acait:acait /data

USER acait

ADD --chown=acait:acait . /app/
ADD --chown=acait:acait docker/ /app/project/

RUN /app/bin/pip install -r requirements.txt
RUN /app/bin/pip install mysqlclient

FROM gcr.io/uwit-mci-axdd/django-test-container:${DJANGO_CONTAINER_VERSION} as app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/
COPY --from=app-container /data/ /data/
