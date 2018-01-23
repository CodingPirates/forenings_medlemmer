FROM python:3.4

# Force stdin, stdout and stderr to be totally unbuffered.
ENV PYTHONUNBUFFERED 1

# Make the base directory for our app.
COPY . /usr/app
WORKDIR /usr/app

# Copy python requirements file.
COPY requirements.txt /usr/app/

# Install from the requirements file.
RUN pip install -r requirements.txt \
    && python manage.py migrate

EXPOSE 8000
EXPOSE 35729

# Set the default command to be executed.
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8000
