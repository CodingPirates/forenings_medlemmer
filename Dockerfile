FROM python:3.7

# Force stdin, stdout and stderr to be totally unbuffered.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Make the base directory for our app.
WORKDIR /app
COPY . /app

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 8000

COPY entrypoint.sh app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]


# Set the default command to be executed.
CMD gunicorn forenings_medlemmer.wsgi:application --bind 0.0.0.0:$PORT
