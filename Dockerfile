FROM python:3.8
WORKDIR /app

RUN apt-get update && \
    apt-get install -y graphviz

RUN wget -O /tmp/sass.tar.gz  https://github.com/sass/dart-sass/releases/download/1.25.0/dart-sass-1.25.0-linux-x64.tar.gz \
    && tar xf /tmp/sass.tar.gz -C /bin \
    && chmod -R a+rx /bin/dart-sass/

COPY pyproject.toml  pyproject.toml
COPY poetry.lock poetry.lock

ENV POETRY_VIRTUALENVS_CREATE false

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry install




EXPOSE 8000


COPY entrypoint.sh entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]

# Force stdin, stdout and stderr to be totally unbuffered.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /app

# Set the default command to be executed.
CMD gunicorn forenings_medlemmer.wsgi:application --bind 0.0.0.0:$PORT
