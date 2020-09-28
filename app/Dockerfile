# pull official base image
FROM python:3.7-alpine
# set work directory

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create directory for the app user
RUN mkdir -p /app

# create the appropriate directories
ENV HOME=/app
ENV APP_HOME=/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install psycopg2 dependencies
RUN apk update \
    && apk add --no-cache --virtual .pynacl_deps build-base \
    && apk add postgresql-dev gcc python3-dev musl-dev libressl-dev libffi-dev

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh $APP_HOME

# copy project
COPY . $APP_HOME

ENTRYPOINT ["/app/web/entrypoint.sh"]