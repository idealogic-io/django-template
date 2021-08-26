FROM python:3.6

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get install -y poppler-utils && \
    apt-get install gettext -y

COPY . /django_boilerplate_app

WORKDIR /django_boilerplate_app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apt-get remove -y build-essential && \
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache

CMD ["/django_boilerplate_app/docker/start.sh"]

EXPOSE 8000
