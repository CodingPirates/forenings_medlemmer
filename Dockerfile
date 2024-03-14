FROM python:3.10
WORKDIR /app

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && apt-get install -y \
    graphviz \
    nodejs


RUN npm install -g npm

# This is not a nice way to install npm packages, but it is the
# closest it gets similar to venv-way of installing project-specific
# packages.
RUN mkdir -p /nodeapp
WORKDIR /nodeapp
COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm install
WORKDIR /app

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
