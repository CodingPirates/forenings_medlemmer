FROM python:3.8

# Force stdin, stdout and stderr to be totally unbuffered.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Make the base directory for our app.
WORKDIR /app
COPY . /app

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get install -y graphviz

# GET SASS
RUN wget https://github.com/sass/dart-sass/releases/download/1.24.4/dart-sass-1.24.4-linux-x64.tar.gz
RUN tar xf dart-sass-1.24.4-linux-x64.tar.gz
RUN rm dart-sass-1.24.4-linux-x64.tar.gz

EXPOSE 8000

COPY entrypoint.sh app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]


# Set the default command to be executed.
CMD gunicorn forenings_medlemmer.wsgi:application --bind 0.0.0.0:$PORT
