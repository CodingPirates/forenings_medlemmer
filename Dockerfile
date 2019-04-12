FROM python:3.7

# Force stdin, stdout and stderr to be totally unbuffered.
ENV PYTHONUNBUFFERED 1

# Make the base directory for our app.
RUN mkdir /app
COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt && python manage.py migrate

EXPOSE 8000
EXPOSE 5432

# Set the default command to be executed.
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
