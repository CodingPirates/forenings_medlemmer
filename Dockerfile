FROM python:3.8
WORKDIR /app

RUN apt-get update && apt-get install -y \
    graphviz \
    nodejs \
    npm

RUN npm install -g npm

COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm install

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
