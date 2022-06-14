FROM python:3-alpine AS base
WORKDIR /usr/src/database
COPY ./database .

FROM python:3-alpine AS producer
WORKDIR /usr/src/app
COPY ./producer/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./producer .
CMD ["python","-u","producer.py"]

FROM base AS consumer
WORKDIR /usr/src/consumer
COPY ./consumer/requirements.txt ./
RUN apk add --no-cache python3 postgresql-libs
RUN apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
RUN pip install --upgrade --no-cache-dir -r requirements.txt
RUN apk --purge del .build-deps
COPY ./consumer .
CMD ["python","-u","consumer.py"]

FROM base as api
WORKDIR /usr/src/api
COPY ./api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./api .
CMD ["uvicorn","api:app","--host","0.0.0.0","--port","8000"]