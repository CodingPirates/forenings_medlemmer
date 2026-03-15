FROM python:3.12
WORKDIR /app

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get update && apt-get install -y \
    graphviz \
    chromium \
    chromium-driver \
    nodejs \
    firefox-esr \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget --content-disposition "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" -P /tmp \
    && tar -xJf /tmp/firefox-*.tar.xz -C /opt/ \
    && rm -f /usr/bin/firefox \
    && ln -s /opt/firefox/firefox /usr/bin/firefox \
    && rm /tmp/firefox-*.tar.xz
    
# Debug: Check Firefox binary location and version
RUN find / -name firefox || true
RUN /usr/bin/firefox --version || true

# Install GeckoDriver for Firefox automation


RUN apt-get update && apt-get install -y jq
RUN GECKO_VERSION=$(wget -qO- https://api.github.com/repos/mozilla/geckodriver/releases/latest | jq -r .tag_name) \
    && wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/${GECKO_VERSION}/geckodriver-${GECKO_VERSION}-linux64.tar.gz" \
    && tar -xzf /tmp/geckodriver.tar.gz -C /tmp \
    && rm -f /usr/local/bin/geckodriver \
    && mv /tmp/geckodriver /usr/local/bin/geckodriver \
    && chmod +x /usr/local/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

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
