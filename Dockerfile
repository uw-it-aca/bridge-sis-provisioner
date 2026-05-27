ARG DJANGO_CONTAINER_VERSION=3.1.1

FROM us-docker.pkg.dev/uwit-mci-axdd/containers/django-container:${DJANGO_CONTAINER_VERSION} AS app-container

USER root

RUN mkdir /data
RUN chown -R acait:acait /data

USER acait

COPY --chown=acait:acait . /app/
COPY --chown=acait:acait docker/ /app/project/

RUN /app/bin/pip install -r requirements.txt

FROM us-docker.pkg.dev/uwit-mci-axdd/containers/django-test-container:${DJANGO_CONTAINER_VERSION} AS app-test-container

COPY --from=app-container /app/ /app/
COPY --from=app-container /static/ /static/
COPY --from=app-container /data/ /data/
